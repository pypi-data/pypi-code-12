
import rinocloud
import os


def set_local_path(directory, create_dir=False):
    """
        sets path for local saving of information
        if create is true we will create the folder even if it doesnt exist
    """
    if not os.path.exists(directory) and create_dir is True:
        os.makedirs(directory)

    if not os.path.exists(directory) and create_dir is False:
        raise AttributeError("Path '%s' does not exist, to make it pass create_dir=True to rinocloud.set_local_path" % directory)

    if os.path.isdir(directory):
        rinocloud.path = directory

    return directory


def set_domain(url):
    rinocloud.api_domain = url
    rinocloud.api_base = '%s/api/1/' % rinocloud.api_domain
    set_rinocloud_urls()


def set_rinocloud_urls():
    rinocloud.urls = {
        'upload': rinocloud.api_base + 'files/upload_multipart/',
        'upload_meta': rinocloud.api_base + 'files/create_object/',
        'create_folder': rinocloud.api_base + 'files/create_folder/',
        'get_metadata': rinocloud.api_base + 'files/get_metadata/',
        'update': rinocloud.api_base + 'files/update_metadata/',
        'download': rinocloud.api_base + 'files/download/?id=',
        'query': rinocloud.api_base + 'files/query/',
        'count': rinocloud.api_base + 'files/query_count/',
        'sign_s3': rinocloud.api_base + 'files/sign_s3/',
        'pre_s3_upload': rinocloud.api_base + 'files/pre_s3_upload/',
        'post_s3_upload': rinocloud.api_base + 'files/post_s3_upload/',
    }
