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
bitstreams = df.bitstream.str.rsplit('.', 1)
bit_name = [x[0] for x in bitstreams]
ext = [x[1] for x in bitstreams]
ext = [e.lower() for e in ext]
df['bit_name'] = bit_name
df['ext'] = ext
exts = df['ext'].unique()

all_df = pd.DataFrame()
for count, e in enumerate(exts):
    new_df = df[df.ext == e]
    if count == 0:
        all_df = new_df
    else:
        all_df = all_df.merge(new_df, on=('bit_name', 'handle', 'title'), how='outer', copy=False, suffixes=('', '_'+str(count)))

bit_names = ['bitstream']
for count, e in enumerate(exts):
    if count > 0:
        all_df = all_df.drop(columns=['ext_'+str(count)])
        bitstream_name = 'bitstream_'+str(count)
        bit_names.append(bitstream_name)

all_df['bitstreams'] = all_df[bit_names].values.astype(str).tolist()

all_df = all_df.drop(columns=['bit_name', 'ext'])
all_df = all_df.drop(columns=bit_names)
print(all_df.head)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
all_df.to_csv(path_or_buf='matchy_'+dt+'.csv', header='column_names', encoding='utf-8', sep=',', index=False)
