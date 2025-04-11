from src.db.database import with_database
from src.models.db.airtable import AirtableTherapist


@with_database
def save_therapists(database, therapists: list[dict]):
    database.query(AirtableTherapist).delete()

    # Clean Unicode characters that might cause encoding issues
    cleaned_therapists = []
    for therapist in therapists:
        cleaned_therapist = {}
        for key, value in therapist.items():
            if isinstance(value, str):
                # Remove problematic Unicode characters
                cleaned_value = value.encode("ascii", "ignore").decode("ascii")
                cleaned_therapist[key] = cleaned_value
            else:
                cleaned_therapist[key] = value
        cleaned_therapists.append(cleaned_therapist)

    return database.add_all(
        [AirtableTherapist(**therapist) for therapist in cleaned_therapists]
    )
