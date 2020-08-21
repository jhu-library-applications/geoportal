import pandas as pd
import argparse
from sheetFeeder import dataSheet
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-m', '--marc')
parser.add_argument('-mt', '--matchingfile')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.marc:
    marc = args.marc
else:
    marc = input('Enter csv with marc data (including \'.csv\'): ')
if args.matchingfile:
    matchingfile = args.matchingfile
else:
    matchingfile = input('Enter matching filename (including \'.csv\'): ')


df_ds = pd.read_csv(filename, index_col='uri', header=0)
df_marc = pd.read_csv(marc, index_col='bib', header=0)
df_match = pd.read_csv(matchingfile, index_col=None, header=0)

frame = pd.merge(df_match, df_ds, on='uri', suffixes=('', '_ds'))
frame = pd.merge(frame, df_marc, on='bib', suffixes=('', '_m'))

print(frame.columns)
print(frame.head)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

frame.to_csv(path_or_buf='mergedCSV_'+dt+'.csv', index=False)

update = input("Do you want to update your google sheet? ")

if update == 'yes':
    my_sheet = dataSheet()
    my_sheet.importCSV('mergedCSV.csv', quote='ALL')
    print("Google sheet updated!")
else:
    pass
