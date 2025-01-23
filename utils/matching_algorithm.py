from typing import List

from fuzzywuzzy import fuzz
from pyairtable.api.types import RecordDict

from models.client_match import ClientMatch


def calculate_match_score(therapist: dict, client: dict):
    """Calculate a match score between a therapist and a client."""
    score = 0

    # Match state
    if client['state'] in therapist['States']:
        score += 15

    # Match demographics
    if str(client['gender']).lower() in str(therapist['Gender']).lower():
        score += 10

    # Gender and other preferences
    gender = therapist.get("Gender: Do you have experience and/or interest in working with individuals who do not identify as cisgender? (i.e. transgender, gender fluid, etc.) ")
    if gender:
        if client['gender'] in ['Transgender', 'Non-binary'] and gender.__contains__("Yes"):
            score += 5

    # Adding other lived experiences (expand based on more fields)
    lgbtq = client.get('lived_experiences')
    if lgbtq:
        if therapist['LGBTQ+: Are you a part of the LGBTQ+ community?'].__eq__("Yes") and lgbtq.__contains__("LGBTQ+"):
            score += 5

    # Match therapeutic style preference
    client_preferences = client['likely_therapists'].split(',')
    therapist_prefs = therapist['Therapeutic Orientation: Please select the modalities you most frequently utilize. ']
    therapist_prefs.append(therapist['Gender'])
    for preference in client_preferences:
        for therapist_pref in therapist_prefs:
            if fuzz.token_set_ratio(preference, therapist_pref) > 80:
                score += 5

    # Fuzzy matching for broader compatibility
    fuzzy_score = fuzz.token_set_ratio(client['likely_therapists'], therapist_prefs)
    score += fuzzy_score * 0.1

    return score

def sort(e: dict):
    return e.get('client_name')


def match_client_with_therapists(client: dict, therapists: list, limit: int) -> List[dict]:
    """Match each client to the best therapist."""
    matches = []
    scores = {}
    for data in therapists:
        therapist = data['fields']
        score = calculate_match_score(therapist, client)
        scores[therapist['Intern Name']] = score
    scores = sorted(scores.items(), key=lambda x:x[1], reverse=True)
    for item in scores[:limit]:
        best_match = item[0]
        score = item[1]
        matches.append({
            "client_name": f"{client['first_name']} {client['last_name']}",
            "therapist_name": best_match,
            "score": score
        })

    matches.sort(key=sort)
    return matches