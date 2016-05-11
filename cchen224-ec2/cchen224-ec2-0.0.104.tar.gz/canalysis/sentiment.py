import csv
import re
from glob import glob

from cutils import ProgressBar
from nltk.corpus import stopwords
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment
# pip install vaderSentiment


STOPWORDS = dict(zip(stopwords.words('english'), [''] * len(stopwords.words('english'))))


def get_sent(vs):
    vs.pop('compound')
    v=vs.values()
    k=vs.keys()
    return k[v.index(max(v))]

def get_sentiment(sentence):
    words = re.sub('[^a-z0-9 ]', ' ', sentence.lower())
    words = re.sub(' +', ' ', words)
    words = ' '.join([word for word in words.split(' ') if word not in STOPWORDS])
    return get_sent(vaderSentiment(words))


# '/Users/cchen224/Downloads/expended_thread_aws/*.txt'
def sentiment(dir_in, fp_out):
    files = glob(dir_in)
    bar = ProgressBar(total=len(files))
    for file in files:
        bar.move().log()
        with open(file, 'r') as i:
            csvreader = csv.reader(i, delimiter='\t')
            with open(fp_out, 'a') as o:
                csvwriter = csv.writer(o)
                is_write = True
                for row in csvreader:
                    if is_write:
                        tid = row[1]
                        uid = row[2]
                        sentence = row[3].strip()
                        words = re.sub('[^a-z0-9 ]', ' ', sentence.lower())
                        words = re.sub(' +', ' ', words)
                        words = ' '.join([word for word in words.split(' ') if word not in STOPWORDS])
                        csvwriter.writerow([tid, uid, sentence, get_sent(vaderSentiment(words))])
                    is_write = row == []
    bar.close()

# sentiment('/Users/cchen224/Downloads/expended_thread_aws/*.txt', '/Users/cchen224/Downloads/sentiments.csv')