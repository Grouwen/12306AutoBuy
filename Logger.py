import logging
import colorlog

INFO = logging.INFO
DEBUG = logging.DEBUG

class Logger:
    def __init__(self,logLevel):
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }

        logger = logging.getLogger('logger_name')

        # 输出到控制台
        console_handler = logging.StreamHandler()

        # 日志级别，logger 和 handler以最高级别为准，不同handler之间可以不一样，不相互影响
        logger.setLevel(logLevel)
        console_handler.setLevel(logLevel)

        console_formatter = colorlog.ColoredFormatter(
            fmt='%(log_color)s[%(asctime)s.%(msecs)03d] -> [%(levelname)s] : %(message)s',
            datefmt='%Y-%m-%d  %H:%M:%S',
            log_colors=log_colors_config
        )
        console_handler.setFormatter(console_formatter)

        # 重复日志问题：
        # 1、防止多次addHandler；
        # 2、loggername 保证每次添加的时候不一样；
        # 3、显示完log之后调用removeHandler
        if not logger.handlers:
            logger.addHandler(console_handler)

        console_handler.close()
        self.logger = logger

    def info(self, *msg):
        self.logger.info(*msg)

    def debug(self, *msg):
        self.logger.debug(*msg)

    def warning(self, *msg):
        self.logger.warning(*msg)

    def error(self, *msg):
        self.logger.error(*msg)

    def critical(self, *msg):
        self.logger.critical(*msg)