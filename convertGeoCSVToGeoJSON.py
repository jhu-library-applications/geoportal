import csv
import json
import argparse
from jsonschema import validate
from datetime import datetime
import uuid

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-p', '--prov')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.prov:
    prov = args.prov
else:
    prov = input('Enter provenance information: ')


def fixGeom(json_file, key, value):
    try:
        value = row[value]
        value = value.split(',')
        # Converts (West, South, East, North) --> (West, East, North, South)
        if len(value) == 4:
            west = value[0]
            south = value[1]
            east = value[2]
            north = value[3]
            centerlat = (float(north)+float(south))/2
            centerlong = (float(east)+float(west))/2
            json_file[key] = 'ENVELOPE('+west+','+east+','+north+','+south+')'
            json_file['b1g_centroid_ss'] = str(centerlat)+','+str(centerlong)
        # If the bounding box missing coordinates, write values as null.
        else:
            json_file[key] = 'NULL'
            json_file['b1g_centroid_ss'] = 'NULL'
    except KeyError:
        pass


def fixRef(json_file, key, value):
    try:
        value = row[value]
        if value:
            value = value.replace(u'\u2018', "'").replace(u'\u2019', "'")
            value = value.replace("'h", "\"h")
            value = value.replace("':", "\":")
            value = value.replace("',", "\",")
            value = value.replace("'}", "\"}")
            value = str(value)
            json_file[key] = value
    except KeyError:
        pass


def addToDict(json_file, key, value):
    try:
        value = row[value]
        if value:
            value = value.strip()
            json_file[key] = value
    except KeyError:
        pass


def addToDictInt(json_file, key, value):
    try:
        value = row[value]
        if value:
            value = int(value)
            json_file[key] = value
    except KeyError:
        pass


def addListToDict(json_file, key, value):
    try:
        value = row[value]
        if value:
            value = value.strip()
            value = value.split('|')
            json_file[key] = value
    except KeyError:
        pass


def addIdentifierAndSlug(row):
    id = row.get('identifier')
    if id is None:
        id = uuid.uuid4()
        json_file['dc_identifier_s'] = id
        json_file['layer_slug_s'] = id
    else:
        addToDict(json_file, 'dc_identifier_s', 'identifier')
        addToDict(json_file, 'layer_slug_s', 'layer_slug')
    return id


with open(filename) as geoMetadata:
    geoMetadata = csv.DictReader(geoMetadata)
    for row in geoMetadata:
        json_file = {}
        identifier = addIdentifierAndSlug()
        addToDict('dc_rights_s', 'rights')
        addToDict(json_file, 'dc_title_s', 'title')
        fixGeom(json_file, 'solr_geom', 'bounding_box')
        addToDictInt(json_file, 'solr_year_i', 'solr_year')
        addToDict(json_file, 'dct_issued_s', 'date_issued')
        addListToDict(json_file, 'dc_creator_sm', 'creators')
        addToDict(json_file, 'dc_description_s', 'description')
        addToDict(json_file, 'dc_format_s', 'format')
        addListToDict(json_file, 'dc_language_sm', 'language')
        addListToDict(json_file, 'dc_publisher_sm', 'publisher')
        addListToDict(json_file, 'dc_source_sm', 'source')
        addListToDict(json_file, 'dc_subject_sm', 'subject')
        addToDict(json_file, 'dc_type_s', 'type')
        addListToDict(json_file, 'dct_isPartOf_sm', 'isPartOf')
        fixRef(json_file, 'dct_references_s', 'references')
        addListToDict(json_file, 'dct_spatial_sm', 'spatial')
        addListToDict(json_file, 'dct_temporal_sm', 'temporal')
        addToDict(json_file, 'layer_geom_type_s', 'geom_type')
        addToDict(json_file, 'layer_id_s', 'layer_id')
        addToDict(json_file, 'layer_modified_dt', 'layer_modified')
        addToDict(json_file, 'suppressed_b', 'suppressed')
        json_file['dct_provenance_s'] = prov
        json_file['geoblacklight_version'] = '1.0'
        dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        c_filename = identifier+'_'+dt+'.json'
        with open(c_filename, 'w') as fp:
            json.dump(json_file, fp)

        with open(c_filename, 'r') as results:
            results = json.load(results)
            with open('geoblacklight-schema.json', 'r') as schema:
                schema = json.load(schema)
                validate(results, schema)
