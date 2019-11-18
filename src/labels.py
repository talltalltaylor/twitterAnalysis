from snorkel.labeling import labeling_function
from snorkel.labeling import LabelModel, PandasLFApplier

BOT = 1
NOT = 0
ABSTAIN = -1

@labeling_function()
def low_followers_tweets(tweet):
    return BOT if tweet.followers < 30 and tweet.tweets < 50 and tweet.ratio < 0.05 else NOT

@labeling_function()
def low_follow_ratio(tweet):
    return BOT if tweet.ratio == 0 else NOT

@labeling_function()
def profile_pic(tweet):
    return BOT if tweet.favs == 0 and tweet.ratio < 0.05 else NOT


lfs = [low_followers_tweets, low_follow_ratio, profile_pic]

def predict_labels(df_train):
    applier = PandasLFApplier(lfs)
    L_train = applier.apply(df_train)

    # Train the label model and compute the training labels
    label_model = LabelModel(cardinality=2, verbose=True)
    label_model.fit(L_train, n_epochs=500, log_freq=50, seed=123)
    df_train["bot"] = label_model.predict(L=L_train, tie_break_policy="abstain")

    return df_train[df_train.bot != ABSTAIN]