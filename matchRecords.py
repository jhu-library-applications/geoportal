import csv
import argparse
import re
from fuzzywuzzy import fuzz
from datetime import datetime

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

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

f = csv.writer(open('matchDSpaceAndMARCRecords'+dt+'.csv', 'w', encoding='utf-8'))
f.writerow(['link']+['itemID']+['j_bib']+['m_bib']+['j_title']+['j_date']+['m_title']+['m_date']+['match'])

with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        j_uri = row['dc.identifier.uri']
        itemID = row['itemID']
        j_title = row['dc.title']
        j_date = row['dc.date.issued']
        j_bib = row['dc.identifier.localbibnumber'].strip()
        if j_bib:
            j_bib = re.search(r'[0-9]+', j_bib)
            j_bib = j_bib.group()
            print(j_bib)
        with open(filename2) as otherMetadata:
            otherMetadata = csv.DictReader(otherMetadata)
            for row in otherMetadata:
                m_uris = row['links'].split('|')
                m_title = row['title']
                m_bib = row['bib']
                m_date = row['date1']
                ratio = fuzz.ratio(j_title, m_bib)
                if j_uri in m_uris:
                    f.writerow([j_uri]+[itemID]+[j_bib]+[m_bib]+[j_title]+[j_date]+[m_title]+[m_date]+['exact'])
                    print("found: "+j_uri)
                    break
                elif j_bib == m_bib:
                    f.writerow([j_uri]+[itemID]+[j_bib]+[m_bib]+[j_title]+[j_date]+[m_title]+[m_date]+['exact'])
                    print("found: "+j_uri)
                    break
                elif ratio > 95:
                    f.writerow([j_uri]+[itemID]+[j_bib]+[m_bib]+[j_title]+[j_date]+[m_title]+[m_date]+['probable match'])
                    print("found: "+j_uri)
                    break
            else:
                f.writerow([j_uri]+[itemID]+[j_bib]+['none']+[j_title]+[j_date]+['none']+['none']+['no match'])
