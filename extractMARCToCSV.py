from pymarc import MARCReader
import csv
import argparse
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
#  Import gacs codes used in 043 fields.
with open('gacs_code.csv') as gacs:
    gacs = csv.DictReader(gacs)
    for row in gacs:
        code = row['code']
        location = row['location']
        gacs_dict[code] = location
# Import type codes used in leader 06.
with open('types.csv') as type_codes:
    type_codes = csv.DictReader(type_codes)
    for row in type_codes:
        code = row['Type']
        name = row['Name']
        types_dict[code] = name

# Creates key/value pair in dict where key = field_name, value = values of MARC tags in record.


def field_finder(record, field_name, tags):
    field = record.get_fields(*tags)
    field_list = []
    for my_field in field:
        my_field = my_field.format_field()
        field_list.append(my_field)
    mrc_fields[field_name] = field_list

# Creates key/value pair in dict where key = field_name, value = values of specific subfield in MARC tag in record.


def subfield_finder(record, field_name, subfields, tags):
    field = record.get_fields(*tags)
    field_list = []
    for my_field in field:
        my_field = my_field.get_subfields(*subfields)
        for field in my_field:
            field_list.append(field)
    mrc_fields[field_name] = field_list


all_fields = []

with open(filename, 'rb') as fh:
    marc_recs = MARCReader(fh, to_unicode=True, force_utf8=True)
    for record in marc_recs:
        mrc_fields = {}
        leader = record.leader
        subfield_finder(record, 'bib', subfields=['a'], tags=['910'])
        subfield_finder(record, 'links', subfields=['u'], tags=['856'])
        field_finder(record, 'authors', tags=['100', '110', '111', '130'])
        field_finder(record, 'contributors',  tags=['700', '710', '711', '730'])
        field_finder(record, 'subjects', tags=['600', '610', '650', '651'])
        field_finder(record, 'descs', tags=['500', '520'])
        field_finder(record, 'lang', tags=['008'])
        subfield_finder(record, 'dates', subfields=['c'], tags=['264', '260'])
        subfield_finder(record, 'titles', subfields=['a', 'b'], tags=['245', '246'])
        subfield_finder(record, 'geos', subfields=['c'], tags=['255'])
        subfield_finder(record, 'locs', subfields=['a'], tags=['043'])
        mrc_fields['type'] = leader[6]
        keys = []

        #  Converts 043 codes to place names.
        for k, v in mrc_fields.items():
            if k == 'locs':
                for count, loc in enumerate(v):
                    for key, value in gacs_dict.items():
                        if loc == key:
                            v[count] = value
            elif k == 'lang':  # Find Lang code.
                v = str(v[0])
                v = v[35:38]
                v = [v]
                mrc_fields[k] = v
            elif k == 'type':  # Convert type code to name.
                for key, value in types_dict.items():
                    if v == key:
                        v = [value]
                        mrc_fields['type'] = v

        # Converts values in k,v pair to strings joined by pipes.
        for k, v in mrc_fields.items():
            keys.append(k)
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
