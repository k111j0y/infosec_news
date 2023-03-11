#! /usr/bin/env python3
################################################################################
##   News Feed Presenter
################################################################################
import configparser, tqdm, json, urllib3, requests, os, bs4, pprint, ast 

import pandas as pd
import snscrape.modules.twitter as sntwitter

from datetime import datetime, timedelta
from tqdm import tqdm
from pysondb import db



################################################################################
## Global Vars
################################################################################
## Define DB source:
news_db = db.getDb("<fix your path here>")

# keyword_list to search for
keyword_list = ['macOS','osx','ios','system32','dcom','PEBear','win32','exploit','stealer','exchange','AADInternals', 'elf','root','python','wireshark','powershell','.net','dotnet','dot net', 'amsi', 'mfa','pth','rce','cve','reversing','yara','suricata','sigma','sentinelone','crowdstrike','carbonblack','logscale','lucene','lpe','artifact','tampering','xss','persistent','persistence','kernel','low conf','med conf','medium conf','high conf','bypass','shellcode', 'github','git','c3','c2']

# List of Twitter twit names to scrape
twitter_users = ['vxunderground','gabby_roncone','johnholtquist','wdormann','thehackernews','inversecos','olafhartong','lorenzofb','thedfirreport','kostastsale','esetresearchgroup','sans_isc','patrickwardle','TheRecord_media','citizenlab','ransomwarenews','pr0xylife' ,'0xdf_', 'malware_traffic']

# Calculate the date and time 24 hours ago
since_date = datetime.today() - timedelta(days=1)

lst_of_tweets = []
filtered_list_of_tweets = []
regex_for_keywords = ''



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
            tweet.hashtags
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
        filtered_list_of_tweets, columns=['Date','Tweet','User','Hashtags']
    )
    for index, row in tweets_df.iterrows():
        print(f'''%%%%%%%%%%%%%%% {row[2]} %%%%%%%%%%%%%%%
Date: {row[0]}
Content: {row[1]}


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
        current_time_string = datetime.now().strftime("%Y-%m-%d %H:%M:%S:%f")
        story_name = str(blog.a.text.replace('\r\n','').replace('\"','\'').strip('^ ').strip(' $'))
        story_href = blog.a.get('href')
        formatted_addition = rf'{{"name": "{story_name}","link": "{story_href}","firstish_seen": "{current_time_string}"}}'
        string_add = str(formatted_addition)
        mydict = ast.literal_eval(string_add)
        news_db.add(mydict)



################################################################################
## CONDITIONAL BLOCK / NAMING
################################################################################
if __name__ == "__main__":
    get_threatable_blog_posts()
    filter_tweets()
