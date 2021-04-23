import json
import argparse
import jsonschema
from jsonschema import validate
from datetime import datetime
import pandas as pd
import re
import aardvarkValidator as aardvark

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-p', '--prov')
parser.add_argument('-d', '--directory')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.prov:
    prov = args.prov
else:
    prov = input('Enter provider information: ')

if args.directory:
    directory = args.directory
else:
    directory = input('Enter directory where JSON files will go: ')


def validate_values(value, columnName):
    valid_results = True
    if isinstance(value, str):
        valueList = [value]
    else:
        valueList = value
    for value in valueList:
        response = aardvark.v_validate(columnName, value)
        if response is True:
            pass
        else:
            valid_results = False
            if item_log.get(columnName):
                oldValue = item_log.get(columnName)
                newValue = oldValue+'|'+value
                item_log[columnName] = newValue
            else:
                item_log[columnName] = value
    return valid_results


def addGeomToDict(key, columnName):
    valid_results = True
    value = row.get(columnName)
    if pd.notna(value):
        value = value.split(',')
        # Converts West, South, East, North --> (West, East, North, South)
        if len(value) == 4:
            west = value[0]
            south = value[1]
            east = value[2]
            north = value[3]
            centerlat = (float(north)+float(south))/2
            centerlong = (float(east)+float(west))/2
            json_file[key] = 'ENVELOPE('+west+','+east+','+north+','+south+')'
            json_file['dcat_centroid_ss'] = str(centerlat)+','+str(centerlong)
        else:
            valid_results = False
            item_log[columnName] = value
    else:
        pass


def addRefToDict(key, columnName):
    valid_results = True
    value = row.get(columnName)
    # Format of values in spreadsheet --> referenceURI,URI|referenceURI,URI
    if pd.notna(value):
        value = value.replace(' ', '')
        valueList = value.split('|')
        value_dict = {}
        for v in valueList:
            v1 = v.split(',')
            value_dict[v1[0]] = v1[1]
        keys = list(value_dict.keys())
        valid_results = validate_values(keys, columnName)
        if valid_results:
            updated_value = json.dumps(value_dict)
            json_file[key] = str(updated_value)
        else:
            valid_results = False
            item_log[columnName] = value
    else:
        pass


def addToDict(key, columnName, validate=False):
    value = row.get(columnName)
    if pd.notna(value):
        value = value.strip()
        if validate:
            valid_results = validate_values(value, columnName)
            if valid_results:
                json_file[key] = value
    else:
        pass


def addIntToDict(key, columnName):
    valid_results = True
    value = row.get(columnName)
    if pd.notna(value):
        value = str(int(value))
        print(value)
        match = re.search(r'\d\d\d\d', value)
        if match:
            value = int(value)
            json_file[key] = value
        else:
            valid_results = False
            item_log[columnName] = value
    else:
        pass


def addBoolToDict(key, columnName):
    value = row.get(columnName)
    if pd.notna(value):
        if isinstance(value, bool):
            value = value
            json_file[key] = value
        else:
            item_log[columnName] = 'Must be boolean value'
    else:
        pass


def addListToDict(key, columnName, validate=False):
    value = row.get(columnName)
    if pd.notna(value):
        value = value.strip()
        value = value.split('|')
        if validate:
            valid_results = validate_values(value, columnName)
            if valid_results:
                json_file[key] = value
        else:
            json_file[key] = value
    else:
        pass


def addRangeToDict(key, columnName):
    value = row.get(columnName)
    if pd.notna(value):
        value = value.strip()
        # Finds string matching pattern YYYY TO YYYY
        match = re.search(r'^\d\d\d\d\-\d\d\d\d$', value)
        if match:
            value = ("["+value+"]").replace('-', ' TO ')
            json_file[key] = [value]
        else:
            item_log[columnName] = value
    else:
        pass


# Load spreadsheet with metadata.
geoMetadata = pd.read_csv(filename)
columns = geoMetadata.columns.tolist()

# Confiirm there are no duplicated columns in spreadsheet.
if columns != set(columns):
    duplicated = [item for item in set(columns) if item not in columns]
    if bool(duplicated):
        print('Columns are duplicated: '+str(duplicated))

# Confirm required columns are in spreadsheet.
if aardvark.reqColumns not in columns:
    reqmissing = set(aardvark.reqColumns) - set(columns)
    for missing in reqmissing:
        print('Warning: missing required column: '+missing)

# Print any columns not used in script.
notElement = set(columns) - set(aardvark.allColumns)
if bool(notElement):
    for column in notElement:
        print('Warning: column \"'+column+'\" not in script.')


allItems = []
# Create JSON file for each row in spreadsheet.
for index, row in geoMetadata.iterrows():
    # Create XMLSchema dateTime format
    dt = datetime.now().isoformat()
    dt = dt[:-7]+'Z'
    item_log = {}
    json_file = {}
    # Required fields
    id = row['geo_id']
    json_file['id'] = id
    json_file['dct_title_s'] = row['title']
    json_file['gbl_mdVersion_s'] = 'Aardvark'
    addListToDict('gbl_resourceClass_sm', 'resourceClass')
    addToDict('dct_accessRights_s', 'access', validate=True)

    # Optional: agent fields.
    addListToDict('dct_creator_sm', 'creator')
    addListToDict('dct_publisher_sm', 'publisher')
    json_file['schema_provider_s'] = prov

    # Optional: dates fields.
    addListToDict('dct_temporal_sm', 'temporal')
    addIntToDict('gbl_indexYear_i', 'indexYear')
    addToDict('dct_issued_s', 'dateIssued')
    json_file['gbl_mdModified_dt'] = dt
    addRangeToDict('gbl_dateRange_drsim', 'dateRange')

    # Optional: description.
    addListToDict('dct_description_sm', 'description')
    addListToDict('dct_language_sm', 'language', validate=True)
    addListToDict('dct_alternative_sm', 'altTitle')
    addListToDict('gbl_resourceType_sm', 'resourceType')
    addListToDict('dct_subject_sm', 'subject')
    addListToDict('dct_spatial_sm', 'spatial')
    addListToDict('dcat_keyword_sm', 'keyword')
    addListToDict('dcat_theme_sm', 'theme')
    addGeomToDict('locn_geometry', 'boundingBox')

    # Optional: external_info.
    addToDict('gbl_wxsIdentifier_s', 'wxs_id')
    addRefToDict('dct_references_s', 'references')
    addListToDict('dct_identifier_sm', 'local_id')

    # Optional: relators.
    addListToDict('pcdm_memberOf_sm', 'memberOf')
    addListToDict('dct_source_sm', 'source')
    addListToDict('dct_relation_sm', 'relation')
    addListToDict('dct_isPartOf_sm', 'isPartOf')
    addListToDict('dct_isVersionOf_sm', 'isVersion')
    addListToDict('dct_replaces_sm', 'replaces')
    addListToDict('dct_isReplacedBy_sm', 'isReplaced')

    # Optional: rights.
    addListToDict('dct_rights_sm', 'copyright')
    addListToDict('dct_rightsHolder_sm', 'rightsHolder')
    addListToDict('dct_license_sm', 'license')

    # Optional: file information.
    addToDict('gbl_fileSize_s', 'fileSize')
    addBoolToDict('gbl_georeferenced_b', 'geoRef')
    addToDict('dct_format_s', 'format', validate=True)

    # Optional: other.
    addBoolToDict('gbl_suppressed_b', 'suppressed')

    # If item_log has found errors in metadata, don't make JSON file.
    if bool(item_log) is True:
        item_log['id'] = id
        item_log['aardvark_valid'] = False
        item_log['json_created'] = False
        allItems.append(item_log)
        continue
    # If no errors, make JSON file.
    else:
        item_log['id'] = id
        item_log['aardvark_valid'] = True
        # Create datetime stamp for filenaming.
        # Create JSON file.
        c_filename = id+'.json'
        full_path = directory+'/'+c_filename
        with open(full_path, 'w') as fp:
            json.dump(json_file, fp)
            item_log['json_created'] = c_filename
        # See if JSON file is valid.
        with open(full_path, 'r') as results:
            results = json.load(results)
            with open('schema-aardvark.json', 'r') as schema:
                schema = json.load(schema)
                try:
                    validate(results, schema)
                    item_log['json_valid'] = True
                except jsonschema.ValidationError as err:
                    error = err.message
                    print(error)
                    item_log['json_valid'] = error
        allItems.append(item_log)


log = pd.DataFrame.from_dict(allItems)
print(log)

errors = []
success = []
for index, row in log.iterrows():
    json_valid = row['json_valid']
    aardvark_valid = row['aardvark_valid']
    if (json_valid is not True) or (aardvark_valid is False):
        id = row['id']
        errors.append(id)
    else:
        success.append(id)
tErrors = len(errors)
tSuccess = len(success)
print('Errors: '+str(tErrors))
print('Success:'+str(tSuccess))

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
log.to_csv('logOfJSONGeneration_'+dt+'.csv', index=False)
