from __future__ import annotations
from typing import List
from rapidfuzz import fuzz
from .models import ProfileEvidence, PairScores, ProfileMatch, Cluster

# Helper normalizers
import re

def norm(s: str | None) -> str:
    if not s:
        return ""
    s = s.lower()
    s = re.sub(r"[^\p{L}0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# Simple token overlap

def jaccard(a: str, b: str) -> float:
    A = set(norm(a).split())
    B = set(norm(b).split())
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

# Weight scheme
WEIGHTS = {
    "name": 0.30,
    "bio": 0.15,
    "employer": 0.15,
    "education": 0.10,
    "links": 0.15,
    "location": 0.10,
    "avatar": 0.05,
    "email": 0.30,   # add-on bonus (capped in total)
    "phone": 0.30,   # add-on bonus
}

EDGE_THRESHOLD = 65.0

# Compute pairwise score between two profiles

def score_pair(a: ProfileEvidence, b: ProfileEvidence) -> PairScores:
    s = PairScores()

    s.name = max(
        fuzz.WRatio(norm(a.display_name), norm(b.display_name)) / 100.0,
        fuzz.WRatio(norm(a.handle), norm(b.handle)) / 100.0,
    )
    s.bio = jaccard(a.bio or "", b.bio or "")
    s.employer = fuzz.WRatio(norm(a.employer), norm(b.employer)) / 100.0
    s.education = fuzz.WRatio(norm(a.education), norm(b.education)) / 100.0

    # links overlap
    links_a = set([norm(x) for x in (a.links or [])])
    links_b = set([norm(x) for x in (b.links or [])])
    s.links = (len(links_a & links_b) / len(links_a | links_b)) if (links_a or links_b) else 0.0

    # location token overlap (simple)
    s.location = jaccard(a.location or "", b.location or "")

    # avatar similarity (placeholder: if exact URL match)
    s.avatar = 1.0 if a.avatar_url and b.avatar_url and a.avatar_url == b.avatar_url else 0.0

    # email/phone exact matches → strong signals
    s.email = 1.0 if set(a.emails) & set(b.emails) else 0.0
    s.phone = 1.0 if set(a.phones) & set(b.phones) else 0.0

    base = (
        s.name * WEIGHTS["name"] +
        s.bio * WEIGHTS["bio"] +
        s.employer * WEIGHTS["employer"] +
        s.education * WEIGHTS["education"] +
        s.links * WEIGHTS["links"] +
        s.location * WEIGHTS["location"] +
        s.avatar * WEIGHTS["avatar"]
    )
    bonus = 0.0
    if s.email > 0: bonus += WEIGHTS["email"]
    if s.phone > 0: bonus += WEIGHTS["phone"]

    s.total = min(100.0, (base + bonus) * 100.0)
    return s

# Build all pair matches

def build_matches(profiles: List[ProfileEvidence]) -> List[ProfileMatch]:
    out: List[ProfileMatch] = []
    for i in range(len(profiles)):
        for j in range(i+1, len(profiles)):
            sc = score_pair(profiles[i], profiles[j])
            out.append(ProfileMatch(i=i, j=j, scores=sc))
    return out

# Simple clustering via thresholded graph components

def build_clusters(profiles: List[ProfileEvidence], matches: List[ProfileMatch]) -> List[Cluster]:
    # Build adjacency
    n = len(profiles)
    adj = {i: set() for i in range(n)}
    for m in matches:
        if m.scores.total >= EDGE_THRESHOLD:
            adj[m.i].add(m.j)
            adj[m.j].add(m.i)

    # DFS components
    seen = set()
    clusters: List[Cluster] = []
    for i in range(n):
        if i in seen: continue
        stack = [i]
        comp = []
        while stack:
            u = stack.pop()
            if u in seen: continue
            seen.add(u)
            comp.append(u)
            for v in adj[u]:
                if v not in seen:
                    stack.append(v)
        # cluster confidence: avg of edges among members (rough)
        if len(comp) == 1:
            conf = profiles[comp[0]].confidence_local * 100.0
        else:
            edges = []
            for a in range(len(comp)):
                for b in range(a+1, len(comp)):
                    # find match
                    i, j = comp[a], comp[b]
                    sc = next((m.scores.total for m in matches if (m.i==i and m.j==j) or (m.i==j and m.j==i)), 0.0)
                    edges.append(sc)
            conf = sum(edges)/len(edges) if edges else 0.0
        clusters.append(Cluster(profile_indices=comp, cluster_confidence=conf))
    return clusters