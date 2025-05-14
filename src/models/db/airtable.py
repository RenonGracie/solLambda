import json

from sqlalchemy import Boolean, Column, String, Text

from src.models.api.therapists import Therapist
from src.models.db.base import Base


class AirtableTherapist(Base):
    __tablename__ = "airtable_therapists"

    id = Column("id", String(100), primary_key=True)

    intern_name = Column("intern_name", Text)
    age = Column("age", String(50))
    email = Column("email", Text)
    calendar_email = Column("calendar_email", Text)
    accepting_new_clients = Column("accepting_new_clients", Boolean)
    biography = Column("biography", Text)
    _availability = Column("availability", Text)
    birth_order = Column("birth_order", String(100))
    caretaker_role = Column("caretaker_role", Boolean)
    caseload_tracker = Column("caseload_tracker", Text)
    has_children = Column("has_children", Boolean)
    cohort = Column("cohort", String(100))

    _diagnoses_specialities = Column("diagnoses_specialities", Text)
    _specialities = Column("diagnoses", Text)
    _diagnoses = Column("specialities", Text)

    _ethnicity = Column("ethnicity", Text)
    gender = Column("gender", String(100))
    identities_as = Column("identities_as", String(100))
    gender_interest = Column("gender_interest", Text)
    immigration_background = Column("immigration_background", String(100))
    lgbtq_part = Column("lgbtq_part", Boolean)
    culture = Column("culture", String(100))
    places = Column("places", String(100))
    married = Column("married", Boolean)
    max_caseload = Column("max_caseload", String(50))
    neurodivergence = Column("neurodivergence", Text)
    performing = Column("performing", Boolean)
    program = Column("program", Text)
    _religion = Column("religion", Text)
    experience_with_risk_clients = Column("experience_with_risk_clients", Text)
    working_with_lgbtq_clients = Column("working_with_lgbtq_clients", Text)
    negative_affect_by_social_media = Column("negative_affect_by_social_media", Boolean)
    _states = Column("states", Text)
    _therapeutic_orientation = Column("therapeutic_orientation", Text)
    family_household = Column("family_household", String(100))

    welcome_video_link = Column("welcome_video_link", Text)
    greetings_video_link = Column("greetings_video_link", Text)
    image_link = Column("image_link", Text)

    _available_slots = Column("available_slots", Text)

    @property
    def availability(self):
        return json.loads(self._availability or "[]")

    @availability.setter
    def availability(self, data):
        self._availability = json.dumps(data)

    @property
    def ethnicity(self):
        return json.loads(self._ethnicity or "[]")

    @ethnicity.setter
    def ethnicity(self, data):
        self._ethnicity = json.dumps(data)

    @property
    def religion(self):
        return json.loads(self._religion or "[]")

    @religion.setter
    def religion(self, data):
        self._religion = json.dumps(data)

    @property
    def diagnoses_specialities(self):
        if self._diagnoses_specialities:
            return json.loads(self._diagnoses_specialities or "[]")
        return json.loads(self._diagnoses or "[]") + json.loads(
            self._specialities or "[]"
        )

    @diagnoses_specialities.setter
    def diagnoses_specialities(self, data):
        self._diagnoses_specialities = json.dumps(data)

    @property
    def states(self):
        return json.loads(self._states or "[]")

    @states.setter
    def states(self, data):
        self._states = json.dumps(data)

    @property
    def therapeutic_orientation(self):
        return json.loads(self._therapeutic_orientation or "[]")

    @therapeutic_orientation.setter
    def therapeutic_orientation(self, data):
        self._therapeutic_orientation = json.dumps(data)

    @property
    def available_slots(self):
        return json.loads(self._available_slots or "[]")

    @available_slots.setter
    def available_slots(self, data):
        self._available_slots = json.dumps(data)

    def to_therapist(self) -> Therapist:
        """
        Convert AirtableTherapist instance to Therapist object.
        """
        from src.models.api.therapists import Therapist

        # Create a dictionary with all the fields
        therapist_dict = {
            "id": self.id,
            "intern_name": self.intern_name,
            "age": self.age,
            "email": self.email,
            "calendar_email": self.calendar_email,
            "accepting_new_clients": self.accepting_new_clients,
            "biography": self.biography,
            "availability": self.availability,
            "birth_order": self.birth_order,
            "caretaker_role": self.caretaker_role,
            "caseload_tracker": self.caseload_tracker,
            "has_children": self.has_children,
            "cohort": self.cohort,
            "diagnoses_specialities": self.diagnoses_specialities,
            "ethnicity": self.ethnicity,
            "gender": self.gender,
            "identities_as": self.identities_as,
            "gender_interest": self.gender_interest,
            "immigration_background": self.immigration_background,
            "lgbtq_part": self.lgbtq_part,
            "culture": self.culture,
            "places": self.places,
            "married": self.married,
            "max_caseload": self.max_caseload,
            "neurodivergence": self.neurodivergence,
            "performing": self.performing,
            "program": self.program,
            "religion": self.religion,
            "experience_with_risk_clients": self.experience_with_risk_clients,
            "working_with_lgbtq_clients": self.working_with_lgbtq_clients,
            "negative_affect_by_social_media": self.negative_affect_by_social_media,
            "states": self.states,
            "therapeutic_orientation": self.therapeutic_orientation,
            "family_household": self.family_household,
            "welcome_video_link": self.welcome_video_link,
            "greetings_video_link": self.greetings_video_link,
            "image_link": self.image_link,
            "available_slots": self.available_slots,
        }

        # Create and return a Therapist object
        return Therapist(json=therapist_dict, is_airtable=False)

    @classmethod
    def from_airtable(cls, airtable_data):
        therapist = cls()
        fields = airtable_data["fields"]

        def parse_bool(field):
            if not field:
                return None
            if field.lower() == "yes":
                return True
            if field.lower() == "no":
                return False
            return None

        diagnoses_specialities = fields.get("Diagnoses + Specialties") or []
        if diagnoses_specialities:
            diagnoses_specialities += (
                json.dumps(
                    fields.get(
                        "Diagnoses: Please select the diagnoses you have experience and/or interest in working with"
                    )
                )
                or []
            )
            diagnoses_specialities += (
                json.dumps(
                    fields.get(
                        "Specialities: Please select any specialities you have experience and/or interest in working with. "
                    )
                )
                or []
            )

        therapist.id = airtable_data["id"]
        therapist.intern_name = fields.get("Intern Name") or fields.get("Name")
        therapist.age = fields.get("Age")
        therapist.email = fields.get("Email") or fields.get("Notes")
        therapist.calendar_email = fields.get("Calendar")
        therapist.accepting_new_clients = parse_bool(
            fields.get("Accepting New Clients")
        )
        therapist.biography = fields.get("Intro Bios (Shortened)")
        therapist._availability = json.dumps(
            fields.get("Availability: When are you available to see clients?")
        )
        therapist.birth_order = fields.get("Birth Order")
        therapist.caretaker_role = parse_bool(
            fields.get("Caretaker Role: Have you ever been in a caretaker role?")
        )
        therapist.caseload_tracker = fields.get("Caseload Tracker")
        therapist.has_children = parse_bool(
            fields.get("Children: Do you have children?")
        )
        therapist.cohort = fields.get("Cohort")
        therapist._ethnicity = json.dumps(fields.get("Ethnicity"))
        therapist.gender = fields.get("Gender")
        therapist.identities_as = fields.get("Identities as (Gender)")
        therapist.gender_interest = fields.get(
            "Gender: Do you have experience and/or interest in working with individuals who do not identify as cisgender? (i.e. transgender, gender fluid, etc.) "
        )
        therapist.immigration_background = fields.get("Immigration Background")
        therapist.lgbtq_part = parse_bool(
            fields.get("LGBTQ+: Are you a part of the LGBTQ+ community?")
        )
        therapist.culture = fields.get("Individualist vs. Collectivist culture")
        therapist.places = fields.get("Many places or only one or two places?")
        therapist.married = parse_bool(
            fields.get("Marriage: Are you / have ever been married?")
        )
        therapist.max_caseload = fields.get("Max Caseload")
        therapist.neurodivergence = fields.get(
            "Neurodivergence: Do you have experience and/or interest in working with individuals who are neurodivergent? "
        )
        therapist.performing = parse_bool(
            fields.get(
                "Performing/Visual Arts: Do you currently participate / have participated in any performing or visual art activities?"
            )
        )
        therapist.program = fields.get("Program")
        therapist._religion = json.dumps(
            fields.get(
                "Religion: Please select the religions you have experience working with and/or understanding of. "
            )
        )
        therapist.experience_with_risk_clients = fields.get(
            "Risk: Do you have experience and/or interest in working with higher-risk clients? "
        )
        therapist.working_with_lgbtq_clients = fields.get(
            "Sexual Orientation: Do you have experience and/or interest in working with individuals who are part of the LGBTQ+ community?"
        )
        therapist.negative_affect_by_social_media = parse_bool(
            fields.get(
                "Social Media: Have you ever been negatively affected by social media?"
            )
        )
        therapist._diagnoses_specialities = diagnoses_specialities
        therapist._states = json.dumps(fields.get("States"))
        therapist._therapeutic_orientation = json.dumps(
            fields.get(
                "Therapeutic Orientation: Please select the modalities you most frequently utilize. "
            )
        )
        therapist.family_household = fields.get(
            "Traditional vs. Non-traditional family household"
        )
        therapist.welcome_video_link = fields.get("Welcome Video")
        therapist.greetings_video_link = fields.get("Greetings Video")

        return therapist
