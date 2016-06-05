from distutils.core import setup
from setuptools import find_packages

install_requires = ['boto3']
setup(name='libaws',
        version='1.0.2',
        description='''awslib is a program can implement amason web service ,such as download bucket files
             and upload files to bucket etc ''',
        author='wukan',
        author_email='kan.wu@gengtalks.com',
        url='https://github.com/wekay102200/genetalk_upload.git',
        license='Genetalks',
        packages=find_packages(),
        include_package_data=True,
        install_requires=install_requires,
        zip_safe=False,
     #   package_dir={
      #      'awslib': 'awslib',
       # },
       #package_data={'awslib': ['common/logger111.conf']},
)
