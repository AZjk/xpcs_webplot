import time
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .webplot_cli import convert_one_file
from .html_utlits import combine_all_htmls
import logging


logger = logging.getLogger(__name__)


class HDF5FileHandler(FileSystemEventHandler):
    """ Watches for new .hdf5 files and adds them to the queue. """

    def __init__(self, task_queue, stop_flag):
        self.task_queue = task_queue
        self.stop_flag = stop_flag

    def on_created(self, event):
        """ Called when a new .hdf5 file is detected. """
        if event.is_directory:
            return

        if event.src_path.endswith(".hdf"):
            if self.stop_flag.value:  # Check stop flag
                logger.info("[Producer] Stop flag set. Ignoring new files.")
                return

            logger.info(f"[Producer] New file detected: {event.src_path}")
            self.task_queue.put(event.src_path)  # Add to queue


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
            logger.info(
                f"[Consumer-{consumer_id}] No tasks available, waiting...")
            time.sleep(1)

    logger.info(f"[Consumer-{consumer_id}] Stop flag set. Exiting.")


def monitor_and_process(folder_path, num_consumers=3, max_running_time=3600, **analysis_kwargs):
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
    for i in range(num_consumers):
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
    for _ in range(num_consumers):
        task_queue.put(None)  # Send stop signal

    for p in consumer_processes:
        p.join()

    logger.info("[Main] All workers stopped. Exiting.")
