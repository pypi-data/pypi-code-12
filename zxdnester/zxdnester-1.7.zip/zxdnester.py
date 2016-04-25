#coding:utf-8

import random
from urllib import urlopen
import sys
reload(sys)
sys.setdefaultencoding('gbk')

WORD_URL = "http://learncodethehardway.org/words.txt"
WORDS = []

PHRASES = {
    "class %%%(%%%):":
        "写一个名为“%%%”的类，其父类是“%%%”。",
    "class %%%(object):\n\tdef ***(self, @@@)":
        "写一个名为“%%%”的类，有一个构造函数“_int_”，以自身和“***”为参数。",
    "class %%%(object):\n\tdef ***(self, @@@)":
        "写一个名为“%%%”的类，有一个名为“***”的方法，以自身和“@@@”为参数。",
    "*** = %%%()":
        "构造一个对象“***”，是“%%%”类型的。",
    "***.***(@@@)":
        "从“***”中调用“***”方法，以自身和“@@@”为参数。",
    "***.*** = '***'":
        "从“***”中调用“***”属性，并赋值为“***”"
    }

PHRASE_FIRST = False
if len(sys.argv) == 2 and sys.argv[1] == "english":
    PHRASE_FIRST = True

for word in urlopen(WORD_URL).readlines():
    WORDS.append(word.strip())

def convert(snippet, phrase):

    class_names = [w.capitalize() for w in
                   random.sample(WORDS, snippet.count("%%%"))]

    other_names = random.sample(WORDS, snippet.count("***"))
    results = []
    param_names = []
    for i in range(0, snippet.count("@@@")):
        param_count = random.randint(1,3)
        param_names.append(', '.join(random.sample(WORDS, param_count)))

    for sentence in snippet, phrase:
        result = sentence[:]
       
        # fake class names
        for word in class_names:
            result = result.replace("%%%", word, 1)

        # fake other names
        for word in other_names:
            result = result.replace("***", word, 1)

        # fake parameter lists
        for word in param_names:
            result = result.replace("@@@", word, 1)

        results.append(result)

    return results

def go():    
    try:
        while True:
            snippets = PHRASES.keys()
            random.shuffle(snippets)

            for snippet in snippets:
                phrase = PHRASES[snippet]
                question, answer = convert(snippet, phrase)
                if PHRASE_FIRST == False:
                    question, answer = answer, question

                print question

                raw_input("> ")
                print "ANSWER: %s\n\n" % answer

    except EOFError:
        print "\nBye"
        

                                     
