# geoportal

## convertCSVToJSON.py

This script converts a CSV with metadata to a JSON file that follows the geoblacklight-schema. This script does not edit the data in the CSV, only converts it to JSON. Enter the CSV column names as the third parameter of either function addToDict or addListToDict, depending on whether there are multiple entries in that column. If there are multiple entries in a column, separate entries with "|". These will automatically be separated by the addListToDict function.

## dspaceRemediation.py

This script selects metadata previously pulled from DSpace and re-organizes it for future use as geoblacklight metadata. The script does this by checking for information from select DSpace elements for importation into a new CSV. Much of this script is specific to Hopkins' implementation of DSpace.

## combineMetadata.py

This script combines metadata for one item from two different CSVs and uploads the combination to Google Sheets using the API. The API must be previously setup to running this script. To match the metadata, the script relies on a "matchingfile" CSV that pairs up an identifier from each CSV with metadata. Then it merges the metadata based on those identifiers. The script expects the two metadata CSVs will have some identically named columns like "title" or "creator", and it adds a suffix to those column names to inidcate the source of that metadata.

## matchRecords.py

This script matches metadata records from two CSVs first by a preferred identifier, then by a less preferred identifier, and finally tries to match metadata records by fuzzing matching their titles. When the metadata records are matched, a new CSV is made with the results of the matching.

## extractMARCToCSV.py

This script uses pymarc to find fields relevant to geoblacklight metadata from MARC records. It also uses four dictionaries to translate certain MARC codes into written strings.

## dictionaries
|File                   | Information                                                             |
|-----------------------|-------------------------------------------------------------------------|
|gacs_code.csv          | List of codes and place names from MARC Code List for Geographic Areas.
|iso_19115topics.csv    | List of ISO 19115 topics and their URIs.                                
|iso_lang.csv           | List of ISO language codes from ISO 639-1 or ISO 639-2 and the name of the language in English. The shortest of the ISO codes available for that language was chosen.
|lcgft_cartographic.csv | List of Library of Congress Genre/Form Terms found under the term "Cartographic materials." Each term is matched with its URI.
|marc_006types.csv      | List of type names and their codes used in the 006 field of MARC records.
|marc_datetypes.csv     | List of date type names and their codes used in the DtSt field of MARC records.
|marc_lang.csv          | List of language names and their codes from the MARC Code List for Languages.
