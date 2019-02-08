import numpy as np

class ODResultGenerator:
  def __init__(self):
    self.clearAll()

  def clearAll(self):
    self.getScore()
    self.getClass()
    self.getBbox()
    self.getMask()

  def getScore(self, score=-1):
    self.score = score

  def getClass(self, className='undefined'):
    self.className = className

  def getBbox(self, x=0, y=0, width=0, height=0):
    self.bbox = {
      'x': x,
      'y': y,
      'width': width,
      'height': height
    }

  def getMask(self, contours = None):
    self.masks = []
    if not(contours is None):
      for ctr in contours:
        msk = ctr.reshape((-1,2)).tolist()
        self.masks.append(msk)

  def pack(self):
    result = {
      'class': self.className,
      'score': self.score,
      'bbox': self.bbox,
      'mask': self.masks
    }
    return result