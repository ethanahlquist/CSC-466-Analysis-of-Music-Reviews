import pandas as pd
import sqlite3

sql_file = '../data/ethan_pitchfork.sqlite'
csv_file = '../data/spotify_pitchfork_cleaned.csv'


def main():
    conn = sqlite3.connect(sql_file)

    # Open the csv
    df_csv = pd.read_csv(csv_file, index_col=0)

    df_csv['reviewid'] = df_csv['reviewid'].astype(int)

    # Add sentiment scores to the original pitchfork sql database
    df_csv.to_sql('album_features', con=conn, if_exists='replace', index=False)

    # Print table that was added
    query = "select * from album_features;"
    df = pd.read_sql_query(query, conn)
    print(df)


if __name__ == "__main__":
    main()
