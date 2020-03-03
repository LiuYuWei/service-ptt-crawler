"""This file is used in setting the feature of os path."""

# import relation package.
import os


class PathSetting:
    """This class is used in setting the feature of os path."""

    def __init__(self):
        """Initial some variable"""
        # get the project path
        self.project_path = os.environ['PROJECT_PATH']

    def path_join(self, *folder_name):
        """path_join: Join two path together.

        Arguments:
            folder_name: tuple, the folder name.

        Returns:
            path: string, the join of path.
        """
        # Check the first folder name contains the PROJECT_PATH or not.
        if self.project_path not in folder_name[0]:
            path = self.project_path
        else:
            path = ''
        # Join the folder name to be a path directory.
        for item in list(folder_name):
            path = os.path.join(path, item)
        return path

    def make_directory(self, *path_dir):
        """make_directory: Make the folder directory.

        Arguments:
            path_dir: tuple, the path directory.
        """
        for item in list(path_dir):
            # Check the first folder name contains the PROJECT_PATH or not.
            if self.project_path not in item:
                self.path_join(item)
            # Make the folder directory.
            if not os.path.exists(item):
                os.makedirs(item)
