import requests       # for making HTTP requests to DBLP and OpenAlex
import time           # for sleep delays between API calls
import json           # for saving output as JSON
from bs4 import BeautifulSoup  # for parsing DBLP HTML pages

#scrapes the dblp conference page for ICSA years (2010-present)
#scrapes all publications available for that year
#dblp structured so easy to get one piece of data, and doi is always conveniently clean 
def get_dois_for_year(year):
    #ICSA papers are published by IEEE, so DOIs start with 10.1109.

    url = f"https://dblp.org/db/conf/icsa/icsa{year}.html"
    
    # User-Agent header required — DBLP blocks requests without it
    headers = {"User-Agent": "Mozilla/5.0"}
    # get raw html
    response = requests.get(url, headers=headers)
    
    # if page doesn't exist, skip it
    if response.status_code != 200:
        print(f"No ICSA page found for {year}")
        return []
    # parse html into searchable struct
    soup = BeautifulSoup(response.text, "html.parser")
    dois = []
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        # ICSA papers are IEEE — filter to 10.1109 DOIs only
        if "doi.org/10.1109" in href:
            doi = href.replace("https://doi.org/", "")
            dois.append(doi)
    
    dois = list(set(dois))  # remove duplicates
    print(f"ICSA {year}: found {len(dois)} DOIs")
    return dois


#scrapes the dblp conference page for WICSA years (2011-2016 excluding 2013)
def get_dois_for_year_wicsa(year):
    # Also published by IEEE so same DOI prefix.

    url = f"https://dblp.org/db/conf/wicsa/wicsa{year}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"No WICSA page found for {year}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    dois = []
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if "doi.org/10.1109" in href:
            doi = href.replace("https://doi.org/", "")
            dois.append(doi)
    
    dois = list(set(dois))  # remove duplicates
    print(f"WICSA {year}: found {len(dois)} DOIs")
    return dois


#scrapes the dblp conference page for ECSA years (2010, 2013)
def get_dois_for_year_ecsa(year):
    """
    ECSA (European Conference on Software Architecture) was co-located
    or used instead of WICSA in these years.
    ECSA is published by Springer, so DOIs start with 10.1007 not 10.1109.
    We filter to DOIs with underscores to get individual papers only,
    excluding the proceedings-level DOI (e.g. 10.1007/978-3-642-15114-9)
    which has no underscore suffix.
    """
    url = f"https://dblp.org/db/conf/ecsa/ecsa{year}.html"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"No ECSA page found for {year}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    dois = []
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        # underscore distinguishes individual paper DOIs from proceedings-level DOIs
        if "doi.org/10." in href and "_" in href:
            doi = href.replace("https://doi.org/", "")
            dois.append(doi)
    
    dois = list(set(dois))  # remove duplicates
    print(f"ECSA {year}: found {len(dois)} DOIs")
    return dois


def get_openalex_data(doi):
    """
    Given a DOI, looks up the paper in OpenAlex and returns
    a list of rows — one row per author-institution pair.

    Each row contains: doi, year, title, author, author_position,
    institution, country_code.
    
    author_position values from OpenAlex: "first", "middle", "last"
    Note: OpenAlex does not give exact numeric positions for middle authors.
    
    If an author has no institution data, we still record them with None
    values so we can track the coverage gap.
    """
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
    
    # email in User-Agent increases rate limit from 10 to 100 req/sec
    headers = {"User-Agent": "mailto:hoyt.a@northeastern.edu"}
    response = requests.get(url, headers=headers)
    
    # if OpenAlex doesn't have this paper, return empty
    if response.status_code != 200:
        return []
    
    work = response.json()
    rows = []

    # get primary topic once per paper — same for all authors on this paper
    # primary_topic is a paper-level field, not author-level
    primary_topic = None
    if work.get("primary_topic"):
        primary_topic = work["primary_topic"].get("display_name")
    
    # loop through every author on the paper
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
                "primary_topic": primary_topic,  # add here
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
                    "primary_topic": primary_topic,  # add here
                })
    
    return rows


def run_pipeline(icsa_years, wicsa_years, ecsa_years):
    """
    Runs the full pipeline across all three conferences:
    ECSA → WICSA → ICSA 
    For each year, fetches DOIs from DBLP then looks up each DOI in OpenAlex.
    Returns all author-institution rows and a list of DOIs with no OpenAlex data.
    """
    all_rows = []
    missing_dois = []  # DOIs where OpenAlex returned nothing — to check for coverage 
    
    # pair each year with the correct fetch function for that conference era
    for year, fetch_fn in [
        *[(y, get_dois_for_year_ecsa) for y in ecsa_years],
        *[(y, get_dois_for_year_wicsa) for y in wicsa_years],
        *[(y, get_dois_for_year) for y in icsa_years],
    ]:
        dois = fetch_fn(year)
        for doi in dois:
            # be polite to OpenAlex — 0.1s sleep keeps us well within rate limits
            time.sleep(0.1)
            rows = get_openalex_data(doi)
            if not rows:
                missing_dois.append(doi)
            else:
                all_rows.extend(rows)
    
    return all_rows, missing_dois


icsa_years = range(2017, 2026)
wicsa_years = [2011, 2012, 2014, 2015, 2016]
ecsa_years = [2010, 2013]

# --- run the pipeline ---
data, missing = run_pipeline(icsa_years, wicsa_years, ecsa_years)

# quick check — print first 3 rows to verify author_position field
print("\nSample rows:")
for row in data[:3]:
    print(row)

# save the flat list of author-institution rows to JSON
# each row = one author at one institution for one paper
with open("data/raw/icsa_affiliations.json", "w") as f:
    json.dump(data, f, indent=2)

# save missing DOIs separately so we can investigate or document coverage gaps
with open("data/raw/missing_dois.txt", "w") as f:
    f.write("\n".join(missing))

print(f"\nDone: {len(data)} author-institution rows")
print(f"Missing: {len(missing)} DOIs returned no OpenAlex data")