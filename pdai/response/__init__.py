import datetime
from typing import ClassVar, Dict, List, Union

from pydantic import BaseModel, Field, field_validator, ConfigDict
from pydantic_core.core_schema import ValidationInfo


class QAResponseCategory(BaseModel):
    UNKNOWN_LABEL: ClassVar[str] = "UNKNOWN"
    LABEL_SPACE: ClassVar[Dict] = {
        "ASSESSMENT OR TIME POINT COMPLETION": [
            "OUT OF WINDOW - PK COLLECTION",
            "OUT OF WINDOW - TREATMENT ADMINISTRATION",
            "OUT OF WINDOW - BIOMARKER COLLECTION OR EXPLORATORY ASSESSMENT",
            "OUT OF WINDOW - EFFICACY ASSESSMENT",
            "OUT OF WINDOW - ECG",
            "OUT OF WINDOW - VITAL SIGNS",
            "OUT OF WINDOW - BLOODS LOCAL",
            "OUT OF WINDOW - BLOODS CENTRAL," "OUT OF WINDOW - OTHER",
            "MISSED ASSESMENT - PK COLLECTION",
            "MISSED ASSESMENT - TREATMENT ADMINISTRATION",
            "MISSED ASSESMENT - BIOMARKER COLLECTION OR EXPLORATORY ASSESSMENT",
            "MISSED ASSESMENT - EFFICACY ASSESSMENT",
            "MISSED ASSESMENT - ECG",
            "MISSED ASSESMENT- VITAL SIGNS",
            "MISSED ASSESMENT - BLOODS LOCAL",
            "MISSED ASSESMENT - BLOODS CENTRAL",
            "MISSED ASSESSMENT - OTHER",
            "ASSESSMENT NOT PROPERLY PERFORMED",
            "ASSESSMENT PERFORMED OUT OF ORDER",
            "INCOMPLETE ASSESSMENT",
            "OTHER ASSESSMENT OR TIME POINT WINDOW",
        ],
        "ELIGIBILITY CRITERIA NOT MET": ["ELIGIBILITY CRITERIA NOT MET"],
        "EXCLUDED MEDICATION, VACCINE OR DEVICE": [
            "MEDICATIION EXCLUDED BY THE PROTOCOL WAS ADMINISTERED",
            "VACCINE EXCLUDED BY THE PROTOCOL WAS ADMINISTERED",
            "DEVICE EXCLUDED BY THE PROTOCOL WAS ADMINISTERED",
            "OTHER EXCLUDED MEDICATION VACCINE OR DEVICE DEVIATION",
        ],
        "FAILURE TO REPORT SAFETY EVENTS PER PROTOCOL": [
            "SAE NOT REPORTED WITHIN THE EXPECTED TIME FRAME",
            "AES OF SPECIAL INTEREST",
            "FAILURE TO CONFIRM CAUSALITY ASSESSMENT WITHIN THE EXPECTED TIME FRAME",
            "LIVER FUNCTION ABNORMALITIES PER PROTOCOL",
            "PREGNANCY",
            "OTHER",
        ],
        "INFORMED CONSENT": [
            "INFORMED CONSENT/ASSENT NOT SIGNED AND/OR DATED BY SUBJECT (PARENT/LEGAL REPRESENTATIVE IF APPLICABLE)",
            "INFORMED CONSENT/ASSENT NOT SIGNED AND/OR DATED BY APPROPRIATE SITE STAFF",
            "INFORMED CONSENT/ASSENT NOT SIGNED PRIOR TO ANY STUDY PROCEDURE",
            "SIGNED INFORMED CONSENT/ASSENT NOT AVAILABLE ON SITE",
            "WRONG INFORMED CONSENT/ASSENT VERSION SIGNED",
            "OTHER INFORMED CONSENT/ASSENT DEVIATION",
        ],
        "NOT WITHDRAWN AFTER DEVELOPING WITHDRAWAL CRITERIA": [
            "NOT DISCONTINUED FROM STUDY TREATMENT",
            "NOT WITHDRAWN FROM STUDY",
            "OTHER DEVIATION OF NOT BEING WITHDRAWN AFTER DEVELOPING WITHDRAWAL CRITERIA",
        ],
        "SITE LEVEL ERROR": [
            "ERRORS IN DELEGATION  LOG COMPLETION",
            "ERRORS IN SITE FILE COMPLETION",
            "ERRORS IN DOCUMENTATION FOR TRAINING",
            "OTHER SITE LEVEL DOCUMENTATION ERRORS",
        ],
        "STUDY PROCEDURE": [
            "ACTIVITY LEVEL ABOVE PROTOCOL SPECIFICATION",
            "BIOLOGICAL SAMPLE SPECIMEN PROCEDURE",
            "DECLINED PARTICIPATION IN STUDY PROCEDURE",
            "DIARY PROCEDURE",
            "DISCONTINUED PARTICIPATION IN STUDY PROCEDURE",
            "EQUIPMENT PROCEDURE",
            "NON STUDY TREATMENT SUPPLY PROCEDURE",
            "NONCOMPLIANCE WITH STUDY PROCEDURE",
            "POST STUDY TREATMENT OBSERVATION NOT DONE",
            "RANDOMIZATION PROCEDURE (E.G. SUBJECT ASSIGNED TO WRONG STRATUM SUBJECT RANDOMIZED OUT OF ORDER)",
            "STUDY BLINDING/UNBLINDING PROCEDURE",
            "OTHER DEVIATION FROM STUDY PROCEDURE",
        ],
        "VISIT COMPLETION": [
            "MISSED VISIT/PHONE CONTACT",
            "OUT OF WINDOW - VISIT/PHONE CONTACT",
            "OTHER VISIT WINDOW DEVIATION",
        ],
        "WRONG STUDY TREATMENT/ADMINISTRATION/DOSE": [
            "EXPIRED STUDY TREATMENT ADMINISTERED",
            "STUDY TREATMENT ADMINISTERED WHILE CONTRAINDICATION",
            "STUDY TREATMENT NOT ADMINISTERED PER PROTOCOL",
            "STUDY TREATMENT NOT AVAILABLE AT SITE FOR ADMINISTRATION",
            "STUDY TREATMENT NOT PREPARED AS PER PROTOCOL (E.G. RECONSTITUTION)",
            "USE OF STUDY TREATMENT IMPACTED BY TEMPERATURE EXCURSION - NOT REPORTED/APPROVED/DISAPPROVED FOR FURTHER USE",
            "WRONG STUDY TREATMENT OR ASSIGNMENT ADMINISTERED",
            "OTHER DEVIATION RELATED TO WRONG STUDY TREATMENT/ADMINISTRATION/DOSE",
        ],
    }

    dvcat: str = Field(default=...)
    dvdecod: str = Field(default=...)
    probability: float = Field(default=...)

    @field_validator("dvcat")
    def validate_dvcat(cls, value: str):
        if value.upper() not in cls.LABEL_SPACE:
            raise ValueError(
                f"Invalid dvcat <{value}>. Accepted values include {list(cls.LABEL_SPACE.keys())}."
            )
        return value

    @field_validator("dvdecod")
    def validate_dvdecod(cls, value, info: ValidationInfo):
        dvcat = info.data.get("dvcat", None)
        if dvcat is None:
            raise ValueError(
                f"Undefined dvcat <{value}>. Accepted values include {list(cls.LABEL_SPACE.keys())}."
            )

        try:
            if value.upper() not in cls.LABEL_SPACE.get(dvcat, []):
                raise ValueError(
                    f"Invalid dvdecod <{value}>. Accepted values include {cls.LABEL_SPACE[dvcat]}"
                )
        except KeyError:
            # raise ValueError(
            #     f"Invalid dvcat <{dvcat}>. Accepted values include {list(cls.LABEL_SPACE.keys())}."
            # )
            value = cls.UNKNOWN_LABEL
        return value

    @field_validator("probability")
    def validate_proba(cls, value: float):
        if value < 0 or value > 1:
            raise ValueError(
                f"Invalid probabilistic value {value}. Should be between 0 and 1."
            )
        return value


class QAResponse(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    dvspondes: str = Field(default=...)
    categories: List[Union[Dict, QAResponseCategory]] = Field(default_factory=list)
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now().ctime())

    @field_validator("categories")
    def validate_categories(cls, value: List):
        validated_categories = []
        for cat in value:
            try:
                if isinstance(cat, dict):
                    cat = QAResponseCategory.parse_obj(cat)
            except ValueError as e:
                raise ValueError(
                    f"Failed to parse {cat} as a QAResponseCategory! Details: {str(e)}"
                )
            validated_categories.append(cat)
        validated_categories = sorted(
            validated_categories, key=lambda cat: cat.probability, reverse=True
        )
        return validated_categories
