import sys
from pathlib import Path
from loguru import logger
from src.config_manager import ConfigManager


class Logger:
    def __init__(self, config: ConfigManager):
        self.config = config
        self._setup_logger()
    
    def _setup_logger(self):
        logger.remove()
        
        log_level = self.config.get('logging.level', 'INFO')
        log_file = self.config.get('logging.log_file', 'data/logs/rodent_detection.log')
        max_size = self.config.get('logging.max_size', '10MB')
        backup_count = self.config.get('logging.backup_count', 5)
        
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            sys.stdout,
            level=log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
        )
        
        logger.add(
            log_file,
            rotation=max_size,
            retention=backup_count,
            level=log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
        )
    
    def get_logger(self):
        return logger


def setup_logger(config: ConfigManager):
    logger_instance = Logger(config)
    return logger_instance.get_logger()