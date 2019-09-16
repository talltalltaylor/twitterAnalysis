# CS5395 -  IND STUDY - Project


### Tweet Analysis DB

This repository was created as part of CS 5395 IND STUDY Project

###    
### Abstract
Twitter data has been used extensively for research in the past years. The large number of users and messages shared every day creates interesting data for many different areas of research. The process to analyze Twitter data requires a series of initial steps independent of the research subject. This study proposes a subject agnostic pipeline to analyze Twitter data. It also includes an exploratory topic analysis using three known unsupervised machine learning models (LDA, LSI and NFM).  A database of over 3 million tweets related to the #MeToo movement was used as case study. Analytics extracted from this dataset illustrate common findings and challenges.

###    
### **See Notebook **
See a sample notebook showing how to use the library.  
Open file: **"TestingLibrary.ipynb"**


###    
### Database Design
Document driven NoSql databases such as MongoDB use the concept of collections. Collections are structures that hold all documents. Collections are similar to tables in relational databases. 
The following are the collections created for this pipeline:

+ **loadedFiles**: This collection will save the directory and file names that have been loaded already. LoadTime and path will be columns. This is to make sure we don't load the same files multiple times.
twitterSearches. This collection will save the searches requested to Twitter API. This will only be used when the tweets are being saved straight from Twitter API.
This is to keep track of what search requests have been done already. It will help to determine the number of results returned for a search and will also help us to make sure we don’t waste requests doing the same searches.

+ **tweet**: This collection will be used to save the complete tweet document. It will also contain a sequence number that will be used in the recovery process.

+ **focusedTweet**: This collection will only contain the interesting information from the tweets. It will only contain the fields that were set on the settings. 

+ **tweetWords**: This collection will save each word separately from every tweet plus some extra information about the tweet. It will also contain interesting tags about that word. (e.g English or not, verb or not, etc.)

+ **htTopics**: This collection will save topic information for each hashtag using the three different unsupervised ML models

+ **loadStatus**: This collection will controls have been loaded into DB already. This collection was created to manage the recovery logic.

+ **tweetCountByFileAgg**: This collection will contain the count of all tweets in the dataset by files loaded.

+ **tweetCountByPeriodAgg**: This collection will contain the count of all tweets in the dataset by period. The period will be specified in the settings collection.

+ **tweetCountByLanguageAgg**: This collection will contain the count of all tweets in the dataset by language.

+ **tweetCountByUserAgg**: This collection will contain the count of all tweets in the dataset by user id. It will also include details about the user itself. The extra information about the user loaded in this collection will be identified in the settings collection.

+ **hashTagCountAgg** : This collection will contain the frequency of all hashtags in the dataset.


###    
### Python Library
The library includes logic to extract data directly from Twitter’s API and to extract data from existent twitter .json files. The library also contains a process to select, clean and organize the data based on the given settings. Logic to export meaningful data to tab delimited .txt files is also included.

The following are the main functions included in the library:

+ **loadDocFromFile**: This method will load tweet .json files into the DB (tweet collection). It goes through all .json files in the directory and load them one by one. It also saves the files already loaded into the 'loadedFiles' collection to make sure we don't load the same file twice.

+ **loadFocusedData**: This method will load the focusedTweet collection with the interesting information we want to study 

+ **loadWordsData**: This method will break text from tweets into words and tag them

+ **loadAggregations**: This method will load the aggregation queries. One or many can be run. The parameters will help decide which ones to run.

+ **findTopics**: This method will find the topics for a hashtag using different models and tools

+ **exportData**: This method will export the data into “|” delimited files
++ Parameters: exportType: (tweetCountByUser, tweetCountByLanguage, tweetCountByFile, tweetCountByMonth, hashtagCount, tweetTextAndPeriod, wordsOnEachTweet, userDetailsOnEachTweet)
++ filepath: the file path where the files will be saved  
++ inc: To set how many lines per files we want to save. This is for collection that have too many records to be saved. memory issues can happens if this number is too bi
Only works when exporting for types tweetTextAndPeriod, wordsOnEachTweet, userDetailsOnEachTweet, we can set how many lines per file
    
+ **extractDocFromAPI**: This method will load tweets from Twitter API. the full code is at https://git.txstate.edu/l-n63/CS7311


###    
### Recovery Process
The pipeline includes a recovery logic to make sure the processes don’t have to get run from the beginning in case of a failure. While inserting into the tweet collection, a sequence number gets attached to each tweet. Then every time any processes need to run, that sequence number is used to control what has already been processed or not. If something fails, the logic will be able to identify the last sequence number processed and continue from there.

###   
### IND STUDY Deliverables:
Deliverable 1:  Report that contains high level overview and summary of existing Natural Language Processing Methods as applied to topic analysis and trending in social media

Deliverable 2: Report on the no-SQL database design, use, and expansion.  Proposal of generic pipeline for topic identification and detection that is language agnostic and to an extent media-agnostic.  

Deliverable 3: Python code as a proof of concept of Deliverable 2 with 2 distinct data sources. 

Deliverable 4: Report that contains possible information integration directions ideas from other domains. 
