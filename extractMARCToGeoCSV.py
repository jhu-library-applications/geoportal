from pymarc import MARCReader
import csv
import argparse
import re
import os
from datetime import datetime
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()
if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.mrc\'): ')


fileDir = os.path.dirname(__file__)

datetypes_dict = {}
marc_lang = {}
cat_dict = {}


def createDict(csvname, column1, column2, dictname):
    with open(csvname) as codes:
        codes = csv.DictReader(codes)
        for row in codes:
            code = row[column1]
            name = row[column2]
            dictname[code] = name


#  Import type codes used in 006.
createDict(os.path.join(fileDir, 'dictionaries/marc_datetypes.csv'), 'Type', 'Name', datetypes_dict)
# Import language codes used in language.
createDict(os.path.join(fileDir, 'dictionaries/marc_lang.csv'), 'Code', 'Name', marc_lang)
# Import category codes used in 007.
createDict(os.path.join(fileDir, 'dictionaries/marc_007categoryMaterial.csv'), 'Code', 'Name', cat_dict)


#  Creates k,v pair in dict where key = field_name, value = values of MARC tags in record.
def field_finder(field_name, tags):
    field_list = []
    field = record.get_fields(*tags)
    for my_field in field:
        my_field = my_field.format_field()
        field_list.append(my_field)
    if field_list:
        field_list = '|'.join(str(e) for e in field_list)
        mrc_fields[field_name] = field_list
    else:
        mrc_fields[field_name] = ''


# Creates k,v pair in dict where key = field_name, value = values of specific subfield in MARC tag in record.
def subfield_finder(field_name, subfields, tags):
    field_list = []
    field = record.get_fields(*tags)
    for my_field in field:
        my_subfield = my_field.get_subfields(*subfields)
        for field in my_subfield:
            if field not in field_list:
                field_list.append(field)
    if field_list:
        field_list = '|'.join(str(e) for e in field_list)
        mrc_fields[field_name] = field_list
    else:
        mrc_fields[field_name] = ''


# Converts code from MARC record into name from imported dictionaries.
def convert_to_name(keyname, dictname):
    v = mrc_fields.get(keyname)
    if '|' in v:
        v = v.split('|')
        for count, item in enumerate(v):
            for key, value in dictname.items():
                if item == key:
                    v[count] = value
        mrc_fields[keyname] = '|'.join(v)
    else:
        for key, value in dictname.items():
            if v == key:
                mrc_fields[keyname] = value

# Finds geographic subject headings from 600 fields.
def geo_finder(field_name, subfields, tags):
    field_list = []
    field = record.get_fields(*tags)
    for my_field in field:
        heading = []
        my_subfield = my_field.get_subfields(*subfields)
        for field in my_subfield:
            heading.append(field)
        heading = '--'.join(str(e) for e in heading)
        if heading not in field_list:
            field_list.append(heading)
    if field_list:
        field_list = '|'.join(str(e) for e in field_list)
        mrc_fields[field_name] = field_list
    else:
        mrc_fields[field_name] = ''


def makeBoundingBox():
    box = []
    coor_list = ['west', 'south', 'east', 'north']
    if mrc_fields.get('north'):
        for item in coor_list:
            direction = mrc_fields.get(item)
            if "|" in direction:
                direction = direction.split('|')
                direction = direction[0]
            else:
                direction = direction
            direction = direction.replace('+', '')
            box.append(direction)
        box = ', '.join(box)
        mrc_fields['bounding_box'] = box
    else:
        mrc_fields['bounding_box'] = ''
    for item in coor_list:
        del mrc_fields[item]


all_fields = []
record_count = 0
with open(filename, 'rb') as fh:
    marc_recs = MARCReader(fh, to_unicode=True)
    for record in marc_recs:
        mrc_fields = {}
        leader = record.leader
        #  Finds fields/subfield values in record.
        field_finder('category', tags=['007'])
        field_finder('008', tags=['008'])
        subfield_finder('bib', subfields=['a'], tags=['910'])
        subfield_finder('oclc', subfields=['a'], tags=['035'])
        subfield_finder('links', subfields=['u'], tags=['856'])
        mrc_fields['title'] = record.title()
        subfield_finder('alt_title', subfields=['a', 'b'], tags=['246'])
        field_finder('authors', tags=['100', '110', '111', '130'])
        subfield_finder('statresp', subfields=['c'], tags=['245'])
        field_finder('contributors',  tags=['700', '710', '711', '730'])
        subfield_finder('publisher', subfields=['b'], tags=['260', '264'])
        field_finder('marc_subjects', tags=['600', '610', '650', '651'])
        geo_finder('spatial_fast', tags=['650'], subfields=['z'])
        subfield_finder('spatial_lcnaf', tags=['651'], subfields=['a', 'z'])
        field_finder('description', tags=['500', '520'])
        subfield_finder('language', subfields=['a', 'b', 'c', 'd', 'f'], tags=['041'])
        subfield_finder('west', subfields=['d'], tags=['034'])
        subfield_finder('east', subfields=['e'], tags=['034'])
        subfield_finder('north', subfields=['f'], tags=['034'])
        subfield_finder('south', subfields=['g'], tags=['034'])
        subfield_finder('temporal', subfields=['x', 'y'], tags=['034'])
        subfield_finder('scale', subfields=['a'], tags=['255'])
        catValue = mrc_fields.get('category')
        if catValue:
            mrc_fields['category'] = catValue[0]
        convert_to_name('category', cat_dict)
        convert_to_name('language', marc_lang)

        # Edit & convert values in dictionary.
        for k, v in mrc_fields.items():
            # Find DtSt and Dates from field 008.
            if k == '008':
                if v:
                    datetype = v[6]
                    date1 = v[7:11].strip()
                    date2 = v[11:15].strip()
                    lang = v[35:38]
                else:
                    datetype = ''
                    date1 = ''
                    date2 = ''
                    lang = ''
            # Finds only oclc number, deleting prefixes.
            elif k == 'oclc' and v != '':
                oclc_list = []
                v = v.split('|')
                for item in v:
                    item = str(item)
                    oclc_num = re.search(r'([0-9]+)', item)
                    if oclc_num:
                        oclc_num = oclc_num.group(1)
                        if oclc_num not in oclc_list:
                            if oclc_num != mrc_fields['bib'][0]:
                                oclc_list.append(oclc_num)
                v = '|'.join(str(e) for e in oclc_list)
                mrc_fields[k] = v

        del mrc_fields['008']
        mrc_fields['datetype'] = datetype
        convert_to_name('datetype', datetypes_dict)
        mrc_fields['date1'] = date1
        mrc_fields['date2'] = date2
        mrc_fields['lang'] = lang
        convert_to_name('lang', marc_lang)
        if mrc_fields.get('language') == '':
            mrc_fields['language'] = mrc_fields.get('lang')
        else:
            pass
        del mrc_fields['lang']
        makeBoundingBox()

        # Adds dict created by this MARC record to all_fields list.
        all_fields.append(mrc_fields)
        record_count = record_count + 1
        print(record_count)

df = pd.DataFrame.from_dict(all_fields)
print(df.head(15))
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='marcRecords_'+dt+'.csv', header='column_names', encoding='utf-8', sep=',', index=False)
