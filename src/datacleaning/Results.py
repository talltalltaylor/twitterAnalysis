import json
import csv
from pymongo import MongoClient


class Results:   
    
    def __init__(self, mongoDBConnectionStr):
        #Inititalizing MongoDB
        client = MongoClient(mongoDBConnectionStr)
        self.db = client.TwitterPTBR_EN
        self.tblTweetWords = self.db.tblTweetWords
        
        
    def printCount(self):
        
        select_tTable = self.tblTweetWords.aggregate( [{"$group": {"_id": "$year", "count": { "$sum": 1 } } } ])

        print("Total counts per year: ")
        for x in select_tTable:
            print(x["_id"] + "," + str(x["count"]))
    
        
    def exportResults(self):
        
        arr = []

        #set header of txt file
        arr.append([ 'word', 'word_orig', 'id_str', 'text', 'year', 'month', \
                     'user_id', 'user_location', 'english_fl', \
                     'machado_fl', 'morpho_fl', 'floresta_fl', 'genesis_fl'])


        select_tTweet = self.tblTweetWords.find()

        #loop through words and insert into array
        for x in select_tTweet:
            arr.append([ x['word'], 
                         x['word_orig'], 
                         x['id_str'], 
                         x['text'],
                         x['year'],
                         x['month'],
                         x['user_id'],
                         x['user_location'],
                         x['english_fl'], 
                         x['machado_fl'], 
                         x['morpho_fl'], 
                         x['floresta_fl'], 
                         x['genesis_fl'] ])    


        #export in array into txt file
        myFile = open('TweetWordsResult.txt', 'w', encoding="utf-8")
        with myFile:
            writer = csv.writer(myFile, delimiter='|')
            writer.writerows(arr)

        
        