# Harmony Map Maker

## Installation

python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt

Rscript -e 'install.packages(c("data.table", "magrittr", "tidygeocoder"), repos="https://cloud.r-project.org")'


## Steps
- Download Harmony Airtable data file to directory, leave name as is.
- Run locations.R to add new locations to locations.tsv and add predicted lat/long. Will create locations.tsv if doesn't exist
- Open locations.tsv. For any entries without final coords (new entries), enter them yourself. Most will be correct in the predicted columns and you can copy paste across. Export to same file.
- Run map.py. Must be run within hours of downloading Harmony data as img url's expire.
