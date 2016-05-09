"""bsw file management functions"""

import shutil
import os


class FileManager(object):
    def __init__(self, out_dir):
        self.out_dir = out_dir

    def create_out_dir(self):
        """Create the output dir if it doens't exist."""
        if not os.path.isdir(self.out_dir):
            os.makedirs(self.out_dir)

    def merge_dirs(self, source_path, dest_path):
        """Copy the contents of source_path to dest_path, creating subdirectories where
        neccessary.

        Will not overwrite contents in dest_path.
        """
        source_path_abs = os.path.abspath(source_path)
        for (dirpath, dirnames, filenames) in os.walk(source_path_abs):
            for filename in filenames:
                source_path_file = os.path.join(dirpath, filename)
                source_path_rel = source_path_file.replace(source_path_abs,
                    "", 1).lstrip(os.path.sep)
                source_path_dir = os.path.dirname(source_path_rel)
                if not os.path.isdir(os.path.join(dest_path, source_path_dir)):
                    os.makedirs(os.path.join(dest_path, source_path_dir))
                if not os.path.isfile(os.path.join(dest_path,
                                                   source_path_rel)):
                    shutil.copyfile(source_path_file, os.path.join(dest_path,
                        source_path_rel))

    def copy_template_assets(self):
        """Copy template asset files to output directory."""
        if os.path.isdir(os.path.join("templates", "static")):
            self.merge_dirs(os.path.join("templates", "static"),
                os.path.join(self.out_dir, "static"))

    def copy_site_assets(self):
        """Copy site asset files to output directory."""
        if os.path.isdir(os.path.join(self.out_dir, "static")):
            self.merge_dirs("static", os.path.join(self.out_dir, "static"))

    def clean_build_path(self):
        """Remove build folder if it exists."""
        if os.path.isdir(self.out_dir):
            shutil.rmtree(self.out_dir)

    def check_required_paths(self):
        """Check that the required bsw project paths exist"""
        template_path = os.path.join(".", "templates", "base.html")
        if not os.path.exists(template_path):
            raise IOError("Base template (templates/base.html) "
                                    "not found")

    def init_with_template(self, template_name, destination):
        """Initialise the destination folder with the specified template
        skeleton.
        """
        module_path = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(module_path, "templates", template_name)
        
        if not os.path.exists(template_path):
            raise IOError("Template {0} not found".format(template_name))

        self.merge_dirs(template_path, destination)
