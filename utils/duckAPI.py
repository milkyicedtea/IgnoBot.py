import requests
from bs4 import BeautifulSoup

#download page
url = "https://www.reddit.com/r/duck/"
response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")

images = soup.find_all("img", attrs = {"alt": "Post image"})

for image in images:
    image_src = image["src"]
    print(image_src)