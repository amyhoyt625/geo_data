import json
from collections import defaultdict
import pandas as pd

# ── Script 1: Raw counts per region per year (with totals) ────────────────────

def calculate_counts(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

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

    regions = ["North America", "W. Europe", "E. Europe",
               "Asia-Pacific", "Latin America", "Middle East & Africa", "Other"]

    print(f"\n=== {conference_name} — per-year regional counts ===")
    print(f"{'Year':<6} {'Total':>6} {'N.Am':>8} {'W.Eu':>8} {'E.Eu':>8} {'A-Pac':>8} {'Lat.Am':>8} {'ME&Af':>8} {'Other':>8}")

    results = []
    region_totals = defaultdict(int)
    grand_total = 0

    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        grand_total += total
        row_out = {"year": year, "conference": conference_name, "total_papers": total}

        counts = []
        for region in regions:
            count = len(year_region_papers[year][region])
            row_out[region] = count
            region_totals[region] += count
            counts.append(f"{count:>8}")

        results.append(row_out)
        print(f"{year:<6} {total:>6} {''.join(counts)}")

    # totals row
    totals_row = [f"{region_totals[r]:>8}" for r in regions]
    print(f"{'TOTAL':<6} {grand_total:>6} {''.join(totals_row)}")

    return results


# ── Script 2: Publications per country per year (with totals) ─────────────────

def calculate_counts_by_country(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

    year_country_papers = defaultdict(lambda: defaultdict(set))
    year_total_papers = defaultdict(set)

    for row in data:
        if not row.get("country_code") or not row.get("doi"):
            continue
        year = row["year"]
        country = row["country_code"]
        doi = row["doi"]
        year_country_papers[year][country].add(doi)
        year_total_papers[year].add(doi)

    # get all countries sorted by total contribution
    all_countries = defaultdict(int)
    for year in year_country_papers:
        for country, dois in year_country_papers[year].items():
            all_countries[country] += len(dois)
    countries = sorted(all_countries, key=lambda c: all_countries[c], reverse=True)

    print(f"\n=== {conference_name} — per-year country counts ===")
    header = f"{'Year':<6} {'Total':>6} " + " ".join(f"{c:>6}" for c in countries)
    print(header)

    results = []
    country_totals = defaultdict(int)
    grand_total = 0

    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        grand_total += total
        row_out = {"year": year, "conference": conference_name, "total_papers": total}

        counts = []
        for country in countries:
            count = len(year_country_papers[year][country])
            row_out[country] = count
            country_totals[country] += count
            counts.append(f"{count:>6}")

        results.append(row_out)
        print(f"{year:<6} {total:>6} {' '.join(counts)}")

    # totals row
    totals_row = " ".join(f"{country_totals[c]:>6}" for c in countries)
    print(f"{'TOTAL':<6} {grand_total:>6} {totals_row}")

    return results


# ── Script 3: Percentages per region per year (with totals) ───────────────────

def calculate_proportions(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

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

    regions = ["North America", "W. Europe", "E. Europe",
               "Asia-Pacific", "Latin America", "Middle East & Africa", "Other"]

    print(f"\n=== {conference_name} — per-year regional proportions ===")
    print(f"{'Year':<6} {'Total':>6} {'N.Am':>8} {'W.Eu':>8} {'E.Eu':>8} {'A-Pac':>8} {'Lat.Am':>8} {'ME&Af':>8} {'Other':>8}")

    results = []
    region_totals = defaultdict(int)
    grand_total = 0

    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        grand_total += total
        row_out = {"year": year, "conference": conference_name, "total_papers": total}

        props = []
        for region in regions:
            count = len(year_region_papers[year][region])
            pct = round(count / total * 100, 1) if total > 0 else 0
            row_out[region] = pct
            region_totals[region] += count
            props.append(f"{pct:>7.1f}%")

        results.append(row_out)
        print(f"{year:<6} {total:>6} {'  '.join(props)}")

    # totals row — percentage of grand total
    totals_row = []
    for region in regions:
        pct = round(region_totals[region] / grand_total * 100, 1) if grand_total > 0 else 0
        totals_row.append(f"{pct:>7.1f}%")
    print(f"{'TOTAL':<6} {grand_total:>6} {'  '.join(totals_row)}")

    return results


# ── Run all three ──────────────────────────────────────────────────────────────

print("=" * 60)
print("SCRIPT 1: Regional counts")
icsa_counts   = calculate_counts("data/clean/icsa_with_regions.json", "ICSA")
icse_counts   = calculate_counts("data/clean/icse_with_regions.json", "ICSE")

print("\n" + "=" * 60)
print("SCRIPT 2: Country counts")
icsa_country  = calculate_counts_by_country("data/clean/icsa_with_regions.json", "ICSA")
icse_country  = calculate_counts_by_country("data/clean/icse_with_regions.json", "ICSE")

print("\n" + "=" * 60)
print("SCRIPT 3: Regional percentages")
icsa_props    = calculate_proportions("data/clean/icsa_with_regions.json", "ICSA")
icse_props    = calculate_proportions("data/clean/icse_with_regions.json", "ICSE")

# ── Save all outputs ───────────────────────────────────────────────────────────

"""
with open("data/clean/region_counts.json", "w") as f:
    json.dump(icsa_counts + icse_counts, f, indent=2)

with open("data/clean/country_counts.json", "w") as f:
    json.dump(icsa_country + icse_country, f, indent=2)

with open("data/clean/proportions.json", "w") as f:
    json.dump(icsa_props + icse_props, f, indent=2)
"""

print("\nSaved:")
print("  data/clean/region_counts.json")
print("  data/clean/country_counts.json")
print("  data/clean/proportions.json")

# excels for the country data

# ICSA country counts to Excel
pd.DataFrame(icsa_country).to_excel("data/clean/icsa_country_counts.xlsx", index=False)

# ICSE country counts to Excel
pd.DataFrame(icse_country).to_excel("data/clean/icse_country_counts.xlsx", index=False)

print("  data/clean/icsa_country_counts.xlsx")
print("  data/clean/icse_country_counts.xlsx")


# for the country percentages
def calculate_proportions_by_country(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

    year_country_papers = defaultdict(lambda: defaultdict(set))
    year_total_papers = defaultdict(set)

    for row in data:
        if not row.get("country_code") or not row.get("doi"):
            continue
        year = row["year"]
        country = row["country_code"]
        doi = row["doi"]
        year_country_papers[year][country].add(doi)
        year_total_papers[year].add(doi)

    # sort countries by total contribution
    all_countries = defaultdict(int)
    for year in year_country_papers:
        for country, dois in year_country_papers[year].items():
            all_countries[country] += len(dois)
    countries = sorted(all_countries, key=lambda c: all_countries[c], reverse=True)

    print(f"\n=== {conference_name} — per-year country percentages ===")
    header = f"{'Year':<6} {'Total':>6} " + " ".join(f"{c:>7}" for c in countries)
    print(header)

    results = []
    country_totals = defaultdict(int)
    grand_total = 0

    for year in sorted(year_total_papers.keys()):
        total = len(year_total_papers[year])
        grand_total += total
        row_out = {"year": year, "conference": conference_name, "total_papers": total}

        pcts = []
        for country in countries:
            count = len(year_country_papers[year][country])
            pct = round(count / total * 100, 1) if total > 0 else 0
            row_out[country] = pct
            country_totals[country] += count
            pcts.append(f"{pct:>6.1f}%")

        results.append(row_out)
        print(f"{year:<6} {total:>6} {' '.join(pcts)}")

    # totals row
    totals_row = []
    for country in countries:
        pct = round(country_totals[country] / grand_total * 100, 1) if grand_total > 0 else 0
        totals_row.append(f"{pct:>6.1f}%")
    print(f"{'TOTAL':<6} {grand_total:>6} {' '.join(totals_row)}")

    return results


# ── Run and save ───────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("SCRIPT 4: Country percentages")
icsa_country_props = calculate_proportions_by_country("data/clean/icsa_with_regions.json", "ICSA")
icse_country_props = calculate_proportions_by_country("data/clean/icse_with_regions.json", "ICSE")

pd.DataFrame(icsa_country_props).to_excel("data/clean/icsa_country_percentages.xlsx", index=False)
pd.DataFrame(icse_country_props).to_excel("data/clean/icse_country_percentages.xlsx", index=False)

print("  data/clean/icsa_country_percentages.xlsx")
print("  data/clean/icse_country_percentages.xlsx")