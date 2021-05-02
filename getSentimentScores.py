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

    query = "PRAGMA table_info(content);"
    query = "SELECT reviewid, content FROM content;"

    df = pd.read_sql_query(query, conn)

    conn.close()

    df_sentiments = df.apply(getSentimentScores, axis=1)

    # df_sentiments.to_csv("./data/sentiments.csv")
    conn = sqlite3.connect('./data/sentiments.sqlite')
    df_sentiments.to_sql("./data/sentiments.sqlite", conn)


if __name__ == "__main__":
    main()
