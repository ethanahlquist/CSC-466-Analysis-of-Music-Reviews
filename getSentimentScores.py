import pandas as pd
import sqlite3
from nltk.sentiment import SentimentIntensityAnalyzer


def getSentimentScores(s):
    sia = SentimentIntensityAnalyzer()
    values = sia.polarity_scores(s['content'])
    s['neg'] = values['neg']
    s['neu'] = values['neu']
    s['pos'] = values['pos']
    s['compound'] = values['compound']

    s = s.drop(labels=['content'])
    return s


def main():
    conn = sqlite3.connect('./data/pitchfork.sqlite')

    """
    Get sentiment scores into a dataframe
    """
    #df_sentiments = df.apply(getSentimentScores, axis=1)

    """
    Export this dataframe to a csv
    """
    # df_sentiments.to_csv("./data/sentiments.csv")

    """
    Open the csv later, so scores are not reprocessed
    """
    df_sentiments = pd.read_csv("./data/sentiments.csv")

    """
    Add sentiment scores to the original pitchfork sql database
    """
    df_sentiments.to_sql('sentiment', con=conn, if_exists='append')

    # Print table that was added
    query = "select * from sentiment;"
    df = pd.read_sql_query(query, conn)
    print(df)


if __name__ == "__main__":
    main()
