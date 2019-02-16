"""The OS file operations"""
import os
import shutil

class FileOperations:
    """The class to handle file operations"""
    def __init__(self, root_dir):
        self.root = root_dir
        self.type_dict = {
            'image/jpeg': 'jpg',
            'image/png': 'png',
        }

    def get_type(self, type_code):
        """Get the type of the file"""
        return self.type_dict[type_code]

    def get_root(self):
        """Get the root of the current directory"""
        return self.root

    def change_root(self, root_dir):
        """Change the root of the current directory"""
        self.root = root_dir

    def get_path(self, name):
        """Get the absolute path of the file"""
        return self.root + '/' + name

    def get_name(self, path):
        """Get the name of the file"""
        return  os.path.basename(path)

    def mkdir(self, dir_name):
        """Create a sub-directory"""
        path = self.get_path(dir_name)
        existed = os.path.exists(path)
        if not existed:
            os.makedirs(path)
        return os.path.abspath(path)

    def rmdir(self, dir_name):
        """Remove a sub-directory"""
        path = self.get_path(dir_name)
        shutil.rmtree(path)
        