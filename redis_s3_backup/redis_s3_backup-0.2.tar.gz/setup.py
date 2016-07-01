from setuptools import setup

setup(name='redis_s3_backup',
        version='0.2',
        description='Backup Redis rdb dump file to AWS S3',
        url='https://github.com/arpith/Redis-S3-Backup',
        author='Arpith Siromoney',
        author_email='arpith@feedreader.co',
        license='MIT',
        packages=['redis_s3_backup'],
        install_requires=[
            'boto3',
        ],
        entry_points={
            'console_scripts':['redis_s3_backup=redis_s3_backup.command_line:main'],
        },
        zip_safe=False)
