# Minimum relational entity model

```mermaid
erDiagram
  USERS ||--o{ REVIEW_ACTIONS : authors
  INSTITUTIONS ||--o{ APPLICATIONS : submits
  INSTITUTIONS ||--o{ USERS : owns
  APPLICATIONS ||--o{ APPLICATION_SNAPSHOTS : archives
  APPLICATIONS ||--o{ DOCUMENTS : includes
  DOCUMENTS ||--o{ EXTRACTED_FIELDS : contains
  APPLICATIONS ||--o{ CLAIMS : asserts
  EXTRACTED_FIELDS ||--o{ CLAIMS : supports
  APPLICATIONS ||--o{ GRAPH_NODES : graphs
  GRAPH_NODES ||--o{ GRAPH_EDGES : source
  GRAPH_NODES ||--o{ GRAPH_EDGES : target
  RULES ||--o{ RULE_VERSIONS : versions
  APPLICATIONS ||--o{ FINDINGS : flags
  FINDINGS ||--o{ FINDING_EVIDENCE : cites
  DOCUMENTS ||--o{ FINDING_EVIDENCE : located_in
  FINDINGS ||--o{ REVIEW_ACTIONS : reviewed_with
  APPLICATIONS ||--o{ VERIFICATIONS : records
  APPLICATIONS ||--o{ CHANGE_RECORDS : compares
  APPLICATIONS ||--o{ REPORTS : generates
  USERS ||--o{ REPORTS : approves
  USERS ||--o{ AUDIT_EVENTS : acts

  USERS { int id PK string username string role int institution_id FK }
  INSTITUTIONS { int id PK string code string name string address_encrypted }
  APPLICATIONS { int id PK int institution_id FK string category int year string state }
  APPLICATION_SNAPSHOTS { int id PK int application_id FK int year json fields }
  DOCUMENTS { int id PK int application_id FK string sha256 string perceptual_hash string path }
  EXTRACTED_FIELDS { int id PK int document_id FK string key string value float confidence json bbox }
  CLAIMS { int id PK int application_id FK string key string value int source_field_id FK }
  GRAPH_NODES { int id PK int application_id FK string entity_type json data }
  GRAPH_EDGES { int id PK int application_id FK int source_id FK int target_id FK string relationship }
  RULES { int id PK string rule_id string category }
  RULE_VERSIONS { int id PK int rule_id FK int version json specification }
  FINDINGS { int id PK int application_id FK string rule_id string official_status string consistency_status string ai_status string manual_status }
  FINDING_EVIDENCE { int id PK int finding_id FK int document_id FK int page json bbox }
  VERIFICATIONS { int id PK int application_id FK string status boolean simulated }
  REVIEW_ACTIONS { int id PK int finding_id FK int user_id FK string action string reason }
  AUDIT_EVENTS { int id PK string prev_hash string hash json before json after }
  CHANGE_RECORDS { int id PK int application_id FK string key string old_value string new_value boolean explained }
  REPORTS { int id PK int application_id FK string path int approved_by FK }
```

The evidence graph is relational, not a remote graph service: `graph_nodes` and `graph_edges` use the same SQLite file. The `neighborhood` helper in `backend/app/engine.py` demonstrates graph traversal with a SQLite recursive CTE.
