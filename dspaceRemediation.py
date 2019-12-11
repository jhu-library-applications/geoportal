import csv
import argparse
import re

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


with open(filename) as geoMetadata:
    geoMetadata = csv.DictReader(geoMetadata)
    for row in geoMetadata:
        itemID = row['itemID']
        authors = row['dc.contributor.author']
        date1 = row['dc.date.issued']
        identifiers = row['dc.identifier.other']+'|'+row['dc.identifier.issn']
        links = row['dc.identifier.uri']
        descs = row['dc.description']+'|'+row['dc.description.abstract']
        lang = row['dc.language.iso']
        publisher = row['dc.publisher']
        subjects = row['dc.subject']
        titles = row['dc.title']+'|'+row['dc.title.alternative']
        type = row['dc.type']
        contibutors = row['dc.contributor.advisor']
        bib = row['dc.identifier.localbibnumber']
        for identifier in identifiers.split('|'):
            if
            oclc = re.search(r'([0-9]+)', identifier)
            if oclc:
                oclc = oclc.group(1)
                print(oclc)
            else:
                collection = identifier
                print(collection)
