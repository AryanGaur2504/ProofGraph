import hashlib, json
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import AuditEvent, now

def canonical(ev):
    return json.dumps({'user_id':ev.user_id,'action':ev.action,'entity':ev.entity,'before':ev.before,'after':ev.after,'created_at':ev.created_at.replace(tzinfo=None).isoformat(),'prev_hash':ev.prev_hash}, sort_keys=True, separators=(',',':'), ensure_ascii=False)

def write_audit(db: Session, user_id, action, entity, before=None, after=None):
    last = db.scalars(select(AuditEvent).order_by(AuditEvent.id.desc()).limit(1)).first()
    ev = AuditEvent(user_id=user_id, action=action, entity=entity, before=before or {}, after=after or {}, created_at=now(), prev_hash=last.hash if last else 'GENESIS')
    ev.hash = hashlib.sha256(canonical(ev).encode()).hexdigest()
    db.add(ev)
    db.flush()
    return ev

def verify_audit(db: Session):
    previous = 'GENESIS'
    events = db.scalars(select(AuditEvent).order_by(AuditEvent.id)).all()
    for ev in events:
        expected = hashlib.sha256(canonical(ev).encode()).hexdigest()
        if ev.prev_hash != previous or ev.hash != expected:
            return {'valid':False,'checked':ev.id,'reason':f'Audit integrity mismatch at event {ev.id}'}
        previous = ev.hash
    return {'valid':True,'checked':len(events),'reason':'Integrity verified for stored chain (app-level tamper evidence only)'}
