import json
from collections import Counter, defaultdict

def analyze(input_file, conference_name):
    with open(input_file) as f:
        data = json.load(f)

    print(f"\n{'='*60}")
    print(f" {conference_name}")
    print(f"{'='*60}")

    # build institution → country mapping
    inst_country = {}
    for r in data:
        if r.get("institution") and r.get("country_code"):
            inst_country[r["institution"]] = r["country_code"]

    # --- top 20 institutions ---
    inst_counts = Counter(
        r["institution"] for r in data 
        if r.get("institution")
    )
    print(f"\n--- top 20 institutions ---")
    for inst, count in inst_counts.most_common(20):
        country = inst_country.get(inst, "??")
        print(f"  {count:>5}  {country:<4}  {inst}")

    # --- top 20 authors with their institution ---
    # store the most recent institution for each author
    author_inst = {}
    author_country = {}
    author_counts = Counter()
    for r in data:
        if r.get("author"):
            author_counts[r["author"]] += 1
            if r.get("institution"):
                author_inst[r["author"]] = r["institution"]
            if r.get("country_code"):
                author_country[r["author"]] = r["country_code"]

    print(f"\n--- top 20 authors ---")
    for author, count in author_counts.most_common(20):
        inst = author_inst.get(author, "unknown institution")
        country = author_country.get(author, "??")
        print(f"  {count:>5}  {country:<4}  {author} — {inst}")

    # --- top topics overall ---
    topic_counts = Counter(
        r["primary_topic"] for r in data
        if r.get("primary_topic")
    )
    print(f"\n--- top 15 topics overall ---")
    for topic, count in topic_counts.most_common(15):
        print(f"  {count:>5}  {topic}")

    # --- top topics per region ---
    region_topics = defaultdict(Counter)
    for r in data:
        if r.get("region") and r.get("primary_topic"):
            region_topics[r["region"]][r["primary_topic"]] += 1

    print(f"\n--- top 5 topics per region ---")
    for region in sorted(region_topics.keys()):
        print(f"\n  {region}:")
        for topic, count in region_topics[region].most_common(5):
            print(f"    {count:>5}  {topic}")

    # --- top institutions per region ---
    region_inst = defaultdict(Counter)
    for r in data:
        if r.get("region") and r.get("institution"):
            region_inst[r["region"]][r["institution"]] += 1

    print(f"\n--- top 5 institutions per region ---")
    for region in sorted(region_inst.keys()):
        print(f"\n  {region}:")
        for inst, count in region_inst[region].most_common(5):
            country = inst_country.get(inst, "??")
            print(f"    {count:>5}  {country:<4}  {inst}")

    # --- first author region breakdown ---
    first_author_regions = Counter(
        r["region"] for r in data
        if r.get("author_position") == "first" and r.get("region")
    )
    total_first = sum(first_author_regions.values())
    print(f"\n--- first author region breakdown ---")
    for region, count in first_author_regions.most_common():
        pct = round(count / total_first * 100, 1) if total_first > 0 else 0
        print(f"  {count:>5}  {pct:>6.1f}%  {region}")


# run for both — use clean files since they have region field
analyze("data/clean/icsa_with_regions.json", "ICSA")
analyze("data/clean/icse_with_regions.json", "ICSE")