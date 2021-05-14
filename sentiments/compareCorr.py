import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from nltk.sentiment import SentimentIntensityAnalyzer


def main():
    conn = sqlite3.connect('../data/pitchfork.sqlite')

    print(pd.read_sql_query("PRAGMA table_info(reviews);", conn))

    query = "SELECT reviewid, compound FROM sentiment;"
    df_sentiment = pd.read_sql_query(query, conn)
    query = "SELECT reviewid, title, score FROM reviews;"
    df_review = pd.read_sql_query(query, conn)

    df_comb = df_review.merge(df_sentiment)
    #corralation = df_comb['compound'].corr(df_comb['score'])

    df_comb['comp_sq'] = df_comb['compound']**2
    df_comb.plot(x='comp_sq', y='score', kind='scatter')
    plt.show()

    """
    df = pd.DataFrame()
    bins = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    df['binned_score'] = pd.cut(df_comb['score'], bins=bins)
    bins = [-1, -.8, -.6, -.4, -.2, 0, .2, .4, .6, .8, 1]
    df['binned_sentiment'] = pd.cut(
        df_comb['compound'], bins=bins).value_counts()

    df.plot.bar(rot=0, color="b", figsize=(6, 4))
    plt.show()
    """

    #new_comb = df_comb[['comp_sq', 'comp_sq']]
    #new_comb.value_counts().plot.bar(rot=0, color="b", figsize=(6, 4))
    # new_comb.value_counts().plot.bar(rot=0, color="b", figsize=(6, 4))

    # #new_comb.plot.hist(x='binned_sq', y='score', kind='scatter')

    # print(df)


if __name__ == "__main__":
    main()
