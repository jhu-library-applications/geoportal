import pandas as pd
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

df = pd.read_csv(filename)
df = df.drop(columns=['description', 'date'])
pivoted = pd.pivot_table(df, index=['bitstream'], values='uri', aggfunc=lambda x: ','.join(str(v) for v in x))
print(pivoted.sort_values(ascending=True, by='bitstream').head())

df = pd.DataFrame(pivoted)
df = df.reset_index()


bitstreams = df.bitstream.str.rsplit('.', 1)
bit_name = [x.rsplit('.', 1) for x in bitstream]
ext = [x[1] for x in bitstreams]
ext = [e.lower() for e in ext]

print(df.head)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
new_name = filename.replace('.csv', '').replace('handlesAndBitstreams', '')
df.to_csv(path_or_buf='sample_'+dt+'.csv', header='column_names', encoding='utf-8', sep=',', index=False)
