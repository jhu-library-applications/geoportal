from pymarc import MARCReader
import csv
import argparse
import re
import os
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.mrc\'): ')

fileDir = os.path.dirname(__file__)

types_dict = {}
level_dict = {}
catsource_dict = {}


def createDict(csvname, column1, column2, dictname):
    with open(csvname) as codes:
        codes = csv.DictReader(codes)
        for row in codes:
            code = row[column1]
            name = row[column2]
            dictname[code] = name


#  Import type codes used in 008 field.
createDict(os.path.join(fileDir, 'dictionaries/marc_typeAuthorities.csv'), 'code', 'name', types_dict)
createDict(os.path.join(fileDir, 'dictionaries/marc_levelAuthorities.csv'), 'code', 'name', level_dict)
createDict(os.path.join(fileDir, 'dictionaries/marc_catsourceAuthorities.csv'), 'code', 'name', catsource_dict)


#  Creates k,v pair in dict where key = field_name, value = values of MARC tags in record.
def field_finder(record, field_name, tags):
    field = record.get_fields(*tags)
    field_list = []
    for my_field in field:
        my_field = my_field.format_field()
        field_list.append(my_field)
    mrc_fields[field_name] = field_list


# Creates k,v pair in dict where key = field_name, value = values of specific subfield in MARC tag in record.
def subfield_finder(record, field_name, subfields, tags):
    field = record.get_fields(*tags)
    field_list = []
    for my_field in field:
        my_field = my_field.get_subfields(*subfields)
        for field in my_field:
            field_list.append(field)
    mrc_fields[field_name] = field_list


# Converts code from MARC record into name from imported dictionaries.
def convert_to_name(keyname, dictname):
    for k, v in mrc_fields.items():
        if k == keyname:
            for key, value in dictname.items():
                if v == key:
                    v = value
                    mrc_fields[k] = v


all_fields = []
record_count = 0

with open(filename, 'rb') as fh:
    marc_recs = MARCReader(fh, to_unicode=True)
    for record in marc_recs:
        mrc_fields = {}
        leader = record.leader
        #  Finds fields/subfield values in record.
        subfield_finder(record, 'number', subfields=['a'], tags=['010'])
        field_finder(record, 'headings', tags=['100', '110', '111', '130'])
        field_finder(record, 'desc', tags=['336', '368', '370', '371', '372', '373'])
        field_finder(record, 'alt_names', tags=['400', '410', '411', '430'])
        field_finder(record, 'see_also', tags=['510', '511', '530'])
        field_finder(record, 'unauthorized_forms', tags=['663', '664', '665', '666'])
        field_finder(record, 'linked_headings', tags=['710', '711'])
        field_finder(record, 'source', tags=['670'])
        field_finder(record, '008', tags=['008'])
        field_finder(record, 'last_updated', tags=['005'])
        mrc_fields['type'] = [leader[6]]
        keys = []
        # Edit & convert values in dictionary.
        for k, v in mrc_fields.items():
            if k == '008':  # Find Lang codes, DtSt and Dates from field 008.
                v = str(v[0])
                type = v[9]
                level = v[33]
                cat_source = v[39]
            elif k == 'last_updated':
                v = str(v[0])
                v = v[:4]
                mrc_fields[k] = v
            elif k == 'number':
                v = str(v[0])
                v = v.replace(" ", "").strip()
                mrc_fields[k] = v

        del mrc_fields['008']
        mrc_fields['type'] = type
        mrc_fields['level'] = level
        mrc_fields['cat_source'] = cat_source
        convert_to_name('type', types_dict)
        convert_to_name('level', level_dict)
        convert_to_name('cat_source', catsource_dict)

        # Converts list values in k,v pair to strings joined by pipes.
        for k, v in mrc_fields.items():
            keys.append(k)
            if isinstance(v, list):
                if len(v) >= 2:
                    v = "|".join(v)
                    mrc_fields[k] = v
                elif len(v) == 1:
                    v = str(v[0])
                    mrc_fields[k] = v
                elif len(v) == 0:
                    v = ''
                    mrc_fields[k] = v
                else:
                    pass
        # Adds dict created by this MARC record to all_fields list.
        all_fields.append(mrc_fields)
        record_count = record_count + 1
        print(record_count)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

with open('marcAuth_'+dt+'.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_fields)
