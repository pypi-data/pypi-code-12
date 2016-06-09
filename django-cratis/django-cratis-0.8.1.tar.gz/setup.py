from setuptools import setup, find_packages


setup(
    name='django-cratis',
    version='0.8.1',
    packages=find_packages(),

    url='',
    license='Simplified BSD License',
    author='Alex Rudakov',
    author_email='ribozz@gmail.com',
    description='Django-cratis is a way to group together django applications, so they form reusable features.',
    long_description='',

    extras_require={
        'django':  ["django>1.8.0", 'pip>8.0.0']
    },

    entry_points={
        'console_scripts': [
            'django = cratis.cli:django_cmd',
            'cratis = cratis.cli:cratis_cmd',

            'django-manage = cratis.django:manage_command [django]',
            'cratis-add = cratis.add:add_feature_to_settings [django]'
        ],
    },
)

