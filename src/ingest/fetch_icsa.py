import requests
import time
import json
from bs4 import BeautifulSoup

def get_dois_for_year(year):
    url = f"https://dblp.org/db/conf/icsa/icsa{year}.html"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"No page found for {year}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    dois = []
    
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if "doi.org/10.1109" in href:
            doi = href.replace("https://doi.org/", "")
            dois.append(doi)
    
    print(f"{year}: found {len(dois)} DOIs")
    return dois


def get_openalex_data(doi):
    url = f"https://api.openalex.org/works/https://doi.org/{doi}"
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


def run_pipeline(years):
    all_rows = []
    missing_dois = []
    
    for year in years:
        dois = get_dois_for_year(year)
        for doi in dois:
            time.sleep(0.1)
            rows = get_openalex_data(doi)
            if not rows:
                missing_dois.append(doi)
            else:
                all_rows.extend(rows)
    
    return all_rows, missing_dois


# test on one year first
years = [2023]
data, missing = run_pipeline(years)

with open("data/raw/icsa_affiliations.json", "w") as f:
    json.dump(data, f, indent=2)

print(f"Done: {len(data)} rows, {len(missing)} missing")


