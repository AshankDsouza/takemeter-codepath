
# Labeling

I am classifying the subrredit /r/chess

The definition of the labels are:

1. sports-news: world championships results, sports news

example: 
"Ding Liren after becoming double World Champion..."
https://www.reddit.com/r/chess/comments/1ubopx8/ding_liren_after_becoming_double_world_champion/

2. educative: informative about the sport

example:
My farewell letter to chess and some controversial tips on how to consistently gain rating

https://www.reddit.com/r/chess/comments/1u3uvb9/my_farewell_letter_to_chess_and_some/

3. entertaining: chess in pop media, historical antidotes and stories, funny videos and pictures, light hearted posts

"unwinnable" position for black from an anime
https://www.reddit.com/r/chess/comments/1u79jwy/unwinnable_position_for_black_from_an_anime/



# Data extraction to dataset from raw data

We need a using the scrapper-chess app which is a Devvit app use it to populate the takemeter_dataset.csv file by:

1. using the files in /data folder populate takemeter_dataset.csv 
    
The data is in the format: RedditPost[]
where the first element in the list is the main post itself and second is the comments and has the comments under .children.

The relavent text from the main post and the comments can be kept in the 'text' column. metadata about the users, date, field values should be kept inside the text column only the post content and its comments. 
If there is a doubt about the json format examine one file and figure its format and where to get the post text and comments. The post content(main post) and its comments should be appended and set under the text column. 

Also make sure that the script errors out if there is a not a minimum of 10 files for each category. 


2. Fill in the columns for each category:
    i. text: the url heading, post and top three comments
    ii. label: keep this as: 
          All files in data/sports_news = sports-news
          All files in data/educative = educative
          All files in data/entertaining = entertaining
    iii. notes: keep this empty for now
    iv. url: fill this with the url of the link

