## Please see [wiki](https://github.com/mjanowiecki/geoportal/wiki) for more information.

### addGeoNames.py

This scripts grabs geographic subject headings from a CSV and converts them to GeoNames hierarchal headings using the functions `convertFASTToGeoNames` and `convertLCNAFToGeoNames` from `convertGeoNamesFromLCNAF.py`

### cleanUpGeoCSV.py

Working with the CSV generated from `extractMARCToGeoCSV.py`, this script cleans up punctuation of specific fields, cleans up author, contributor, and publisher names, and adds additional fields with default values. To clean up names, this script uses functions from `verifyHeadings.py` to grab the authorized name label from the Library of Congress Name Authority File if available.

### convertGeoCSVToGeoJSON.py

This script converts a CSV with metadata to a JSON file that follows the [GeoBlacklight Metadata Elements, Version 1.0](https://github.com/geoblacklight/geoblacklight/wiki/GeoBlacklight-1.0-Metadata-Elements). This script does not edit the majority of metadata from the CSV, only converts it to JSON format. It does, however, reorder the bounding box coordinates from the Klokan Tech Bounding Box tool, and calculates the center of the box. It also add backslashes to the reference elements and checks for curly quotes.  

Enter the CSV column names as the third parameter of either function `addToDict` or `addListToDict`, depending on whether there are multiple entries in that column. If there are multiple entries in a column, separate entries with "|". These will automatically be separated by the `addListToDict` function.

### convertGeoNamesFromLCNAF.py

This script uses `BeautifulSoup` and `rdflib` libraries to read LCNAF and FAST records, and find the corresponding GeoNames heading in the linked data. The function `getParents()` finds the parent (and grandparent if applicable) of the geographic location and builds an hierarchal name from their labels.

### extractMARCToGeoCSV.py

This script uses [pymarc](https://pypi.org/project/pymarc/) to find fields relevant to GeoBlacklight metadata from MARC records. It also uses four dictionaries to translate certain MARC codes into written strings.

### verifyHeadings.py

This script `BeautifulSoup` and `rdflib` libraries to read LCNAF and FAST records, and find the authorized name label from an already available URI or from a search based on the name string.

### dictionaries
|File                   | Information                                                             |
|:-----------------------|:-------------------------------------------------------------------------|
|gacs_code.csv          | List of codes and place names from MARC Code List for Geographic Areas.
|iso_19115topics.csv    | List of ISO 19115 topics and their URIs.                                
|iso_lang.csv           | List of ISO language codes from ISO 639-1 or ISO 639-2 and the name of the language in English. The shortest of the ISO codes available for that language was chosen.
|lcgft_cartographic.csv | List of Library of Congress Genre/Form Terms found under the term "Cartographic materials." Each term is matched with its URI.
|marc_007categoryMaterial.csv| List of record type names and their codes used in the 007 field of MARC record.
|marc_catsourceAuthorities.csv| List of cataloging source names and their codes used in the 008 field.
|marc_datetypes.csv     | List of date type names and their codes used in the DtSt field of MARC records.
|marc_lang.csv          | List of language names and their codes from the MARC Code List for Languages.
|marc_levelAuthorities.csv| List of authority level names and their codes used in the 008 field for authority records.
|marc_typeAuthorities.csv| List of kind of record names and their codes used in the 008 field for authority records.
