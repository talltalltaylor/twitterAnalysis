import nltk
from nltk.corpus import words
from nltk.corpus import machado, mac_morpho, floresta, genesis
from bson.objectid import ObjectId
import json
import requests
from pymongo import MongoClient


class CleanAndTag:   

    def __init__(self, mongoDBConnectionStr):
        #Inititalizing MongoDB
        client = MongoClient(mongoDBConnectionStr)
        self.db = client.TwitterPTBR_EN
        self.tblTweet = self.db.tblTweet
        self.tblTweetWords = self.db.tblTweetWords
        
        
    def breakTextIntoWords(self):

        select_tTweet = self.tblTweet.find({ },{ "text": "1", "created_at": "1", "id_str" : "1", "user" : "1"  })

        #loop through tweets
        for tweet in select_tTweet:
            
            #get relevant information from tweet
            id_str = tweet['id_str']
            text =  tweet['text'].replace("\\", "").replace('\"', "").replace("\r","").replace("\n","").replace("\t", "").rstrip()
            created_at =  tweet['created_at']
            year =  tweet['created_at'][26:30]
            month =  tweet['created_at'][4:7]
            user_id =  tweet['user']['id_str']
            user_location =  tweet['user']['location']
            
            try:
                #insert new record for each word
                for word in nltk.word_tokenize(text):
                    data = '{"word":"' + word + \
                          '","word_orig":"' + word  + \
                          '","id_str":"' + id_str  + \
                          '", "text":"' + text + \
                          '", "year":"' + year + \
                          '", "month":"' + month + \
                          '", "user_id":"' + user_id + \
                          '", "user_location":"' + user_location + \
                          '", "english_fl":"' + "U" + \
                          '", "machado_fl":"' + "U" + \
                          '", "morpho_fl":"' + "U" + \
                          '", "floresta_fl":"' + "U" + \
                          '", "genesis_fl":"' + "U" +'"}'
                    
                    x = json.loads(data)
                    result = self.tblTweetWords.insert_one(x)
                
            except:
                continue



        
    def cleanWords(self):
        
        select_tTweetWords = self.tblTweetWords.find()

        #loop through all words
        for x in select_tTweetWords:

            cleanWord = x['word_orig'].replace("\\", "").replace("@","").replace("!", "").replace("/", "").replace("*", "")
            cleanWord = cleanWord.replace("-", "").replace("~", "").replace("`", "").replace("#", "").replace("$", "")
            cleanWord = cleanWord.replace("%", "").replace("^", "").replace("&", "").replace("(", "").replace(")", "")
            cleanWord = cleanWord.replace("=", "").replace("+", "").replace("{", "").replace("}", "").replace("[", "")
            cleanWord = cleanWord.replace("]", "").replace("|", "").replace("'", "").replace('"', "").replace("?", "")
            cleanWord = cleanWord.replace(":", "").replace(";", "").replace("<", "").replace(">", "").replace(",", "")
            cleanWord = cleanWord.replace(".", "").replace("_", "").replace("\\\\", "")

            #update collection with cleaned word
            self.tblTweetWords.update_one( { "_id": ObjectId(x['_id']) }, { "$set": { "word": "" + cleanWord + "" } })
        
        
     
    
    def tagWords(self):
        
        english_fl = 'U'
        machado_fl = 'U'
        morpho_fl = 'U'
        floresta_fl = 'U'
        genesis_fl = 'U'    

        select_tTweetWords = self.tblTweetWords.find()

        #loop through words and tag them
        for x in select_tTweetWords:
            
            word = x['word'].rstrip().lstrip()
            
            if word in words.words():      
                english_fl = "Y"
            else:
                english_fl = "N"

            if word in machado.words():      
                machado_fl= "Y"
            else:
                machado_fl = "N"

            if word in mac_morpho.words():      
                morpho_fl = "Y"
            else:
                morpho_fl = "N"

            if word in floresta.words():      
                floresta_fl = "Y"
            else:
                floresta_fl = "N"

            if word in genesis.words():      
                genesis_fl = "Y"
            else:
                genesis_fl = "N"
                
                
            #update flags in collection
            self.tblTweetWords.update_one( { "_id": ObjectId(x['_id']) }, { "$set": { "english_fl": "" + english_fl + "" , \
                                                                           "machado_fl": "" + machado_fl + "" , \
                                                                           "morpho_fl": "" + morpho_fl + "" , \
                                                                           "floresta_fl": "" + floresta_fl + "" , \
                                                                           "genesis_fl": "" + genesis_fl + "" } })
            
            
