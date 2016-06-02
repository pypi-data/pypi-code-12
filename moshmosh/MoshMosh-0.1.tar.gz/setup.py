from setuptools import setup

setup(
    name='MoshMosh',
    version='0.1',
    packages=['moshmosh'],
    package_data={'moshmosh': [
        'GifBreakerUI_Bloom.html',
        'GifBreakerUI_Overlay.html',
        'GifBreakerUI_Shmear.html',
        'GifBreakerUI_homepage.html',
    ]}
    #py_modules=['MoshinSomeStuff','GifBreakerUI_webfrontend']
)

