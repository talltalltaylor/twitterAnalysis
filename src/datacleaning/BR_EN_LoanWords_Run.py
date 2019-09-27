
class BR_EN_LoanWords_MainRun:   
            
    def run(self):
        
        myTwitterBearerToken = "[YOUR BearerToken]"
        myMongoDBConnectionSTR = "mongodb://localhost:27017"
        
        #Test for Requesting Tweets from 30Day API
        #nexttoken can be used in a for loop for pagination if you result results more tweets than the maximum tweets per request
        my30DayTweetRequest = TweetExtract(myMongoDBConnectionSTR, myTwitterBearerToken )
        query = "lang:pt place_country:BR"
        nextToken = my30DayTweetRequest.requestTweet("30day", "30DaysDev.json", query, "201812010000", "201812110000", "", "10")
       
    
        ##Test for Requesting Tweets from fullarchive API
        ##nexttoken can be used in a for loop for pagination if you result results more tweets than the maximum tweets per request
        myFullarchiveTweetRequest = TweetExtract(myMongoDBConnectionSTR, myTwitterBearerToken )
        query = "lang:pt place_country:BR"
        nextToken = myFullarchiveTweetRequest.requestTweet("fullarchive", "FullArchDev.json", query, "201701010000", "201701310000", "", "10")
       
        #Breakdown words, clean and tag them
        myCleanAndTag = CleanAndTag(myMongoDBConnectionSTR)
        myCleanAndTag.breakTextIntoWords()
        myCleanAndTag.cleanWords()
        myCleanAndTag.tagWords()
        
        #Print&ExportResults
        myResults = Results(myMongoDBConnectionSTR)
        myResults.printCount()
        myResults.exportResults()
        