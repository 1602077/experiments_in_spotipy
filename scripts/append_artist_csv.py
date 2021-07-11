import pandas as pd
import glob
import os

master_df = pd.DataFrame()

artist_csvs = glob.glob(os.path.join("../data/artists/","*.csv"))
for f in artist_csvs:
    df = pd.read_csv(f)
    master_df = master_df.append(df, ignore_index=True)

master_df = master_df[~(master_df['popularity'] <= 10)]
print(master_df.describe())
print(len(master_df.index))
master_df.to_csv("../data/master_data.csv", index=False)
