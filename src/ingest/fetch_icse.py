import requests       # for making HTTP requests to DBLP and OpenAlex
import time           # for sleep delays between API calls
import json           # for saving output as JSON
from bs4 import BeautifulSoup  # for parsing DBLP HTML pages


def scrape_dblp_page(url):
    """
    Helper function — fetches a single DBLP page and returns
    a list of IEEE DOIs found on it.
    Used by get_dois_for_year_icse to avoid repeating the same
    scraping logic for simple vs volume-split years.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return None  # None means page doesn't exist, [] means page exists but no DOIs
    
    soup = BeautifulSoup(response.text, "html.parser")
    dois = []
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        # ICSE is published by IEEE (10.1109) and ACM (10.1145)
        # we include both since ICSE switched publishers over the years
        if "doi.org/10.1109" in href or "doi.org/10.1145" in href:
            doi = href.replace("https://doi.org/", "")
            dois.append(doi)
    
    return list(set(dois))  # deduplicate


def get_dois_for_year_icse(year):
    """
    Scrapes DBLP for all ICSE papers in a given year.
    
    ICSE has two URL patterns:
    - Simple: icse{year}.html — used for most years (2011-2014, 2016-2024)
    - Volume split: icse{year}-1.html + icse{year}-2.html — used for 2010, 2015
    
    We try the simple URL first, then fall back to volume split.
    For volume split years we scrape both volumes and combine the DOIs.
    """
    # try simple URL first
    simple_url = f"https://dblp.org/db/conf/icse/icse{year}.html"
    time.sleep(0.5)  # be polite to DBLP — more conservative delay than OpenAlex
    dois = scrape_dblp_page(simple_url)
    
    if dois is not None:
        # simple URL worked
        print(f"ICSE {year}: found {len(dois)} DOIs")
        return dois
    
    # simple URL was 404 — try volume split
    all_dois = []
    for vol in [1, 2, 3]:  # try up to 3 volumes in case there are more
        vol_url = f"https://dblp.org/db/conf/icse/icse{year}-{vol}.html"
        time.sleep(0.5)
        vol_dois = scrape_dblp_page(vol_url)
        
        if vol_dois is None:
            break  # no more volumes
        all_dois.extend(vol_dois)
    
    if not all_dois:
        print(f"ICSE {year}: no page found")
        return []
    
    all_dois = list(set(all_dois))  # deduplicate across volumes
    print(f"ICSE {year}: found {len(all_dois)} DOIs (volume split)")
    return all_dois


def get_openalex_data(doi):
    """
    Given a DOI, looks up the paper in OpenAlex and returns
    a list of rows — one row per author-institution pair.

    Each row contains: doi, year, title, author, institution, country_code.
    If an author has no institution data, we still record them with None
    values so we can track the coverage gap.
    """
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    
    # email in User-Agent increases rate limit from 10 to 100 req/sec
    headers = {"User-Agent": "mailto:hoyt.a@northeastern.edu"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return []
    
    work = response.json()
    rows = []
    
    for authorship in work.get("authorships", []):
        author_name = authorship["author"]["display_name"]
        institutions = authorship.get("institutions", [])
        
        if not institutions:
            rows.append({
                "doi": doi,
                "year": work.get("publication_year"),
                "title": work.get("display_name"),
                "author": author_name,
                "institution": None,
                "country_code": None,
            })
        else:
            for inst in institutions:
                rows.append({
                    "doi": doi,
                    "year": work.get("publication_year"),
                    "title": work.get("display_name"),
                    "author": author_name,
                    "institution": inst.get("display_name"),
                    "country_code": inst.get("country_code"),
                })
    
    return rows


def run_icse_pipeline(years):
    """
    Runs the full pipeline for ICSE across all given years.
    For each year: scrapes DBLP for DOIs, then looks up each DOI
    in OpenAlex for author-institution data.
    """
    all_rows = []
    missing_dois = []
    
    for year in years:
        dois = get_dois_for_year_icse(year)
        for doi in dois:
            time.sleep(0.1)  # polite rate limiting for OpenAlex
            rows = get_openalex_data(doi)
            if not rows:
                missing_dois.append(doi)
            else:
                all_rows.extend(rows)
    
    return all_rows, missing_dois


# --- run the pipeline ---
# ICSE 2010-2024 (2025 TBD once we confirm URL pattern)
icse_years = range(2010, 2025)

data, missing = run_icse_pipeline(icse_years)

# save results
with open("data/raw/icse_affiliations.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data/raw/icse_missing_dois.txt", "w") as f:
    f.write("\n".join(missing))

print(f"Done: {len(data)} author-institution rows")
print(f"Missing: {len(missing)} DOIs returned no OpenAlex data")