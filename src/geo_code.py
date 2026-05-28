import requests
import time
from urllib.parse import quote

ROR_API = "https://api.ror.org/v2/organizations"

#institution_to_country(name: str) -> str
# This function takes the name of an institution and returns the country it is located in.
def institution_to_country(name: str) -> str:
    """
    Takes a raw institution name string (messy or clean) and returns
    the country name if ROR returns a confident match (chosen=True).
    Returns None if no confident match is found.
 
    Examples:
        institution_to_country("MIT")               -> "United States"
        institution_to_country("TU Berlin")         -> "Germany"
        institution_to_country("gibberish xyz 999") -> None
    """
    if not name or not name.strip():
        return None
 

    url = f"{ROR_API}?affiliation={quote(name.strip())}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"  [ERROR] Request failed for '{name}': {e}")
        return None
 
    items = data.get("items", [])
    for item in items:
        if item.get("chosen") is True:
            locations = item.get("organization", {}).get("locations", [])
            if locations:
                country = locations[0].get("geonames_details", {}).get("country_name")
                return country
 
    return None
 
 
# ------------------------------------------------------------------
# Extended version: returns full match metadata (useful for analysis)
# ------------------------------------------------------------------
 
def institution_to_country_detailed(name: str) -> dict:
    """
    Returns a dict with:
        - country:       str or None
        - ror_id:        str or None
        - org_name:      str or None  (ROR canonical name)
        - match_type:    str or None  (e.g. "SINGLE SEARCH")
        - score:         float or None
        - confident:     bool         (True if chosen=True)
    """
    result = {
        "input":      name,
        "country":    None,
        "ror_id":     None,
        "org_name":   None,
        "match_type": None,
        "score":      None,
        "confident":  False,
    }
 
    if not name or not name.strip():
        return result
 
    url = f"{ROR_API}?affiliation={quote(name.strip())}"
 
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"  [ERROR] '{name}': {e}")
        return result
 
    items = data.get("items", [])
    if not items:
        return result
 
    # Always grab the top result's score for analysis
    top = items[0]
    result["score"]      = top.get("score")
    result["match_type"] = top.get("matching_type")
 
    # Only trust chosen=True (as per ROR docs)
    for item in items:
        if item.get("chosen") is True:
            org = item.get("organization", {})
            locations = org.get("locations", [])
 
            result["confident"] = True
            result["ror_id"]    = org.get("id")
            result["score"]     = item.get("score")
            result["match_type"]= item.get("matching_type")
 
            # Get canonical display name
            for name_entry in org.get("names", []):
                if "ror_display" in name_entry.get("types", []):
                    result["org_name"] = name_entry.get("value")
                    break
 
            if locations:
                geo = locations[0].get("geonames_details", {})
                result["country"] = geo.get("country_name")
 
            break
 
    return result
 
 
# ------------------------------------------------------------------
# Test suite — 25 real institution strings from SE conferences
# ------------------------------------------------------------------
 
TEST_INSTITUTIONS = [
    # Clean names
    "MIT",
    "Massachusetts Institute of Technology",
    "Carnegie Mellon University",
    "University of Toronto",
    "ETH Zurich",
    "TU Delft",
    "University of Melbourne",
    "Peking University",
    "Indian Institute of Technology Bombay",
    "University of São Paulo",
    # Messy / real-world strings
    "Dept. of Computer Science, University of Oxford, UK",
    "Software Engineering Institute, Carnegie Mellon, Pittsburgh, PA",
    "Politecnico di Milano, Italy",
    "INRIA, France",
    "National University of Singapore (NUS)",
    "Chalmers University of Technology, Gothenburg, Sweden",
    "Tsinghua University, Beijing, China",
    "Seoul National University",
    "University of Cape Town, South Africa",
    "Pontificia Universidad Católica de Chile",
    # Edge cases
    "MIT CSAIL",                          # sub-unit, not a ROR entry
    "Microsoft Research",
    "IBM Research - Zurich",
    "Anonymous Institution",              # should return None
    "",                                   # empty string
]
 
 
def run_test_suite():
    print("=" * 65)
    print("ROR Geocoding Prototype — Test Suite")
    print("=" * 65)
 
    results = []
    confident_count = 0
    no_match_count  = 0
 
    for name in TEST_INSTITUTIONS:
        if not name.strip():
            print(f"\n  [SKIP] empty string")
            results.append({"input": name, "confident": False, "country": None})
            no_match_count += 1
            continue
 
        detail = institution_to_country_detailed(name)
        results.append(detail)
 
        status = "✓ CONFIDENT" if detail["confident"] else "✗ NO MATCH "
        country = detail["country"] or "—"
        org     = detail["org_name"] or "—"
        score   = f"{detail['score']:.2f}" if detail["score"] is not None else "—"
 
        print(f"\n  Input:   {name}")
        print(f"  Status:  {status}  |  Score: {score}")
        if detail["confident"]:
            print(f"  Matched: {org}")
            print(f"  Country: {country}")
            confident_count += 1
        else:
            no_match_count += 1
 
        time.sleep(0.3)   # be polite to the API
 
    # Summary
    total = len(TEST_INSTITUTIONS)
    print("\n" + "=" * 65)
    print(f"Summary: {total} inputs tested")
    print(f"  Confident matches (chosen=True): {confident_count}")
    print(f"  No confident match:              {no_match_count}")
    print(f"  Match rate: {confident_count / total * 100:.0f}%")
    print("=" * 65)
 
    return results
 
 
if __name__ == "__main__":
    run_test_suite()