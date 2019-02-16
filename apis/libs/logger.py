"""The customized logger"""
class Logger:
    """Logger with a customized header"""
    def __init__(self, header, logger):
        self.set_header(header)
        self.logger = logger

    def set_header(self, header):
        """Set the header information"""
        self.header = header

    def info(self, message):
        """Info with header"""
        self.logger.info(str(self.header) + ' > ' + str(message))

    def debug(self, message):
        """Debug with header"""
        self.logger.debug(str(self.header) + ' > ' + str(message))

    def warning(self, message):
        """Warning with header"""
        self.logger.warning(str(self.header) + ' > ' + str(message))

    def error(self, message):
        """Error with header"""
        self.logger.error(str(self.header) + ' > ' + str(message))

    def critical(self, message):
        """Critical with header"""
        self.logger.critical(str(self.header) + ' > ' + str(message))
        