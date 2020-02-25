import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

df = pd.read_csv(filename)
bitstreams = df.bitstream.str.rsplit('.', 1)
bit_name = [x[0] for x in bitstreams]
ext = [x[1] for x in bitstreams]
df['bit_name'] = bit_name
df['ext'] = ext
print(df.head)

new_df = df.copy()

df2 = df.merge(new_df, on=('bit_name', 'handle', 'title'), how='inner', copy=False)
df2 = df2.drop_duplicates()
print(df2.columns)
print(df2)
