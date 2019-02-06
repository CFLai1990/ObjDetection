class Logger:
  'Logger with a customized header'
  def __init__(self, header, logger):
    self.setHeader(header)
    self.logger = logger

  def setHeader(self, header):
    self.header = header

  def info(self, message):
    self.logger.info(str(self.header) + ' > ' + str(message))

  def debug(self, message):
    self.logger.debug(str(self.header) + ' > ' + str(message))

  def warning(self, message):
    self.logger.warning(str(self.header) + ' > ' + str(message))

  def error(self, message):
    self.logger.error(str(self.header) + ' > ' + str(message))
    
  def critical(self, message):
    self.logger.critical(str(self.header) + ' > ' + str(message))