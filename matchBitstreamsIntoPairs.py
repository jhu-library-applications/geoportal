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
bitstreams = df.bitstream.str.rsplit('.')
ext = bitstreams[1].lowercase()
bit_name = bitstreams[0]
df['ext'] = ext
df['bit_name']
