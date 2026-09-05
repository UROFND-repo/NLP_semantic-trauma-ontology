# Trauma Narrative Semantic Ontology

<p align="left">
  <a href="https://creativecommons.org/licenses/by/4.0/">
    <img src="https://licensebuttons.net/l/by/4.0/88x31.png"
         alt="Creative Commons Attribution 4.0 International">
  </a>
</p>

This repository contains the rule-based trauma-narrative processing framework developed for the **UROFND clustering study**, an exploratory investigation of clinical heterogeneity in functional neurological disorder (FND). The framework was used post hoc to characterize short trauma-related narratives after the clinical profiles had already been identified. It does **not** perform dimensionality reduction, patient clustering, prediction, or diagnostic classification.

The reusable module converts brief, unstructured clinician descriptions into transparent semantic indicators describing documentation status, developmental timing, trauma or adversity type, relational context, family and social context, and derived trauma patterns. The public workflow contains no UROFND narratives, participant data, cluster assignments, prevalences, or study results.

## Explore the Ontology

| Resource | Purpose |
|---|---|
| [**Interactive Ontology Tree**](https://monteiro-sara.github.io/NLP_semantic-trauma-ontology/) | Explore the complete ontology as an interactive hierarchical tree |
| [**Ontology Tree Structure Markdown**](https://github.com/arasorietnom/NLP_semantic-trauma-ontology/blob/main/TRAUMA_ONTOLOGY.md?plain=1) | Complete semantic hierarchy, definitions, and derivation rules |
| [**Reproducible Python Code**](code/trauma_narrative_ontology.py) | Data-independent ontology implementation and public Python API |


## Objectives

The framework is intended to:

- standardize heterogeneous clinician-recorded trauma narratives;
- separate multiple events documented within one participant record;
- assign transparent, clinically interpretable semantic labels;
- retain valid co-occurrence between timing, trauma type, and relational context;
- prevent information from being transferred across unrelated events;
- aggregate event-level information into participant-level indicators; and
- support reproducible secondary analyses of brief clinical narratives.

## Methodological approach

The pipeline uses deterministic text processing and a predefined clinical ontology. It does not use Sentence-BERT or another embedding model to assign the published categorical indicators.

1. Text is lowercased and normalized for diacritics, punctuation, whitespace, and predefined clinical abbreviations.
2. Semicolons are treated as boundaries between distinct event descriptions.
3. Each segment is analyzed independently as a semantic block.
4. Lexical dictionaries and regular expressions identify documentation status, timing, adversity type, relational context, and family or social adversity.
5. Boolean composition rules generate derived indicators only when their required components occur within the same segment.
6. Segment-level indicators are aggregated to the participant level using OR logic for binary features and summation for true count variables.
7. Cross-event participant profiles are recalculated after aggregation.

The participant remains the final statistical unit. Any group comparisons, regression models, or visualizations are downstream analyses and are not part of the reusable ontology engine.

## Processing hierarchy

```text
Participant narrative
└── Text normalization
    └── Semicolon-delimited event segments
        └── Segment-level semantic labels
            ├── Documentation status
            ├── Developmental timing
            ├── Trauma/adversity type
            ├── Relationship context
            └── Family/social context
                └── Within-segment derivations
                    └── Participant-level aggregation
                        ├── Presence across any segment
                        ├── Number of adversity types
                        └── Cross-event composite profiles
```

Semantic labels are non-mutually exclusive. For example, one event may simultaneously encode childhood timing, physical abuse, emotional abuse, a parental reference, direct parental abuse, and childhood interpersonal trauma.

## Documentation status

Documentation status is handled separately from trauma content. The originating dataset used the following conventions:

| Source value | Interpretation | Analytical treatment |
|---|---|---|
| `NR` or an equivalent explicit negative statement | Participant reported no trauma | Evaluable negative; trauma indicators coded absent |
| `NA`, `ND`, an empty field, or equivalent | Information unavailable | Missing documentation; excluded from semantic-feature denominators |
| Substantive narrative | Evaluable documentation | Ontology extraction applied |

These mappings are corpus-specific and must be adapted when source systems use different codes.

## Semantic domains

The ontology covers:

- **developmental timing:** childhood (`<18` years), adulthood (`≥18` years), both periods, or unknown timing;
- **trauma/adversity type:** sexual, physical, and emotional abuse; neglect; bullying or harassment; conjugal violence; workplace trauma; accident-related trauma; bereavement or loss; and war or collective violence;
- **relationship context:** mother, father, sibling, extended family, partner, and peer or school references;
- **family/social context:** family violence and instability, witnessed parental violence, parental illness or incapacity, financial adversity, institutional adversity, and neurodevelopment-related adversity;
- **within-segment derivations:** childhood-specific abuse and neglect, childhood and adult interpersonal trauma, direct parental abuse, and family-associated sexual-abuse context; and
- **participant-level composites:** number of adversity types, repeated or chronic trauma, exposure across childhood and adulthood, contextual family adversity, multiple bereavements, and a study-defined complex-trauma profile.

Derived outputs are descriptive research variables rather than diagnoses or independently validated clinical classifications.

## Example of multilabel extraction

The segment:

```text
physical and emotional abuse by father during childhood
```

may be represented as:

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

```text
physical abuse during childhood; war exposure during childhood
```

the two segments are processed independently. Childhood timing is attached only to the first event, whereas adulthood, sexual abuse, and partner context are attached only to the second.


## Interpretation and validation

The ontology is deterministic and auditable, but rule-based extraction remains sensitive to wording, negation, ambiguity, spelling, and local documentation practices. Before reuse in another corpus:

1. verify the meanings of documentation codes;
2. adapt the lexical dictionaries to the target language and setting;
3. manually annotate an independent validation sample;
4. report precision, recall, and agreement for clinically important labels;
5. inspect false-positive and false-negative classifications; and
6. manually verify sensitive relational indicators before publication.


## Terms of use and attribution

The source code, ontology, documentation, and data-free visualization are made available for reuse, reproduction, and adaptation under the **Creative Commons Attribution 4.0 International licence (CC BY 4.0)**. Reusers may copy, redistribute, and adapt these materials for any lawful purpose, provided that appropriate credit is given, a link to the licence is supplied, and modifications are indicated.

Copyright and attribution notices must be retained in redistributed or adapted versions. Scholarly publications, presentations, software, or derivative ontologies that use or substantially adapt this framework should cite both the repository release used and the associated UROFND publication once available.

The licence applies only to the publicly released code, ontology, documentation, and synthetic examples. It does not grant access to or permission to reproduce the underlying clinical narratives or participant-level data.

CC BY 4.0 licence text: <https://creativecommons.org/licenses/by/4.0/>

## Citation

Until the associated UROFND manuscript has a final bibliographic record, please cite:

> Monteiro, S. (2026). *Trauma Narrative Semantic Ontology* (Version 1.0.0) [Computer software]. <https://github.com/arasorietnom/NLP_semantic-trauma-ontology/>

Please additionally cite the final UROFND clustering article:

> Monteiro, S., Maillard, A., Louis, E., Hentzen, C., Al Chare, I., Baltasis, S., Adrien, V., & Garcin, B. (2026). Towards a Multidimensional Exploration of Functional Neurological Disorder. Manuscript in submission. 
