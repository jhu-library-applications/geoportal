import pandas as pd
import argparse
from datetime import datetime
import numpy as np
import verifyHeadings as vh

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-v', '--verify')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.verify:
    verify = args.verify
else:
    verify = input('Enter yes to verify headings; else enter csv file: ')

df = pd.read_csv(filename)
searchList = []


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
            if "http://id.loc.gov/authorities/names/" in x:
                termURI = x.rsplit(' ', 1)
                uri = termURI[-1].strip()
                x = termURI[0].strip()
            else:
                uri = 'None'
            vocabDict = {'vocab': vocab, 'term': x, 'uri': uri,
                         'field': columnName, 'oindex': index}
            print(vocabDict)
            searchList.append(vocabDict)


# Clean up MARC spreadsheet.
df['title'] = df['title'].str.rstrip('/')
df['title'] = df['title'].str.rstrip('.')
df['description'] = df['description'].str.replace('|', ' ')
df['description'] = df['description'].str.replace('  ', ' ')
df['description'] = df['bounding_box'].str.replace('|', ',')
df['description'] = df['title']+'. '+df['description']+' '+df['scale']
df['rights'] = 'Public'
df['suppressed'] = 'False'
df['type'] = 'Image'
df['geom_type'] = 'Image'
df['solr_year'] = np.nan
df['subject'] = np.nan
df['date_issued'] = np.nan
df['creators'] = np.nan

# Create dictonary with headings to validate.
if verify == 'yes':
    for index, data in df.iterrows():
        addDictonary('authors', 'lcnaf')
        addDictonary('contributors', 'lcnaf')
        addDictonary('publisher', 'lcnaf')
    # Convert dictonary to dataframe.
    df_2 = pd.DataFrame.from_dict(searchList)
    df_2.term = df_2['term'].str.strip()
    df_2.term = df_2['term'].str.rstrip(',')
    # Group/condense matching headings together in order to perform fewer searches.
    # Create column 'oindex' to keep track of original index of headings.
    pivoted = pd.pivot_table(df_2, index=['term', 'vocab', 'field', 'uri'],
                             values='oindex',
                             aggfunc=lambda x: '|'.join(str(v) for v in x))
    print(pivoted.head)
    pivoted.reset_index(inplace=True)
    # Convert dataframe back to dictionary.
    updatedList = pd.DataFrame.to_dict(pivoted, orient='records')
    # Verify headings in dictionary.
    results = vh.verifyHeadingList(updatedList)
    results = pd.DataFrame.from_dict(results)
    results.to_csv('fullNameResults'+dt+'.csv', encoding='utf-8', index=False)

# Get validation results from previous generated spreadsheet.
else:
    results = pd.read_csv(verify)

# Split results into verified and not_verified headings.
verified = results.dropna(how='any')
not_verified = results.loc[pd.isna(results['authURI'])]

# De-condense headings and organize verified headings by original index.
verified.oindex = verified.oindex.str.split('|')
verified = verified.explode('oindex')
verified = pd.pivot_table(verified, index=['oindex', 'field'],
                          values='authLabel',
                          aggfunc=lambda x: '|'.join(str(v) for v in x))
verified.reset_index(inplace=True)

# Sort headings into contributor, publisher, or author columns.
verified = pd.DataFrame.pivot(verified, index='oindex',
                              columns='field', values='authLabel')
verified = verified.rename(columns={'contributors': 'verified_contributors',
                                    'publisher': 'verified_publisher',
                                    'authors': 'verified_authors'})
verified.to_csv(path_or_buf='testing'+dt+'.csv', encoding='utf-8')

# De-condense headings and organize not_verified headings by original index.
not_verified.oindex = not_verified.oindex.str.split('|')
not_verified = not_verified.explode('oindex')
not_verified = pd.pivot_table(not_verified, index=['oindex', 'field'],
                              values='term',
                              aggfunc=lambda x: '|'.join(str(v) for v in x))
not_verified.reset_index(inplace=True)

# Sort not_verified headings into contributor, publisher, or author columns.
not_verified = pd.DataFrame.pivot(not_verified, index='oindex',
                                  columns='field', values='term')
not_verified = not_verified.rename(columns={'contributors': 'na_contributors',
                                            'publisher': 'na_publisher',
                                            'authors': 'na_authors'})
not_verified.to_csv(path_or_buf='testing2'+dt+'.csv', encoding='utf-8')

# Merge not_verified headings and verified headings into marc spreadsheet.
verified.reset_index(inplace=True)
not_verified.reset_index(inplace=True)
verified.oindex = verified.oindex.astype('int64')
not_verified.oindex = not_verified.oindex.astype('int64')
new_df = pd.merge(df, verified, how='left', left_index=True, right_on='oindex')
new_df = pd.merge(new_df, not_verified, how='left', on='oindex')

# Delete old author, contributor, and publisher columns.
new_df = new_df.drop(columns=['authors', 'contributors',
                              'publisher', 'oindex', 'scale'])
print(new_df.head)

# Create updated marc spreadsheet.
new_name = '02_'+filename
new_df.to_csv(path_or_buf=new_name, encoding='utf-8', index=False)
