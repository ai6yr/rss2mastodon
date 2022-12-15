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
try:
   max_image_size  = int(config['mastodon']['max_image_size'])
except:
   max_image_size = 1600
try:
   feeddelay  = int(config['feed']['feed_delay'])
except:
   feeddelay = 180
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
   try:
    data = (feedparser.parse(feedurl))
    entries = data["entries"]
    for entry in entries:
  #       print ("----------------")
#        print (entry)
         clean = re.sub("<.*?>", "", entry['summary'])
         # next section is all completely messy and needs to be replaced, hack to linkify urls
         clean = clean.replace("&amp;","&")
         clean = clean.replace("nitter.net","https://nitter.net")
         clean = clean.replace("go.usa.gov","https://go.usa.gov")
         clean = clean.replace("wpc.ncep.noaa.gov","https://wpc.ncep.noaa.gov")
         clean = clean.replace(" weather.gov"," https://weather.gov")
         clean = clean.replace("nwschat.weather.gov"," https://nwschat.weather.gov")
         # end messy hacking
         tootText = clean + feedtags 
         tootText = tootText[:499]
         spottime = dateutil.parser.parse(entry['published']).timestamp()
         title = entry['title']
         firsttwo = title[:2]
         firstthree = title[:3]
         if (spottime > lastspottime):
        # if (1):
        #   print (tootText)
        #   time.sleep(10)
           if (clean == lastpost):
               print ("skip: retweet")
           elif ("RT" in firsttwo):
               print ("skip: retweet")
           elif ("Re" in firstthree):
               print ("skip: reply")
           else:
              isposted = False
              print (clean)
              soup = BeautifulSoup(entry['summary'], 'html.parser')
              medialist = []
              for video in soup.findAll('source'):
                print("***VIDEO:",video.get('src'))
                imgfile = video.get('src')
                temp = tempfile.NamedTemporaryFile()
                res = requests.get(imgfile, stream = True)
                if res.status_code == 200:
                    shutil.copyfileobj(res.raw, temp)
                    print('Image sucessfully Downloaded')
                    print (temp.name)
                    try:
                      mediaid = mastodonBot.media_post(temp.name, mime_type="video/mp4")
                      medialist.append(mediaid)
                    except Exception as e:
                      print (e)
                      print ("Unable to upload video")
                else:
                       print('Video Couldn\'t be retrieved')
                temp.close()
              for img in soup.findAll('img'):
                print("***IMAGE:",img.get('src'))
                imgfile = img.get('src')
                temp = tempfile.NamedTemporaryFile()
                res = requests.get(imgfile, stream = True)
                if res.status_code == 200:
                    shutil.copyfileobj(res.raw, temp)
                    print('Image sucessfully Downloaded')
                    print (temp.name)
                    #ensure image will fit on server
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
                    try:
                       mediaid = mastodonBot.media_post(temp.name, mime_type="image/png")
                       medialist.append(mediaid)
                    except Exception as e:
                       print ("Unable to upload image.")
                       print (e)
                else:
                       print('Image Couldn\'t be retrieved')
                temp.close()
              if (isposted == False):
                   try:
                       postedToot = mastodonBot.status_post(tootText,None,medialist,False,feedvisibility)
                       lastpost = postedToot
                   except Exception as e:
                       print(e)
                    
              lastspottime = spottime
    now = datetime.now().timestamp()
   except e as Exception:
      print (e) 
   time.sleep(feeddelay)
