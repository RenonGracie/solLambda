import re

"""Table to Map States to Abbreviations Courtesy https://gist.github.com/Quenty/74156dcc4e21d341ce52da14a701c40c"""
statename_to_abbr = {
    # Other
    "District of Columbia": "DC",
    # States
    "Alabama": "AL",
    "Montana": "MT",
    "Alaska": "AK",
    "Nebraska": "NE",
    "Arizona": "AZ",
    "Nevada": "NV",
    "Arkansas": "AR",
    "New Hampshire": "NH",
    "California": "CA",
    "New Jersey": "NJ",
    "Colorado": "CO",
    "New Mexico": "NM",
    "Connecticut": "CT",
    "New York": "NY",
    "Delaware": "DE",
    "North Carolina": "NC",
    "Florida": "FL",
    "North Dakota": "ND",
    "Georgia": "GA",
    "Ohio": "OH",
    "Hawaii": "HI",
    "Oklahoma": "OK",
    "Idaho": "ID",
    "Oregon": "OR",
    "Illinois": "IL",
    "Pennsylvania": "PA",
    "Indiana": "IN",
    "Rhode Island": "RI",
    "Iowa": "IA",
    "South Carolina": "SC",
    "Kansas": "KS",
    "South Dakota": "SD",
    "Kentucky": "KY",
    "Tennessee": "TN",
    "Louisiana": "LA",
    "Texas": "TX",
    "Maine": "ME",
    "Utah": "UT",
    "Maryland": "MD",
    "Vermont": "VT",
    "Massachusetts": "MA",
    "Virginia": "VA",
    "Michigan": "MI",
    "Washington": "WA",
    "Minnesota": "MN",
    "West Virginia": "WV",
    "Mississippi": "MS",
    "Wisconsin": "WI",
    "Missouri": "MO",
    "Wyoming": "WY",
}


def multiple_replace(lookup, text):
    # re.IGNORECASE flags allows provides case insensitivity (i.e. matches New York, new york, NEW YORK, etc.)
    regex = re.compile(r"\b(" + "|".join(lookup.keys()) + r")\b", re.IGNORECASE)
    # For each match, look-up corresponding value in dictionary and peform subsstituion
    # we convert match to title to capitalize first letter in each word
    return regex.sub(lambda mo: lookup[mo.string.title()[mo.start() : mo.end()]], text)
