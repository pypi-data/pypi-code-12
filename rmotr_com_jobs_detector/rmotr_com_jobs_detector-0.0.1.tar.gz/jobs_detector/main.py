# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import click
import requests
from bs4 import BeautifulSoup
from collections import Counter
from jobs_detector import settings

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen
    
DEFAULT_KEYWORDS = [
    'Remote',
    'Python',
    'Javascript',
    'Postgres',
    'Pandas',
    'React'
]


@click.group()
def jobs_detector():
    
    pass


@jobs_detector.command()
@click.option('-i', '--post-id', type=str, required=True)
@click.option('-k', '--keywords', type=str, default=','.join(DEFAULT_KEYWORDS))
@click.option('-c', '--combinations', type=str,
              callback=lambda _, x: x.split(',') if x else x)
              
def hacker_news(post_id, keywords, combinations):
    """
    This subcommand aims to get jobs statistics by parsing "who is hiring?"
    HackerNews posts based on given set of keywords.
    """
    # HINT: You will probably want to use the `BeautifulSoup` tool to
    # parse the HTML content of the website
    url = settings.BASE_URL.format(post_id)
    page = urlopen(url)
    soup = BeautifulSoup(page, 'html.parser')

    comments = soup.find_all('tr', class_ = 'athing')
    jobs = [comment for comment in comments if comment.find("img", width="0")]
    total = len(jobs)
    
    keywords = [word.strip() for word in keywords.split(',')]
    look_up_keywords = search_for_keyword(jobs, keywords)
    
    print ('Total job posts: {}\n'.format(total))
    
    print ("Keywords:")
    for key, value in look_up_keywords.items():
        percentage = int(round(value * 100.0 / total))
        print ('{}: {} ({}%)'.format(key.capitalize(), value, percentage))
        
    
    if not combinations:
        return
    
    look_up_combinations = search_for_combinations(jobs, combinations)
    print ("\nCombinations:")
    for key, value in look_up_combinations.items():
        percentage = int(round(value * 100.0 / total))
        print ('{}: {} ({}%)'.format(key.capitalize(), value, percentage))

def search_for_keyword(jobs, keywords):
    look_up = Counter(keywords)
    combinations = Counter(keywords)
    for job in jobs:
        for keyword in keywords:
            if keyword.lower() in job.get_text().lower():
                look_up[keyword] += 1
    return look_up

def search_for_combinations(jobs, combinations):
    # combinations: ["python-django", "paython-remote"]
    
    look_up = Counter(combinations)
    
    for job in jobs:
        for combination in combinations:
            comb = combination.split("-")
            
            if all([word.lower() in job.get_text().lower() for word in comb]):
                look_up[combination] += 1
    
    return look_up
    
if __name__ == '__main__':
    jobs_detector()

