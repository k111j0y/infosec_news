# infosec_news
A py script to reach out to a blog, twitter, mastodon, and more to follow.
It will
  -pull posts
  -filter for keywords
  -present you with the matches

This script currently makes use of an already curated blog list @ https://threatable.io (huge props to the people organizing that!).
More to come!

# Project Notes
snscrape or twitter have a 41 parameter limit for "or" statements. So, you need to grab <i>all</i> the tweets from your users. Regex seemed to be the easiest method to parse with. 

# Noteworthy Items
As it stands, you have to hard code users and keywords into the program.  This is easily changed, but left as an exercise to the user if they chose.  (Just use the input() function).
In this script the newsDB has been overridden and output just comes to the screen.  I'm currently working on the best way to store and present data.
