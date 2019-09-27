#TweetExtract
import json
import requests
from pymongo import MongoClient

class TweetExtract:
    
        
    def __init__(self, mongoDBConnectionStr, twitterBearer):
        
        #Inititalizing MongoDB
        client = MongoClient(mongoDBConnectionStr)
        self.db = client.TwitterPTBR_EN
        self.tblTweet = self.db.tblTweet
        self.tblResults = self.db.tblResults
        
        self.headers = {"Authorization":"Bearer " + twitterBearer + "", "Content-Type": "application/json"}  

    

    def requestTweet(self, apiName, devEnviroment, query, dateStart, dateEnd, nextToken, maxResults):
    
        #Api URL
        if apiName == "30day":
            endpoint = "https://api.twitter.com/1.1/tweets/search/30day/" + devEnviroment
        elif apiName == "fullarchive":
            endpoint = "https://api.twitter.com/1.1/tweets/search/fullarchive/" + devEnviroment
        else:
            return -1
    
    
        if nextToken == "":
            data = '{"query":"' + query + '","fromDate":"' + dateStart + '","toDate":"' + dateEnd + '", "maxResults":"' + maxResults + '"}' 
        else:
            data = '{"query":"' + query + '","fromDate":"' + dateStart + '","toDate":"' + dateEnd +', "next":"' + next_token + '", "maxResults":"' + maxResults + '"}'


        response = requests.post(endpoint,data=data,headers=self.headers).json()
        
        tweets = json.loads(json.dumps(response, indent = 2))

        
        #Insert into tblResults table
        try:
            result = self.tblResults.insert_one(tweets)
        except:
            print("Could not insert results")
        
    
        #Insert into tblTweet table
        for tweet in tweets['results']:
            try:
                result = self.tblTweet.insert_one(tweet)
            except:
                print("Could not insert Tweet")

        
        #Get "next"token
        if not 'next' in tweets:
            return ""
        else:
            return tweets['next']

    