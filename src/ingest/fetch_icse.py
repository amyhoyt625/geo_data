import requests       # for making HTTP requests to DBLP and OpenAlex
import time           # for sleep delays between API calls
import json           # for saving output as JSON
from bs4 import BeautifulSoup  # for parsing DBLP HTML pages
from requests.exceptions import ConnectionError


def safe_get(url, headers, retries=3, wait=10):
    """
    Wrapper around requests.get that retries on connection errors.
    Waits 'wait' seconds between retries — gives DBLP time to recover.
    """
    for attempt in range(retries):
        try:
            return requests.get(url, headers=headers)
        except ConnectionError:
            if attempt < retries - 1:
                print(f"Connection error, retrying in {wait}s... (attempt {attempt + 1}/{retries})")
                time.sleep(wait)
            else:
                print(f"Failed after {retries} attempts: {url}")
                return None
    return None


def scrape_dblp_page(url):
    """
    Helper function — fetches a single DBLP page and returns
    a list of IEEE/ACM DOIs found on it.
    Used by get_dois_for_year_icse to avoid repeating the same
    scraping logic for simple vs volume-split years.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    response = safe_get(url, headers)
    
    if response is None or response.status_code != 200:
        return None  # None means page doesn't exist
    
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
    simple_url = f"https://dblp.org/db/conf/icse/icse{year}.html"
    time.sleep(0.5)  # be polite to DBLP
    dois = scrape_dblp_page(simple_url)
    
    if dois is not None:
        print(f"ICSE {year}: found {len(dois)} DOIs")
        return dois
    
    # simple URL was 404 — try volume split
    all_dois = []
    for vol in [1, 2, 3]:
        vol_url = f"https://dblp.org/db/conf/icse/icse{year}-{vol}.html"
        time.sleep(0.5)
        vol_dois = scrape_dblp_page(vol_url)
        
        if vol_dois is None:
            break
        all_dois.extend(vol_dois)
    
    if not all_dois:
        print(f"ICSE {year}: no page found")
        return []
    
    all_dois = list(set(all_dois))
    print(f"ICSE {year}: found {len(all_dois)} DOIs (volume split)")
    return all_dois


def get_openalex_data(doi):
    """
    Given a DOI, looks up the paper in OpenAlex and returns
    a list of rows — one row per author-institution pair.

    Each row contains: doi, year, title, author, author_position,
    institution, country_code, primary_topic.

    author_position values from OpenAlex: "first", "middle", "last"
    primary_topic is paper-level — same value for all authors on a paper.

    If an author has no institution data, we still record them with None
    values so we can track the coverage gap.
    """
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    
    # email in User-Agent increases rate limit from 10 to 100 req/sec
    headers = {"User-Agent": "mailto:hoyt.a@northeastern.edu"}
    response = safe_get(url, headers)
    
    if response is None or response.status_code != 200:
        return []
    
    work = response.json()
    rows = []

    # get primary topic once per paper — same for all authors
    primary_topic = None
    if work.get("primary_topic"):
        primary_topic = work["primary_topic"].get("display_name")

    for authorship in work.get("authorships", []):
        author_name = authorship["author"]["display_name"]
        # OpenAlex returns "first", "middle", or "last"
        author_pos = authorship.get("author_position", "unknown")
        institutions = authorship.get("institutions", [])
        
        if not institutions:
            rows.append({
                "doi": doi,
                "year": work.get("publication_year"),
                "title": work.get("display_name"),
                "author": author_name,
                "author_position": author_pos,
                "institution": None,
                "country_code": None,
                "primary_topic": primary_topic,
            })
        else:
            for inst in institutions:
                rows.append({
                    "doi": doi,
                    "year": work.get("publication_year"),
                    "title": work.get("display_name"),
                    "author": author_name,
                    "author_position": author_pos,
                    "institution": inst.get("display_name"),
                    "country_code": inst.get("country_code"),
                    "primary_topic": primary_topic,
                })
    
    return rows


def run_icse_pipeline(years):
    """
    Runs the full pipeline for ICSE across all given years.
    Saves results year by year so progress isn't lost if interrupted.
    """
    all_rows = []
    missing_dois = []
    
    for year in years:
        dois = get_dois_for_year_icse(year)
        year_rows = []

        for doi in dois:
            time.sleep(0.1)  # polite rate limiting for OpenAlex
            rows = get_openalex_data(doi)
            if not rows:
                missing_dois.append(doi)
            else:
                year_rows.extend(rows)

        # save each year immediately so progress isn't lost on crash
        with open(f"data/raw/icse_{year}.json", "w") as f:
            json.dump(year_rows, f, indent=2)
        print(f"  -> saved {len(year_rows)} rows for {year}")

        all_rows.extend(year_rows)
    
    return all_rows, missing_dois


# --- run the pipeline ---
icse_years = range(2010, 2026)

data, missing = run_icse_pipeline(icse_years)

# save combined file
with open("data/raw/icse_affiliations.json", "w") as f:
    json.dump(data, f, indent=2)

with open("data/raw/icse_missing_dois.txt", "w") as f:
    f.write("\n".join(missing))

print(f"Done: {len(data)} author-institution rows")
print(f"Missing: {len(missing)} DOIs returned no OpenAlex data")