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
    """ Watches for new .hdf5 files (via renaming) and adds them to the queue when fully written. """
    def __init__(self, task_queue, stop_flag, max_wait=60, check_interval=0.5):
        self.task_queue = task_queue
        self.stop_flag = stop_flag
        self.max_wait = max_wait  # Max wait time for file to be fully written
        self.check_interval = check_interval  # Interval to check file size stability

    def on_created(self, event):
        """ Called when a new file is created. We ignore `.temp` files and wait for renaming. """
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
        """ Called when a file is renamed. This ensures we catch `.hdf.temp -> .hdf` renaming. """
        if event.is_directory:
            return
        src_path = event.src_path
        dest_path = event.dest_path
        # We only care about files renamed to `.hdf`
        if dest_path.endswith(".hdf"):
            # logger.info(f"[Producer] File renamed: {src_path} -> {dest_path}")
            self.process_hdf_file(dest_path)

    def process_hdf_file(self, file_path):
        """ Wait for the file to be fully written before adding it to the queue. """
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
        Waits for the file size to stabilize and ensures it is readable.
        Returns True if the file is ready, False otherwise.
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
    """ Sets up the watchdog observer to monitor the folder in real-time. """
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
    """ Processes HDF5 files from the queue. """
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
    """ Main function to monitor a folder and process HDF5 files with a time limit. """

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
