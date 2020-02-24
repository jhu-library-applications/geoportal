import csv
import argparse
import re
from fuzzywuzzy import fuzz
from datetime import datetime
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-t', '--file2')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.file2:
    filename2 = args.file2
else:
    filename2 = input('Enter filename (including \'.csv\'): ')


def addToDict(key, value):
    try:
        value = row[value]
        if value:
            value = value.strip()
            j_dict[key] = value
            return value
    except KeyError:
        pass


def addMARC():
    j_dict['m_bib'] = m_bib
    j_dict['m_title'] = m_title
    j_dict['m_date'] = m_date
    j_dict['m_category'] = m_category


all_files = []
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    # Open DSpace records from CSV.
    for row in itemMetadata:
        j_dict = {}
        j_uri = addToDict('j_uri', 'dc.identifier.uri')
        itemID = addToDict('itemID', 'itemID')
        j_title = addToDict('j_title', 'dc.title')
        j_date = addToDict('j_date', 'dc.date.issued')
        j_bib = row['dc.identifier.localbibnumber'].strip()
        if j_bib:
            j_bib = re.search(r'[0-9]+', j_bib)
            j_bib = j_bib.group()
            j_dict['j_bib'] = j_bib
        with open(filename2) as otherMetadata:
            otherMetadata = csv.DictReader(otherMetadata)
            # Open MARC records from CSV.
            for row in otherMetadata:
                m_uris = row['links'].split('|')
                m_title = row['title']
                m_bib = row['bib']
                m_date = row['date1']
                m_category = row['category']
                # Find title fuzzy ratio.
                ratio = fuzz.ratio(j_title, m_title)
                # p_ratio = fuzz.partial_ratio(j_title, m_title)
                # Try to match by URI.
                if j_uri in m_uris:
                    addMARC()
                    j_dict['match'] = 'exact'
                    break
                # Try to match by Horizon bib number.
                elif j_bib == m_bib:
                    addMARC()
                    j_dict['match'] = 'exact'
                    break
                # Try to match title with fuzzy matching.
                elif ratio > 90 and m_date == j_date:
                    old_ratio = j_dict.get(ratio)
                    if (old_ratio is None) or (old_ratio < ratio):
                        addMARC()
                        j_dict['ratio'] = [ratio]
                        j_dict['match'] = 'probable'
                    else:
                        pass
                # elif p_ratio > 95 and m_date == j_date:
                #     old_ratio = j_dict.get(p_ratio)
                #     if old_ratio < p_ratio:
                #         addMARC()
                #         j_dict['ratio'] = [ratio]
                #         j_dict['match'] = 'probable'
                #     else:
                #         pass
            else:
                j_dict['match'] = 'none'
        all_files.append(j_dict)

df = pd.DataFrame.from_dict(all_files)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='matchedDspaceAndMARC_'+dt+'.csv', header='column_names', encoding='utf-8', sep=',', index=False)
