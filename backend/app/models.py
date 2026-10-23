from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, Text, DateTime, ForeignKey, Boolean, JSON, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(300))
    role: Mapped[str] = mapped_column(String(32))
    institution_id: Mapped[int | None] = mapped_column(ForeignKey('institutions.id'), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Institution(Base):
    __tablename__ = 'institutions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(300))
    code: Mapped[str] = mapped_column(String(80), unique=True)
    address_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)

class Application(Base):
    __tablename__ = 'applications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    institution_id: Mapped[int] = mapped_column(ForeignKey('institutions.id'), index=True)
    category: Mapped[str] = mapped_column(String(120))
    year: Mapped[int] = mapped_column(Integer)
    state: Mapped[str] = mapped_column(String(80), default='Submitted')
    submitted: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ApplicationSnapshot(Base):
    __tablename__ = 'application_snapshots'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    year: Mapped[int] = mapped_column(Integer)
    fields: Mapped[dict] = mapped_column(JSON, default=dict)

class Document(Base):
    __tablename__ = 'documents'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'), index=True)
    kind: Mapped[str] = mapped_column(String(100), default='other')
    name: Mapped[str] = mapped_column(String(250))
    path: Mapped[str] = mapped_column(Text)
    mime: Mapped[str] = mapped_column(String(120))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    perceptual_hash: Mapped[str | None] = mapped_column(String(32))
    expiry: Mapped[str | None] = mapped_column(String(15))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    processing_status: Mapped[str] = mapped_column(String(30), default='complete')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ExtractedField(Base):
    __tablename__ = 'extracted_fields'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey('documents.id'), index=True)
    key: Mapped[str] = mapped_column(String(100))
    value: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    page: Mapped[int] = mapped_column(Integer, default=1)
    bbox: Mapped[list] = mapped_column(JSON, default=list)
    corrected: Mapped[bool] = mapped_column(Boolean, default=False)

class Claim(Base):
    __tablename__ = 'claims'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    key: Mapped[str] = mapped_column(String(120))
    value: Mapped[str] = mapped_column(Text)
    source_field_id: Mapped[int | None] = mapped_column(ForeignKey('extracted_fields.id'))

class GraphNode(Base):
    __tablename__ = 'graph_nodes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    entity_type: Mapped[str] = mapped_column(String(60))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(250))
    data: Mapped[dict] = mapped_column(JSON, default=dict)

class GraphEdge(Base):
    __tablename__ = 'graph_edges'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    source_id: Mapped[int] = mapped_column(ForeignKey('graph_nodes.id'))
    target_id: Mapped[int] = mapped_column(ForeignKey('graph_nodes.id'))
    relationship: Mapped[str] = mapped_column(String(55))
    data: Mapped[dict] = mapped_column(JSON, default=dict)

class Rule(Base):
    __tablename__ = 'rules'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(100), unique=True)
    category: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

class RuleVersion(Base):
    __tablename__ = 'rule_versions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey('rules.id'))
    version: Mapped[int] = mapped_column(Integer)
    effective_from: Mapped[str] = mapped_column(String(12))
    severity: Mapped[str] = mapped_column(String(30), default='Medium')
    specification: Mapped[dict] = mapped_column(JSON, default=dict)
    source_citation: Mapped[str] = mapped_column(Text, default='SAMPLE / DEMO RULE')
    __table_args__ = (UniqueConstraint('rule_id', 'version'),)

class Finding(Base):
    __tablename__ = 'findings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'), index=True)
    title: Mapped[str] = mapped_column(String(240))
    category: Mapped[str] = mapped_column(String(60))
    severity: Mapped[str] = mapped_column(String(20))
    reason: Mapped[str] = mapped_column(Text)
    next_action: Mapped[str] = mapped_column(Text)
    rule_id: Mapped[str] = mapped_column(String(100))
    rule_version: Mapped[int] = mapped_column(Integer)
    source_a: Mapped[dict] = mapped_column(JSON, default=dict)
    source_b: Mapped[dict] = mapped_column(JSON, default=dict)
    official_status: Mapped[str] = mapped_column(String(60), default='PENDING')
    consistency_status: Mapped[str] = mapped_column(String(60), default='NOT_CHECKED')
    ai_status: Mapped[str] = mapped_column(String(60), default='NOT_EVALUATED')
    manual_status: Mapped[str] = mapped_column(String(60), default='PENDING_REVIEW')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class FindingEvidence(Base):
    __tablename__ = 'finding_evidence'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey('findings.id'))
    document_id: Mapped[int | None] = mapped_column(ForeignKey('documents.id'))
    field_id: Mapped[int | None] = mapped_column(ForeignKey('extracted_fields.id'))
    page: Mapped[int] = mapped_column(Integer, default=1)
    bbox: Mapped[list] = mapped_column(JSON, default=list)
    side: Mapped[str] = mapped_column(String(10), default='A')

class Verification(Base):
    __tablename__ = 'verifications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    document_id: Mapped[int | None] = mapped_column(ForeignKey('documents.id'))
    source: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(60))
    simulated: Mapped[bool] = mapped_column(Boolean, default=True)
    detail: Mapped[str] = mapped_column(Text)
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class ReviewAction(Base):
    __tablename__ = 'review_actions'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    finding_id: Mapped[int] = mapped_column(ForeignKey('findings.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    action: Mapped[str] = mapped_column(String(60))
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)

class AuditEvent(Base):
    __tablename__ = 'audit_events'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(Integer)
    action: Mapped[str] = mapped_column(String(120))
    entity: Mapped[str] = mapped_column(String(120))
    before: Mapped[dict] = mapped_column(JSON, default=dict)
    after: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    prev_hash: Mapped[str] = mapped_column(String(64))
    hash: Mapped[str] = mapped_column(String(64))

class ChangeRecord(Base):
    __tablename__ = 'change_records'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    key: Mapped[str] = mapped_column(String(120))
    old_value: Mapped[str] = mapped_column(Text)
    new_value: Mapped[str] = mapped_column(Text)
    explained: Mapped[bool] = mapped_column(Boolean, default=False)
    explanation: Mapped[str] = mapped_column(Text, default='')
    evidence_required: Mapped[str] = mapped_column(Text, default='')

class Report(Base):
    __tablename__ = 'reports'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey('applications.id'))
    path: Mapped[str] = mapped_column(Text)
    kind: Mapped[str] = mapped_column(String(60))
    approved_by: Mapped[int | None] = mapped_column(ForeignKey('users.id'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
