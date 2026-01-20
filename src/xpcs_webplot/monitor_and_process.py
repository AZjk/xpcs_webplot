import os
import time
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .webplot_cli import convert_one_file
from .html_utlits import combine_all_htmls
import logging
import h5py


logger = logging.getLogger(__name__)


logger = logging.getLogger(__name__)


class HDF5FileHandler(FileSystemEventHandler):
    """
    File system event handler for monitoring and processing HDF5 files.

    Watches for new .hdf files (typically via renaming from .hdf.temp) and
    adds them to a processing queue when fully written and readable.

    Parameters
    ----------
    task_queue : multiprocessing.Queue
        Queue to which ready HDF files will be added for processing.
    stop_flag : multiprocessing.Value
        Shared boolean flag to signal when to stop monitoring.
    max_wait : float, optional
        Maximum time (in seconds) to wait for file to stabilize. Default is 60.
    check_interval : float, optional
        Time interval (in seconds) between file stability checks. Default is 0.5.

    Attributes
    ----------
    task_queue : multiprocessing.Queue
        Queue for file processing tasks.
    stop_flag : multiprocessing.Value
        Stop signal for the handler.
    max_wait : float
        Maximum wait time for file stability.
    check_interval : float
        Check interval for file stability.

    Methods
    -------
    on_created(event)
        Handle file creation events.
    on_moved(event)
        Handle file rename events.
    process_hdf_file(file_path)
        Process and queue an HDF file.
    wait_for_file_stability(file_path)
        Wait for file to be fully written and readable.

    See Also
    --------
    producer : Uses this handler to monitor directories
    consumer : Processes files from the queue

    Notes
    -----
    This handler is designed to work with the watchdog library's Observer
    pattern for file system monitoring.
    """
    def __init__(self, task_queue, stop_flag, max_wait=60, check_interval=0.5):
        self.task_queue = task_queue
        self.stop_flag = stop_flag
        self.max_wait = max_wait  # Max wait time for file to be fully written
        self.check_interval = check_interval  # Interval to check file size stability

    def on_created(self, event):
        """
        Handle file creation events.

        Called when a new file is created. Ignores temporary files and
        processes .hdf files directly if created (not renamed).

        Parameters
        ----------
        event : FileSystemEvent
            Event object containing information about the created file.

        Returns
        -------
        None

        Notes
        -----
        - Ignores directory creation events
        - Ignores .hdf.temp files (waits for rename)
        - Processes .hdf files that are created directly
        """
        if event.is_directory:
            return

        file_path = event.src_path
        # Ignore temporary files, wait for the final rename
        if file_path.endswith(".hdf.temp"):
            return
        # If a direct .hdf file is created (unlikely in your case, but just in case)
        if file_path.endswith(".hdf"):
            self.process_hdf_file(file_path)

    def on_moved(self, event):
        """
        Handle file rename events.

        Called when a file is renamed. Catches .hdf.temp -> .hdf renaming
        which is the typical pattern for HDF file creation.

        Parameters
        ----------
        event : FileSystemEvent
            Event object containing source and destination paths.

        Returns
        -------
        None

        Notes
        -----
        Only processes files that are renamed to end with .hdf extension.
        """
        if event.is_directory:
            return
        src_path = event.src_path
        dest_path = event.dest_path
        # We only care about files renamed to `.hdf`
        if dest_path.endswith(".hdf"):
            # logger.info(f"[Producer] File renamed: {src_path} -> {dest_path}")
            self.process_hdf_file(dest_path)

    def process_hdf_file(self, file_path):
        """
        Wait for file to be fully written, then add to processing queue.

        Checks the stop flag and waits for file stability before queueing
        the file for processing.

        Parameters
        ----------
        file_path : str
            Path to the HDF file to process.

        Returns
        -------
        None

        Notes
        -----
        - Respects the stop_flag to avoid processing during shutdown
        - Uses wait_for_file_stability to ensure file is ready
        - Logs warnings for incomplete or locked files
        """
        if self.stop_flag.value:  # Check stop flag
            logger.info("[Producer] Stop flag set. Ignoring new files.")
            return

        if self.wait_for_file_stability(file_path):
            logger.info(f"[Producer] New file ready: {file_path}")
            self.task_queue.put(file_path)  # Add to queue
        else:
            logger.warning(
                f"[Producer] Skipping {file_path}: File may be incomplete or locked.")

    def wait_for_file_stability(self, file_path):
        """
        Wait for file size to stabilize and ensure it is readable.

        Monitors file size changes and attempts to open the file with h5py
        to confirm it's fully written and readable.

        Parameters
        ----------
        file_path : str
            Path to the file to check.

        Returns
        -------
        bool
            True if file is stable and readable, False if timeout occurred.

        Notes
        -----
        The function waits until:
        1. File size stops changing between checks
        2. File can be opened successfully with h5py
        
        If max_wait time is exceeded, returns False.
        """
        t0 = time.time()
        prev_size = -1

        while time.time() - t0 < self.max_wait:
            if not os.path.exists(file_path):
                time.sleep(self.check_interval)
                continue  # Wait until file appears

            try:
                curr_size = os.path.getsize(file_path)
                if curr_size == prev_size:
                    # Try opening the file to confirm it's readable
                    with h5py.File(file_path, "r"):
                        return True  # File is ready!
                prev_size = curr_size
                time.sleep(self.check_interval)

            except (OSError, BlockingIOError):
                # File is likely still being written
                time.sleep(self.check_interval)
        return False  # Timed out, file is still unstable


def producer(folder_path, task_queue, stop_flag):
    """
    Set up watchdog observer to monitor folder for new HDF files.

    Creates and starts a file system observer that watches for new HDF files
    in the specified folder and adds them to the processing queue.

    Parameters
    ----------
    folder_path : str
        Path to the folder to monitor.
    task_queue : multiprocessing.Queue
        Queue to which new files will be added.
    stop_flag : multiprocessing.Value
        Shared boolean flag to signal when to stop monitoring.

    Returns
    -------
    None

    Notes
    -----
    - Runs in a separate process
    - Monitors folder non-recursively (only top level)
    - Stops when stop_flag is set or KeyboardInterrupt is received

    See Also
    --------
    HDF5FileHandler : Event handler used by this function
    consumer : Processes files from the queue
    monitor_and_process : Main orchestration function
    """
    event_handler = HDF5FileHandler(task_queue, stop_flag)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()

    try:
        while not stop_flag.value:
            time.sleep(1)  # Keep the observer running
    except KeyboardInterrupt:
        logger.info("\n[Producer] Stopping observer...")

    observer.stop()
    observer.join()


def consumer(consumer_id, task_queue, stop_flag, **analysis_kwargs):
    """
    Process HDF5 files from the queue.

    Worker process that retrieves files from the queue and converts them
    to web format, then updates the combined HTML index.

    Parameters
    ----------
    consumer_id : int
        Unique identifier for this consumer worker.
    task_queue : multiprocessing.Queue
        Queue from which to retrieve files for processing.
    stop_flag : multiprocessing.Value
        Shared boolean flag to signal when to stop processing.
    **analysis_kwargs : dict
        Keyword arguments to pass to convert_one_file, including:
        - target_dir : Output directory for results
        - num_img : Number of images per row
        - dpi : Image resolution
        - overwrite : Whether to overwrite existing files

    Returns
    -------
    None

    Notes
    -----
    - Runs in a separate process
    - Processes files until stop_flag is set or None is received from queue
    - Updates combined HTML index after each file is processed
    - Uses timeout on queue.get to avoid hanging

    See Also
    --------
    producer : Adds files to the queue
    convert_one_file : Converts individual HDF files
    combine_all_htmls : Updates combined HTML index
    """
    while not stop_flag.value:
        try:
            file_path = task_queue.get(timeout=5)  # Timeout to avoid hanging
            if file_path is None:  # Stop signal
                break

            logger.info(f"[Consumer-{consumer_id}] Processing: {file_path}")
            convert_one_file(file_path, **analysis_kwargs)
            combine_all_htmls(analysis_kwargs["target_dir"])

        except multiprocessing.queues.Empty:
            # logger.info(
            #     f"[Consumer-{consumer_id}] No tasks available, waiting...")
            time.sleep(1)

    logger.info(f"[Consumer-{consumer_id}] Stop flag set. Exiting.")


def monitor_and_process(folder_path, num_workers=3, max_running_time=3600, **analysis_kwargs):
    """
    Monitor folder for new HDF files and process them with time limit.

    Main orchestration function that sets up producer-consumer architecture
    to monitor a folder for new HDF files and process them in parallel.

    Parameters
    ----------
    folder_path : str
        Path to the folder to monitor for new HDF files.
    num_workers : int, optional
        Number of consumer worker processes for parallel processing.
        Default is 3.
    max_running_time : int, optional
        Maximum time (in seconds) to run the monitoring. After this time,
        all workers will be stopped gracefully. Default is 3600 (1 hour).
    **analysis_kwargs : dict
        Keyword arguments to pass to file conversion, including:
        - target_dir : Output directory for results
        - num_img : Number of images per row
        - dpi : Image resolution
        - overwrite : Whether to overwrite existing files

    Returns
    -------
    None

    Notes
    -----
    The function uses a producer-consumer pattern:
    1. Producer process monitors folder for new files
    2. Multiple consumer processes convert files in parallel
    3. Shared queue coordinates work distribution
    4. Shared stop flag enables graceful shutdown
    
    The monitoring stops when:
    - max_running_time is reached
    - KeyboardInterrupt (Ctrl+C) is received
    
    All processes are joined before the function returns.

    See Also
    --------
    producer : Producer process function
    consumer : Consumer process function
    HDF5FileHandler : File system event handler

    Examples
    --------
    Monitor folder for 2 hours with 8 workers:
    >>> monitor_and_process('/path/to/data', num_workers=8,
    ...                     max_running_time=7200, target_dir='output')
    """

    start_time = time.time()
    task_queue = multiprocessing.Queue()

    # Shared stop flag
    # 'b' means boolean (True/False)
    stop_flag = multiprocessing.Value('b', False)

    # Start Producer Process
    producer_process = multiprocessing.Process(
        target=producer, args=(folder_path, task_queue, stop_flag), daemon=True
    )
    producer_process.start()

    # Start Consumer Processes
    consumer_processes = []
    for i in range(num_workers):
        p = multiprocessing.Process(
            target=consumer, args=(
                i, task_queue, stop_flag), kwargs=analysis_kwargs
        )
        p.start()
        consumer_processes.append(p)

    # Monitor running time
    try:
        while time.time() - start_time < max_running_time:
            time.sleep(1)  # Keep checking time every second
    except KeyboardInterrupt:
        logger.info("\n[Main] Stopping all workers due to user interruption.")

    logger.info("[Main] Max running time reached. Setting stop flag...")

    # Set stop flag to True → signals all processes to stop
    stop_flag.value = True

    # Stop Producer
    producer_process.join()

    # Stop Consumers
    for _ in range(num_workers):
        task_queue.put(None)  # Send stop signal

    for p in consumer_processes:
        p.join()

    logger.info("[Main] All workers stopped. Exiting.")
