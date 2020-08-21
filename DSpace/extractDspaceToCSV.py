import csv
import argparse
import re
from datetime import datetime
import os
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-hi', '--hierarchy')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.hierarchy:
    hierarchy = args.hierarchy
else:
    hierarchy = input('Enter hierarchy, solo, parent, or child: ')

fileDir = os.path.dirname(__file__)

lang_dict = {}


def createDict(csvname, columnName1, columnName2, dictname):
    with open(csvname) as codes:
        codes = csv.DictReader(codes)
        for row in codes:
            code = row[columnName1]
            name = row[columnName2]
            dictname[code] = name


#  Import gacs codes used in 043 fields.
createDict(os.path.join(fileDir, 'dictionaries/iso_lang.csv'), 'code', 'language', lang_dict)


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


def create_references(uri, bitstream):
    dict = {}
    dict['http://schema.org/url'] = uri
    if image_link:
        dict['http://iiif.io/api/image'] = image_link
        dict['http://schema.org/downloadUrl'] = image_link
    return dict


keyList = ['hierarchy', 'uri', 'identifier', 'rights', 'title', 'layer_slug', 'solr_geom', 'solr_year', 'creators', 'description', 'collection', 'format', 'language', 'publisher', 'source', 'subject', 'type', 'isPartOf', 'date_issued', 'references', 'spatial', 'temporal', 'geo_type', 'layer_id', 'layer_modified', 'suppressed', 'bib', 'oclc', 'bitstreams']


dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open('remediatedDspaceMetadata_'+dt+'.csv', 'w'))
f.writerows([keyList])

with open(filename) as geoMetadata:
    geoMetadata = csv.DictReader(geoMetadata)
    for row in geoMetadata:
        hierarchy = hierarchy
        geoDict = dict.fromkeys(keyList)
        id = uuid.uuid4()
        uri = row['dc.identifier.uri']
        bitstream = key_finder('bitstream_1')
        bitstream_2 = key_finder('bitstream_2')
        bitstreams = [bitstream, bitstream_2]
        references = create_references(uri, bitstream)
        advisor = key_finder('dc.contributor.advisor')
        authors = key_finder('dc.contributor.author')
        editor = key_finder('dc.contributor.editor')
        other = key_finder('dc.contributor.other')
        contributors = combine_keys(keyList=[authors, advisor, editor, other])
        desc = key_finder('dc.description')
        abstract = key_finder('dc.description.abstract')
        sponsor = key_finder('dc.description.sponsorship')
        toc = key_finder('dc.description.tableofcontents')
        descs = combine_keys(keyList=[desc, abstract, sponsor, toc])
        title = key_finder('dc.title')
        alt_title = key_finder('dc.title.alternative')
        title = combine_keys(keyList=[title, alt_title])
        subject = key_finder('dc.subject')
        ddc = key_finder('dc.subject.ddc')
        subjects = combine_keys(keyList=[subject, ddc])
        date1 = key_finder('dc.date.issued')
        id_other = key_finder('dc.identifier.other')
        lang = key_finder('dc.language.iso')
        publisher = key_finder('dc.publisher')
        type = key_finder('dc.type')
        bib = key_finder('dc.identifier.localbibnumber')
        image_link = key_finder('image_link')

        geoDict['identifier'] = 'http://hopkinsgeoportal/'+id
        geoDict['layer_slug'] = id
        geoDict['uri'] = uri
        geoDict['bitstreams'] = bitstreams
        geoDict['references'] = references
        geoDict['creators'] = contributors
        geoDict['description'] = descs
        geoDict['subject'] = subjects
        geoDict['date_issued'] = date1
        geoDict['publisher'] = publisher
        geoDict['type'] = type
        geoDict['rights'] = 'Public'
        geoDict['suppressed'] = 'false'
        for id in id_other.split('|'):
            oclc = re.search(r'[0-9]{7,10}', id)
            if oclc:
                oclc = oclc.group(0)
            else:
                collection = id
                geoDict['collection'] = collection
        lang = lang.split('|')
        for count, code in enumerate(lang):
            lang[count] = code[:2]
        for count, code in enumerate(lang):
            for k, v in lang_dict.items():
                if code == k:
                    lang[count] = v
        lang = '|'.join(lang)
        geoDict['language'] = lang
        if hierarchy == 'child':
            geoDict['hierarchy'] = hierarchy
            bit_parts = bitstream.rsplit('.', 1)
            bit_title = bit_parts[0]
            geoDict['title'] = bit_title
        else:
            geoDict['hierarchy'] = hierarchy
            geoDict['title'] = title

        values = list(geoDict.values())

        f.writerows([values])
