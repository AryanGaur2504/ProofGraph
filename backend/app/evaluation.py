"""Seed-label evaluation only; baseline data is user input, not measured by system."""
import json
from pathlib import Path
from sqlalchemy import select
from .models import Finding, Application, Document, ExtractedField
ROOT=Path(__file__).resolve().parents[1]

def evaluate(db):
    labels_file=ROOT/'evaluation_labels.json'
    if not labels_file.exists():
        return {'notice':'No evaluation labels. Run python seed.py first.','dataset':'SYNTHETIC DEMONSTRATION DATA'}
    labels=json.loads(labels_file.read_text())
    tp=fp=tn=fn=0; correct_class=total_class=correct_extract=total_extract=0
    for labeled in labels:
        app=db.get(Application,labeled['application_id'])
        if not app: continue
        found=db.scalars(select(Finding).where(Finding.application_id==app.id,Finding.manual_status!='SUPERSEDED')).all()
        predicted=bool(found); expected=bool(labeled['defect'])
        if predicted and expected: tp+=1
        elif predicted: fp+=1
        elif expected: fn+=1
        else: tn+=1
        docs=db.scalars(select(Document).where(Document.application_id==app.id)).all()
        for d in docs:
            if d.name not in labeled.get('expected_docs',{}): continue
            total_class+=1
            if d.kind==labeled['expected_docs'][d.name]: correct_class+=1
        for key,actual in labeled.get('expected_fields',{}).items():
            total_extract+=1
            candidates=[f.value for d in docs for f in db.scalars(select(ExtractedField).where(ExtractedField.document_id==d.id,ExtractedField.key==key))]
            if str(actual) in candidates: correct_extract+=1
    safe=lambda a,b: round(a/b,4) if b else None
    return {'dataset':'Prototype evaluation on labelled synthetic data only','cases':tp+fp+tn+fn,'confusion':{'TP':tp,'FP':fp,'TN':tn,'FN':fn},'classification_accuracy':safe(correct_class,total_class),'extraction_accuracy':safe(correct_extract,total_extract),'validation_accuracy':safe(tp+tn,tp+fp+tn+fn),'anomaly_precision':safe(tp,tp+fp),'anomaly_recall':safe(tp,tp+fn),'time_to_report_seconds':None,'baseline_review_minutes':None,'tool_review_minutes':None,'notes':'Timing values must be collected experimentally; no fabricated improvements. Precision/recall summarize seeded case-level flags, not real-world forgery detection.'}
