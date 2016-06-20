import os

from services.account_storage_service import AccountStorageService
from utils.printer import printer


class PortService(object):

    def __init__(self, task, storage_service=None):

        self._task = task

        if storage_service is None:
            self.storage = AccountStorageService()
        else:
            # Override for the storage service
            self.storage = storage_service

        self.s3_root = self.storage.location

    @property
    def task(self):
        return self._task

    def upload_input_ports(self, port_list=None, exclude_list=None):
        """
        Takes the workflow value for each port and does the following:
            * If local filesystem -> Uploads locally files to s3.
                S3 location will be as follows:
                    gbd-customer-data/<acct_id>/<workflow_name>/<task_name>/<port_name>/
            * If S3 url -> do nothing.
        :returns the update workflow with S3 urls.
        """

        input_ports = self._task.input_ports

        for port in input_ports:

            # If port list is not None, then only allow port names in the list
            if port_list and port.name not in port_list:
                continue

            # Exclude ports as provided
            if exclude_list and port.name in exclude_list:
                continue

            # port_value = port.get('value', None)

            # Check if the port value is a valid file system location
            if not port.value or not os.path.isabs(port.value) or not os.path.isdir(port.value):
                continue

            # The prefix for each key that is uploaded, not including the the acct id.
            prefix = '{run_name}/{port}'.format(
                run_name=self._task.run_name,
                # task=self._task.name,
                port=port.name
            )

            port_files = self._get_port_files(port.value, prefix)

            # Update the port value with an S3 url
            port.value = '%s/%s' % (self.s3_root, prefix)

            if len(port_files) == 0:
                printer('Port %s is empty, push to S3 skipped' % port.name)
            else:
                self.storage.upload(port_files)
                printer('Port %s pushed to account storage, %s files' % (port.name, len(port_files)))

    @staticmethod
    def _get_port_files(local_path, prefix):
        """
        Find files for the local_path and return tuples of filename and keynames
        :param local_path: the local path to search for files
        :param prefix: the S3 prefix for each key name on S3
        """
        source_files = []

        for root, dirs, files in os.walk(local_path, topdown=False):

            for name in files:
                fname = os.path.join(root, name)

                key_name = '%s/%s' % (prefix, fname[len(local_path) + 1:])

                source_files.append((fname, key_name))

        return source_files

    # TODO Implement
    # def download_output_port(self, workflow, arg_outputs=[]):
    #     """
    #     Download the outputs for the given workflow from s3, maintaining
    #     the namespace structure.
    #     :param workflow:
    #     :param arg_outputs:
    #     """
    #     output_location = os.path.join(os.getcwd(), 'Workflows', workflow['name'], 'outputs')
    #
    #     # Get input directories
    #     outputs = next(os.walk(output_location))[1]
    #
    #     # Filter input dirs by workflow inputs
    #     if len(arg_outputs) > 0:
    #         outputs = set(outputs).intersection(arg_outputs)
    #
    #     for next_output in outputs:
    #         s3_folder = '%s/%s' % (workflow['name'], next_output)
    #         dir_path = os.path.join(output_location, next_output)
    #         # Get all keys contained in the folder
    #         try:
    #             key_names = self.storage.list(s3_folder=s3_folder)
    #         except ClientError:
    #             # TODO is this the only reason this will fail?
    #             raise ValueError("Account Storage location does not exist")
    #
    #         self.storage.download(dir_path, key_names)
