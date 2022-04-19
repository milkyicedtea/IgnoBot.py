import os
import requests

catapi_key = os.getenv('catapi_key')

url = 'https://api.thecatapi.com/v1/breeds/search'

headers = {catapi_key}

response = requests.request('GET', url, headers = headers)

print(response.text)