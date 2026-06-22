# Domain

In reddit when we come across a subreddit that we like we scroll through it and it usually works fine, however, a possible improvement can acheived by using a ML model to categorise the subreddit into distinct mutually exclusive categories. 

For example in our chosen domain which is chess we have different types of people who are interested in chess. The things one person is interested in could pertain only to one of two categories and not to all. In such a case the user would have to wade through a large number of posts which may not be interesting to them at all. For example, a person interested in chess could be learner who just wants to learn more about the game and is not interested in Magnus Carlens victories or shocking upsets in the world championships. 


# Labeling

I am classifying the subrredit /r/chess

The definition and examples of the labels are:

1. sports-news: world championships results, sports news, anything related to current events in the chess sport. 

example: 
"Ding Liren after becoming double World Champion..."
https://www.reddit.com/r/chess/comments/1ubopx8/ding_liren_after_becoming_double_world_champion/

example:
"Individual Medalists for the FIDE World Team Blitz Championship 2026 |"
https://www.reddit.com/r/chess/comments/1ubpdwf/individual_medalists_for_the_fide_world_team/


2. educative: informative about the sport, information about chess tactics, strategies and articles that distills some information about chess including not particularly useful information as well. 

example:
"My farewell letter to chess and some controversial tips on how to consistently gain rating..."

https://www.reddit.com/r/chess/comments/1u3uvb9/my_farewell_letter_to_chess_and_some/

example:
Is there any good analysis of aging and chess performance decline?
https://www.reddit.com/r/chess/comments/1u2o99a/is_there_any_good_analysis_of_aging_and_chess/

3. entertaining: chess in pop media, historical antidotes and stories, funny videos and pictures, light hearted posts involving chess in any way. 

example:
" "unwinnable" position for black from an anime..."
https://www.reddit.com/r/chess/comments/1u79jwy/unwinnable_position_for_black_from_an_anime/

example:
My girlfriend doodled a logo for Dragon Chilling
https://www.reddit.com/r/chess/comments/1ubn2cl/comment/osx9y94/


## Label edge cases (hardest anticipated edge case)

Examples:
1. "Endgame.AI to the finals!!!
News/Events..."

Here, this could either relate to entertainment as a fun post about chess engines or it could be a news post about a recent event in chess news in which case it would be in the sports-news category.

2. "Pragg is honoured with a cash award of INR 50 lakhs (US $52,331) by Tamil Nadu Chief Minister Vijay (who also happens to be one of India's most popular superstars) for winning Norway Chess 2026."

Here, this could either be a fun post about an interesting event or it could also be categorised as a sport event news. 

Possible solutions to the edge cases:
We can probably pull in some of the metadata and tags into the text column of the dataset which might be helpful as the tags in the subreddit post does categorise into our labels somewhat. 


# Data extraction to dataset from raw data

I have manually annotated the raw data in /data into the subfolders which correspond to the three labels that I have chosen.

We will populate the takemeter_dataset.csv file by:

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


# Data Collection Plan & Evaluation Metrics

Collection: manually pull r/chess posts (main post + top comments) via the saved raw JSON, annotate into the three label folders, then build takemeter_dataset.csv. Aim for a balanced set across labels to avoid the class imbalance that hurt the first run.

Metrics: report per-class precision, recall, F1, and overall accuracy.
- Accuracy alone hides per-class failure (e.g. minority 'sports-news'), so we track per-class metrics.
- F1 balances precision and recall, which matters under class imbalance.
- A confusion matrix is used to see exactly which labels get confused (the chess-topic → 'sports-news' over-generalization).


# "Good Enough" Performance

Target: overall accuracy ≥ 0.80 AND each per-class F1 ≥ 0.70, beating the zero-shot baseline. Below this the model is not useful for filtering the subreddit.


# AI Tool Plan

Use the model for failure pattern analysis: feed misclassified test examples back and group the errors (e.g. "chess topic defaulted to sports-news regardless of genre") to decide which edge cases need more annotated data. May also use AI to generate synthetic minority-class data and to assist annotation of edge cases.

