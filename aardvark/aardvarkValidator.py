import pandas as pd

reqColumns = ['geo_id', 'title', 'resourceClass', 'access']
optColumns = ['local_id', 'description', 'language', 'creator', 'publisher',
              'subject', 'temporal', 'indexYear', 'dateIssued', 'spatial',
              'boundingBox', 'source', 'format', 'wxs_id', 'references',
              'type', 'isPartOf', 'resourceType', 'suppressed', 'memberOf',
              'keyword', 'altTitle', 'theme', 'dateRange', 'relation',
              'isVersion', 'replaces', 'isReplaced', 'copyright',
              'rightsHolder', 'license', 'fileSize', 'geoRef']
allColumns = reqColumns + optColumns
builtIntoScript = ['provider', 'version', 'dcat_centroid_ss', 'mdModified']


df = pd.read_csv('aardvark_controlled.csv')


def v_validate(columnName, value):
    columnList = list(df[columnName])
    if value in columnList:
        response = True
        return response
    else:
        response = False
        return response
