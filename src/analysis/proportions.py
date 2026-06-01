import json
from collections import defaultdict

def calculate_proportions(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)
    
    # count author-institution rows per year per region
    # using a set of (doi, region) to count papers not just rows
    year_region_papers = defaultdict(lambda: defaultdict(set))
    year_total_papers = defaultdict(set)
    
    for row in data:
        if not row.get("region") or not row.get("doi"):
            continue
        year = row["year"]
        region = row["region"]
        doi = row["doi"]
        year_region_papers[year][region].add(doi)
        year_total_papers[year].add(doi)
    
    print(f"\n=== {conference_name} — per-year regional proportions ===")
    print(f"{'Year':<6} {'Total':>6} {'N.Am':>8} {'W.Eu':>8} {'E.Eu':>8} {'A-Pac':>8} {'Lat.Am':>8} {'ME&Af':>8} {'Other':>8}")
    
    regions = ["North America", "W. Europe", "E. Europe", 
               "Asia-Pacific", "Latin America", "Middle East & Africa", "Other"]
    
    results = []
    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        row_out = {"year": year, "conference": conference_name, "total_papers": total}
        
        props = []
        for region in regions:
            count = len(year_region_papers[year][region])
            pct = round(count / total * 100, 1) if total > 0 else 0
            row_out[region] = pct
            props.append(f"{pct:>7.1f}%")
        
        results.append(row_out)
        print(f"{year:<6} {total:>6} {'  '.join(props)}")
    
    return results

# run for both
icsa = calculate_proportions("data/clean/icsa_with_regions.json", "ICSA")
icse = calculate_proportions("data/clean/icse_with_regions.json", "ICSE")

# save combined results
all_results = icsa + icse
with open("data/clean/proportions.json", "w") as f:
    json.dump(all_results, f, indent=2)

print(f"\nSaved to data/clean/proportions.json")