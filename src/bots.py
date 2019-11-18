from pyTwitterDB import pyTwitterDB_class
import labels as l
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn import preprocessing
from sklearn.ensemble import RandomForestClassifier

bots_for_training = ['help_laura', 'GWhV8mU5pMy2Ier', 'AnthonyBurnha19', 'IgnotoLugar', 'Lady_Sybilla', 'AllMoviesCorp',
             'batianhu56', 'IvyFoliage', 'Zeus24513824', 'mohanLa19052950', 'TrooHefner', 'P48063445',
             'carly04633486', 'Vanessa79764758', 'bold_picture', 'thinkpraybot', 'vtmtst', '1104Bj',
             'Lxxxx3326', 'Inmycrescentph1', 'quivadaq', 'vnewsapp', 'kclarkson1984', 'metoomilitary', 
             'gxcioxfe2246', 'pakknews786', 'OraGree38601022', 'ImPaigeTurned', 'Rony34148153', 'barberaaussant8'
             'AyeshaAgreval', 'echoserviceinfo', 'heidica04028948', 'rivabromberg181', 'alapro3', 'StartupsBot',
             'TriendBot', 'alt_rightbot', 'Infobotz', 'NeoBot_CS', 'RandomRussiaBot', 'trumpscuttlebot',
             'GetTriggeredBot', 'Toronto_Bot', 'bot_political', 'TokenRobot', 'bunnies_bot', 'CowboySciFiBot',
             'xBot', 'Evisceratebot', 'nuance_bot', 'YegBot', 'amwritingbot', 'ChoosingLoveBot', 'AwarenessBot',
             'Junecoh92208168', 'testforme1111', 'wncfssuirkf2488', 'thisisLuara', 'kapoorsikha852'
             'js2246004', 'GuptaMansi4311', 'maudartrip2723', 'maksimmaki96', 'replyxa', 'AnaKnowBest',
             'Myasjn1', '1c22e80193b54cb', 'KarloMAkso228', 'GorbanVika', 'anlopanov', 'Mohamme19097850',
             'TommyLorenzo02', 'OOuBZJkQZPpx4vj', 'sotibifec1987', 'fEfdheUWhHFFmNU', '4wZYkgSTbQC1Ang',
             'Nadeem40749320', 'iGeekAppleBOT', 'iamtrendbot', 'python_rt_bot', 'Favstar_Bot', 'SharkTankBot'
             'EliteCamBot3', 'MarkCur66369169', '4wZYkgSTbQC1Ang', 'ethan29346463', 'G56tpXMHwQRY0LP',
             '1Ps47zuZkkj56yx', 'xoify1Qq2yMLCah', 'V3NFy8rtFaiwlgz', '3Pk3iIqR8NfYtdr', 'oSSSsC5F15eWD8k',
             'JccTtyv2OSa5PyZ', 'WAe4cNr33AHrBFm', 'pqb75wltPZRJvH7', 'LnIfMdYvMKn4oUt', 'PittmanTammy2'
             '9ffKFZe70xvD9ak', '2vXtuFX0h1hPna4', 'aw1JFVYNONAveOA', 'VPw5L2P3rQ8P4uz', 'YuebZzttXo5d6WK',
             'PGHvgeaTs4deKn9', '0D6Egd4x2ENmyaM', 'rrlqfuiftq996', 'yeovlojvjv1852', 'My40275573',
             'gujfyycofbf456', 'hawcsvbmay2035', 'sodaglbg2493', 'mica_ekperigin', 'janaalimzhan_95',
             'Krspeh2', 'malikabobrys_92', 'Yucp9zWntMFQwAJ', 'pooolnkxvlswj11', 'yeah99583781', 'yeah82601237',
             'followe77169037', 'Moretz91492110', '7kLkWtOBloXxBzQ', 'hMNOJElqFW6BuxD', 'h2AN6WoRQDIS1zE', 'MerleneSchindl7']

bots_for_test_set = ['p1vvXEZ2nsn7Cpm', 'flviV4Nb5thoG1L', 'YAhTc2CYzdZwQF8', 'ogibltlshd2', 'onpblgvh9', 'cubmisasi1979',
                     'stanlepdida1970', 'Debra59279534', 'enmeapoval1972', 'bjj6HCLeHxY1g3Y', 'zoltqn1976', 
                     'stagadconwa1983', 'brugakkafneu191', 'traninatin1987', '1c22e80193b54cb', 'DailyManosphere',
                     'atheism_agent', 'feminism_agent', 'bxpn8s5m23_234', 'GvrMjoW5gzshmUM', 'philbertblogs1',
                     '6a190cdab3264d0', 'M3ge99', '0ghbelV9UApNoP2', 'GeoWorld_EN', 'misssophiebot', 'xclusivedevelop',
                     'cbc_diff', 'AbhinaySalaska3', 'Davidmarting1', 'fukuikidokodo', 'bikirimatsukeru', 'miaienpai',
                     'botsukijitaihe', '4wZYkgSTbQC1Ang', 'Slingevent', 'nimomeibanari', 'dzuchinshikokud',
                     'minpachidorisa', 'metsubokumatsur', 'ethan29346463', 'LguruNf', 'magplanet2015', 'MXh9gMMPjep2QkG',
                     'gj8yVZATKdPatDg', 'LexfpHcNALjKC6G', '0J1TqTavQ9MY6U2', 'ziKq4ZTbmqUhtRk', 'vanessahudson31',
                     'mariannegdun', 'NorreisSonja', 'gilberttara6953', '1O7HIuuJZ2b4t9l', 'HoltWinifred1', 'BondLiesa',
                     'NadiaHy6', 'DeberaAldous', 'geraldinewlu', 'McLeodCyntia', 'LorraineMinccy', 'Syience_News',
                     'victoriablack64', 'RebekaTeddie', 'pqb75wltPZRJvH7', 'lucilleoberts', '0IHiLfxQuHUaXkf',
                     'terryctrudy', 'ReevsRobert', 'SlfXb9OPU3iB2oQ', 'VnEicmrO8a9hbLD', 'ScottNe49772135',
                     'ixDj0bys7D0FxEo', 'JUXPnWUc91kRgdJ', 'Earth1News', 'rrlqfuiftq996', 'arpitlko68', 'aloks3854',
                     'as0798477', 'giftchristmas17', 'md_fahim7', 'pierrecardin_ag', 'IvkTavis', 'news007top1',
                     'abdullah1212239', 'deondethlefsen2', 'JabNews1', 'bodybuildingki3', 'ApplAccessories',
                     'LATESTNEWS113', 'mshcnn', 'gerardbutler182', 'maggregator', 'today_global', 'stories_daily',
                     'marissacastan21', 'nicolas95545906', 'AISSTraining', 'inocenc52158170', 'moveeztalk',
                     'kap1290', 'shaunguerpinar3', 'theamedpost', 'gooxwgpxahmcj11', 'natsudenrubibu', 'kikoshitetsuket',
                     'axsnsnltnvqos21', 'faeberisko2099', 'mitrasites2016', 'GigiTrevino10', 'pvwgkiagxy2134',
                     'nowstreamit']

classifier = RandomForestClassifier(n_estimators=10, class_weight='balanced')

class bot_classifier(pyTwitterDB_class):

    def __init__(self, mongoDB_database, strFocusedTweetFields, strFocusedTweetUserFields):
        
        super().__init__(mongoDB_database, strFocusedTweetFields, strFocusedTweetUserFields)
        self.model = classifier
        self.bots_for_test_set = bots_for_test_set
        self.bots_for_training = bots_for_training


    # searches mongodb for accounts with 
    # suspicious follow ratio and tweet:account_age ratio
    # to be labeled as bots and used for training
    def suggest_bots(self, min_num, max_num):

        '''min_date = datetime.strptime(min_datetime, "%a %b %d %H:%M:%S +0000 %Y")
        max_date = datetime.strptime(max_datetime, "%a %b %d %H:%M:%S +0000 %Y")

        tweets = self.c_tweet.find({
            "created_at" : {
                "$gte": min_date,
                "$lt": max_date
            }
        })'''
        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
        suggested_bots = []

        for tweet in tweets:
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age.date() - profile_age.date()
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            text = tweet['text']
            default_pic = tweet['user']['default_profile_image']

            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            
            if float(ratio) < 0.05:
                bot_dict = {'Screen Name': screen_name, 'Follow Ratio': ratio, 
                            'Age of Account in Days': age.days,'Text': text, 'Default?': default_pic}
                suggested_bots.append(bot_dict)
            
        return suggested_bots

    
    def find_names_with_bot(self, min_num, max_num):
        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
        suggested_bots = []

        for tweet in tweets:
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age.date() - profile_age.date()
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            text = tweet['text']

            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            
            if 'bot' in screen_name.lower():
                bot_dict = {'Screen Name': screen_name, 'Follow Ratio': ratio, 
                            'Age of Account in Days': age.days,'Text': text}
                suggested_bots.append(bot_dict)
            
        return suggested_bots

    
    def followers_tweets(self, min_num, max_num):
        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
        suggested_bots = []

        for tweet in tweets:
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age.date() - profile_age.date()
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            tweets = tweet['user']['statuses_count']
            text = tweet['text']
            user_lists = tweet['user']['listed_count']
            user_favorites = tweet['user']['favourites_count']

            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            
            if followers < 30 and tweets < 50:
                bot_dict = {'Screen Name': screen_name, 'Follow Ratio': ratio, 
                            'Followers': followers, 'Tweet Count': tweets,
                            'Age of Account in Days': age.days,'Text': text, 'Favs': user_favorites, 'Lists': user_lists}
                suggested_bots.append(bot_dict)
            
        return suggested_bots


    # gets tweets between min and max from db and returns a dataframe
    # currently finds based on seq_no, but may change the search criteria
    # to include period or date
    def make_dataframe_of_humans(self, min_num, max_num, size, bots):

        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
            
        tweet_list = []

        for tweet in tweets:
            user_name = tweet['user']['name']
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age - profile_age
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            user_lists = tweet['user']['listed_count']
            user_favorites = tweet['user']['favourites_count']
            tweet_count = tweet['user']['statuses_count']
            tweet_replies = tweet['reply_count']
            tweet_favorites = tweet['favorite_count']
            retweets = tweet['retweet_count']
            protected = tweet['user']['protected']
            verified = tweet['user']['verified']
            default_pic = tweet['user']['default_profile_image']

            if size == 0:
                break

            tweet_dict = {}
            if screen_name not in bots:
                tweet_dict.update({
                    'followers': followers, 'following': following, 'ratio': ratio, 'age': age.days,
                    'name': screen_name,'tweets': tweet_count, 'favs': user_favorites, 'lists': user_lists})
            else:
                continue

            tweet_list.append(tweet_dict)
            size -= 1
        
        return pd.DataFrame(tweet_list)

    
    def make_dataframe_of_bots(self, min_num, max_num, size, bots):

        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
            
        tweet_list = []

        for tweet in tweets:
            user_name = tweet['user']['name']
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age - profile_age
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            user_lists = tweet['user']['listed_count']
            user_favorites = tweet['user']['favourites_count']
            tweet_count = tweet['user']['statuses_count']
            tweet_replies = tweet['reply_count']
            tweet_favorites = tweet['favorite_count']
            retweets = tweet['retweet_count']
            protected = tweet['user']['protected']
            verified = tweet['user']['verified']
            default_pic = tweet['user']['default_profile_image']

            if size == 0:
                break

            tweet_dict = {}

            if screen_name in bots:
                tweet_dict.update({
                    'followers': followers, 'following': following, 'ratio': ratio, 'age': age.days,
                    'name': screen_name,'tweets': tweet_count, 'favs': user_favorites, 'lists': user_lists})
            else:
                continue

            tweet_list.append(tweet_dict)
            size -= 1
        
        return pd.DataFrame(tweet_list)
    
    def get_unlabeled_training_data(self, min_num, max_num):

        tweets = self.c_tweet.find({"seq_no": {"$gt":min_num,"$lte": max_num}})
            
        tweet_list = []

        for tweet in tweets:
            seq_no = tweet['seq_no']
            user_name = tweet['user']['name']
            screen_name = tweet['user']['screen_name']
            profile_age = datetime.strptime(tweet['user']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            tweet_age = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
            age = tweet_age - profile_age
            followers = tweet['user']['followers_count']
            following = tweet['user']['friends_count']
            if following != 0:
                ratio = followers/following
            else:
                ratio = -1
            user_lists = tweet['user']['listed_count']
            user_favorites = tweet['user']['favourites_count']
            tweet_count = tweet['user']['statuses_count']
            tweet_replies = tweet['reply_count']
            tweet_favorites = tweet['favorite_count']
            retweets = tweet['retweet_count']
            protected = tweet['user']['protected']
            verified = tweet['user']['verified']
            default_pic = tweet['user']['default_profile_image']

            tweet_dict = {}
            tweet_dict.update({
                    'followers': followers, 'following': following, 'ratio': ratio, 'age': age.days,
                    'tweets': tweet_count, 'favs': user_favorites, 'lists': user_lists})

            tweet_list.append(tweet_dict)

        return pd.DataFrame(tweet_list)
    
    # takes a dataframe of known bots and 
    # concatenates it with the dataframe of regular users
    # also shuffles the accounts for training
    def mix(self, humans, bots):
        new_dataframe = pd.concat([humans, bots])
        return new_dataframe.sample(frac=1)


    def label(self, data, bot=False):
        labels = []
        match_list = data['name']
        if bot:
            for name in match_list:
                labels.append(1)
        else:
            for name in match_list:
                labels.append(0)
        data['bot'] = labels
        return data


    def split(self, data):
        X = pd.DataFrame(data, columns=['followers', 'following', 'ratio', 'age', 'tweets', 'favs', 'lists'])
        y = pd.DataFrame(data, columns=['bot'])
        return X, y


    def fit_predict(self, X_train, y_train, X_test):
        self.model.fit(X_train, y_train)
        self.test_y_predicted = self.model.predict(X_test)
    

    def get_accuracy(self, iteration, y_test):
        accuracy = np.mean(np.ravel(self.test_y_predicted) == np.ravel(y_test)) * 100    
        print('--------------------------------')
        print('Iteration:', iteration)
        print('\n')
        print('y-test set:',y_test.shape)
        print('\n')
        print("Accuracy rate for %f " % (accuracy)) 
        print('--------------------------------')

    # margin selection of uncertain examples
    # k = number of desired samples
    def select(self, X, k):
        probability = self.model.predict_proba(X)
        rev = np.sort(probability, axis=1)[:, ::-1]
        values = rev[:, 0] - rev[:, 1]
        selection = np.argsort(values)[:k]
        return selection

    # k = number of uncertain samples that will be labeled and added to training
    # start is the starting seq_no of the tweets that will be used for training
    # end is that last eq_no, e.g. start=0, end=1000000
    # step is the amount of tweets we will process each iteration and select k from
    # e.g. step = 100000, start=0, end=1000000 will produce 11 iterations, 10 if i=0
    # i is the starting iteration, e.g. i = 0 OR i = 1, depending on how you like to count
    def run(self, X_train, y_train, X_test, y_test, k, start, end, step, i):

        print('X_train:', X_train.shape, 'y_train:', y_train.shape, 'X_test:', X_test.shape, 'y_test:', y_test.shape)

        y_train_raveled = np.ravel(y_train)

        #train and predict
        self.fit_predict(X_train, y_train_raveled, X_test)
        self.get_accuracy(i, y_test)

        # get unlabeled data, predict, select uncertain examples via entropy
        unlabeled_df = self.get_unlabeled_training_data(start, start + step)
        selections = self.select(unlabeled_df, k)

        # predict labels for all selections
        df_preds = l.predict_labels(unlabeled_df.loc[selections])

        # split and add predictions to training set
        new_X, new_y = self.split(df_preds)
        X_train = pd.concat([X_train, new_X])
        y_train = pd.concat([y_train, new_y])

        # Update exit condition, make recursive call
        start += step
        i += 1
        if start <= end:
            self.run(X_train, y_train, X_test, y_test, k, start, end, step, i)





    