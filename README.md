## Please see [wiki](https://github.com/mjanowiecki/geoportal/wiki) for more information.

### combineMetadata.py

This script combines metadata for one item from two different CSVs and uploads the combination to Google Sheets using the API. The API must be previously setup to run this script. To match the metadata, the script relies on a "matchingfile" CSV that pairs up an identifier from each CSV with metadata. Then it merges the metadata based on those identifiers. The script expects the two metadata CSVs will have some identically named columns like "title" or "creator", and it adds a suffix to those column names to indicate the source of that metadata.

### convertGeoCSVToGeoJSON.py

This script converts a CSV with metadata to a JSON file that follows the [GeoBlacklight Metadata Elements, Version 1.0](https://github.com/geoblacklight/geoblacklight/wiki/GeoBlacklight-1.0-Metadata-Elements). This script does not edit the majority of information from the CSV, only converts it to JSON. It does, however, reorder the bounding box coordinates from the Klokan Tech Bounding Box tool, and calculates the center of the box. It also add backslashes to the reference elements and checks for curly quotes.  

Enter the CSV column names as the third parameter of either function addToDict or addListToDict, depending on whether there are multiple entries in that column. If there are multiple entries in a column, separate entries with "|". These will automatically be separated by the addListToDict function.

### extractDspaceToCSV.py

This script selects metadata previously pulled from DSpace and re-organizes it for future use as [GeoBlacklight Metadata](https://github.com/geoblacklight/geoblacklight/wiki/GeoBlacklight-1.0-Metadata-Elements). The script does this by checking for information from select DSpace elements for importation into a new CSV. Much of this script is specific to Hopkins' implementation of DSpace.

### extractMARCToGeoCSV.py

This script uses [pymarc](https://pypi.org/project/pymarc/) to find fields relevant to GeoBlacklight metadata from MARC records. It also uses four dictionaries to translate certain MARC codes into written strings.

### matchBitstreamsIntoPairs.py

This script ingests a CSV that lists DSpace bitstreams by item handle, and matches access and preservation files of the same image together (for instance, map001.jpg and map001.tif) by name. These are put into a new CSV as a list in a column called 'bitstreams' and organized by handle. If no matches are found for a bitstream, it is added to the CSV as a single item in a list.

### matchDspaceAndMARCRecords.py

This script attempts to match DSpace records and MARC records first by a preferred identifier, then by a less preferred identifier, and finally tries to match the records by fuzzing matching their titles. A new CSV is made and categorizes the results as exact, probable, or no matches.


### dictionaries
|File                   | Information                                                             |
|-----------------------|-------------------------------------------------------------------------|
|gacs_code.csv          | List of codes and place names from MARC Code List for Geographic Areas.
|iso_19115topics.csv    | List of ISO 19115 topics and their URIs.                                
|iso_lang.csv           | List of ISO language codes from ISO 639-1 or ISO 639-2 and the name of the language in English. The shortest of the ISO codes available for that language was chosen.
|lcgft_cartographic.csv | List of Library of Congress Genre/Form Terms found under the term "Cartographic materials." Each term is matched with its URI.
|marc_006types.csv      | List of type names and their codes used in the 006 field of MARC records.
|marc_datetypes.csv     | List of date type names and their codes used in the DtSt field of MARC records.
|marc_lang.csv          | List of language names and their codes from the MARC Code List for Languages.
