#!/usr/bin/env python
# coding:utf-8

# Python imports
import json
import requests

# Bibblio Python imports
from helpers import construct_recommendations_url
from urls import enrichment_url


# Content Item Endpoints
def recommendations(access_token, content_item_id):
	'''
	Name: recommendations
	Parameters: access_token, content_item_id
	Return: dictionary
	'''

	headers = {'Authorization': 'Bearer ' + str(access_token)}
	recommendations_url =\
		construct_recommendations_url(enrichment_url, content_item_id)

	request = requests.get(recommendations_url, headers=headers)
	if request.status_code == 200:
		recommendations = request.json()
		return recommendations

	return {'status': request.status_code, "message": request.text}
