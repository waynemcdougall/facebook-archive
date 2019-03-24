# facebook-archive
Archive posts to a Facebook page - you must be an admin or be able to get a page access token

Inspired by the following article:
https://hackernoon.com/graphapi-get-query-fetch-public-facebook-page-feed-3-step-tutorial-example-access-token-auth-post-d7403c717fbf

Requirements:
python2
Modules listed in requirements.txt

You need to:
1. Identify the Facebook Graph ID of the group / page you are archiving
2. Get a Page Access Token for that page
3. Edit facebook-archive.py to put in that Page Access Token in the line that says
token="lotsoflettersandnumbers"

The default page access token only lasts about 2 hours. You can get a token that lasts about 6 months, but I forgot how.

Usage:

python2 facebook-archive <Graph-ID>
  
  
