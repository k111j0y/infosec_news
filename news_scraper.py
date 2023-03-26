#! /usr/bin/env python3
################################################################################
##   News Feed Presenter
################################################################################
## https://towardsdatascience.com/an-extensive-guide-to-collecting-tweets-from-twitter-api-v2-for-academic-research-using-python-3-518fcb71df2a
## https://www.threatable.io/

import configparser, tqdm, json, urllib3, requests, os, bs4, pprint, ast , re, html2text

import pandas as pd
import snscrape.modules.twitter as sntwitter

from datetime import datetime, timedelta
from tqdm import tqdm
from pysondb import db



################################################################################
## Global Vars
################################################################################
## Define DB source:
news_db = db.getDb("<PATH HERE>")



# keyword_list to search for
keyword_list = ['']

# List of Twitter twit names to scrape
twitter_users = ['']

# Calculate the date and time 24 hours ago
since_date = datetime.today() - timedelta(days=1)


# Twitter golbals
lst_of_tweets = []
filtered_list_of_tweets = []
regex_for_keywords = ''

# Masto Globals
instance_url = 'https://mastodon.social'

mastodon_users_list = [
    ''
]

################################################################################
## MASTODON 
################################################################################
def masto_user_id_lookup(acct):
    URL = f'https://mastodon.social/api/v1/accounts/lookup'
    params = {
        'acct': acct
    }
    mast_api_req = requests.get(URL, params=params)
    masto_user = json.loads(mast_api_req.text)
    return masto_user


def scrape_toots(masto_user):
    try:
        masto_user = masto_user_id_lookup(acct=f'{masto_user}') 
        mast_user_id = masto_user['id']
        mastodon_api_endpoint = f'{instance_url}/api/v1/accounts/{mast_user_id}/statuses'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Accept': 'application/json'
        }
        params = {
            'only_media': 'false',
            'exclude_replies': 'true',
            'exclude_reblogs': 'true',
            'limit': '30'
        }
        req_user_toots = requests.get(mastodon_api_endpoint, params=params, headers=headers)
        user_toots = req_user_toots.json()
        filtered_list_of_toots = []
        for toot in user_toots:
            if toot['created_at'][:16] > since_date.strftime("%Y-%m-%dT%H:%M:%S%f")[0:16]:
                user_name = toot['account']['username']
                toot_id = toot['id']
                toot_content = str(html2text.html2text(toot['content'])).replace('\n',' ').strip('“').replace("’","'").strip('”')
                toot_time = toot['created_at']
                toot_tags = toot['tags']
                formatted_toot_information = rf'{{"user":"{user_name}", "content": "{toot_content}", "content_id": "{toot_id}", "date": "{toot_time}", "hashtags": "{toot_tags}"}}'
                filtered_list_of_toots.append(formatted_toot_information)
                #return filtered_list_of_toots
                #string_add = str(formatted_toot_information)
                #print(string_add)
                #user_toots_dict = ast.literal_eval(string_add)
                #news_db.add(user_toots_dict)
                print(filtered_list_of_toots)
    except SyntaxError:
        print("Syntax Error Found")
        pass
    except Exception as e:
        print("NON Syntax Error Found")
        pass


def toots_loop():
    for masto_user in mastodon_users_list:
        scrape_toots(masto_user)


################################################################################
## TWITTER 
################################################################################
def filter_tweets():
    for twit in twitter_users:
        query = f'from:{twit} since:{since_date.strftime("%Y-%m-%d")}'
        #print(query)
        scraper = sntwitter.TwitterSearchScraper(query)
        for i,tweet in enumerate(scraper.get_items()):
            data_i_want = [
            tweet.date.strftime("%Y-%m-%d  %H:%M:%S"),
            tweet.rawContent,
            tweet.user.username,
            tweet.hashtags,
            tweet.id
            ]
            lst_of_tweets.append(data_i_want)
            if i > 30:
                break
    regex_for_keywords = '(?i)(?:'
    for i in keyword_list:
        regex_for_keywords += f"{i}|"
    regex_for_keywords = regex_for_keywords[0:-1:]
    regex_for_keywords += ")"
    #return regex_for_keywords
    for tweet in lst_of_tweets:
        if re.search(rf'{regex_for_keywords}', rf'{tweet}') is None:
            continue
        else:
            filtered_list_of_tweets.append(tweet)
    tweets_df = pd.DataFrame(
        filtered_list_of_tweets, columns=['Date','Tweet','User','Hashtags','ID']
    )
    for index, row in tweets_df.iterrows():
        print(f'''%%%%%%%%%%%%%%% {row[2]} %%%%%%%%%%%%%%%
Date: {row[0]}
Content: {row[1]}
Hashtags: {row[3]}
ID: {row[4]}

''')


################################################################################
## Threatable.io
################################################################################
def get_threatable_blog_posts():
    browser_session = requests.Session()
    thtAbleBrwsrSes = browser_session.get('https://www.threatable.io/')
    allTextOnPage = bs4.BeautifulSoup(thtAbleBrwsrSes.text, 'html.parser')
    thtAbleBodySectionFilter = allTextOnPage.find_all('tbody')
    thtAbleBlogsSectFilter = thtAbleBodySectionFilter[0]
    threatableIndividualBlogPost = thtAbleBlogsSectFilter.find_all('tr')
    for blog in threatableIndividualBlogPost:
        current_time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        story_name = str(blog.a.text.replace('\r\n','').replace('\"','\'').strip('^ ').strip(' $'))
        story_href = blog.a.get('href')
        story_author = ''
        if story_name.count("|") >= 1:
            story_author = str(story_name.split("|")[1].strip(" by "))
        else:
            continue
        formatted_addition = rf'{{"user":"{story_author}", "content": "{story_name}", "content_id": "", "date": "{current_time_string}", "hashtags": "{story_href}"}}'
        # string_add = str(formatted_addition)
        # mydict = ast.literal_eval(string_add)
        # news_db.add(mydict)
        print(formatted_addition)


################################################################################
## CLOSING // RUN IT
################################################################################
if __name__ == "__main__":
    get_threatable_blog_posts()
    filter_tweets()
    toots_loop()






