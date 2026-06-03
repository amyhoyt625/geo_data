import json
from collections import defaultdict

def get_period(year):
    """Group years into 3-year periods."""
    if year <= 2012:
        return "2010-2012"
    elif year <= 2015:
        return "2013-2015"
    elif year <= 2018:
        return "2016-2018"
    elif year <= 2021:
        return "2019-2021"
    elif year <= 2024:
        return "2022-2024"
    else:
        return "2025-present"

def calculate_proportions(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

    regions = ["North America", "W. Europe", "E. Europe",
               "Asia-Pacific", "Latin America", "Middle East & Africa", "Other"]

    # --- per-year ---
    year_region_papers = defaultdict(lambda: defaultdict(set))
    year_total_papers = defaultdict(set)

    # --- per-period ---
    period_region_papers = defaultdict(lambda: defaultdict(set))
    period_total_papers = defaultdict(set)

    for row in data:
        if not row.get("region") or not row.get("doi"):
            continue
        year = row["year"]
        region = row["region"]
        doi = row["doi"]
        period = get_period(year)

        year_region_papers[year][region].add(doi)
        year_total_papers[year].add(doi)

        period_region_papers[period][region].add(doi)
        period_total_papers[period].add(doi)

    # --- print per-year ---
    print(f"\n=== {conference_name} — per-year ===")
    print(f"{'Year':<6} {'Total':>6} {'N.Am':>8} {'W.Eu':>8} {'E.Eu':>8} {'A-Pac':>8} {'Lat.Am':>8} {'ME&Af':>8} {'Other':>8}")

    year_results = []
    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        row_out = {"year": year, "period": get_period(year), "conference": conference_name, "total_papers": total}
        props = []
        for region in regions:
            count = len(year_region_papers[year][region])
            pct = round(count / total * 100, 1) if total > 0 else 0
            row_out[region] = pct
            props.append(f"{pct:>7.1f}%")
        year_results.append(row_out)
        print(f"{year:<6} {total:>6} {'  '.join(props)}")

    # --- print per-period ---
    print(f"\n=== {conference_name} — per 3-year period ===")
    print(f"{'Period':<12} {'Total':>6} {'N.Am':>8} {'W.Eu':>8} {'E.Eu':>8} {'A-Pac':>8} {'Lat.Am':>8} {'ME&Af':>8} {'Other':>8}")

    period_results = []
    for period in ["2010-2012", "2013-2015", "2016-2018", "2019-2021", "2022-2024", "2025-present"]:
        if period not in period_total_papers:
            continue
        total = len(period_total_papers[period])
        row_out = {"period": period, "conference": conference_name, "total_papers": total}
        props = []
        for region in regions:
            count = len(period_region_papers[period][region])
            pct = round(count / total * 100, 1) if total > 0 else 0
            row_out[region] = pct
            props.append(f"{pct:>7.1f}%")
        period_results.append(row_out)
        print(f"{period:<12} {total:>6} {'  '.join(props)}")

    return year_results, period_results


# run for both
icsa_years, icsa_periods = calculate_proportions("data/clean/icsa_with_regions.json", "ICSA")
icse_years, icse_periods = calculate_proportions("data/clean/icse_with_regions.json", "ICSE")

# save all results
with open("data/clean/proportions_yearly.json", "w") as f:
    json.dump(icsa_years + icse_years, f, indent=2)

with open("data/clean/proportions_5year.json", "w") as f:
    json.dump(icsa_periods + icse_periods, f, indent=2)

print(f"\nSaved yearly and 3-year proportions to data/clean/")