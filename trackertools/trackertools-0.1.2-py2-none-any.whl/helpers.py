import os
import logging
import requests
import lxml.html as lh
import mechanize

# Set up output dir
wdir=os.path.abspath(os.path.dirname(__file__))

# Set up the logger
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')
logger.setLevel(logging.DEBUG)

def write_text_to_file(filename, text):

    with open(os.path.join(wdir, 'output', filename), 'w') as f:
        f.write(text)
        logger.debug("Wrote to %s" % filename)

def get_latest_user_agent(browser="Chrome", cached=False, filepath=None):
    if not filepath:
        cache_fname = 'cached_user_agents.txt'
    else:
        cache_fname = 'testing_cached_user_agents.txt'

    default_user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0',
                   ]

    # for testing
    if not filepath:
        url = "https://techblog.willshouse.com/2012/01/03/most-common-user-agents/"
        r = requests.get(url, verify=False)
        html = r.text
        doc = lh.document_fromstring(html)
    else:
        with open(filepath, 'r') as f:
            html = f.read()
        doc = lh.document_fromstring(html)

    # Download from web
    if not cached:
        #logger.debug("get_latest_user_agent doc is: %s" % doc)
        # Create the first cache
        with open(os.path.join(wdir, 'output', cache_fname), 'w') as f:
            for web_useragent in doc.xpath("//td[@class='useragent']"):
                #logger.debug(web_useragent.text_content())
                f.write("%s\n" % web_useragent.text_content())

    # Create the first cache if it doesn't exist
    if not os.path.isfile(os.path.join(wdir, 'output', cache_fname)):
        with open(os.path.join(wdir, 'output', cache_fname), 'w') as f:
            for ua in default_user_agents:
                f.write("%s\n" % ua)

    # Create the user_agent list
    user_agents = open(os.path.join(wdir, 'output', cache_fname)).readlines()

    for ua in user_agents:
        if browser in ua:
            return ua.strip('\n')

    if filepath:
        os.remove(os.path.join(wdir, 'output', cache_fname))

    return None
