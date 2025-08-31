from __future__ import annotations
from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Dict, Any

class Inputs(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

class Provenance(BaseModel):
    method: str
    fetched_at: str
    http_status: Optional[int] = None
    note: Optional[str] = None

class ProfileEvidence(BaseModel):
    platform: str
    url: Optional[str] = None
    handle: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    employer: Optional[str] = None
    education: Optional[str] = None
    links: List[str] = []
    emails: List[str] = []
    phones: List[str] = []
    confidence_local: float = 0.0
    provenance: Optional[Provenance] = None
    raw: Dict[str, Any] = {}

class PairScores(BaseModel):
    name: float = 0.0
    bio: float = 0.0
    employer: float = 0.0
    education: float = 0.0
    links: float = 0.0
    location: float = 0.0
    avatar: float = 0.0
    email: float = 0.0
    phone: float = 0.0
    total: float = 0.0

class ProfileMatch(BaseModel):
    i: int
    j: int
    scores: PairScores

class Cluster(BaseModel):
    profile_indices: List[int]
    cluster_confidence: float

class CaseResult(BaseModel):
    inputs: Inputs
    profiles: List[ProfileEvidence]
    matches: List[ProfileMatch]
    clusters: List[Cluster]