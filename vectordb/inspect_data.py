import pandas as pd

df = pd.read_csv("data/wiki_movie_plots_deduped.csv")
print(df.columns)

col = 'Origin/Ethnicity'

print(list(df[col].unique()))