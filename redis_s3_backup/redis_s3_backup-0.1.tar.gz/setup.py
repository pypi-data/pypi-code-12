from setuptools import setup

setup(name='redis_s3_backup',
        version='0.1',
        description='Backup Redis rdb dump file to AWS S3',
        url='https://github.com/arpith/Redis-S3-Backup',
        author='Arpith Siromoney',
        author_email='arpith@feedreader.co',
        license='MIT',
        packages=['redis_s3_backup'],
        zip_safe=False)
