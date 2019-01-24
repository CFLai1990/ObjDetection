class Logger:
  'Logger with a customized header'
  def __init__(self, header, logger):
    self.setHeader(header)
    self.logger = logger

  def setHeader(self, header):
    self.header = header

  def info(self, message):
    self.logger.info(self.header + ' > ' + message)

  def debug(self, message):
    self.logger.debug(self.header + ' > ' + message)

  def warning(self, message):
    self.logger.warning(self.header + ' > ' + message)

  def error(self, message):
    self.logger.error(self.header + ' > ' + message)
    
  def critical(self, message):
    self.logger.critical(self.header + ' > ' + message)