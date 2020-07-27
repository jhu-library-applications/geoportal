import pandas as pd
import argparse
from datetime import datetime
import numpy as np
import convertGeoNamesFromLCNAF as geo

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-v', '--verify', choices=['yes', 'no'])
parser.add_argument('-fa', '--fast',)
parser.add_argument('-lc', '--lcnaf')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter marc spreadsheet filename (including \'.csv\'): ')
if args.verify:
    verify = args.verify
else:
    verify = input("Enter 'yes' to verify headings; 'no' to skip: ")
if verify == 'no':
    if args.fast:
        fastresults = args.fast
    else:
        fastresults = input('Enter name of fast result csv')
    if args.lcnaf:
        lcnafresults = args.lcnaf
    else:
        lcnaf = input('Enter name of lcnaf result csv')

df = pd.read_csv(filename)
fastList = []
lcnafList = []


# Create dictionary to use in convertLCNAFToGeoNames function.
def addDictonary(columnName, vocab):
    term = data.get(columnName)
    if pd.isna(term):
        pass
    else:
        if '|' in term:
            terms = term.split('|')
        else:
            terms = [term]
        for x in terms:
            vocabDict = {'term': x, 'oindex': index}
            if vocab == 'fast':
                fastList.append(vocabDict)
            else:
                lcnafList.append(vocabDict)


# Group matching headings together in order to perform fewer searches.
# Create column 'oindex' to keep track of original index of headings.
def condenseHeadings(listName):
    df_2 = pd.DataFrame.from_dict(listName)
    df_2 = df_2.replace(r'^\s*$', np.nan, regex=True)
    df_2.dropna(axis=0, inplace=True)
    pivoted = pd.pivot_table(df_2, index=['term'], values='oindex',
                             aggfunc=lambda x: '|'.join(str(v) for v in x))
    pivoted.reset_index(inplace=True)
    listName = pd.DataFrame.to_dict(pivoted, orient='records')
    return listName


# Group headings by original index.
# For each original index number, get rid of duplicate headings.
def explodeHeadingsByIndex(dataframe):
    dataframe.oindex = dataframe.oindex.str.split('|')
    dataframe = dataframe.drop(columns=['term', 'geoname0',
                                        'name0', 'geoname1',
                                        'name1', 'geoname2',
                                        'name2'])
    dataframe = dataframe.explode('oindex')
    dataframe = dataframe.dropna()
    dataframe = pd.pivot_table(dataframe, index=['oindex'], values='fullName',
                               aggfunc=lambda x: '|'.join(str(v) for v in x))
    dataframe.fullName = dataframe.fullName.str.split('|')
    dataframe.fullName = dataframe.apply(lambda row:
                                         set(row['fullName']), axis=1)
    dataframe.fullName = dataframe.fullName.str.join('|')
    dataframe.reset_index(inplace=True)
    return dataframe


# Create spreadsheet with headings converted to GeoNames.
if verify == 'yes':
    for index, data in df.iterrows():
        addDictonary('spatial_fast', 'fast')
        addDictonary('spatial_lcnaf', 'lcnaf')

    fastList = condenseHeadings(fastList)
    lcnafList = condenseHeadings(lcnafList)
    lcnafresults = geo.convertLCNAFToGeoNames(lcnafList, 'yes')
    fastresults = geo.convertFASTToGeoNames(fastList, 'yes')

    fastresults = pd.DataFrame.from_dict(fastresults)
    lcnafresults = pd.DataFrame.from_dict(lcnafresults)
    lcnafresults.to_csv('lcnaf_'+filename, index=False)
    fastresults.to_csv('fast_'+filename, index=False)
# Use pre-existing spreadsheet with headings converted to GeoNames.
else:
    fastresults = pd.read_csv(fastresults)
    lcnafresults = pd.read_csv(lcnafresults)

fastresults = explodeHeadingsByIndex(fastresults)
lcnafresults = explodeHeadingsByIndex(lcnafresults)

# Merge results from FAST and LCNAF into one new column 'spatial_coverage.'
# Remove duplicate result from spatial_coverage.
frame = pd.merge(fastresults, lcnafresults, on='oindex', suffixes=('_1', '_2'))
print(frame.head)
frame['spatial_coverage'] = frame['fullName_1']+'|'+frame['fullName_2']
frame.spatial_coverage = frame.spatial_coverage.str.split('|')
frame.spatial_coverage = frame.apply(lambda row:
                                     set(row['spatial_coverage']), axis=1)
frame.spatial_coverage = frame.spatial_coverage.str.join('|')
frame = frame.drop(columns=['fullName_1', 'fullName_2'])

# Merge 'spatial_coverage' column into marc spreadsheet.
frame.oindex = frame.oindex.astype('int64')
print(frame.head)
updated = pd.merge(df, frame, left_index=True, right_on='oindex')
updated = updated.drop(columns=['oindex', 'spatial_fast', 'spatial_lcnaf'])

# Create updated marc spreadsheet.
new_name = filename.replace('02', '03')
updated.to_csv(path_or_buf=new_name, encoding='utf-8', index=False)
