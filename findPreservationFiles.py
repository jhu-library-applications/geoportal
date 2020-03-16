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
bitstreams = df.bitstream.str.rsplit('.', 1)
ext = [x[1] for x in bitstreams]
ext = [e.lower() for e in ext]
df['ext'] = ext

pivoted = pd.pivot_table(df, index=['handle'], values=['ext', 'bitstream'], aggfunc=lambda x: ','.join(str(v) for v in x))
print(pivoted.sort_values(ascending=True, by='handle').head())

df = pd.DataFrame(pivoted)
df = df.reset_index()

unique = []
pres_list = []
for index, value in df.ext.items():
    values = value.split(',')
    values = list(set(values))
    unique.append(values)
    pres = []
    if len(values) == 1:
        pres.append(values[0])
    else:
        for v in values:
            if v == 'tif':
                pres.append(v)
            elif v == 'tiff':
                pres.append(v)
            elif v == 'jp2':
                pres.append(v)
            else:
                pass
    pres_list.append(pres)

df['unique'] = unique
df['pres'] = pres_list
del df['ext']

pres_bits = []
for index, value in df.bitstream.items():
    exts = df.at[index, 'pres']
    bits = []
    values = value.split(',')
    print(values)
    for v in values:
        v_list = v.rsplit('.', 1)
        try:
            if v_list[1].lower() in exts:
                bits.append(v)
            else:
                pass
        except IndexError:
            pass
    pres_bits.append(bits)

df['pres_bits'] = pres_bits

print(df.head)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
new_name = filename.replace('.csv', '').replace('handlesAndBitstreams', '')
df.to_csv(path_or_buf='sample_'+dt+'.csv', header='column_names', encoding='utf-8', sep=',', index=False)
