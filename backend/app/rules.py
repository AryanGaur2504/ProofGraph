import json
from datetime import date
from pathlib import Path
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import Rule, RuleVersion

PACK = Path(__file__).resolve().parents[1]/'rules'/'sample_rules.json'
def sample_pack(): return json.loads(PACK.read_text(encoding='utf-8'))
def install_rules(db:Session):
    pack=sample_pack()
    for record in pack['rules']:
        rule=db.scalars(select(Rule).where(Rule.rule_id==record['id'])).first()
        if rule: continue
        rule=Rule(rule_id=record['id'],category=record['category'],description=record['description'])
        db.add(rule); db.flush()
        db.add(RuleVersion(rule_id=rule.id,version=1,effective_from=pack['effective_from'],severity=record['severity'],specification=record['specification'],source_citation=record['source_citation']))
    db.flush()

def current_rules(db):
    rules=db.scalars(select(Rule)).all()
    effective_date=date.today().isoformat()
    return [{'id':r.rule_id,'description':r.description,'category':r.category,'version':v.version,'effective_from':v.effective_from,'severity':v.severity,'specification':v.specification,'source_citation':v.source_citation} for r in rules if (v:=db.scalars(select(RuleVersion).where(RuleVersion.rule_id==r.id,RuleVersion.effective_from<=effective_date).order_by(RuleVersion.version.desc())).first())]

def checklist(db, category):
    pack=sample_pack()
    return pack['categories'].get(category,pack['categories']['Extension of Approval'])
