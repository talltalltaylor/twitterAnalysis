import os
import json
import datetime
from pymongo import MongoClient
from time import strptime,sleep
#from threading import Thread
import nltk
from nltk.corpus import words, stopwords, wordnet
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import pos_tag
from nltk.tokenize import word_tokenize
import csv
import string
from sklearn.decomposition import NMF, LatentDirichletAllocation, TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer

stopWords = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

stemmer = PorterStemmer()
lemmatiser = WordNetLemmatizer()

stop = set(stopwords.words('english'))
exclude = set(string.punctuation) 
lemma = WordNetLemmatizer()

topic_doc_complete = []



class pyTwitterDB_class:   

    def __init__(self, mongoDB_database, strFocusedTweetFields, strFocusedTweetUserFields):
        #Inititalizing MongoDB collections        
        self.db = mongoDB_database                
        self.db.dc_bSettings = self.db.dbSettings
        self.c_loadedFiles = self.db.loadedFiles
        self.c_twitterSearches = self.db.twitterSearches
        self.c_tweet = self.db.tweet
        self.c_focusedTweet = self.db.focusedTweet
        self.c_tweetWords = self.db.tweetWords
        self.c_tweetSentences = self.db.tweetSentences
        self.c_topicsByHashTag = self.db.topicsByHashTag
        self.c_processStatus = self.db.processStatus
        self.c_tweetCountByFileAgg = self.db.tweetCountByFileAgg
        self.c_tweetCountByPeriodAgg = self.db.tweetCountByPeriodAgg
        self.c_tweetCountByLanguageAgg = self.db.tweetCountByLanguageAgg
        self.c_tweetCountByUserAgg = self.db.tweetCountByUserAgg
        self.c_wordCountAgg = self.db.wordCountAgg
        self.c_hashTagCountAgg = self.db.hashTagCountAgg
        self.c_userLocationCountAgg = self.db.userLocationCountAgg
        self.c_loadStatus = self.db.loadStatus         
        self.c_htTopics = self.db.htTopics
        
        
        
        #load these settings from DB. If no settings yet, use default        
        self.strFocusedTweetFields = strFocusedTweetFields
        self.periodGrain = "month"         
        self.add_lowerCase_fields_FL = 'Y'
        self.label_EnWords_FL = 'N'
        self.pos_tag_label_FL = 'Y'
        self.lemm_word_FL = 'Y'
        self.ignore_stop_words_FL = 'Y'
                
        #put fields chosen into an array of fields. these fields will be the ones used in the FocusedTweet collection.             
        self.strFocusedTweetFieldsArr = strFocusedTweetFields.split(";")        
        self.strFocusedTweetUserFieldsArr = strFocusedTweetUserFields.split(";")
    
        

  
    # This method will load the settings saved in the DB into class variables
    def loadSettings(self):
        print("Code for loadSettings")
         

    # This method will update the setting into DB. it will also update the class variables 
    # Parameters: strFocusedTweetFields (e.g "created_date", "user_id", "user_screen_name", "in_reponse_to_tweet") Default fields that can not be removed: id_str, created_date
    #             periodGrainForAgg: (Options: year, month or day)
    #             ignore_stop_words_fl: (Y/N) This will determine if we want to ignore stop words or not when breaking the text into words
    #             *** more parameters to come ***
    #
    def updateSettings(self, strFocusedTweetFields, periodGrainForAgg):
        print("Code for updateSettings")

        
    # This method will load tweet .json files into the DB (tweet collection)
    # It goes through all .json files in the directory and load them one by one. 
    # It also saves the files already loaded into the 'loadedFiles' collection to make sure we don't load the same file twice
    # Parameters: directory = the directory where the files are stored
    def loadDocFromFile(self, directory):
        seq_no = 1

        print ("loading process started...")
        
        #find the current max sequence number
        select_cTweet = self.c_tweet.aggregate( [{"$group": {"_id": "seq_agg" , "count": { "$max": "$seq_no" } } } ])
        for tweetCount in select_cTweet:
            seq_no = tweetCount["count"] + 1                

        #loop through the files in the dictory
        for filename in os.listdir(directory):
            if filename.endswith(".json"):                
                strpath = os.path.join(directory, filename)                               

                #find if file already loaded
                isFileLoaded = self.c_loadedFiles.count_documents({"file_path": strpath.replace("\\", "/") })        

                if isFileLoaded > 0:
                    #if the processing of that file did not finish. Deletes every record for that file so we can start over
                    select_cLoadedFiles = self.c_loadedFiles.find({ "file_path": strpath.replace("\\", "/")})                
                    if select_cLoadedFiles[0]["end_load_time"] == "loading":            
                        self.c_tweet.delete_many({"file_path": strpath.replace("\\", "/")})
                        self.c_loadedFiles.delete_many({"file_path": strpath.replace("\\", "/")})            
                        isFileLoaded=0

                #if file has already been loaded, ignores the file
                if isFileLoaded == 0:

                    #save path in loaded files collection to track which files have already been processed
                    data_loadedfiles = '{"start_load_time":"' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '","end_load_time":"' + "loading" + '","file_path":"' + strpath.replace("\\", "/") + '"}'        
                    self.c_loadedFiles.insert_one(json.loads(data_loadedfiles))

                    #open file and goes through each document to insert tweet into DB (inserts into tweet collection)                    
                    with open(strpath, encoding="utf8") as f:
                        for line in f:        
                            data = json.loads(line)

                            #adding extra fields to document to suport future logic (processed_fl, load_time, file_path )
                            a_dict = {'processed_fl': 'N', 'seq_no': seq_no, 'seq_agg': "A", 'load_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 'file_path': strpath.replace("\\", "/")}    
                            data.update(a_dict)                                        

                            #ignores documents that are just status
                            if 'info' not in data:
                                self.c_tweet.insert_one(data)
                                seq_no = seq_no+1

                    #update end load time 
                    self.c_loadedFiles.update_one({ "file_path" : strpath.replace("\\", "/") },{ "$set" : { "end_load_time" : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") } });            

                continue        
            else:
                print ("Error loading into tweet collection")        

    
        print ("loading process completed.")
        
        
    
    # this method will use Twitter API to extract data and save into DB 
    # Parameters: twitterBearer = Bearer from you Twitter developer account
    #             apiName = (30day/fullarchive)
    #             devEnviroment = name of your deve enviroment
    #             query = query to select data from Twitter API
    #             dateStart = period start date
    #             dateEnd = period end date
    #             nextToken = token to start from 
    #             maxResults = maximum number of results that you want to return
    def extractDocFromAPI (self, twitterBearer, apiName, devEnviroment, query, dateStart, dateEnd, nextToken, maxResults):        
        print("Code for extractDocFromAPI. Details for this code on https://git.txstate.edu/l-n63/CS7311 ")        
                  
            
    
    # This method will load the focusedtweet collection with the interesting information we want to study     
    def loadFocusedData(self, inc):
        
        print ("loading process started...")
            
        last_seq_no = -1
        max_seq_no = 0
        minV = 0

        #get the max sequence number from the tweet collection
        select_cTweet = self.c_tweet.aggregate( [{"$group": {"_id": "seq_agg" , "count": { "$max": "$seq_no" } } } ])
        for tweetCount in select_cTweet:
            max_seq_no = tweetCount["count"]

        #check if the process has already been run or not. This is to make sure we can restart a process from where we stopped
        hasStarted = self.c_loadStatus.count_documents({"collection_name": "focusedTweet" })        
        if hasStarted > 0:
            select_cLoadStatus = self.c_loadStatus.find({"collection_name": "focusedTweet" })                
            if select_cLoadStatus[0]["status"] == "loading":
                last_seq_no = select_cLoadStatus[0]["min_seq"]-1
                self.c_focusedTweet.delete_many({ "seq_no" : { "$gte" : select_cLoadStatus[0]["min_seq"] } })        
            elif select_cLoadStatus[0]["status"] == "success":
                last_seq_no = select_cLoadStatus[0]["max_seq"] 
        else:
            data = '{"collection_name":"' + "focusedTweet" + '"}'    
            doc = json.loads(data)
            self.c_loadStatus.insert_one(doc)


        try:
            #loop through tweet sequence numbers to insert into DB. The variable "inc" will dictate how many tweet we will isert at a time int DB
            minV = last_seq_no+1
            while minV <= max_seq_no:        
                self.c_loadStatus.update_one({"collection_name": "focusedTweet" }, { "$set" : { "min_seq" : minV, "max_seq" : minV+inc, "status" : "loading" } } )
                self.loadFocusedDataMinMax(minV, minV+inc)
                minV=minV+inc
            
            #if everyhting was successfull, saves status as "success"
            self.c_loadStatus.update_one({"collection_name": "focusedTweet" }, { "$set" : { "max_seq" : max_seq_no, "status" : "success" } } )
        
        except Exception as e:
            print("Error on loadFocusedData. " +str(e))            
                
            
        print ("loading process completed.")
        
        
        
    def loadFocusedDataMinMax(self, minV, maxV):     

        file_data = []

        select_cTweet = self.c_tweet.find({"seq_no":{ "$gt":minV,"$lte":maxV} })

        #loop through tweets
        for tweet in select_cTweet:    

            #Get all the basic info about the tweet. (These will always be saved independet of configurations)    
            id_str = tweet['id_str']
            text =  tweet['text'].replace("\\", "").replace('\"', "").replace("\r","").replace("\n","").replace("\t", "").rstrip()    
            year =  tweet['created_at'][26:30]
            month_name =  tweet['created_at'][4:7]
            month_no =  str(strptime(month_name,'%b').tm_mon)
            day =  tweet['created_at'][8:10]
            user_id =  tweet['user']['id_str']
            seq_no = tweet['seq_no']

            #when the tweet is large, the full text is saved ion the field extended_tweet
            if 'extended_tweet' in tweet:
                text = tweet['extended_tweet']['full_text'].replace("\\", "").replace('\"', "").replace("\r","").replace("\n","").replace("\t", "").rstrip()

            text_lower = text.lower()
            
            #get Hashtags
            ht_children = []
            for gt_tweet in tweet['entities']['hashtags']:
                ht_children.append({
                    'text': gt_tweet['text'], 'text_lower': gt_tweet['text'].lower()
                }) 
                

            #creating the json doc
            data = '{"id_str":"' + id_str + \
                    '", "text":"' + text + \
                    '", "text_lower":"' + text_lower + \
                    '", "year":"' + year + \
                    '", "month_name":"' + month_name + '", "month_no":"' + month_no + '", "day":"' + day + \
                    '", "user_id":"' + user_id + '", "hashtags":"' + "" + '"}'
            doc = json.loads(data)
            doc['hashtags'] = ht_children


            def addFieldToDoc(field_name, field_content):
                #if it is a string, clean tab and enter characters
                if isinstance(field_content,str):
                    field_content.replace("\\", "").replace('\"', "").replace("\r","").replace("\n","").replace("\t", "").rstrip()

                if field_content is None:
                    field_content = "None"            

                a_dict = {field_name : field_content}    
                doc.update(a_dict)     


            #go through the list of fields from configuration and add to the document
            for i in self.strFocusedTweetFieldsArr:         
                field_name = i
                field_content = tweet[i]
                addFieldToDoc(field_name, field_content)

            #go through the list of user fields from configuration and add to the document
            for i in self.strFocusedTweetUserFieldsArr:         
                field_name = 'user_' + i
                field_content = tweet['user'][i]
                addFieldToDoc(field_name, field_content)                        


            #add seq number to the end
            a_dict = {'seq_no': seq_no, 'seq_agg': "A"}    
            doc.update(a_dict)  

            #add this tweet doc to the array. the array of all tweets will be used to insertMany into mongoDB 
            file_data.append(doc)

        try:
            self.c_focusedTweet.insert_many(file_data)
        except:
            print("Error loading focused tweet")
            


    # This method will load the tweetWords collection
    def loadWordsData(self, inc):
        
        print ("loading process started...")        
            
        last_seq_no = -1
        max_seq_no = 0
        minV = 0

        #get the max sequence number from the tweet collection                    
        select_cFocusedTweet = self.c_focusedTweet.aggregate( [{"$group": {"_id": "seq_agg" , "maxSeqNo": { "$max": "$seq_no" } } } ])
        for tweetCount in select_cFocusedTweet:
            max_seq_no = tweetCount["maxSeqNo"]               

        #check if the process has already been run or not. This is to make sure we can restart a process from where we stopped
        hasStarted = self.c_loadStatus.count_documents({"collection_name": "tweetWords" })        
        if hasStarted > 0:
            select_cLoadStatus = self.c_loadStatus.find({"collection_name": "tweetWords" })                
            if select_cLoadStatus[0]["status"] == "loading":
                last_seq_no = select_cLoadStatus[0]["min_seq"]-1
                self.c_tweetWords.delete_many({ "seq_no" : { "$gte" : select_cLoadStatus[0]["min_seq"] } })        
            elif select_cLoadStatus[0]["status"] == "success":
                last_seq_no = select_cLoadStatus[0]["max_seq"] 
        else:
            data = '{"collection_name":"' + "tweetWords" + '"}'    
            doc = json.loads(data)
            self.c_loadStatus.insert_one(doc)        
                    
        
        try:
            #loop through tweet sequence numbers to insert into DB. The variable "inc" will dictate how many tweets we will isert at a time int DB
            minV = last_seq_no+1                        
            while minV <= max_seq_no:                    
                self.c_loadStatus.update_one({"collection_name": "tweetWords" }, { "$set" : { "min_seq" : minV, "max_seq" : minV+inc, "status" : "loading" } } )
                self.breakTextIntoWords(minV, minV+inc)
                minV=minV+inc                

            #if everyhting was successfull, saves status as "success"
            self.c_loadStatus.update_one({"collection_name": "tweetWords" }, { "$set" : { "max_seq" : max_seq_no, "status" : "success" } } )            
            

        except Exception as e:            
            print("Error on loadWordsData. " +str(e))    
            
           
        print ("loading process completed.")
            
            
            
    # This method will break text from tweet into words and tag them    
    def breakTextIntoWords(self, minV, maxV):

        file_data = []
        seq_no = 0

        select_cTweetWords = self.c_tweetWords.aggregate( [{"$group": {"_id": "seq_agg" , "maxSeqNo": { "$max": "$seq_no" } } } ])
        for tweetCount in select_cTweetWords:
            max_seq_no = tweetCount["maxSeqNo"] 
            seq_no = max_seq_no                                
        
        select_cFocusedTweet = self.c_focusedTweet.find({"seq_no":{ "$gt":minV,"$lte":maxV}})        

        #loop through tweets
        for tweet in select_cFocusedTweet:                
                        
            
            #Get all the basic info about the tweet. (These will always be saved independet of configurations)    
            id_str = tweet['id_str']
            text =  tweet['text']
            text_lower =  tweet['text_lower']
            year =  tweet['year']
            month_name =  tweet['month_name']
            month_no =  tweet['month_no']
            day =  tweet['day']
            user_id =  tweet['user_id']
            seq_no_tweet = tweet['seq_no']
            ht_children = tweet['hashtags']

            try:            
                #insert new record for each word        
                #for word in tokenizer.tokenize(text):
                for word in pos_tag(tokenizer.tokenize(text)):

                    if word[0] not in stopWords:

                        cleanWord = word[0].replace("\\", "").replace("@","").replace("!", "").replace("/", "").replace("*", "")
                        cleanWord = cleanWord.replace("-", "").replace("~", "").replace("`", "").replace("#", "").replace("$", "")
                        cleanWord = cleanWord.replace("%", "").replace("^", "").replace("&", "").replace("(", "").replace(")", "")
                        cleanWord = cleanWord.replace("=", "").replace("+", "").replace("{", "").replace("}", "").replace("[", "")
                        cleanWord = cleanWord.replace("]", "").replace("|", "").replace("'", "").replace('"', "").replace("?", "")
                        cleanWord = cleanWord.replace(":", "").replace(";", "").replace("<", "").replace(">", "").replace(",", "")
                        cleanWord = cleanWord.replace(".", "").replace("_", "").replace("\\\\", "")

                        cleanWordLw = cleanWord.lower()

                        seq_no = seq_no+1

                        #lemmatize word                
                        tag = word[1].lower()[0]

                        if tag == 'j':
                            tag = wordnet.ADJ
                        elif tag == 'v':
                            tag = wordnet.VERB
                        elif tag == 'n':
                            tag = wordnet.NOUN
                        elif tag == 'r':
                            tag = wordnet.ADV
                        else:
                            tag  = ''

                        if tag in ("j", "n", "v", "r"):
                            lemm_word = lemmatiser.lemmatize(cleanWordLw, pos=tag)
                        else:
                            lemm_word = lemmatiser.lemmatize(cleanWordLw)                                                                                                      


                        data = '{"word_orig":"' + word[0] + \
                              '","word":"' + cleanWord  + \
                              '","word_lower":"' + cleanWordLw  + \
                              '","word_tag":"' + word[1]  + \
                              '","word_lemm":"' + lemm_word + \
                              '","id_str":"' + id_str  + \
                              '", "text":"' + text + \
                              '", "text_lower":"' + text_lower + \
                              '", "year":"' + year + \
                              '", "month_name":"' + month_name + '", "month_no":"' + month_no + '", "day":"' + day + \
                              '", "user_id":"' + user_id + '", "hashtags":"' + "" + '"}'
                        doc = json.loads(data) 
                        doc['hashtags'] = ht_children                        

                        a_dict = {'seq_no_tweet': seq_no_tweet, 'seq_no': seq_no, 'seq_agg': "A"}    
                        doc.update(a_dict)

                        #add this tweet doc to the array. the array of all tweets will be used to insertMany into mongoDB 
                        file_data.append(doc)                                               

            except Exception as e:
                print("Error on loadWordsData. " +str(e) + " | err tweet_id: " + id_str)                

        try:
            self.c_tweetWords.insert_many(file_data)
        except Exception as e:
            print("Error on loadWordsData | " +str(e) ) 


                
    ###########################                          
    #load aggregations         
    def loadAggregations(self, aggType):
    
        print ("loading process started....")
        
        if (aggType == 'tweetCountByFile'):
            self.tweetCountByFile()                
        elif (aggType == 'hashtagCount'):
            self.hashtagCount()
        elif (aggType == 'tweetCountByLanguageAgg'):
            self.tweetCountByLanguageAgg()
        elif (aggType == 'tweetCountByPeriodAgg'):
            self.tweetCountByPeriodAgg()
        elif (aggType == 'tweetCountByUser'):
            self.tweetCountByUser()    
        elif (aggType == 'tweetCountByUser'):
            self.tweetCountByUser()
            
        print ("loading process completed.")

                
    #load aggregation on tweetCountByFileAgg collection
    def tweetCountByFile(self):
    
        #delete everything from the collection because we will repopulate it
        result = self.c_tweetCountByFileAgg.delete_many({}) 
        select_cTweet = self.c_tweet.aggregate( [{"$group": {"_id": {"file_path": "$file_path"}, "count": { "$sum": 1 } } } ])

        for tweetCount in select_cTweet:
            try:        
                data = '{"file_path":"' + tweetCount["_id"]["file_path"] + \
                '", "count":"' + str(tweetCount["count"]) + '"}'                

                x = json.loads(data)
                result = self.c_tweetCountByFileAgg.insert_one(x)
                
            except Exception as e:            
                print("Error running aggreagation: tweetCountByFile | " +str(e))
                continue                 
                
                
    #load aggregation on hashTagCountAgg collection
    def hashtagCount(self):     

        result = self.c_hashTagCountAgg.delete_many({}) 
        select_cfocusedTweet = self.c_focusedTweet.aggregate( [ { "$unwind": '$hashtags' }, 
                                                        { "$project": { "hashtags": 1, "text": '$hashtags.text_lower'} },
                                                        {"$group": { "_id": { "text": '$text' }, "count": { "$sum": 1 } } } ])

        for tweetCount in select_cfocusedTweet:

            try:    
                data = '{"hashtag_text":"' + tweetCount["_id"]["text"] + '"}'   
                x = json.loads(data)        

                a_dict = {'count': tweetCount["count"]}    
                x.update(a_dict)

                result = self.c_hashTagCountAgg.insert_one(x)

            except Exception as e:            
                print("Error running aggreagation: hashtagCount | " +str(e))
                continue   
            
                    
    #load aggregation on tweetCountByLanguageAgg collection          
    def tweetCountByLanguageAgg(self):

        result = self.c_tweetCountByLanguageAgg.delete_many({}) 
        select_cfocusedTweet = self.c_focusedTweet.aggregate( [{"$group": {"_id": {"lang": "$lang"}, "count": { "$sum": 1 } } } ])

        for tweetCount in select_cfocusedTweet:
            try:        
                data = '{"lang":"' + tweetCount["_id"]["lang"] + \
                '", "count":"' + str(tweetCount["count"]) + '"}'                

                x = json.loads(data)
                result = self.c_tweetCountByLanguageAgg.insert_one(x)

            except Exception as e:            
                print("Error running aggreagation: tweetCountByLanguageAgg | " +str(e))
                continue
                

                
    #load aggregation on tweetCountByPeriodAgg collection            
    def tweetCountByPeriodAgg(self):

        result = self.c_tweetCountByPeriodAgg.delete_many({}) 
        select_cfocusedTweet = self.c_focusedTweet.aggregate( [{"$group": {"_id": {"year": "$year", "month_no": "$month_no"}, "count": { "$sum": 1 } } } ])

        for tweetCount in select_cfocusedTweet:

            try:        
                data = '{"year":"' + tweetCount["_id"]["year"] + \
                      '","month_no":"' + tweetCount["_id"]["month_no"]  + \
                      '", "count":"' + str(tweetCount["count"]) + '"}'                

                x = json.loads(data)
                result = self.c_tweetCountByPeriodAgg.insert_one(x)

            except Exception as e:            
                print("Error running aggreagation: tweetCountByPeriodAgg | " +str(e))
                continue                                         


    #load aggregation on tweetCountByUserAgg collection
    def tweetCountByUser(self):

        result = self.c_tweetCountByUserAgg.delete_many({}) 
        select_cfocusedTweet = self.c_focusedTweet.aggregate( [{"$group": {"_id": {"user_id": "$user_id", "user_screen_name" : "$user_screen_name"}, "count": { "$sum": 1 } } } ])    

        for tweetCount in select_cfocusedTweet:
            try:        
                data = '{"user_id":"' + tweetCount["_id"]["user_id"] + \
                '", "user_screen_name":"' + tweetCount["_id"]["user_screen_name"]  + \
                '", "count":"' + str(tweetCount["count"]) + '"}'                        

                x = json.loads(data)
                result = self.c_tweetCountByUserAgg.insert_one(x)

            except Exception as e:            
                print("Error running aggregation: tweetCountByUser | " +str(e))
                continue
                  


    ###########################                
    # Exports data into file
    # Parameters: exportType: (tweetCountByUser, tweetCountByLanguage, tweetCountByFile, tweetCountByMonth, hashtagCount, tweetTextAndPeriod, wordsOnEachTweet, userDetailsOnEachTweet)
    #             filepath: the file path where the files will be saved  
    #             inc: To set how many lines per files we want to save. This is for collection that have too many records to be saved. memory issues can happens if this number is too bi
    #                  Only works when exporting for types tweetTextAndPeriod, wordsOnEachTweet, userDetailsOnEachTweet, we can set how many lines per file
    def exportData(self, exportType, filepath, inc):         

        arr = []
        

        #export tweetCountByUser
        if (exportType == 'tweetCountByUser'):

            #set header of txt file
            arr.append([ 'user_id', 'user_screen_name', 'count'])

            #get data from database and loop through records and insert into array
            select_tweetCountByUser = self.c_tweetCountByUserAgg.find()        
            for x in select_tweetCountByUser:
                arr.append([ x['user_id'], x['user_screen_name'],  x['count']])        

            #set file path
            file = filepath + '\\tweetCountByUser.txt'
            
            
        
        #export tweetCountByLanguage
        if (exportType == 'tweetCountByLanguage'):

            #set header of txt file
            arr.append([ 'lang', 'count'])

            #get data from database and loop through records and insert into array
            select_tweetCountByLang = self.c_tweetCountByLanguageAgg.find()        
            for x in select_tweetCountByLang:
                arr.append([ x['lang'],  x['count']])        

            #set file path
            file = filepath + '\\tweetCountByLanguage.txt'
            
                    

        
        #export tweetCountByFile
        if (exportType == 'tweetCountByFile'):

            #set header of txt file
            arr.append([ 'file_path', 'count'])

            #get data from database and loop through records and insert into array
            select_tweetCountByFile = self.c_tweetCountByFileAgg.find()        
            for x in select_tweetCountByFile:
                arr.append([ x['file_path'],  x['count']])        

            #set file path
            file = filepath + '\\tweetCountByFile.txt'



        #export tweetCountByMonth
        if (exportType == 'tweetCountByMonth'):        

            #set header of txt file
            arr.append([ 'year', 'month_no', 'count'])   

            #get data from database and loop through records and insert into array
            select_tCountByPeriod = self.c_tweetCountByPeriodAgg.find()        
            for x in select_tCountByPeriod:
                arr.append([ x['year'], x['month_no'], x['count']])         

            #set file path
            file = filepath + '\\tweetCountByMonth.txt'        



        #export hashtagCount
        if (exportType == 'hashtagCount'): 

            #set header of txt file
            arr.append([ 'hashtag_text', 'count'])            

            #get data from database and loop through records and insert into array
            select_hashtagCountByDay = self.c_hashTagCountAgg.find()        
            for x in select_hashtagCountByDay:
                arr.append([ x['hashtag_text'],  x['count']])

            #set file path
            file = filepath + '\\hashtagCount.txt'        

            
        #export topics by hashtag
        if (exportType == 'topicByHashtag'): 

            #set header of txt file
            arr.append([ 'ht', 'ht_count', 'lib', 'model', 'no_words', 'topic_no', 'topic'])       

            #get data from database and loop through records and insert into array
            select_cHTTopics = self.c_htTopics.find()        
            for x in select_cHTTopics:
                arr.append([ x['ht'], x['ht_count'],  x['lib'],  x['model'],  x['no_words'],  x['topic_no'],  x['topic']])

            #set file path
            file = filepath + '\\topicByHashtag.txt'        


        #export tweetTextAndPeriod
        if (exportType == 'tweetTextAndPeriod'):

            i = 0                

            #get data from database and loop through records and insert into array
            select_focusedTweet = self.c_focusedTweet.find() 
            for x in select_focusedTweet:

                if (i % inc == 0 and i != 0):                                                
                    self.exportToFile(arr, file) #export in array into txt file


                if (i==0 or i % inc==0):                
                    arr = []
                    file = filepath + '\\tweetTextAndPeriod_' + str(i) + '.txt' #set file path
                    arr.append([ 'text', 'text_lower', 'year', 'month_no', 'day', 'user_id'])

                arr.append([ x['text'], x['text_lower'], x['year'],  x['month_no'],  x['day'],  x['user_id']])                                    

                i = i +1



        #export words
        if (exportType == 'wordsOnEachTweet'):  

            i = 0                

            #get data from database
            select_tweetWords = self.c_tweetWords.find()
            for x in select_tweetWords:

                if (i % inc == 0 and i != 0):                                                
                    self.exportToFile(arr, file) #export in array into txt file                

                if (i==0 or i % inc==0):                
                    arr = []
                    file = filepath + '\\wordsOnEachTweet_' + str(i)  + '.txt' #set file path
                    arr.append([ 'word_orig', 'word', 'word_lower', 'word_tag', 'word_lemm', 'id_str', 'text', 'seq_no_tweet', 'seq_no'])


                arr.append([ x['word_orig'],  x['word'],  x['word_lower'],  x['word_tag'],  x['word_lemm'],  x['id_str'],  x['text'],  x['seq_no_tweet'],  x['seq_no']])

                i = i +1



        #user details on Each Tweet
        if (exportType == 'userDetailsOnEachTweet'):  

            i = 0                

            #get data from database
            select_Tweet = self.c_tweet.find()
            for tweet in select_Tweet:

                if (i % inc == 0 and i != 0):                                                
                    self.exportToFile(arr, file) #export in array into txt file                

                if (i==0 or i % inc==0):                
                    arr = []
                    file = filepath + '\\userDetailsOnEachTweet_' + str(i)  + '.txt' #set file path
                    arr.append([ 'id_str', 'user_id', 'user_location', 'user_name', 'user_screen_name', 'user_description', 'user_verified', 'user_followers_count', 'user_friends_count', \
                    'user_statuses_count', 'user_created_at', 'user_time_zone', 'user_lang', 'user_geo_enabled'])


                #get relevant information from tweet
                id_str = tweet['id_str'] 
                user_id = tweet['user']['id_str']
                user_location = tweet['user']['location']
                user_name = tweet['user']['name']
                user_screen_name = tweet['user']['screen_name']
                user_description = tweet['user']['description']                                
                user_verified = tweet['user']['verified']
                user_followers_count = tweet['user']['followers_count']
                user_friends_count = tweet['user']['friends_count']
                user_statuses_count = tweet['user']['statuses_count']
                user_created_at = tweet['user']['created_at']
                user_time_zone = tweet['user']['time_zone']
                user_lang = tweet['user']['lang']        
                user_geo_enabled = tweet['user']['geo_enabled']        

                if user_description is not None:            
                    user_description = user_description.replace("|", "").strip().replace("\n", "").replace("\r", "")

                if user_location is not None:            
                    user_location = user_location.replace("|", "").strip().replace("\n", "").replace("\r", "")

                if user_name is not None:        
                    user_name = user_name.replace("|", "").strip().replace("\n", "").replace("\r", "")

                if user_screen_name is not None: 
                    user_screen_name = user_screen_name.replace("|", "").strip().replace("\n", "").replace("\r", "")


                arr.append([id_str, user_id, user_location, user_name, user_screen_name, user_description, user_verified, user_followers_count, user_friends_count, user_statuses_count, \
                        user_created_at, user_time_zone, user_lang, user_geo_enabled])  


                i = i +1                

        #export in array into txt file
        self.exportToFile(arr, file)
    
    
    
    ###########################
    #Exports an array to a file
    def exportToFile(self, arrData, file): 

        myFile = open(file, 'w', encoding="utf-8")
        with myFile:
            writer = csv.writer(myFile, delimiter='|')
            writer.writerows(arrData)    
                                    
    
    
    
    ######### Topic Analysis #########################################
    
    #create one array with all tweets of one hashtag for topic analysis
    def get_docs(self, ht, max_doc_ctn):    
        
        ctn=0
        doc = ""
        topic_doc_complete.append(doc)
        
        select_cTweet = self.c_focusedTweet.find({"hashtags.text_lower" : ht }) 
        #loop through tweets
        for tweet in select_cTweet:     
            if ctn < max_doc_ctn:
                doc = tweet['text_lower']
                topic_doc_complete.append(doc)
            ctn=ctn+1    
            

    #clean documents for topic analysis
    def clean(self, doc): 
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
        return normalized
    
    
    #topic analysis using gensim model 
    def gensim_model(self, num_topics_lda, num_topics_lsi, ht, tc):

        import gensim
        from gensim import corpora

        doc_clean = [self.clean(doc).split() for doc in topic_doc_complete]   

        # Creating the term dictionary of our courpus, where every unique term is assigned an index. dictionary = corpora.Dictionary(doc_clean)
        dictionary = corpora.Dictionary(doc_clean)            

        # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
        doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]

        # Creating the object for LDA model using gensim library
        Lda = gensim.models.ldamodel.LdaModel    

        # Build the LDA model
        lda_model = gensim.models.LdaModel(corpus=doc_term_matrix, num_topics=num_topics_lda, id2word=dictionary)    

        # Build the LSI model
        lsi_model = gensim.models.LsiModel(corpus=doc_term_matrix, num_topics=num_topics_lsi, id2word=dictionary)    


        file_data = []     
        for idx in range(num_topics_lda):                
            topic = idx+1
            strtopic = str(topic)

            data = '{"ht":"' + ht + \
                    '", "ht_count":"' + str(tc) + \
                    '", "lib":"' + "gensim" + \
                    '", "model":"' + "lda" + \
                    '", "no_tweets":"' + str(tc) + \
                    '", "topic_no":"' + strtopic + \
                    '", "topic":"' + str(lda_model.print_topic(idx, num_topics_lda)).replace('"', "-") + '"}'

            x = json.loads(data)
            file_data.append(x)



        for idx in range(num_topics_lsi):        
            data = '{"ht":"' + ht + \
                '", "ht_count":"' + str(tc) + \
                '", "lib":"' + "gensim" + \
                '", "model":"' + "lsi" + \
                '", "no_tweets":"' + str(tc) + \
                '", "topic_no":"' + str(idx+1) +\
                '", "topic":"' + str(lsi_model.print_topic(idx, num_topics_lsi)).replace('"', "-") + '"}'

            x = json.loads(data)
            file_data.append(x)


        self.c_htTopics.insert_many(file_data)        
        

            
    #topic analysis using sklearn model 
    def skl_model(self, num_topics_lda, num_topics_lsi, num_topics_nmf, ht, tc):    

        vectorizer = CountVectorizer(min_df=0.009, max_df=0.97, stop_words='english', lowercase=True, token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')

        data_vectorized = vectorizer.fit_transform(topic_doc_complete)

        # Build a Latent Dirichlet Allocation Model
        lda_model = LatentDirichletAllocation(n_components=num_topics_lda, max_iter=5,learning_method='online',learning_offset=50.,random_state=0)
        lda_Z = lda_model.fit_transform(data_vectorized)

        # Build a Non-Negative Matrix Factorization Model
        nmf_model = NMF(num_topics_nmf)
        nmf_Z = nmf_model.fit_transform(data_vectorized)

        # Build a Latent Semantic Indexing Model
        lsi_model = TruncatedSVD(1)
        lsi_Z = lsi_model.fit_transform(data_vectorized)


        file_data = []

        for idx, topic in enumerate(lda_model.components_):  
            topic = str([( str(topic[i]) + "*" + vectorizer.get_feature_names()[i] + " + " )
                            for i in topic.argsort()[:-num_topics_lda - 1:-1]]).replace("[", "").replace("]", "").replace("'", "").replace(",", "")

            data = '{"ht":"' + ht + \
                '", "ht_count":"' + tc + \
                '", "lib":"' + "sklearn" + \
                '", "model":"' + "lda" + \
                '", "no_tweets":"' + str(tc) + \
                '", "topic_no":"' + str(idx+1) +\
                '", "topic":"' + topic + '"}'

            x = json.loads(data)
            file_data.append(x)



        for idx, topic in enumerate(lsi_model.components_):  
            topic = str([( str(topic[i]) + "*" + vectorizer.get_feature_names()[i] + " + " )
                            for i in topic.argsort()[:-num_topics_lsi - 1:-1]]).replace("[", "").replace("]", "").replace("'", "").replace(",", "")

            data = '{"ht":"' + ht + \
                '", "ht_count":"' + tc + \
                '", "lib":"' + "sklearn" + \
                '", "model":"' + "lsi" + \
                '", "no_tweets":"' + str(tc) + \
                '", "topic_no":"' + str(idx+1) +\
                '", "topic":"' + topic + '"}'

            x = json.loads(data)
            file_data.append(x)




        for idx, topic in enumerate(nmf_model.components_):  
            topic = str([( str(topic[i]) + "*" + vectorizer.get_feature_names()[i] + " + ")
                            for i in topic.argsort()[:-num_topics_nmf - 1:-1]]).replace("[", "").replace("]", "").replace("'", "").replace(",", "")

            data = '{"ht":"' + ht + \
                '", "ht_count":"' + tc + \
                '", "lib":"' + "sklearn" + \
                '", "model":"' + "nmf" + \
                '", "no_tweets":"' + str(tc) + \
                '", "topic_no":"' + str(idx+1) +\
                '", "topic":"' + topic + '"}'

            x = json.loads(data)
            file_data.append(x)        


        self.c_htTopics.insert_many(file_data)            
        
        

    #find topics for each hashtag  
    def findTopics(self, num_topics_lda, num_topics_lsi, num_topics_nmf, max_no_tweets_perHT, model):

        print ("loading process started....")
        
        #find all hashtag and their count
        select_cHashtagCount = self.c_hashTagCountAgg.find().sort("count", -1)  

        #loop through hashtags
        for tweet in  select_cHashtagCount: 

            ht = tweet['hashtag_text']
            count = tweet['count']

            #get all tweets for that hashtag
            topic_doc_complete.clear()
            self.get_docs(ht, max_no_tweets_perHT) 

            #run topic models
            try:
                if model == "gensim":
                    self.gensim_model(num_topics_lda, num_topics_lsi, ht, str(count))        
                elif model == "sklearn":
                    self.skl_model(num_topics_lda, num_topics_lsi, num_topics_nmf, ht, str(count))                 
            except Exception as e:                                      
                print("Error finding topics for hashtag " + ht + ", using model " + model +". Err msg: " + str(e)) 
                continue        
                
        print ("loading process completed.")