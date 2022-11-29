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


# Load the config
config = configparser.ConfigParser()
config.read('config.ini')

feedurl = config['feed']['feed_url']
feedname = config['feed']['feed_name']
feedvisibility = config['feed']['feed_visibility']
feedtags = config['feed']['feed_tags']
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
         spottime = dateutil.parser.parse(entry['published']).timestamp()
         firsttwo = clean[:2]
         firstthree = clean[:3]
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
              tootText = clean + feedtags + " ***EXPERIMENTAL BOT***DO NOT USE FOR OFFICIAL ADVICE***"
              soup = BeautifulSoup(entry['summary'], 'html.parser')
              for img in soup.findAll('img'):
                print("***IMAGE:",img.get('src'))
                imgfile = img.get('src')
                temp = tempfile.NamedTemporaryFile()
                res = requests.get(imgfile, stream = True)
                if res.status_code == 200:
                    shutil.copyfileobj(res.raw, temp)
                    print('Image sucessfully Downloaded')
                    print (temp.name)
                    mediaid = mastodonBot.media_post(temp.name, mime_type="image/jpeg")
                    try:
                       postedToot = mastodonBot.status_post(clean,None,mediaid,False, feedvisibility)
                       lastpost = clean
                       isposted = True
                    except Exception as e:
                       print(e)
                else:
                       print('Image Couldn\'t be retrieved')
                temp.close()
              if (isposted == False):
                   try:
                       postedToot = mastodonBot.status_post(tootText,None,None,False,feedvisibility)
                       lastpost = clean
                   except Exception as e:
                       print(e)
                    
              lastspottime = spottime
    now = datetime.now().timestamp()
#    print ("time:",now)
    time.sleep(60)
