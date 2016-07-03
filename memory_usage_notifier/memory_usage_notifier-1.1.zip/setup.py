from setuptools import setup

setup(name='memory_usage_notifier',
      version='1.1',
      description='RAM Status Notifier',
      long_description='Checks your current RAM status and shows a notifier on desktop',
      keywords='memory RAM status notifier check RAM status python checker',
      url='https://github.com/prateekM59/memory_usage_notifier',
      author='Prateek Mahajan',
      author_email='prateekmahajan59@gmail.com',
      license='MIT',
      entry_points = {
          'console_scripts': [
               'checkMem=memory_usage_notifier.command_line:checkStatus',
               'startMemNotifier=memory_usage_notifier.command_line:startChecker',
          ],
      },
      packages = ['memory_usage_notifier'],
      install_requires=[
            'psutil',
      ],
      zip_safe=False) 