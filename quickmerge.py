import pandas as pd
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-f2', '--file2')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.file2:
    filename2 = args.file2
else:
    filename2 = input('Enter csv with marc data (including \'.csv\'): ')

df_print = pd.read_csv(filename, index_col='j_uri', header=0)
df_elect = pd.read_csv(filename2, index_col='j_uri', header=0)
values = {'map_holder': df_elect.map_holder}
frame = df_print.fillna(value=values, axis='index')
# frame = pd.merge(df_print, df_elect, how='left', on='j_uri')

frame = frame.drop_duplicates()
print(frame.columns)
print(frame.head)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

frame.to_csv(path_or_buf='mergedCSV_'+dt+'.csv')
