import os
import shutil

class FileOperations:
    'The class to handle file operations'
    def __init__(self, rootDir):
        self.root = rootDir
        self.typeDict = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
        }

    def getType(self, typeCode):
        return self.typeDict[typeCode]

    def getRoot(self):
        return self.root

    def changeRoot(self, rootDir):
        self.root = rootDir

    def getPath(self, name):
        return self.root + '/' + name

    def getName(self, path):
        return  os.path.basename(path)

    def mkdir(self, dirName):
        path = self.getPath(dirName)
        existed = os.path.exists(path)
        if not existed:
            os.makedirs(path)
        return os.path.abspath(path)

    def rmdir(self, dirName):
        path = self.getPath(dirName)
        shutil.rmtree(path)