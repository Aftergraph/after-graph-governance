#!/usr/bin/env python3
"""Provenance-aware compatibility graph for Aftergraph Release Intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from scripts.ari_model import ResultState, evidence_meets, validate_edge


@dataclass(frozen=True, slots=True)
class Endpoint:
    component: str
    version: str
    commit: str

    @classmethod
    def from_document(cls, document: dict) -> "Endpoint":
        return cls(
            component=document["component"],
            version=document["version"],
            commit=document["commit"],
        )


@dataclass(frozen=True, slots=True)
class CompatibilityEdge:
    source: Endpoint
    target: Endpoint
    relation: str
    state: str
    evidence_level: str
    evidence: tuple[tuple[str, str], ...]

    @classmethod
    def from_document(cls, document: dict) -> "CompatibilityEdge":
        errors = validate_edge(document)
        if errors:
            raise ValueError("; ".join(errors))
        return cls(
            source=Endpoint.from_document(document["from"]),
            target=Endpoint.from_document(document["to"]),
            relation=document["relation"],
            state=document["state"],
            evidence_level=document["evidence_level"],
            evidence=tuple((item["kind"], item["ref"]) for item in document["evidence"]),
        )


class CompatibilityGraph:
    def __init__(self, edge_documents: Iterable[dict] | None = None) -> None:
        self._edges: list[CompatibilityEdge] = []
        for document in edge_documents or ():
            self.add(document)

    def add(self, edge_doc: dict) -> None:
        self._edges.append(CompatibilityEdge.from_document(edge_doc))

    def between(self, left: Endpoint, right: Endpoint) -> list[CompatibilityEdge]:
        matches: list[CompatibilityEdge] = []
        for edge in self._edges:
            if edge.source == left and edge.target == right:
                matches.append(edge)
            elif edge.relation == "tested-with" and edge.source == right and edge.target == left:
                matches.append(edge)
        return matches

    def best_state(self, left: Endpoint, right: Endpoint, minimum_evidence: str) -> ResultState:
        edges = self.between(left, right)
        if not edges:
            return ResultState.UNKNOWN

        if any(edge.state == "fail" or edge.relation == "incompatible-with" for edge in edges):
            return ResultState.FAIL
        if any(edge.state == "stale" for edge in edges):
            return ResultState.STALE

        passing = [
            edge
            for edge in edges
            if edge.state == "pass" and evidence_meets(edge.evidence_level, minimum_evidence)
        ]
        if passing:
            return ResultState.PASS

        if all(edge.state == "not-applicable" for edge in edges):
            return ResultState.N_A

        return ResultState.UNKNOWN
