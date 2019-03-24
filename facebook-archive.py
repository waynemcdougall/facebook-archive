"""
facebook-archive: a tool to download all posts from a Facebook page and place in a database

Copyright 2018 Wayne W. McDougall

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contact details:
waynemcdougall@gmail.com

Wayne W. McDougall
714 Richardson Road
Hillsborough
Auckland 1041
New Zealand
"""

# Inspired by the article at 
# https://hackernoon.com/graphapi-get-query-fetch-public-facebook-page-feed-3-ste$

token="EAACqYdryyxMBAMwz9nDhyBN9VHYY3rdK33mYcSIWQmomXwChvqthm3T6jAmISkVrK6r0vRedm0L1kZAOh88oA9CnCJlsL8vkZA6gIzqFYxkJroh3XYILt7oohGxSOk3yoQGjZCKWmZBAZBKUB1ZClzu007A9zP5iHDKEoU4XurULO8KLCE3BZBm2qHmjCQZCtasZD"
# https://developers.facebook.com/tools/explorer/
# Page Access Token

import json
import urllib2
import time
import re
import argparse
import sqlite3

print("""
    facebook-archive Version 2.00:  Copyright 2018 Wayne W. McDougall
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions.
""")

def loadPage(db,url):

  c = db.cursor()
  c.execute('''select processedto_time from settings''')
  p = c.fetchone()
  if p:
    processedto_time=p[0]-86400;
  else:
    print("Missing processed_to time. Working back to the start of time")
    processedto_time=0;
  count = 0
  while True:
    # delay
    time.sleep(1)
    # download
    response = urllib2.urlopen(url)
    content = response.read()
    payload = ''
    try:
      payload = json.loads(content)
    except:
      print ("JSON decoding failed!")	
      print (content)
      return 0
    # print payload 
    if 'data' in payload:
        for post in payload['data']:
            if 'id' in post:
                c.execute('''select status from posts where id=?''',(post['id'],))
                p = c.fetchone()
                if (not p):
                  count = count + 1
                  print (count)
                  c.execute('''INSERT INTO posts(id,status,created_time,full_picture,link,description,message,name,object_id,parent_id,permalink_url,picture,source,status_type,type) VALUES(?,0,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (post['id'],post['created_time'],post.get('full_picture',''),post.get('link',''),post.get('description',''),post.get('message',''),post.get('name',''),post.get('object_id',''),post.get('parent_id',''),post.get('permalink_url',''),post.get('picture',''),post.get('source',''),post['status_type'],post['type']))
                  db.commit()
                else:
                   if post['created_time'] < processedto_time:
                     print ("Found a post more than a day older than one I have already stored")
                     return 1
        if 'paging' in payload:
            if 'next' in payload['paging']:
               url=payload['paging']['next']
            else:
               print ("That seems to be all\n")
               return 1
        else:
            print ("No paging found - that's weird")
            print (payload)
            return 0
    else:
       print ('Unknown payload:')
       print (payload)

# entry point:

# get args
parser = argparse.ArgumentParser()
parser.add_argument('id', help='ID of Graph API resource')
# parser.add_argument('token', '--token', help='Authentication token')
args = parser.parse_args()

# setup database
db = sqlite3.connect('facebook.sql')
c = db.cursor()
c.execute('CREATE TABLE if not exists settings (processedto_time integer);')
c.execute('CREATE TABLE if not exists posts(id text PRIMARY KEY, status integer, tags text,created_time integer,full_picture text,link text,description text,message text,name text,object_id text,parent_id text,permalink_url text,picture text,source text,status_type text,type text)');
c.execute('CREATE TABLE if not exists tags(tag text PRIMARY KEY, parenttag text)');
db.commit()

# read post IDs
try:
    if loadPage(db,"https://graph.facebook.com/%s/posts?date_format=U&fields=id,created_time,full_picture,link,description,name,message,parent_id,object_id,permalink_url,picture,source,status_type,type&access_token=%s" % (args.id, token)):
      print ("Finished")
      c.execute("update settings set processedto_time=(select max(created_time) from posts)")
      db.commit()
except urllib2.HTTPError as e:
    print ("Download failed:",e)
    error_message = e.read()
    print (error_message)
except KeyboardInterrupt:
    print ("Canceled!")

