import os
import sys
from bs4 import BeautifulSoup
import codecs


def perfect_html():
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(".html"):
                soup = None
                try:
                    open_file = os.path.join(root, file)
                    soup = get_soup(open_file)
                    html = soup.prettify(formatter="minimal")
                    if html:
                        write_over_original(open_file, html)
                except Exception, e:
                    print("Could not make {file} beautiful: {error}".format(
                        file=open_file,
                        error=e)
                    )


def write_over_original(file, html):
    with codecs.open(file, 'w', 'utf-8') as f:
        f.write(html)


def get_soup(file):
    text = None
    with open(file, 'r') as f:
        text = f.read()
    decoded_text = text.encode('utf-8').decode(
        'ascii', 'ignore')
    return BeautifulSoup(decoded_text, 'html.parser')

# if __name__ == '__main__':
#     main()
