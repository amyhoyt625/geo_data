import requests
import time
from urllib.parse import quote

ROR_API = "https://api.ror.org/v2/organizations"

#institution_to_country(name: str) -> str
# This function takes the name of an institution and returns the country it is located in.
def institution_to_country(name: str) -> str:
    