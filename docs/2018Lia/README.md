## CS7311 - Project 
### English loanwords in Brazilian Portuguese

This repository was created as part of CS 7311 Project to analyze  the use of English loan words in Brazilian Portuguese informal writing using Twitter data.


This repository includes an initial version of the automation process to get similar results using new data



## Classes:
### Class TweetExtract:

-Functionality to request data from twitters APIs and save it in MongoDB database. 

-The MongoDB connection string and Tweet Bearer token are required as parameters.

-Once instantiated the class can be called to do searches on Twitter and accepts the following parameters: 
ApiName (30Day or fullarchive), Query, StartDate, EndDate and MaxResults. 

 
### Class TagAndClean.py:

Uses the Tweets collection saved on MongoDB to breakdown the words in the tweets text, clean them and tag the words according to the NLTK corpora. 

 
### Class Results.py:

Has options to print or export some of the results. 

 
### Class BR_EN_LoanWords_Run.py:

Main class showing simple examples of how to use the other three classes


 
## Data:
The repository also includes some of the source and result datasets used in the project including the complete list of words and their tags, the final list of English words found with their frequency per year and the frequency of tweets per state. It also includes some of the source data such as the Unitex-PB word list.



## Report:
The final report and presentation for the project are also saved in this repository

 
