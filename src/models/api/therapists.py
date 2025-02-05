from pydantic import BaseModel


class Therapist(BaseModel):
    id: str
    intern_name: str
    age: str
    email: str

    availability: list[str]
    birth_order: str
    caretaker_role: bool | None
    caseload_tracker: str
    has_children: bool | None
    cohort: str
    diagnoses: list[str]
    ethnicity: list[str]
    gender: str
    gender_interest: str
    immigration_background: str
    lgbtq_part: bool | None
    culture: str
    places: str
    married: bool | None
    max_caseload: str
    neurodivergence: str
    performing: bool | None
    program: str
    religion: list[str] | None
    experience_with_risk_clients: str
    working_with_lgbtq_clients: str
    negative_affect_by_social_media: bool | None
    specialities: list[str]
    states: list[str]
    therapeutic_orientation: list[str]
    family_household: str

    video_link: str | None
    image_link: str | None

    def __init__(self, json: dict, **data):
        fields = json["fields"]

        def parce_bool(field: str) -> bool | None:
            if field.lower().__eq__("yes"):
                return True
            elif field.lower().__eq__("no"):
                return False
            else:
                return None

        super().__init__(
            id=json["id"],
            intern_name=fields["Intern Name"],
            age=fields["Age"],
            email=fields["Email"],
            availability=fields["Availability: When are you available to see clients?"],
            birth_order=fields["Birth Order"],
            caretaker_role=parce_bool(
                fields["Caretaker Role: Have you ever been in a caretaker role?"]
            ),
            caseload_tracker=fields["Caseload Tracker"],
            has_children=parce_bool(fields["Children: Do you have children?"]),
            cohort=fields["Cohort"],
            diagnoses=fields[
                "Diagnoses: Please select the diagnoses you have experience and/or interest in working with"
            ],
            ethnicity=fields["Ethnicity"],
            gender=fields["Gender"],
            gender_interest=fields[
                "Gender: Do you have experience and/or interest in working with individuals who do not identify as cisgender? (i.e. transgender, gender fluid, etc.) "
            ],
            immigration_background=fields["Immigration Background"],
            lgbtq_part=parce_bool(
                fields["LGBTQ+: Are you a part of the LGBTQ+ community?"]
            ),
            culture=fields["Individualist vs. Collectivist culture"],
            places=fields["Many places or only one or two places?"],
            married=parce_bool(fields["Marriage: Are you / have ever been married?"]),
            max_caseload=fields["Max Caseload"],
            neurodivergence=fields[
                "Neurodivergence: Do you have experience and/or interest in working with individuals who are neurodivergent? "
            ],
            performing=parce_bool(
                fields[
                    "Performing/Visual Arts: Do you currently participate / have participated in any performing or visual art activities?"
                ]
            ),
            program=fields["Program"],
            religion=fields.get(
                "Religion: Please select the religions you have experience working with and/or understanding of. "
            ),
            experience_with_risk_clients=fields[
                "Risk: Do you have experience and/or interest in working with higher-risk clients? "
            ],
            working_with_lgbtq_clients=fields[
                "Sexual Orientation: Do you have experience and/or interest in working with individuals who are part of the LGBTQ+ community?"
            ],
            negative_affect_by_social_media=parce_bool(
                fields[
                    "Social Media: Have you ever been negatively affected by social media?"
                ]
            ),
            specialities=fields[
                "Specialities: Please select any specialities you have experience and/or interest in working with. "
            ],
            states=fields["States"],
            therapeutic_orientation=fields[
                "Therapeutic Orientation: Please select the modalities you most frequently utilize. "
            ],
            family_household=fields["Traditional vs. Non-traditional family household"],
        )


class Therapists(BaseModel):
    therapists: list[Therapist]
