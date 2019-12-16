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


lang_dict = {}


def createDict(csvname, columnName1, columnName2, dictname):
    with open(csvname) as codes:
        codes = csv.DictReader(codes)
        for row in codes:
            code = row[columnName1]
            name = row[columnName2]
            dictname[code] = name


#  Import gacs codes used in 043 fields.
createDict('iso_lang.csv', 'code', 'language', lang_dict)


def key_finder(columnName):
    try:
        value = row[columnName]
        return value
    except KeyError:
        value = ''
    return value


def combine_keys(keyList):
    string = ''
    newKeyList = []
    for value in keyList:
        if value:
            newKeyList.append(value)
    string = '|'.join(newKeyList)
    return string


f = csv.writer(open('name.csv', 'w'))
f.writerow(['itemID']+['uri']+['bib']+['oclc']+['lang']+['authors']+['contributors']+['descriptions']+['title']+['alt_title']+['subjects']+['date1']+['collection']+['id_issn']+['publisher']+['type'])

with open(filename) as geoMetadata:
    geoMetadata = csv.DictReader(geoMetadata)
    for row in geoMetadata:
        itemID = row['itemID']
        uri = row['dc.identifier.uri']
        advisor = key_finder('dc.contributor.advisor')
        authors = key_finder('dc.contributor.author')
        editor = key_finder('dc.contributor.editor')
        other = key_finder('dc.contributor.other')
        contributors = combine_keys(keyList=[advisor, editor, other])
        desc = key_finder('dc.description')
        abstract = key_finder('dc.description.abstract')
        sponsor = key_finder('dc.description.sponsorship')
        toc = key_finder('dc.description.tableofcontents')
        descs = combine_keys(keyList=[desc, abstract, sponsor, toc])
        title = key_finder('dc.title')
        alt_title = key_finder('dc.title.alternative')
        subject = key_finder('dc.subject')
        ddc = key_finder('dc.subject.ddc')
        subjects = combine_keys(keyList=[subject, ddc])
        date1 = key_finder('dc.date.issued')
        id_other = key_finder('dc.identifier.other')
        id_issn = key_finder('dc.identifier.issn')
        lang = key_finder('dc.language.iso')
        publisher = key_finder('dc.publisher')
        type = key_finder('dc.type')
        bib = key_finder('dc.identifier.localbibnumber')
        for id in id_other.split('|'):
            oclc = re.search(r'[0-9]{7,10}', id)
            if oclc:
                oclc = oclc.group(0)
            else:
                collection = id
        lang = lang.split('|')
        for count, code in enumerate(lang):
            lang[count] = code[:2]
        for count, code in enumerate(lang):
            for k, v in lang_dict.items():
                if code == k:
                    lang[count] = v
        lang = '|'.join(lang)
        print(lang)

        f.writerow([itemID]+[uri]+[bib]+[oclc]+[lang]+[authors]+[contributors]+[descs]+[title]+[alt_title]+[subjects]+[date1]+[collection]+[id_issn]+[publisher]+[type])
