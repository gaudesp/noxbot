import logging
from os.path import dirname, abspath, join

root_directory = dirname(dirname(abspath(__file__)))

def set_logging(file_level: int = logging.DEBUG, console_level: int = logging.INFO, filename: str = "discord.log") -> tuple[logging.Logger, logging.StreamHandler]:
	logger = logging.getLogger("discord")
	logger.setLevel(logging.DEBUG)
	log_formatter = logging.Formatter(fmt="[{asctime}] [{levelname:<8}] {name}: {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{")

	file_handler = logging.FileHandler(filename=join(root_directory, filename), encoding="utf-8", mode='w')
	file_handler.setFormatter(log_formatter)
	file_handler.setLevel(file_level)
	logger.addHandler(file_handler)

	console_handler = logging.StreamHandler()
	console_handler.setFormatter(log_formatter)
	console_handler.setLevel(console_level)
	logger.addHandler(console_handler)

	return logger, console_handler
