# Trauma Narrative Semantic Ontology

## Purpose

This ontology supports reproducible, rule-based characterization of clinician-recorded trauma narratives in functional neurological disorder (FND). It converts short, unstructured French-language clinical descriptions into interpretable semantic indicators while preserving the existing clinical clusters. The narrative analysis does not perform additional dimensionality reduction or patient reclustering.

## Unit of analysis

The participant remains the statistical unit. Within each participant record, semicolons are treated as boundaries between clinically distinct event descriptions. Each resulting segment is analyzed as an independent semantic block before its labels are aggregated to the participant level.

```text
Participant narrative
└── Semicolon-delimited event segments
    └── Segment-level semantic labels
        ├── Timing
        ├── Trauma type
        ├── Relationship context
        └── Within-segment combinations
            └── Participant-level aggregation
                ├── Presence of each semantic feature
                ├── Number of adversity types
                └── Cross-event composite profiles
```

This structure permits multiple related labels within one event while preventing associations across unrelated events. For example, childhood timing in one segment is not transferred to a separate adult event.

## Ontology structure

```text
Trauma Narrative Ontology
│
├── Documentation status
│   ├── Not recorded
│   ├── No trauma reported
│   ├── Uncertain documentation
│   ├── CTQ referenced
│   └── Any adversity identified
│
├── Timing
│   ├── Infancy
│   ├── Childhood
│   ├── Adolescence
│   ├── Adulthood
│   ├── Multiple developmental periods [derived]
│   └── Unknown timing
│
├── Trauma type
│   ├── Sexual abuse
│   ├── Physical abuse
│   ├── Emotional abuse
│   ├── Neglect
│   ├── Bullying or harassment
│   ├── Conjugal violence
│   ├── Accident-related trauma
│   ├── Bereavement or loss
│   ├── War or collective violence
│   └── Workplace trauma
│
├── Relationship context
│   ├── Father mentioned
│   ├── Mother mentioned
│   ├── Sibling mentioned
│   ├── Extended family mentioned
│   ├── Partner mentioned
│   └── Peer or school mentioned
│
├── Family and social context
│   ├── Direct parental abuse
│   ├── Family violence
│   ├── Witnessed parental violence
│   ├── Experienced conjugal violence
│   ├── Family instability
│   ├── Parental illness or incapacity
│   ├── Financial adversity
│   ├── Institutional adversity
│   └── Neurodevelopment-related adversity
│
├── Developmentally specific profiles [derived within segment]
│   ├── Childhood sexual abuse
│   ├── Childhood physical abuse
│   ├── Childhood emotional abuse
│   ├── Childhood neglect
│   ├── Childhood family violence
│   ├── Childhood interpersonal trauma
│   └── Adult interpersonal trauma
│
├── Sexual-abuse relationship context [derived within segment]
│   ├── Family-associated sexual abuse
│   ├── Father in sexual-abuse narrative
│   ├── Mother in sexual-abuse narrative
│   ├── Sibling in sexual-abuse narrative
│   └── Extended family in sexual-abuse narrative
│
└── Participant-level composite profiles [derived across segments]
    ├── Number of adversity types
    ├── Repeated or chronic trauma
    ├── Multiple developmental periods
    ├── Contextual family adversity
    ├── Multiple bereavements
    └── Complex trauma
```

## Semantic domains

| Domain | Included concepts |
|---|---|
| Documentation status | Not recorded, no trauma reported, uncertainty, CTQ reference, and any identified adversity |
| Timing | Infancy, childhood, adolescence, adulthood, multiple periods, and unknown timing |
| Trauma type | Sexual, physical, and emotional abuse; neglect; bullying; conjugal violence; accidents; bereavement; war; and workplace trauma |
| Relationship context | Father, mother, sibling, extended family, partner, and peer or school references |
| Family and social context | Parental and family violence, witnessed violence, family instability, parental incapacity, financial adversity, institutional adversity, and neurodevelopment-related adversity |
| Derived profiles | Developmentally specific trauma, interpersonal trauma, repeated adversity, contextual family adversity, and complex trauma |

Broad-domain presence is defined as the occurrence of at least one constituent semantic indicator. Domains and individual labels are not mutually exclusive.

## Example of multilabel extraction

The segment:

> Physical and emotional abuse by father during childhood

is represented as:

```text
Childhood
├── Physical abuse
├── Emotional abuse
├── Father mentioned
├── Direct parental abuse
├── Childhood physical abuse
├── Childhood emotional abuse
└── Childhood interpersonal trauma
```

If a participant instead reports:

> Physical abuse during childhood; sexual assault by a partner at age 25

the two events are processed independently. Childhood timing is attached only to the first segment, while adulthood, sexual abuse, and partner context are attached to the second.

## Derivation rules

### Segment-level rules

1. Text is lowercased, accents and punctuation are normalized, and predefined clinical abbreviations are expanded.
2. Semicolons divide the narrative into event-level semantic blocks.
3. Trauma type, timing, and relationship indicators are extracted independently within each segment.
4. Derived combinations are created only when the required concepts occur within the same segment. For example, `childhood physical abuse` requires both childhood timing and physical abuse within that event block.
5. A segment may receive multiple labels.

### Participant-level rules

1. Binary segment indicators are aggregated using presence across any segment.
2. Count variables, such as age mentions and bereavement counts, are summed.
3. The number of adversity types is calculated from distinct participant-level trauma-type indicators.
4. Multiple developmental periods are present when events span at least two life periods.
5. Complex trauma is identified when at least one of the following is present:
   - repeated or chronic trauma;
   - trauma across multiple developmental periods;
   - at least three adversity types; or
   - both childhood and adult interpersonal trauma.

## Documentation status and denominators

Documentation status is kept separate from trauma content:

| Source value | Interpretation |
|---|---|
| Empty, `NR`, `NA`, `ND`, or `non renseigné` | Not recorded |
| `RAS`, `rien à signaler`, `pas de trauma`, or equivalent | Evaluated with no trauma reported |
| Substantive event description | Evaluable trauma documentation |

Documentation completeness is reported using the full clustered sample. Semantic-feature prevalence is calculated only among participants with evaluable trauma documentation, both overall and within each cluster.

## Sexual-abuse relationship context

Relationship indicators are linked to childhood sexual abuse only when they occur within the same semantic segment. The current rule-based system detects within-segment co-occurrence; it does not establish grammatical agency or independently confirm perpetrator identity. Accordingly, these outputs are described as **relationship context in sexual-abuse narratives** until manually verified against the source record.

```text
Childhood sexual abuse
├── Father in same segment
├── Mother in same segment
├── Sibling in same segment
├── Extended family in same segment
├── Partner in same segment
├── Peer or school context in same segment
└── Unspecified relationship
```

A participant may be represented in more than one relationship category when multiple events or relationships are documented.

## Interpretation

The ontology produces descriptive semantic indicators rather than validated diagnostic classifications. Cluster comparisons characterize the clinical narratives associated with existing data-derived profiles; they do not independently validate the clusters. Sensitive derived indicators, particularly relationship-specific sexual-abuse categories, should undergo manual review before publication.

## Data protection

Only ontology code, documentation, and synthetic examples should be published. Raw clinician narratives, participant identifiers, segment tables, and participant-level semantic outputs must not be committed to a public repository.

