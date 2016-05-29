import requests
import json
from bs4 import BeautifulSoup
import random
import timessh
import traceback

class PlayReviews():
    
    def get_reviews(self, app_id):
        sort_by_time = '0'
        sort_by_helpfulness = '2'
        sort_by_time = '1'
        # app_id = "com.buyhatke.assistant"
        reviews = []
        page_num = 0
        is_last_page = False

        while is_last_page is False:
            if page_num % 3 == 0:
                time.sleep(random.random()+1)

            (reviews_html_string, is_last_page) = self.__fetch_reviews(app_id, page_num, sort_by_helpfulness)
            # print(reviews_html_string)
            # print(is_last_page)
            if len(reviews_html_string) > 0:
                reviews.extend(self.__parse_reviews(reviews_html_string))
            page_num = page_num + 1
        print(page_num)
        return reviews

    def __fetch_reviews(self, app_id, page_num, sort_by):
        url = "https://play.google.com/store/getreviews"
        querystring = {"authuser":"0"}
        payload = {'reviewType':'0', 'pageNum':page_num, 'id':app_id, 'xhr':'1', 'reviewSortOrder':sort_by}
        response = requests.request("POST", url, data=payload, params=querystring)
        
        if(len(response.content)>4):
            response = response.content[4:]
            # print(response)
            try:
                response = json.loads(response)
                if len(response)>0:
                    if len(response[0]) == 4:
                        reviews_html = response[0][2]
                        if response[0][1] == 1:
                            is_last_page = False
                        else:
                            is_last_page = True
                        return (reviews_html, is_last_page)
                    else:
                        return('',True)
                else:
                    return('', True)

                
            
            except ValueError as e:
                traceback.print_exc()
                print("google blocked you, maybe sleep")
                return('',True)
        else:
            return('', True)

    def __parse_reviews(self, reviews_html_string):
        soup = BeautifulSoup(reviews_html_string, 'html.parser')
        reviews = []
        review_body_list = soup.findAll("div",{"class":"review-body"})
        review_author_list = soup.findAll("span",{"class":"author-name"})
        review_date_list = soup.findAll("span",{"class":"review-date"})
        review_title_list = soup.findAll("span",{"class":"review-title"})
        review_rating_list = soup.findAll("div",{"class":"tiny-star"})
        review_user_id_list = soup.findAll()
        
        for i in range(len(review_body_list)):
            review = {"title":review_title_list[i].text, "body":review_body_list[i].text, 
            "date":review_date_list[i].text, "author":review_author_list[i].text, "rating":review_rating_list[i]['aria-label']}
            reviews.append(review)
        return reviews

x = PlayReviews()
y = x.get_reviews("com.daamitt.walnut.app")
