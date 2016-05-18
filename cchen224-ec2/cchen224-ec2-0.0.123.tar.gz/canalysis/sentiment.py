import csv
import re
from glob import glob
from datetime import datetime

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
def sentiment_threads(dir_in, fp_out):
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
                        tid = row[0]
                        uid = row[1]
                        sentence = row[3].strip()
                        words = re.sub('[^a-z0-9 ]', ' ', sentence.lower())
                        words = re.sub(' +', ' ', words)
                        words = ' '.join([word for word in words.split(' ') if word not in STOPWORDS])
                        csvwriter.writerow([tid, uid, sentence, get_sent(vaderSentiment(words))])
                    is_write = row == []
    bar.close()
# sentiment('/Users/cchen224/Downloads/expended_thread_aws/*.txt', '/Users/cchen224/Downloads/sentiments.csv')


def sentiment(fp_in, fp_out):
    with open(fp_in, 'r') as i:
        csvreader = csv.reader(i)
        with open(fp_out, 'w') as o:
            csvwriter = csv.writer(o)
            for row in csvreader:
                tid = row[0]
                uid = row[1]
                sentence = row[3].strip()
                words = re.sub('[^a-z0-9 ]', ' ', sentence.lower())
                words = re.sub(' +', ' ', words)
                words = ' '.join([word for word in words.split(' ') if word not in STOPWORDS])

                sentiment = get_sent(vaderSentiment(words))

                row.pop(6)
                row.pop(5)
                row.pop(4)
                row.append(sentiment)
                csvwriter.writerow(row)
# sentiment('/Users/../Volumes/cchen224/tweets_07_ads.csv', '/Users/../Volumes/cchen224/tweets_07_ads_sentiment.csv')
sentiment('/Users/../Volumes/cchen224/tweets_06_ads.csv', '/Users/../Volumes/cchen224/tweets_06_ads_sentiment.csv')