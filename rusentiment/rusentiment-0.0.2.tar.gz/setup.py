import setuptools

setuptools.setup(
    name = "rusentiment",
    packages = setuptools.find_packages(),
    version = "0.0.2",
    description = "Sentiment analysis library based on machine learning methods",

    install_requires = [
        "numpy>=1.7.1",
    ],

    entry_points = {
        "console_scripts": [
            "sentiment = sentiment.main:main"
        ]
    },

    author = "Sergey Smetanin",
    author_email = "sismetanin@gmail.com",
    license = "MIT",
    url = "https://github.com/Smeta/rusentiment",
    download_url = "https://github.com/Smeta/rusentiment/tarball/0.0.2",
    keywords = ["russian text analysis", "sentiment analysis", "syntactic features"]
)