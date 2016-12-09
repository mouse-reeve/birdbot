''' let's learn about birds '''
from bs4 import BeautifulSoup
import json
import os
import PIL
import random
import re
import requests
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

# pick a mythological creature
# extract first sentence
# cut sentence at first verb

# make a bird fact
print 'The %s (%s) ...' % (bird, scientific)

# attach birdfact to image

# tweet it out
