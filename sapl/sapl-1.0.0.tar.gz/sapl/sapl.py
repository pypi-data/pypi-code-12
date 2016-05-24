# coding: utf-8

from __future__ import print_function

from operator import add

from pyspark.mllib.feature import HashingTF
from pyspark.mllib.regression import LabeledPoint

import json
import string
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from unidecode import unidecode

import re

import os

###################
#Constants & Paths#
###################

WORDS='/home/hujiawei/Documents/Alex/Ressources/Lexicons/mylex/final_lexicon.json'
EMOJIS_LEXICON_PATH = "../data/lexicons/emojis_lexicon.json"
SMILEYS_LEXICON_PATH = "../data/lexicons/smileys_lexicon.json"

STOPWORDS_PATH="../data/wordlists/fr.json"
PREFIXS_PATH="../data/wordlists/prefixs.json"

URL_REGEX=r"^(http(s?)\:\/\/|~/|/)?([a-zA-Z]{1}([\w\-]+\.)+([\w]{2,5}))(:[\d]{1,5})?/?(\w+\.[\w]{3,4})?((\?\w+=\w+)?(&\w+=\w+)*)?"
TWITTER_URL_REGEX=ur"https://t.co/(\w)*"
TWITTER_USERNAME_REGEX=ur"@(\w)*"

CATEGORIES={0.0:'negatif', 1.0:'neutre',2.0:'positif'}

FEATURE_COUNT=250
NEGATIVE_TRESHOLD=-.25
POSITIVE_TRESHOLD=.3





class Preprocessor:
    def __init__(self, feature_count=FEATURE_COUNT, emojis_lexicon_path=EMOJIS_LEXICON_PATH, smileys_lexicon_path=SMILEYS_LEXICON_PATH,
                 stopwords_path=STOPWORDS_PATH, prefixs_path=PREFIXS_PATH):
        print(os.getcwd())
        self.loadEmojisLexicon(emojis_lexicon_path)
        self.loadSmileysLexicon(smileys_lexicon_path)
        self.loadStopwords(stopwords_path)
        self.loadPrefixs(prefixs_path)
        self.hasher = HashingTF(feature_count)

    def loadLexicon(self, lexicon_path):
        """Loads a lexicon from a jsonfile, returns a list of words and the lexicon dictionnary"""
        with open(lexicon_path) as lexicon_file:
            lexicon = json.load(lexicon_file)
        lwords    = [lexi['word'] for lexi in lexicon]
        return lwords, lexicon

    def loadEmojisLexicon(self, emojis_lexicon_path=EMOJIS_LEXICON_PATH):
        self.emojis_list, self.emojis_lexicon = self.loadLexicon(emojis_lexicon_path)

    def loadSmileysLexicon(self, smileys_lexicon_path=SMILEYS_LEXICON_PATH):
        self.smileys_list, self.smileys_lexicon = self.loadLexicon(smileys_lexicon_path)

    def loadStopwords(self, stopwords_path=STOPWORDS_PATH):
        self.stopwords_list, _ = self.loadLexicon(stopwords_path)
        self.regexstopwords_list = map(lambda word: r"\b%s\b" % word, self.stopwords_list)

    def loadPrefixs(self, prefixs_path=PREFIXS_PATH):
        self.prefixs_list, _ = self.loadLexicon(prefixs_path)

    ##########################
    #Pre treatement functions#
    ##########################

    def removeWords(self, wordslist, tweet):
        for word in wordslist:
            tweet=re.sub(word, " ", tweet)
        return tweet

    def removePunctuation(self, tweet):
        tweet=tweet.replace(","," ")
        return "".join(l for l in tweet if l not in string.punctuation)

    def removeUrls(self, tweet_text):
        return re.sub(TWITTER_URL_REGEX, "url", tweet_text)

    def removeUsernames(self, tweet_text):
        return re.sub(TWITTER_USERNAME_REGEX, "username", tweet_text)

    def removeListElementsFromString(self, aList, aString):
        return reduce(lambda s, elt: s.replace(elt," "), aList, aString)

    def extractListElementsFromStringAndClean(self, aList, aString):
        rList=[elt for elt in aList if elt in aString]
        aString=self.removeListElementsFromString(rList, aString)
        return aString, rList

    def computeScore(self, wordList, lexicon):
        return sum([float(row['value']) for row in lexicon if row['word'] in wordList])

    def getLabel(self, score):
        rlabel=1.0
        if score<NEGATIVE_TRESHOLD:
            rlabel=0.0
        elif score>POSITIVE_TRESHOLD:
            rlabel=2.0
        else:
            rlabel=1.0
        return rlabel

    #####################################
    #Defining some Tweet level functions#
    #####################################
    def detectFrench(self, tweet):
        is_french = False
        try:
            is_french = (detect(tweet)=='fr')
        except LangDetectException:
            print("err: "+tweet)
        return is_french

    def clean(self, tweet):
        tweet_without_emojis, emojis_list=self.extractListElementsFromStringAndClean(self.emojis_list, tweet)
        tweet_without_smileys, smileys_list=self.extractListElementsFromStringAndClean(self.smileys_list, tweet_without_emojis)
        text_tweet=tweet_without_smileys.lower()
        text_tweet=self.removeUrls(text_tweet)
        text_tweet=self.removeUsernames(text_tweet)
        text_tweet=unidecode(text_tweet)
        text_tweet=self.removeWords(self.regexstopwords_list,text_tweet)
        text_tweet=self.removeWords(self.prefixs_list,text_tweet)
        clean_tweet=self.removePunctuation(text_tweet)
        return (clean_tweet, emojis_list, smileys_list)

    def preprocessTweet(self, tweet):
        clean_tweet, emojis_list, smileys_list = self.clean(tweet)
        emoji_score = self.computeScore(emojis_list, self.emojis_lexicon)
        smiley_score = self.computeScore(smileys_list, self.smileys_lexicon)
        score=emoji_score+smiley_score
        label=self.getLabel(score)
        hashed = self.hasher.transform(clean_tweet.split())
        return LabeledPoint(label, hashed)


