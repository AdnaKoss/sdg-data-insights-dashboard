"""
Indicator catalogue and SDG mapping for the SDG Data Insights Dashboard.

Every indicator below is pulled from the World Bank Open Data API
(https://api.worldbank.org/v2/), which requires no API key and covers all
217 World Bank member/reporting economies back to the 1960s for most series.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

WORLD_BANK_API_BASE = "https://api.worldbank.org/v2"

# World Bank indicator code -> metadata used across the app (fetching,
# labelling charts, and building the policy brief narrative).
INDICATORS: dict[str, dict] = {
    "IT.NET.USER.ZS": {
        "name": "Internet users",
        "unit": "% of population",
        "category": "Digital Access",
        "sdg": "SDG 9.c",
        "sdg_label": "Universal access to ICT",
        "higher_is_better": True,
    },
    "IT.CEL.SETS.P2": {
        "name": "Mobile cellular subscriptions",
        "unit": "per 100 people",
        "category": "Digital Access",
        "sdg": "SDG 9",
        "sdg_label": "Industry, Innovation & Infrastructure",
        "higher_is_better": True,
    },
    "SE.ADT.LITR.ZS": {
        "name": "Adult literacy rate",
        "unit": "% of people ages 15+",
        "category": "Education",
        "sdg": "SDG 4.6",
        "sdg_label": "Literacy and numeracy",
        "higher_is_better": True,
    },
    "SE.SEC.ENRR": {
        "name": "Secondary school enrollment",
        "unit": "% gross",
        "category": "Education",
        "sdg": "SDG 4.1",
        "sdg_label": "Free, equitable quality education",
        "higher_is_better": True,
    },
    "SI.POV.DDAY": {
        "name": "Poverty headcount ratio",
        "unit": "% of population at $2.15/day (2017 PPP)",
        "category": "Poverty",
        "sdg": "SDG 1.1",
        "sdg_label": "Eradicate extreme poverty",
        "higher_is_better": False,
    },
    "NY.GDP.PCAP.CD": {
        "name": "GDP per capita",
        "unit": "current US$",
        "category": "Economy",
        "sdg": "SDG 8.1",
        "sdg_label": "Sustainable economic growth",
        "higher_is_better": True,
    },
    "SG.GEN.PARL.ZS": {
        "name": "Women in national parliaments",
        "unit": "% of seats held by women",
        "category": "Gender Equality",
        "sdg": "SDG 5.5",
        "sdg_label": "Women's full participation in leadership",
        "higher_is_better": True,
    },
}

# Subset of indicators used to build the "digital readiness" composite score
# that feeds the clustering model. Kept separate from INDICATORS so the
# composite's definition is explicit and easy to change.
DIGITAL_READINESS_INDICATORS = [
    "IT.NET.USER.ZS",
    "IT.CEL.SETS.P2",
    "SE.ADT.LITR.ZS",
    "SE.SEC.ENRR",
]

DEFAULT_INDICATOR = "IT.NET.USER.ZS"

YEAR_START = 2000
YEAR_END = 2024

CLUSTER_LABELS = ["Emerging", "Advancing", "Established", "Digital Leaders"]
N_CLUSTERS = 4
