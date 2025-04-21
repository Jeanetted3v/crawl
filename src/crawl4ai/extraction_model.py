from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class PartyEnum(Enum):
    PAP = "People's Action Party"
    WP = "Workers' Party"
    PSP = "Progress Singapore Party"
    SDP = "Singapore Democratic Party"
    RP = "Reform Party"


class Candidate(BaseModel):
    name: str
    party: str
    constituency: str
    bio: Optional[str] = None


class ExtractedParty(BaseModel):
    name: str
    candidates: List[Candidate] = []
    additional_info: Optional[str] = None


class ExtractedConstituency(BaseModel):
    name: str
    contesting_parties: List[str] = []
    candidates: List[Candidate] = []


class ExtractedElectionData(BaseModel):
    constituencies: List[ExtractedConstituency] = []

