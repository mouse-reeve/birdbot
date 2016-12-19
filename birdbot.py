''' let's learn about birds '''
import blacklist
from bs4 import BeautifulSoup
from html import unescape
import json
import os
import random
import re
import requests
import settings
from TwitterAPI import TwitterAPI
from urllib.request import urlretrieve

# pick a bird form the list
line = json.loads(random.choice(open('birdlist').readlines()))
url = line['url']
bird = line['name'][0].lower() + line['name'][1:]

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
pronouns = ['she ', 'he ']
prompts = [
    'acts like ',
    'doesn\'t ',
    'has ',
    'is just ',
    'is only ',
    'keeps ',
    'loves to ',
    'lives in ',
    'makes ',
    'should really ',
    'totally ',
    'takes ',
    'thinks ',
    'travels ',
    'tries to ',
    'tends to ',
    'was ',
    'wasn\'t ',
    'will ',
]

pronoun = random.choice(pronouns)
prompt = pronoun + random.choice(prompts)

api = TwitterAPI(settings.API_KEY, settings.API_SECRET,
                 settings.ACCESS_TOKEN, settings.ACCESS_SECRET)
# get tweets
tweets = api.request('search/tweets', {'q': '"%s"' % prompt})

fact = 'The %s (%s) %s' % (bird, scientific, re.sub(pronoun, '', prompt))

# look through tweets
for tweet in tweets:
    if not 'text' in tweet:
        continue
    text = tweet['text']

    # lowercase just the prompt
    text = re.sub(prompt, prompt, text, flags=re.IGNORECASE)

    # require that the prompt be the first thing in the sentence
    if not re.match(r'(^|.*[\.\?\!].)\b%s' % prompt, text):
        continue

    # separate out usable string
    search = re.search(r'\b%s\b.*[\.\?!]' % prompt.strip(), text)
    try:
        text = search.group()
    except AttributeError:
        continue

    # avoid &amp; and similar
    text = unescape(text)

    # end at end of sentence
    text = re.sub(r'([\.?!\n\r]).*$', r'\g<1>', text)
    if blacklist.check_blacklist(text):
        continue
    if not re.search(r'["@)\|]|http|\bshe\b|\bher\b|\bhe\b|\bhim\b', text) \
            and len(fact + text) < 140:
        fact += text
        break

# post that bird!
image_file = open(outpath, 'rb')
data = image_file.read()
r = api.request('statuses/update_with_media',
                {'status': fact}, {'media[]': data})
