import logging
import os


def setup_custom_logger(name):
    """
    Set up a custom logger with the specified name and add file handler.
    Ensures that each logger only adds handlers once.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Define the custom formatter
        formatter = CustomFormatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s', '%Y-%m-%d %H:%M:%S')

        # Create a file handler and set its formatter
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(formatter)

        # Add the file handler to the logger
        logger.addHandler(file_handler)

    return logger


class CustomFormatter(logging.Formatter):
    """
    Custom formatter to include the filename in each log entry.
    """

    def format(self, record):
        record.filename = os.path.basename(__file__)
        return super().format(record)
