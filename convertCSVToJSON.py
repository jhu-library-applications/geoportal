import csv
import json
import argparse
from jsonschema import validate
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


def addToDict(json_file, key, value):
    try:
        value = row[value]
        value = value.strip()
        json_file[key] = value
    except KeyError:
        pass


def addListToDict(json_file, key, value):
    try:
        value = row[value]
        value = value.strip()
        value = value.split('|')
        json_file[key] = value
    except KeyError:
        pass


def addDictToDict(json_file, key, value):
    try:
        value = row[value]
        value = value.strip()
        value = '{'+value+'}'
        json_file[key] = value
    except KeyError:
        pass


with open(filename) as geoMetadata:
    geoMetadata = csv.DictReader(geoMetadata)
    for row in geoMetadata:
        json_file = {}
        identifier = row['identifier']
        addToDict(json_file, 'dc_identifier_s', 'identifier')
        addToDict(json_file, 'dc_rights_s', 'rights')
        addToDict(json_file, 'dc_title_s', 'title')
        addToDict(json_file, 'layer_slug_s', 'layer_slug')
        addToDict(json_file, 'solr_geom', 'solr_geom')
        addListToDict(json_file, 'dc_creator_sm', 'creators')
        addToDict(json_file, 'dc_description_s', 'description')
        addToDict(json_file, 'dc_format_s', 'format')
        addListToDict(json_file, 'dc_language_sm', 'language')
        addListToDict(json_file, 'dc_publisher_sm', 'publisher')
        addListToDict(json_file, 'dc_source_sm', 'source')
        addListToDict(json_file, 'dc_subject_sm', 'subject')
        addToDict(json_file, 'dc_type_s', 'type')
        addListToDict(json_file, 'dct_isPartOf_sm', 'isPartOf')
        addToDict(json_file, 'dc_type_s', 'type')
        addDictToDict(json_file, 'dct_references_s', 'references')
        addListToDict(json_file, 'dct_spatial_sm', 'spatial')
        addListToDict(json_file, 'dct_temporal_sm', 'temporal')
        addToDict(json_file, 'layer_geom_type_s', 'geom_type')
        addToDict(json_file, 'layer_id_s', 'layer_id')
        addToDict(json_file, 'layer_modified_dt', 'layer_modified')
        addToDict(json_file, 'suppressed_b', 'suppressed')
        json_file['dct_provenance_s'] = 'Hopkins'
        json_file['geoblacklight_version'] = '1.0'
        print(json_file)
        date_time = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        filename = identifier.replace('http://hopkinsgeoportal/', '')
        with open(filename+date_time+'.json', 'w') as fp:
            json.dump(json_file, fp)

        with open(filename+date_time+'.json', 'r') as results:
            results = json.load(results)
            with open('geoblacklight-schema.json', 'r') as schema:
                schema = json.load(schema)
                validate(results, schema)
