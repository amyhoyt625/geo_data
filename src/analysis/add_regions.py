import json

# map country codes to regions
# based on standard geographic groupings
REGION_MAP = {
    # North America
    "US": "North America", "CA": "North America", "MX": "North America",
    "BM": "North America", "GL": "North America",
    # Western Europe
    "DE": "W. Europe", "FR": "W. Europe", "GB": "W. Europe",
    "NL": "W. Europe", "IT": "W. Europe", "ES": "W. Europe",
    "SE": "W. Europe", "CH": "W. Europe", "AT": "W. Europe",
    "BE": "W. Europe", "FI": "W. Europe", "DK": "W. Europe",
    "NO": "W. Europe", "PT": "W. Europe", "IE": "W. Europe",
    "LU": "W. Europe", "GR": "W. Europe", "IS": "W. Europe",
    "MT": "W. Europe",
    # Eastern Europe
    "CZ": "E. Europe", "PL": "E. Europe", "HU": "E. Europe",
    "RO": "E. Europe", "SK": "E. Europe", "HR": "E. Europe",
    "RS": "E. Europe", "SI": "E. Europe", "BG": "E. Europe",
    "RU": "E. Europe", "EE": "E. Europe", "MK": "E. Europe",
    # Asia-Pacific
    "CN": "Asia-Pacific", "JP": "Asia-Pacific", "AU": "Asia-Pacific",
    "KR": "Asia-Pacific", "SG": "Asia-Pacific", "HK": "Asia-Pacific",
    "TW": "Asia-Pacific", "IN": "Asia-Pacific", "NZ": "Asia-Pacific",
    "TH": "Asia-Pacific", "MY": "Asia-Pacific", "ID": "Asia-Pacific",
    "PK": "Asia-Pacific", "VN": "Asia-Pacific", "MO": "Asia-Pacific",
    # Latin America
    "BR": "Latin America", "AR": "Latin America", "CL": "Latin America",
    "CO": "Latin America", "UY": "Latin America", "PE": "Latin America",
    "BB": "Latin America", "EC": "Latin America",
    # Middle East
    "IL": "Middle East", "SA": "Middle East", "AE": "Middle East",
    "IR": "Middle East", "KW": "Middle East", "JO": "Middle East",
    "PS": "Middle East", "TR": "Middle East",
    # Africa
    "ZA": "Africa", "EG": "Africa", "TN": "Africa", "DZ": "Africa",
    "LY": "Africa", "MA": "Africa", "NA": "Africa",
}

def add_regions(input_file, output_file):
    with open(input_file) as f:
        data = json.load(f)
    
    unknown = set()
    for row in data:
        code = row.get("country_code")
        if code in REGION_MAP:
            row["region"] = REGION_MAP[code]
        else:
            row["region"] = "Other"
            if code:
                unknown.add(code)  # track unmapped codes
    
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"Done: {len(data)} rows")
    if unknown:
        print(f"Unmapped country codes (added as 'Other'): {sorted(unknown)}")

# run for both conferences
add_regions("data/raw/icsa_affiliations.json", "data/clean/icsa_with_regions.json")
add_regions("data/raw/icse_affiliations.json", "data/clean/icse_with_regions.json")