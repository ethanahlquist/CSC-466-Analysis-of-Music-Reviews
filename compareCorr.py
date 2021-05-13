import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer


def main():
    conn = sqlite3.connect('./data/pitchfork.sqlite')

    print(pd.read_sql_query("PRAGMA table_info(reviews);", conn))

    query = "SELECT reviewid, compound FROM sentiment;"
    df_sentiment = pd.read_sql_query(query, conn)
    query = "SELECT reviewid, title, score FROM reviews;"
    df_review = pd.read_sql_query(query, conn)

    df_comb = df_review.merge(df_sentiment)
    #corralation = df_comb['compound'].corr(df_comb['score'])

    df_comb['comp_sq'] = df_comb['compound']**2
    df_comb['binned_sq'] = pd.cut(df_comb['comp_sq'], bins=5)

    #df_comb.plot(x='binned_sq', y='score', kind='scatter')

    new_comb = df_comb[['binned_sq', 'score']]

    #new_comb.plot.hist(x='binned_sq', y='score', kind='scatter')
    plt.show()

    # print(df)


if __name__ == "__main__":
    main()
