from pymarc import MARCReader
import csv
import argparse
import re
from sheetFeeder import dataSheet

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.mrc\'): ')

gacs_dict = {}
types_dict = {}
datetypes_dict = {}
lang_dict = {}


def createDict(csvname, column1, column2, dictname):
    with open(csvname) as codes:
        codes = csv.DictReader(codes)
        for row in codes:
            code = row[column1]
            name = row[column2]
            dictname[code] = name


#  Import gacs codes used in 043 fields.
createDict('gacs_code.csv', 'code', 'location', gacs_dict)
#  Import type codes used in leader 006.
createDict('types.csv', 'Type', 'Name', types_dict)
#  Import date type codes used in leader 008.
createDict('date_types.csv', 'Type', 'Name', datetypes_dict)
createDict('marc_lang.csv', 'Code', 'Name', lang_dict)


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
            for count, item in enumerate(v):
                print(v)
                for key, value in dictname.items():
                    if item == key:
                        v[count] = value


all_fields = []

with open(filename, 'rb') as fh:
    marc_recs = MARCReader(fh, to_unicode=True, force_utf8=True)
    for record in marc_recs:
        print(record)
        mrc_fields = {}
        leader = record.leader
        #  Finds fields/subfield values in record.
        subfield_finder(record, 'bib', subfields=['a'], tags=['910'])
        subfield_finder(record, 'oclc', subfields=['a'], tags=['035'])
        subfield_finder(record, 'links', subfields=['u'], tags=['856'])
        field_finder(record, 'authors', tags=['100', '110', '111', '130'])
        field_finder(record, 'contributors',  tags=['700', '710', '711', '730'])
        subfield_finder(record, 'publisher', subfields=['b'], tags=['260', '264'])
        field_finder(record, 'subjects', tags=['600', '610', '650', '651'])
        field_finder(record, 'descs', tags=['500', '520'])
        field_finder(record, '008', tags=['008'])
        subfield_finder(record, 'title', subfields=['a', 'b'], tags=['245', '246'])
        subfield_finder(record, 'alt_title', subfields=['a', 'b'], tags=['246'])
        subfield_finder(record, 'scales', subfields=['a', 'b', 'c'], tags=['034'])
        subfield_finder(record, 'coord', subfields=['d', 'e', 'f', 'g'], tags=['034'])
        subfield_finder(record, 'cdates', subfields=['x', 'y'], tags=['034'])
        subfield_finder(record, 'geos', subfields=['c'], tags=['255'])
        subfield_finder(record, 'locs', subfields=['a'], tags=['043'])
        mrc_fields['type'] = [leader[6]]
        keys = []
        # Edit & convert values in dictionary.
        for k, v in mrc_fields.items():
            if k == '008':  # Find Lang codes, DtSt and Dates from field 008.
                v = str(v[0])
                datetype = [v[6]]
                date1 = v[7:11].strip()
                date2 = v[11:15].strip()
                lang = [v[35:38]]
            elif k == 'oclc':  # Finds only oclc number, deleting prefixes.
                oclc_list = []
                for item in v:
                    item = str(item)
                    oclc_num = re.search(r'([0-9]+)', item)
                    if oclc_num:
                        oclc_num = oclc_num.group(1)
                        if oclc_num not in oclc_list:
                            if oclc_num != mrc_fields['bib'][0]:
                                oclc_list.append(oclc_num)
                v = oclc_list
                mrc_fields[k] = v

        del mrc_fields['008']
        mrc_fields['datetype'] = datetype
        mrc_fields['date1'] = date1
        mrc_fields['date2'] = date2
        mrc_fields['lang'] = lang
        convert_to_name('datetype', datetypes_dict)
        convert_to_name('locs', gacs_dict)
        convert_to_name('type', types_dict)
        convert_to_name('lang', lang_dict)

        # Converts list values in k,v pair to strings joined by pipes.
        for k, v in mrc_fields.items():
            keys.append(k)
            if isinstance(v, list):
                if len(v) > 2:
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

print(all_fields)
with open('marc.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(all_fields)

# my_sheet = dataSheet('13x9Rke5v_zznRSaxFxqu_yoOWsvd4p0GmIN2-uI3NhI', 'Sheet1!A:Z')
# my_sheet.importCSV('marc.csv', quote='ALL')
