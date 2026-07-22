"""Portable rule-based ontology for short French trauma narratives.

The module normalizes a narrative, splits semicolon-delimited event blocks,
assigns non-mutually-exclusive semantic labels to each block, and aggregates
those labels to the participant level. It performs no clustering, modelling,
statistical testing, plotting, file I/O, or project-specific data handling.
"""

from __future__ import annotations

import re
import unicodedata
from collections import OrderedDict
from typing import Any, Iterable, Mapping

PREFIX = "trauma_"


NORMALIZATION_MAP: OrderedDict[str, str] = OrderedDict([
    (r"\bt\.?s\.?\b", "tentative suicide"),
    (r"\bts\b", "tentative suicide"),
    (r"\bptsd\b|\bespt\b", "stress post traumatique"),
    (r"\bavp\b", "accident voie publique"),
    (r"\btcc?\b", "traumatisme cranien"),
    (r"\bras\b", "rien a signaler"),
    (r"\bnr\b", "aucun trauma rapporte"),
    (r"\bna\b", "non disponible"),
    (r"\bnd\b", "non renseigne"),
])


PATTERNS: dict[str, tuple[str, ...]] = {
    "missing_unavailable": (
        r"^$", r"^non renseigne$", r"^non disponible$",
    ),
    "no_trauma_reported": (
        r"\bpas de notion de trauma\b", r"\bpas de trauma\b",
        r"\baucun trauma\b", r"\bpas de traumatisme\b",
        r"\brien a signaler\b", r"\baucun trauma rapporte\b",
        r"\bpas grand chose\b",
    ),
    "ctq_reference": (r"\bctq\b", r"\bselon ctq\b", r"\bctq montrant\b"),
    "uncertain": (r"\bpossible\b", r"\bpas clair\b", r"\ba verifier\b", r"\bnon evalue\b", r"\bamnesie\b"),
    "sexual_abuse": (
        r"\bviols?\b", r"\bviolee?s?\b", r"\btentative de viol\b",
        r"\babus sexuel(?:s|le|les)?\b", r"\baggressions? sexuelles?\b",
        r"\bagressions? sexuelles?\b", r"\bviolences? sexuelles?\b",
        r"\battouchements?\b", r"\bharcelement sexuel\b",
        r"\btrauma sexuel\b", r"\bsexual trauma\b", r"\binceste\b",
        r"\bpedophil(?:e|ie)\b", r"\bcomportement pedophile\b", r"\bexcision\b",
    ),
    "physical_abuse": (
        r"\bviolences? physiques?\b", r"\bmaltraitances? physiques?\b",
        r"\babus physiques?\b", r"\bagressions? physiques?\b",
        r"\bcoups\b", r"\betranglement\b", r"\bpere violent\b",
        r"\bmere violente\b", r"\bparents? violents?\b",
        r"\bfrere violent\b", r"\bsoeur violente\b",
    ),
    "emotional_abuse": (
        r"\bmaltraitance affective\b", r"\bmaltraitance emotionnelle\b",
        r"\bviolences? psychologiques?\b", r"\bperverse narciss",
        r"\belevee a la dure\b", r"\bpeur de son pere\b",
        r"\bmere alcoolique\b", r"\bpere alcoolique\b",
        r"\bmaltraitance maternelle\b",
    ),
    "neglect": (
        r"\bnegligence\b", r"\bcarence affective\b", r"\bsouvent seule\b",
        r"\bnon reconnue par son pere\b", r"\belevee seule\b", r"\babandon\b",
        r"\bseparee de sa mere\b", r"\bseparation avec la mere\b",
    ),
    "bullying_harassment": (
        r"\bharcelement\b", r"\bharcelement scolaire\b", r"\bmoqueries\b",
        r"\bexclusion\b", r"\bmis a l'ecart\b",
    ),
    "conjugal_violence": (
        r"\bviolences conjugales\b", r"\bconjugale\b", r"\bavec mari\b",
        r"\bpar le conjoint\b", r"\bseparation conjugale\b",
    ),
    "workplace_trauma": (
        r"\btrauma travail\b", r"\babus au travail\b", r"\bcentre de formation\b",
        r"\bburn ?out\b",
    ),
    "war_collective_violence": (r"\bguerres?\b", r"\bguerre civile\b", r"\battentats?\b", r"\barmee\b"),
    "accident_trauma": (
        r"\baccident voie publique\b", r"\baccident de voiture\b", r"\baccident\b",
        r"\btbi\b", r"\breanimation\b", r"\btraumatisme cranien\b",
    ),
    "institutional_adversity": (r"\bjuge pour enfants\b", r"\bdass\b", r"\bplacement\b"),
    "family_instability": (
        r"\bdivorce (?:des )?parents\b", r"\bseparation des parents\b",
        r"\bnon reconnue par son pere\b", r"\badoptee\b",
        r"\bproblemes? familiaux\b", r"\bconflits familiaux\b",
    ),
    "financial_adversity": (r"\bdifficultes financieres\b", r"\bpauvrete\b", r"\bprecarite\b"),
    "parental_illness_incapacity": (
        r"\bhospitalisation du pere\b", r"\bhospitalisation de la mere\b",
        r"\bcoma du pere\b", r"\bmaladie du pere\b", r"\bmaladie de la mere\b",
        r"\bpere a eu un avc\b", r"\bparents? depressifs?\b",
    ),
    "bereavement_loss": (
        r"\bdeces\b", r"\bdecede[e]?\b", r"\bdeuil\b", r"\bfausses couches\b",
        r"\bnombreux deces\b",
    ),
    "neurodevelopment_related_adversity": (
        r"\bautism", r"\btsa\b", r"\bneurodivergent\b",
        r"\bdevelopmental delay\b", r"\bretard de developpement\b",
    ),
    "repeated_chronic": (
        r"\brepete(?:s|e|es)?\b", r"\bmultiples\b", r"\bnombreux trauma\b",
        r"\bsevere\b", r"\bgraves\b", r"\+{3,}",
    ),
    "mother": (r"\bmere\b", r"\bbelle mere\b"),
    "father": (r"\bpere\b", r"\bbeau pere\b"),
    "sibling": (r"\bfrere\b", r"\bsoeurs?\b"),
    "extended_family": (r"\boncles?\b", r"\bcousin(?:e)?\b"),
    "partner": (r"\bmari\b", r"\bconjoint\b", r"\bcompagnon\b", r"\bcompagne\b"),
    "peer_school": (r"\bcamarade\b", r"\becole\b", r"\bprimaire\b", r"\bcollege\b", r"\bscolarite\b"),
}


FEATURE_HIERARCHY: OrderedDict[str, tuple[tuple[str, str], ...]] = OrderedDict({
    "Documentation": (
        ("trauma_missing_not_recorded", "Unavailable documentation"),
        ("trauma_no_trauma_reported", "No trauma reported"),
        ("trauma_any_adversity", "Any adversity identified"),
    ),
    "Timing": (
        ("trauma_timing_childhood_under18", "Childhood (<18 years)"),
        ("trauma_timing_adulthood_18plus", "Adulthood (>=18 years)"),
        ("trauma_timing_both_age_periods", "Both age periods"),
        ("trauma_timing_unknown", "Timing unknown"),
    ),
    "Exposure patterns": (
        ("trauma_childhood_interpersonal_trauma", "Childhood interpersonal trauma"),
        ("trauma_adult_interpersonal_trauma", "Adult interpersonal trauma"),
        ("trauma_repeated_chronic", "Repeated or chronic trauma"),
        ("trauma_complex_trauma", "Complex-trauma pattern"),
    ),
    "Sexual abuse": (
        ("trauma_sexual_abuse", "Any sexual abuse"),
        ("trauma_childhood_sexual_abuse", "Childhood sexual abuse"),
        ("trauma_family_context_sexual_abuse", "Family context in sexual-abuse segment"),
        ("trauma_father_in_sexual_abuse_segment", "Father mentioned in sexual-abuse segment"),
        ("trauma_mother_in_sexual_abuse_segment", "Mother mentioned in sexual-abuse segment"),
        ("trauma_sibling_in_sexual_abuse_segment", "Sibling mentioned in sexual-abuse segment"),
        ("trauma_extended_family_in_sexual_abuse_segment", "Extended family mentioned in sexual-abuse segment"),
    ),
    "Physical and emotional adversity": (
        ("trauma_physical_abuse", "Physical abuse"),
        ("trauma_childhood_physical_abuse", "Childhood physical abuse"),
        ("trauma_emotional_abuse", "Emotional abuse"),
        ("trauma_childhood_emotional_abuse", "Childhood emotional abuse"),
        ("trauma_neglect", "Neglect"),
        ("trauma_childhood_neglect", "Childhood neglect"),
    ),
    "Family and relational context": (
        ("trauma_contextual_family_adversity", "Contextual family adversity"),
        ("trauma_parental_abuse_direct", "Direct parental abuse"),
        ("trauma_family_violence_any", "Family violence"),
        ("trauma_witnessed_parental_violence", "Witnessed parental violence"),
        ("trauma_family_instability", "Family instability"),
        ("trauma_parental_illness_incapacity", "Parental illness or incapacity"),
        ("trauma_financial_adversity", "Financial adversity"),
        ("trauma_institutional_adversity", "Institutional adversity"),
    ),
    "Other adversity": (
        ("trauma_bullying_harassment", "Bullying or harassment"),
        ("trauma_conjugal_violence_experienced", "Experienced conjugal violence"),
        ("trauma_workplace_trauma", "Workplace trauma"),
        ("trauma_accident_trauma", "Accident-related trauma"),
        ("trauma_bereavement_loss", "Bereavement or loss"),
        ("trauma_war_collective_violence", "War or collective violence"),
        ("trauma_neurodevelopment_related_adversity", "Neurodevelopment-related adversity"),
    ),
})

FEATURE_LABELS = {
    feature: label
    for entries in FEATURE_HIERARCHY.values()
    for feature, label in entries
}


def _ascii(text: Any) -> str:
    if text is None:
        return ""
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode()


def normalize_text(text: Any) -> str:
    """Normalize case, accents, punctuation, whitespace, and study codes."""
    value = _ascii(text).lower()
    value = value.translate(str.maketrans({"’": "'", "‘": "'", "´": "'", "`": "'"}))
    value = re.sub(r"\s*;\s*", " ; ", value)
    value = re.sub(r"(?:;\s*){2,}", " ; ", value)
    value = re.sub(r"\s*,\s*", ", ", value)
    value = re.sub(r"\s*\.\s*", ". ", value)
    value = re.sub(r"\s*/\s*", " / ", value)
    for pattern, replacement in NORMALIZATION_MAP.items():
        value = re.sub(pattern, replacement, value)
    return re.sub(r"\s+", " ", value).strip()


def split_segments(text: Any) -> list[str]:
    """Return semicolon-delimited semantic event blocks."""
    return [part.strip(" .;,:/") for part in normalize_text(text).split(";") if part.strip(" .;,:/")]


def _has(text: str, key: str) -> bool:
    return any(re.search(pattern, text) for pattern in PATTERNS[key])


def extract_ages(text: str) -> list[int]:
    """Extract explicit ages expressed in years."""
    ages: list[int] = []
    for match in re.finditer(r"(?:age de|age|a l'?age de|a l'?age|a)\s*(\d{1,2})\s*ans", text):
        ages.append(int(match.group(1)))
    for pattern in (r"entre\s*(\d{1,2})\s*et\s*(\d{1,2})\s*ans", r"(\d{1,2})\s*a\s*(\d{1,2})\s*ans"):
        for match in re.finditer(pattern, text):
            ages.extend((int(match.group(1)), int(match.group(2))))
    return ages


def _timing(text: str) -> dict[str, int]:
    ages = extract_ages(text)
    childhood = _has_any(text, (
        r"\benfance\b", r"\benfant\b", r"\binfantile", r"\bnourrisson\b",
        r"\bbebe\b", r"\badolesc", r"\bado\b", r"\bprimaire\b",
        r"\bcollege\b", r"\blycee\b", r"\bscolarite\b", r"\bdass\b",
    )) or any(age < 18 for age in ages)
    adulthood = _has_any(text, (
        r"\badulte\b", r"\bage adulte\b", r"\bau travail\b", r"\bburn ?out\b",
        r"\bmari\b", r"\bconjoint\b", r"\bcompagnon\b", r"\bcompagne\b",
        r"\bviolences? conjugales?\b", r"\barmee\b", r"\bguerres?\b",
    )) or any(age >= 18 for age in ages)
    return {
        PREFIX + "timing_childhood_under18": int(childhood),
        PREFIX + "timing_adulthood_18plus": int(adulthood),
        PREFIX + "timing_both_age_periods": int(childhood and adulthood),
        PREFIX + "timing_unknown": int(not childhood and not adulthood),
        PREFIX + "n_age_mentions": len(ages),
    }


def _has_any(text: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text) for pattern in patterns)


def classify_segment(segment: Any) -> dict[str, int]:
    """Assign ontology indicators to one event block.

    Boolean combinations involving timing, trauma type, or relationship are
    deliberately calculated here, before participant-level aggregation.
    """
    text = normalize_text(segment)
    out: dict[str, int] = {}
    out[PREFIX + "missing_not_recorded"] = int(_has(text, "missing_unavailable"))
    out[PREFIX + "no_trauma_reported"] = int(_has(text, "no_trauma_reported"))
    out[PREFIX + "ctq_reference"] = int(_has(text, "ctq_reference"))
    out[PREFIX + "uncertain"] = int(_has(text, "uncertain"))

    types = (
        "sexual_abuse", "physical_abuse", "emotional_abuse", "neglect",
        "bullying_harassment", "conjugal_violence", "workplace_trauma",
        "war_collective_violence", "accident_trauma", "institutional_adversity",
        "family_instability", "financial_adversity", "parental_illness_incapacity",
        "bereavement_loss", "neurodevelopment_related_adversity", "repeated_chronic",
    )
    for key in types:
        out[PREFIX + key] = int(_has(text, key))

    relationships = ("mother", "father", "sibling", "extended_family", "partner", "peer_school")
    for key in relationships:
        out[PREFIX + key + "_mentioned"] = int(_has(text, key))
    out.update(_timing(text))

    child = bool(out[PREFIX + "timing_childhood_under18"])
    adult = bool(out[PREFIX + "timing_adulthood_18plus"])
    sex = bool(out[PREFIX + "sexual_abuse"])
    physical = bool(out[PREFIX + "physical_abuse"])
    emotional = bool(out[PREFIX + "emotional_abuse"])
    neglect = bool(out[PREFIX + "neglect"])
    family = any(out[PREFIX + key + "_mentioned"] for key in ("mother", "father", "sibling", "extended_family"))

    abuse_terms = r"\b(?:maltraitance|violence|abus)\b"
    out[PREFIX + "parental_abuse_direct"] = int(_has_any(text, (
        r"\bmaltraitance.*(?:pere|mere)\b", r"\bparents? violents?\b",
        r"\bpere violent\b", r"\bmere violente\b",
        r"\bpar (?:le pere|la mere)\b.*" + abuse_terms,
    )))
    out[PREFIX + "witnessed_parental_violence"] = int(_has_any(text, (
        r"\bdu pere sur la mere\b", r"\bviolence.*pere.*sur.*mere\b",
        r"\bviolences? familiales?\b",
    )))
    out[PREFIX + "conjugal_violence_experienced"] = int(_has(text, "conjugal_violence"))
    out[PREFIX + "family_violence_any"] = int(_has_any(text, (
        r"\bviolences? familiales?\b", r"\bparents? violents?\b",
        r"\bpere violent\b", r"\bmere violente\b", r"\bmaltraitance.*(?:pere|mere)\b",
    )))
    out[PREFIX + "childhood_family_violence_any"] = int(child and out[PREFIX + "family_violence_any"])

    out[PREFIX + "family_context_sexual_abuse"] = int(sex and family)
    for relation in ("father", "mother", "sibling", "extended_family"):
        out[PREFIX + relation + "_in_sexual_abuse_segment"] = int(
            sex and out[PREFIX + relation + "_mentioned"]
        )

    out[PREFIX + "childhood_sexual_abuse"] = int(sex and child)
    out[PREFIX + "childhood_physical_abuse"] = int(physical and child)
    out[PREFIX + "childhood_emotional_abuse"] = int(emotional and child)
    out[PREFIX + "childhood_neglect"] = int(neglect and child)
    out[PREFIX + "childhood_interpersonal_trauma"] = int(child and any((
        sex, physical, emotional, neglect,
        bool(out[PREFIX + "bullying_harassment"]),
        bool(out[PREFIX + "parental_abuse_direct"]),
        bool(out[PREFIX + "witnessed_parental_violence"]),
        bool(out[PREFIX + "family_violence_any"]),
    )))
    out[PREFIX + "adult_interpersonal_trauma"] = int(adult and any((
        sex, bool(out[PREFIX + "conjugal_violence_experienced"]),
        bool(out[PREFIX + "workplace_trauma"]),
    )))

    out[PREFIX + "bereavement_count"] = sum(bool(re.search(pattern, text)) for pattern in (
        r"\bmere decedee\b|\bdeces mere\b", r"\bpere decede\b|\bdeces pere\b",
        r"\bsoeur decedee\b|\bfrere decede\b", r"\bfausses couches\b", r"\bnombreux deces\b",
    ))
    out[PREFIX + "contextual_family_adversity"] = int(any(out[PREFIX + key] for key in (
        "family_instability", "financial_adversity", "parental_illness_incapacity",
        "bereavement_loss", "institutional_adversity", "family_violence_any",
    )))

    adversity_types = (
        "sexual_abuse", "physical_abuse", "emotional_abuse", "neglect",
        "bullying_harassment", "conjugal_violence", "war_collective_violence",
        "workplace_trauma", "accident_trauma", "bereavement_loss", "financial_adversity",
    )
    out[PREFIX + "n_adversity_types"] = sum(out[PREFIX + key] for key in adversity_types)
    out[PREFIX + "multiple_bereavements"] = int(out[PREFIX + "bereavement_count"] >= 2)
    out[PREFIX + "complex_trauma"] = int(any((
        out[PREFIX + "repeated_chronic"],
        out[PREFIX + "timing_both_age_periods"],
        out[PREFIX + "n_adversity_types"] >= 3,
        out[PREFIX + "childhood_interpersonal_trauma"] and out[PREFIX + "adult_interpersonal_trauma"],
    )))
    out[PREFIX + "any_adversity"] = int(any(out[PREFIX + key] for key in (
        "sexual_abuse", "physical_abuse", "emotional_abuse", "neglect",
        "bullying_harassment", "conjugal_violence", "workplace_trauma",
        "war_collective_violence", "accident_trauma", "institutional_adversity",
        "family_instability", "financial_adversity", "parental_illness_incapacity",
        "bereavement_loss", "neurodevelopment_related_adversity", "family_violence_any",
    )))

    if out[PREFIX + "missing_not_recorded"] or out[PREFIX + "no_trauma_reported"]:
        for feature in tuple(out):
            if feature not in {
                PREFIX + "missing_not_recorded", PREFIX + "no_trauma_reported",
                PREFIX + "ctq_reference", PREFIX + "uncertain",
            }:
                out[feature] = 0
    elif not out[PREFIX + "any_adversity"]:
        out[PREFIX + "timing_unknown"] = 0
    return out


COUNT_FEATURES = frozenset({
    PREFIX + "n_age_mentions", PREFIX + "bereavement_count", PREFIX + "n_adversity_types",
})


def aggregate_segments(segment_features: Iterable[Mapping[str, int]]) -> dict[str, int]:
    """Aggregate segment outputs to one participant-level feature mapping."""
    rows = list(segment_features)
    if not rows:
        return {
            PREFIX + "missing_not_recorded": 1,
            PREFIX + "no_trauma_reported": 0,
            PREFIX + "any_adversity": 0,
        }
    keys = set().union(*(row.keys() for row in rows))
    out = {
        key: (sum(int(row.get(key, 0)) for row in rows) if key in COUNT_FEATURES
              else max(int(row.get(key, 0)) for row in rows))
        for key in keys
    }

    # A missing or negative marker does not override a substantive event in
    # another segment. Participant-level composites may span distinct events.
    substantive = bool(out.get(PREFIX + "any_adversity", 0))
    out[PREFIX + "missing_not_recorded"] = int(
        not substantive and all(row.get(PREFIX + "missing_not_recorded", 0) for row in rows)
    )
    out[PREFIX + "no_trauma_reported"] = int(
        not substantive and not out[PREFIX + "missing_not_recorded"]
        and any(row.get(PREFIX + "no_trauma_reported", 0) for row in rows)
    )
    child = bool(out.get(PREFIX + "timing_childhood_under18", 0))
    adult = bool(out.get(PREFIX + "timing_adulthood_18plus", 0))
    out[PREFIX + "timing_both_age_periods"] = int(child and adult)
    out[PREFIX + "timing_unknown"] = int(substantive and not child and not adult)

    type_keys = (
        "sexual_abuse", "physical_abuse", "emotional_abuse", "neglect",
        "bullying_harassment", "conjugal_violence", "war_collective_violence",
        "workplace_trauma", "accident_trauma", "bereavement_loss", "financial_adversity",
    )
    out[PREFIX + "n_adversity_types"] = sum(bool(out.get(PREFIX + key, 0)) for key in type_keys)
    out[PREFIX + "multiple_bereavements"] = int(out.get(PREFIX + "bereavement_count", 0) >= 2)
    out[PREFIX + "complex_trauma"] = int(any((
        out.get(PREFIX + "repeated_chronic", 0),
        out[PREFIX + "timing_both_age_periods"],
        out[PREFIX + "n_adversity_types"] >= 3,
        out.get(PREFIX + "childhood_interpersonal_trauma", 0)
        and out.get(PREFIX + "adult_interpersonal_trauma", 0),
    )))
    return out


def classify_narrative(text: Any) -> dict[str, Any]:
    """Process one participant narrative and return an auditable result."""
    normalized = normalize_text(text)
    segments = split_segments(normalized)
    segment_features = [classify_segment(segment) for segment in segments]
    return {
        "normalized_text": normalized,
        "segments": segments,
        "segment_features": segment_features,
        "participant_features": aggregate_segments(segment_features),
    }


def feature_catalog() -> list[dict[str, str]]:
    """Return the public hierarchy as records suitable for documentation."""
    return [
        {"domain": domain, "feature": feature, "label": label}
        for domain, entries in FEATURE_HIERARCHY.items()
        for feature, label in entries
    ]


__all__ = [
    "FEATURE_HIERARCHY", "FEATURE_LABELS", "NORMALIZATION_MAP", "PATTERNS",
    "aggregate_segments", "classify_narrative", "classify_segment",
    "extract_ages", "feature_catalog", "normalize_text", "split_segments",
]
