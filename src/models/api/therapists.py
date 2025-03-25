from datetime import datetime

from pydantic import BaseModel


class GoogleEvent(BaseModel):
    start_date: datetime | None
    end_date: datetime | None
    recurrence: list[str] | None

    client_email: str | None


class AvailableSlots(BaseModel):
    available_slots: list[datetime] | None


class Therapist(AvailableSlots):
    id: str
    intern_name: str | None
    age: str | None
    email: str | None

    calendar_email: str | None

    biography: str | None

    availability: list[str] | None
    birth_order: str | None
    caretaker_role: bool | None
    caseload_tracker: str | None
    has_children: bool | None
    cohort: str | None
    diagnoses: list[str] | None
    ethnicity: list[str] | None
    gender: str | None
    gender_interest: str | None
    immigration_background: str | None
    lgbtq_part: bool | None
    culture: str | None
    places: str | None
    married: bool | None
    max_caseload: str | None
    neurodivergence: str | None
    performing: bool | None
    program: str | None
    religion: list[str] | None
    experience_with_risk_clients: str | None
    working_with_lgbtq_clients: str | None
    negative_affect_by_social_media: bool | None
    specialities: list[str] | None
    states: list[str] | None
    therapeutic_orientation: list[str] | None
    family_household: str | None

    welcome_video_link: str | None
    greetings_video_link: str | None
    image_link: str | None

    available_slots: list[datetime] | None

    def __init__(self, json: dict):
        fields = json["fields"]

        def parce_bool(field: str) -> bool | None:
            if not field:
                return None
            if field.lower().__eq__("yes"):
                return True
            elif field.lower().__eq__("no"):
                return False
            else:
                return None

        super().__init__(
            id=json["id"],
            intern_name=fields.get("Intern Name") or fields.get("Name"),
            age=fields.get("Age"),
            email=fields.get("Email") or fields.get("Notes"),
            calendar_email=fields.get("Calendar"),
            biography=fields.get("Intro Bios (Shortened)"),
            availability=fields.get(
                "Availability: When are you available to see clients?"
            ),
            birth_order=fields.get("Birth Order"),
            caretaker_role=parce_bool(
                fields.get("Caretaker Role: Have you ever been in a caretaker role?")
            ),
            caseload_tracker=fields.get("Caseload Tracker"),
            has_children=parce_bool(fields.get("Children: Do you have children?")),
            cohort=fields.get("Cohort"),
            diagnoses=fields.get(
                "Diagnoses: Please select the diagnoses you have experience and/or interest in working with"
            ),
            ethnicity=fields.get("Ethnicity"),
            gender=fields.get("Gender"),
            gender_interest=fields.get(
                "Gender: Do you have experience and/or interest in working with individuals who do not identify as cisgender? (i.e. transgender, gender fluid, etc.) "
            ),
            immigration_background=fields.get("Immigration Background"),
            lgbtq_part=parce_bool(
                fields.get("LGBTQ+: Are you a part of the LGBTQ+ community?")
            ),
            culture=fields.get("Individualist vs. Collectivist culture"),
            places=fields.get("Many places or only one or two places?"),
            married=parce_bool(
                fields.get("Marriage: Are you / have ever been married?")
            ),
            max_caseload=fields.get("Max Caseload"),
            neurodivergence=fields.get(
                "Neurodivergence: Do you have experience and/or interest in working with individuals who are neurodivergent? "
            ),
            performing=parce_bool(
                fields.get(
                    "Performing/Visual Arts: Do you currently participate / have participated in any performing or visual art activities?"
                )
            ),
            program=fields.get("Program"),
            religion=fields.get(
                "Religion: Please select the religions you have experience working with and/or understanding of. "
            ),
            experience_with_risk_clients=fields.get(
                "Risk: Do you have experience and/or interest in working with higher-risk clients? "
            ),
            working_with_lgbtq_clients=fields.get(
                "Sexual Orientation: Do you have experience and/or interest in working with individuals who are part of the LGBTQ+ community?"
            ),
            negative_affect_by_social_media=parce_bool(
                fields.get(
                    "Social Media: Have you ever been negatively affected by social media?"
                )
            ),
            specialities=fields.get(
                "Specialities: Please select any specialities you have experience and/or interest in working with. "
            ),
            states=fields.get("States"),
            therapeutic_orientation=fields.get(
                "Therapeutic Orientation: Please select the modalities you most frequently utilize. "
            ),
            family_household=fields.get(
                "Traditional vs. Non-traditional family household"
            ),
        )


class Therapists(BaseModel):
    therapists: list[Therapist]
