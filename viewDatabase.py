import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

sql_file = './data/pitchfork.sqlite'


def main():
    conn = sqlite3.connect(sql_file)

    # Get all tables:
    print("# Get all tables:")
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    print(f"\n{query}\n")
    print(pd.read_sql_query(query, conn).squeeze().tolist())

    print("# Show field in a table")
    query = "PRAGMA table_info(album_features);"
    print(f"\n{query}\n")
    print(pd.read_sql_query(query, conn))

    print("# Display a table")
    query = "SELECT * FROM album_features;"
    print(f"\n{query}\n")
    print(pd.read_sql_query(query, conn))

    query = "SELECT reviewid, compound FROM sentiment;"
    print(f"\n{query}\n")
    df_sentiment = pd.read_sql_query(query, conn)
    print(df_sentiment)

    query = "SELECT reviewid, title, score FROM reviews;"
    print(f"\n{query}\n")
    df_review = pd.read_sql_query(query, conn)
    print(df_review)


if __name__ == "__main__":
    main()
