''' let's learn about birds '''
from bs4 import BeautifulSoup
import json
import os
import random
import re
import requests
import settings
from TwitterAPI import TwitterAPI
from urllib import urlretrieve

# pick a bird form the list
line = json.loads(random.choice(open('birdlist').readlines()))
url = line['url']
bird = line['name']

# download the bird's wikipedia entry
entry = requests.get('http://en.wikipedia.org%s' % url)
soup = BeautifulSoup(entry.text)

scientific = soup.find(class_='binomial').text

# find thumbnail
src = soup.find(class_='image').find('img')['src']
# compute full sized image url from thumbnail
extension = '.JPG' if '.JPG' in src else '.jpg'
src = src.split(extension)[0] + extension
image_url = 'https:' + re.sub('thumb/', '', src)
# download bird image
filename = re.sub(' ', '-', bird.lower()) + '.jpg'
outpath = os.getcwd() + '/images/%s' % filename
urlretrieve(image_url, outpath)

# search twitter for the fact
prompts = [
    'she acts like ',
    'she finds ',
    'she is just ',
    'she is only ',
    'she loves to ',
    'she lives in ',
    'she should really ',
    'she takes ',
    'she travels ',
    'she tries to ',
    'she tends to ',
]
# https://twitter.com/search?f=tweets&vertical=default&q=%22tends%20to%22&src=typd
prompt = random.choice(prompts)
twitter_url = 'https://twitter.com/search?f=tweets&vertical=default&q="'
twitter_url += prompt
twitter_url += '"&src=typd'
tweets = requests.get(twitter_url)
soup = BeautifulSoup(tweets.text)

fact = 'The %s (%s) %s' % (bird, scientific, re.sub('she ', '', prompt))

# look through tweets
for tweet in soup.find_all(class_='tweet-text'):
    text = tweet.text
    text = text.split(prompt)[-1]
    # end at end of sentence
    text = re.sub(r'([\.?!\n\r]).*$', r'\g<1>', text)
    if not '"' in text and len(fact + text) < 140:
        fact += text
        break

# post that bird!
api = TwitterAPI(settings.API_KEY, settings.API_SECRET,
                 settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
image_file = open(outpath, 'rb')
data = image_file.read()
r = api.request('statuses/update_with_media',
                {'status': fact}, {'media[]': data})
