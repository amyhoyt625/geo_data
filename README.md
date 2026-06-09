# geo_data: Geographic Diversity in SE Research

Replication package for "Geodiversity in ICSA and ICSE Publications"
Amy Hoyt, Tina Jiang, Grace Koo, Rona Liu-Zhong — Northeastern University

This repository contains all code and data needed to reproduce the
bibliometric analysis of author geographic representation at ICSA and
ICSE (2010-2025).


## Requirements

Python 3.8 or higher is required. Install dependencies with:

    pip install -r requirements.txt

Dependencies include:
    requests
    beautifulsoup4
    pycountry
    geopandas
    matplotlib
    pandas


## Repository Structure

    geo_data/
    ├── data/
    │   └── raw/
    │       ├── icsa_affiliations.json
    │       └── icse_affiliations.json
    ├── src/
    │   ├── ingest/
    │   │   ├── fetch_icsa.py
    │   │   └── fetch_icse.py
    │   └── analysis/
    │       ├── add_regions.py
    │       ├── proportions.py
    │       └── top_stats.py
    ├── figures/
    │   ├── geo_map_icsa.png
    │   ├── geo_map_icse.png
    │   ├── icsa_fig_region_line.png
    │   └── icse_fig_region_line.png
    ├── RESULTS.md
    ├── LIMITATIONS.md
    └── PHASE1.md


## Reproducing the Results

The pipeline runs in two stages: data ingestion and analysis.
If you want to skip ingestion and use the already-collected raw data,
start from Step 2.


### Step 1 - Ingest Data (optional, raw data already provided)

Scrape DOIs from DBLP and fetch author affiliation data from OpenAlex.
Note: ingestion takes several hours due to rate limiting delays.
Your email is sent as a User-Agent header to OpenAlex to obtain higher
rate limits. Edit the EMAIL variable at the top of each script before
running.

    python src/ingest/fetch_icsa.py
    python src/ingest/fetch_icse.py

Output is written to:
    data/raw/icsa_affiliations.json
    data/raw/icse_affiliations.json


### Step 2 - Add Region Labels

Map country codes to geographic regions using the lookup table:

    python src/analysis/add_regions.py

This adds a region field to each record based on ISO 3166-1 alpha-2
country codes. The seven regions used are: North America, Western Europe,
Eastern Europe, Asia-Pacific, Latin America, Middle East, and Africa.


### Step 3 - Compute Proportions and Summary Statistics

Generate the regional proportion tables and country/institution rankings:

    python src/analysis/proportions.py
    python src/analysis/top_stats.py

These scripts produce the data underlying Tables I-XII in the paper.


### Step 4 - Generate Figures

Produce the choropleth maps and regional trend line charts:

    python src/analysis/figures.py

Output figures are written to the figures/ directory.


## Raw Data

If you want to inspect the raw data directly without running any scripts:

    data/raw/icsa_affiliations.json — 1,943 author-institution rows
    data/raw/icse_affiliations.json — 13,030 author-institution rows

Each record contains:
    doi           — paper DOI
    year          — publication year
    author        — author display name
    author_pos    — position in author list (1 = first author)
    institution   — institution display name
    country_code  — ISO 3166-1 alpha-2 country code


## Coverage

Match rates between DBLP and OpenAlex were 94.1% for ICSA and 95.9%
for ICSE. Unmatched records were omitted from analysis.


## Notes

French Guiana is excluded from choropleth visualizations. As an overseas
territory of France it inherits all French publication counts, which
produces a misleading visual artifact.

Regional percentages in the proportion tables do not sum to 100% because
internationally co-authored papers are counted in each represented region.
