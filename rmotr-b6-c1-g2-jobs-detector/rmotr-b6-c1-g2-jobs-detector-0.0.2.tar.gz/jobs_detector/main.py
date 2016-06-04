import click
import requests
from bs4 import BeautifulSoup
import collections

from jobs_detector import settings # gets BASE_DIR, BASE_URL

DEFAULT_KEYWORDS = [
    'Remote',
    'Postgres',
    'Python',
    'Javascript',
    'React',
    'Pandas'
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
    keywords = keywords.split(',') # get keywords as a list
    keywords = [keyword.title() for keyword in keywords] # make sure uppercase
    
    combinations = combinations or [] # blank list if no -c flag used
    # convert python-django to Python-Django
    combinations = [combo.title() for combo in combinations]
    
    # Initialize a defaultdict to count each of our keywords & combos
    keyword_counts = collections.defaultdict(int)
    
    # Get the html from the page and parse it using BeautifulSoup
    page = requests.get(settings.BASE_URL.format(post_id))
    soup = BeautifulSoup(page.text, 'html.parser')
    
    # Find each post on the page
    job_posts = []
    # Every post on the page is in a <tr> with class "athing".
    posts = soup.find_all("tr", class_="athing")
    for post in posts:
        # Each post has an <img> element to pad it on the left.  For root posts
        #  (job posts) this element has width 0.  For comments on job posts,
        #  the width is larger.
        if post.find("img", width="0"):
            job_posts.append(post)
    
    # Increment dict values for matches in a post
    for post in job_posts:
        search_comment(
            post.get_text(),
            keyword_counts,
            keywords,
            combinations
        )
    
    # Print out counts from dict
    display_counts(
        keyword_counts, 
        keywords, 
        combinations, 
        len(job_posts)
    )
    
def search_comment(comment, keyword_counts, keywords, combinations):
    '''
    Reads in a comment from the website
    Searches for all matches to keywords and combinations
    Modifies keyword_counts to update with each match found
    comment: string
    keyword_counts: defaultdict(int) that will be updated
    keywords: list of kewords
    combinations: list of combo-keywords ['Remote-Python-Flask', 'Remote-Django']
    '''
    comment = comment.lower() # compare lowercase everything
    
    for keyword in keywords:
        if keyword.lower() in comment:
            keyword_counts[keyword] += 1
            
    for combination in combinations:
        combo_keywords = combination.lower().split('-')
        if all(keyword in comment for keyword in combo_keywords):
            keyword_counts[combination] += 1
            
def display_counts(keyword_counts, keywords, combinations, total_posts):
    '''
    Prints out info on # of counts for each keyword and percentages of total posts
    Keywords:
    Remote: 174 (19%)
    Postgres: 81 (9%)
    Python: 144 (16%)
    Javascript: 118 (13%)
    React: 133 (14%)
    Pandas: 5 (0%)
    
    Combinations:
    Remote-Python-Flask: 2 (0%)
    Remote-Django: 6 (0%)
    '''
    print('Total job posts: {}\n'.format(total_posts))
    display_info('Keywords', keyword_counts, keywords, total_posts)
    
    if combinations:
        print('')
        display_info('Combinations', keyword_counts, combinations, total_posts)
        
def display_info(name, keyword_counts, key_list, total_posts):
    '''
    Given a list of key terms it prints out data on each one
    '''
    print('{}:'.format(name))
    for key in key_list:
        count = keyword_counts[key]
        try:
            percent = int(count / float(total_posts) * 100)
        except ZeroDivisionError:
            percent = 0
        print('{}: {} ({}%)'.format(key, count, percent))

if __name__ == '__main__':
    jobs_detector()
