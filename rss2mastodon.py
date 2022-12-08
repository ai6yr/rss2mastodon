"""
RSS -> Fediverse gateway

AI6YR - Nov 2022
"""
# imports (obviously)
import configparser
from mastodon import Mastodon
import requests
import time
from datetime import datetime
import dateutil
import json
import feedparser
from bs4 import BeautifulSoup
import re
import tempfile
import shutil
from PIL import Image

# Load the config
config = configparser.ConfigParser()
config.read('config.ini')

feedurl = config['feed']['feed_url']
feedname = config['feed']['feed_name']
feedvisibility = config['feed']['feed_visibility']
feedtags = config['feed']['feed_tags']
max_image_size  = int(config['mastodon']['max_image_size'])
print (feedurl)
print (feedname)
# connect to mastodon
mastodonBot = Mastodon(
    access_token=config['mastodon']['access_token'],
    api_base_url=config['mastodon']['app_url']
)

print ("Starting RSS watcher:" + feedname)
lastpost = ""
lastspottime = datetime.now().timestamp()
while(1):
    data = (feedparser.parse(feedurl))
    entries = data["entries"]
#    print (entries)
    for entry in entries:
         #print (entry['summary'])
         clean = re.sub("<.*?>", "", entry['summary'])
         clean = clean.replace("&amp;" ,"&")
         spottime = dateutil.parser.parse(entry['published']).timestamp()
         firsttwo = clean[:2]
         firstthree = clean[:3]
#         if (1):
         if (spottime > lastspottime):
           if (clean == lastpost):
               print ("skip: retweet")
           elif ("RT" in firsttwo):
               print ("skip: retweet")
           elif ("Re" in firstthree):
               print ("skip: reply")
           else:
              isposted = False
              print (clean)
              tootText = clean + feedtags 
              tootText = tootText[:499]
              soup = BeautifulSoup(entry['summary'], 'html.parser')
              medialist = []
              for img in soup.findAll('img'):
                print("***IMAGE:",img.get('src'))
                imgfile = img.get('src')
                temp = tempfile.NamedTemporaryFile()
                res = requests.get(imgfile, stream = True)
                if res.status_code == 200:
                    shutil.copyfileobj(res.raw, temp)
                    print('Image sucessfully Downloaded')
                    print (temp.name)
                    image = Image.open(temp.name)
                    if ((image.size[0]>max_image_size) or (image.size[1]>max_image_size)):
                        origx = image.size[0]
                        origy = image.size[1]
                        if (origx>origy):
                             newx = int(max_image_size)
                             newy = int(origy * (max_image_size/origx))
                        else:
                             newy = int(max_image_size)
                             newx = int(origx * (max_image_size/origy))
                        image = image.resize((newx,newy))
                        print ("new image size",image.size)
                        image.save(temp, format="png")
                    mediaid = mastodonBot.media_post(temp.name, mime_type="image/jpeg")
                    medialist.append(mediaid)
                else:
                       print('Image Couldn\'t be retrieved')
                temp.close()

              try:
                       postedToot = mastodonBot.status_post(tootText,None,medialist,False,feedvisibility)
                       lastpost = clean
              except Exception as e:
                       print(e)
                    
              lastspottime = spottime
    now = datetime.now().timestamp()
#    print ("time:",now)
    time.sleep(60)
