# Data Sources Reference

This document inventories repository data assets and records verifiable structure, coverage, and provenance signals based on direct file/header inspection.

## data

**Location**
data/literature.db, data/literature.json

**Source**
Not explicitly identifiable from local file metadata; verify against project ingestion notes/scripts.

**Description**
1 sqlite/db file(s); sample tables from `data/literature.db`: analysis_runs, papers, papers_fts, papers_fts_config, papers_fts_data, papers_fts_docsize, papers_fts_idx 1 .json file(s); sample keys from `data/literature.json`: zotero_collection, pdf_folder, description; records=unknown

**Coverage**
- Time: Not explicit in filenames; verify in source metadata/content.
- Geography: Not explicit in inspected headers/keys.
- Unit of observation: Not explicit from inspected headers/keys.

**Caveats**
Provider/publication is not explicit in local metadata for this source group; verify provenance from ingestion scripts/notes before citation.


## Cross-Cutting Caveats

- Source attribution can be incomplete when provider/publication metadata is absent from local files; confirm against acquisition logs, scripts, or citations before publication use.
- Coverage summaries rely on inspected headers, sheet names, keys, and filename date patterns; validate against canonical source documentation for final claims.
- Mixed file formats and vintages can introduce schema drift and crosswalk inconsistencies; validate joins and harmonization assumptions before pooled analysis.
- Descriptive and predictive associations in these datasets do not establish causal effects without explicit identification design.

