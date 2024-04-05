from pythonforandroid.recipe import CompiledComponentsPythonRecipe
import shutil
import os


class MySQLConnectorPythonRecipe(CompiledComponentsPythonRecipe):

    name = 'mysql-connector-python'
    version = '8.3.0'
    url = (
        "https://dev.mysql.com/get/Downloads/Connector-Python/"
        f"mysql-connector-python-{version}-src.tar.gz"
    )
    call_hostpython_via_targetpython = False

    depends = ['python3', 'setuptools']

    def post_download(self, archive_fn, destination_dir):
        super(MySQLConnectorPythonRecipe, self).post_download(archive_fn, destination_dir)
        # Extract the downloaded tarball and ensure correct directory structure
        self.extract_tar(archive_fn, destination_dir)
        # Move contents to the expected directory structure
        extracted_dir = os.path.join(
            destination_dir, 
            f'mysql-connector-python-{self.version}-src'
        )
        if os.path.exists(extracted_dir):
            for item in os.listdir(extracted_dir):
                shutil.move(
                    os.path.join(extracted_dir, item), 
                    destination_dir
                )
            shutil.rmtree(extracted_dir)


recipe = MySQLConnectorPythonRecipe()
