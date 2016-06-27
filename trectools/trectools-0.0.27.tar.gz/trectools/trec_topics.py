from lxml import etree
import os
import codecs

class TrecTopics:

    def __init__(self, topics={}):
        self.topics = topics

    def set_topics(self, topics):
        self.topics = topics

    def set_topic(self, topic_id, topic_text):
        self.topics[topic_id] = topic_text

    def printfile(self, filename="output.xml", outputdir=None):
        if outputdir is None:
            outputdir = os.getcwd()

        root = etree.Element('topics')

        for qid, text in sorted(self.topics.iteritems(), key=lambda x:x[0]):
            topic = etree.SubElement(root, 'top')
            tid = etree.SubElement(topic, 'num')
            tid.text = str(qid)
            ttext = etree.SubElement(topic, 'title')
            ttext.text = text

        filepath = os.path.join(outputdir, filename)
        print "Printing to %s" % (filepath)
        #f = codecs.open(os.path.join(outputdir, filename), "w", encoding="utf-8")
        f = open(filepath, "w")
        f.writelines(etree.tostring(root, pretty_print=True))
        f.close()


