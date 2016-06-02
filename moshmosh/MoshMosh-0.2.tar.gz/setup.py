from setuptools import setup

setup(
    name='MoshMosh',
    version='0.2',
    packages=['moshmosh'],
    install_requires=['flask','pymosh','visvis','PIL','opencv'],
    package_data={'moshmosh': [
        'GifBreakerUI_Bloom.html',
        'GifBreakerUI_Overlay.html',
        'GifBreakerUI_Shmear.html',
        'GifBreakerUI_homepage.html',
    ]}
    #py_modules=['MoshinSomeStuff','GifBreakerUI_webfrontend']
)

