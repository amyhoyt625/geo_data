# Phase 1: Data Collection and Setup


## Datasets Targeted

Two conference series were ingested:

ICSA (International Conference on Software Architecture), which also
covers its predecessor names WICSA (Working IEEE/IFIP Conference on
Software Architecture) and ECSA (European Conference on Software
Architecture), spanning 2010-2025.

ICSE (International Conference on Software Engineering), spanning
2010-2025.

Data was collected from two sources:

DBLP (dblp.org) - used to retrieve paper-level DOIs for each conference
year. DBLP was chosen for its clean, consistently structured conference
pages and stable URL patterns.

OpenAlex (openalex.org) - used to retrieve author affiliation metadata
per DOI, including institution names and ISO 3166-1 alpha-2 country codes.
OpenAlex performs institution-to-country geocoding internally, eliminating
the need for a separate resolution step.


## Data Collection Pipeline

Collection was done in two stages:

Stage 1 - DBLP scraping: Conference pages were scraped using
BeautifulSoup to extract paper titles, author names, publication years,
and DOIs for each year of each conference series.

Stage 2 - OpenAlex lookup: Each DOI was submitted to the OpenAlex Works
API, which returned structured authorship records including institutional
affiliation names and country codes.

The Northeastern University email address was included in the OpenAlex
User-Agent header to obtain higher API rate limits. DBLP rate-limiting
was handled with a 2-second delay between requests and a retry wrapper
with a 30-second wait on failure.


## Cleaning Activities

Country codes were provided in ISO 3166-1 alpha-2 format and converted
to alpha-3 using the pycountry library for compatibility with geographic
visualization tools.

French Guiana was identified as an outlier during visualization. As an
overseas territory of France, it inherited all French-affiliated
publication counts and was excluded from the final choropleth map.

Records that could not be matched between DBLP and OpenAlex were omitted
from analysis. Final coverage rates were 94.1% for ICSA and 95.9% for
ICSE.

Author affiliations were mapped to seven geographic regions using a
manually verified country-to-region lookup table: North America, Western
Europe, Eastern Europe, Asia-Pacific, Latin America, Middle East, and
Africa.


## Data Location

Raw data files:
    data/raw/icsa_affiliations.json
    data/raw/icse_affiliations.json

Ingestion scripts:
    src/ingest/fetch_icsa.py
    src/ingest/fetch_icse.py

Region mapping:
    src/analysis/add_regions.py


## Sample Code

Fetching author affiliation data from OpenAlex for a single DOI:

    import requests
    import time

    EMAIL = "hoyt.a@northeastern.edu"
    HEADERS = {"User-Agent": f"mailto:{EMAIL}"}

    def fetch_affiliations(doi):
        url = f"https://api.openalex.org/works/doi:{doi}"
        response = requests.get(url, headers=HEADERS)
        if response.status_code != 200:
            return None
        data = response.json()
        rows = []
        for authorship in data.get("authorships", []):
            for institution in authorship.get("institutions", []):
                rows.append({
                    "doi": doi,
                    "author": authorship["author"]["display_name"],
                    "institution": institution.get("display_name"),
                    "country_code": institution.get("country_code")
                })
        return rows

    time.sleep(2.0)  # respect rate limits between requests


## Repository

https://github.com/amyhoyt625/geo_data
