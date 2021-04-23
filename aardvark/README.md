## Instructions: How to run convertCSVToAaardvarkJSON.py

1. Create metadata in a CSV with the column headers listed in `reqColumns` and `optColumns` [aardvarkValidator.py](/aardvarkValidator.py). You can also make a spreadsheet with these headers by downloading [example.xlsx](/example.xlsx) from this folder (just delete row 1 and save as a UTF-8 CSV before using the script).
   - Seperate multiple values with a pipe `|`. 
   - For `boundingBox`, structure your cooridnates as `West, South, East, North`.
   - For `dateRange`, structure your range as `YYYY-YYYY`.
   - For `references`, structure your references as `referenceURI,URI|referenceURI,URI`.
2. Download `aardvark` folder
3. Place your metadata CSV in the `aardvark` folder on your computer
4. Run [convertCSVToAardvarkJSON.py](/convvertCSVToAardvarkJSON.py) from `aardvark` folder
   - Script delivers warning if your column headers aren't named correctly
   - Script validates `access`, `language` ,  and `format`against controlled values contained in `aardvark_controlled.csv`
   - Formats `locn_geometry`, `dct_references_s` according to aardvark schema requirements
   - Adds `gbl_mdVersion_s`, `schema_provider_s`, `gbl_mdModified_dt` and `dcat_centroid_ss` automatically according to inputs and default values
   - Creates CSV log for each item, giving information about errors, success of JSON creation, and JSON validation status