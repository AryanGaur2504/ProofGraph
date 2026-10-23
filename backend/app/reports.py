from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.enums import TA_CENTER
from xml.sax.saxutils import escape


def build_report(case, kind='evidence', approved=False):
    buffer=BytesIO(); style=getSampleStyleSheet()
    style.add(ParagraphStyle(name='ReportTitle',parent=style['Heading1'],textColor=colors.HexColor('#0B2545'),alignment=TA_CENTER,spaceAfter=16))
    style.add(ParagraphStyle(name='FinePrint',parent=style['BodyText'],fontSize=8,textColor=colors.HexColor('#475569'),leading=11))
    document=SimpleDocTemplate(buffer,pagesize=A4,leftMargin=42,rightMargin=42,topMargin=40,bottomMargin=37)
    story=[Paragraph('PROOFGRAPH | EVIDENCE-LINKED REVIEW',style['ReportTitle']),
           Paragraph('SYNTHETIC DEMONSTRATION DATA · NO AICTE ENDORSEMENT · '+('APPROVED FOR PROTOTYPE WORKFLOW RELEASE - NOT OFFICIAL' if approved else 'DRAFT - REQUIRES OFFICER APPROVAL'),style['FinePrint']),Spacer(1,15),
           Paragraph(f"Case #{case['id']} - {escape(case['institution'])}",style['Heading2']),
           Paragraph(f"{escape(case['category'])} | Year {case['year']} | State: {escape(case['state'])}",style['BodyText']),Spacer(1,10),
           Paragraph('Internal consistency and AI anomaly signals are NOT issuing-authority authentication. All regulatory references below are SAMPLE / DEMO rules.',style['FinePrint']),Spacer(1,18)]
    if kind=='deficiency':
        story.extend([Paragraph('Draft clarification / deficiency notice',style['Heading2']),Paragraph('The following items merit clarification or additional supporting documentation. This draft is not an official finding or adverse determination.',style['BodyText']),Spacer(1,13)])
    for f in case['findings']:
        if f['manual_status']=='SUPERSEDED': continue
        a,b=f.get('source_a') or {},f.get('source_b') or {}
        src=lambda x: escape(f"{x.get('document_name','Not provided')}, page {x.get('page') or 'N/A'}, field {x.get('field') or 'N/A'}, bbox {[round(float(v),1) for v in x.get('bbox') or []]}, value {x.get('value') or 'N/A'}")
        content=[Paragraph(f"{escape(f['title'])} - {escape(f['severity'])}",style['Heading3']),
                 Paragraph(escape(f['reason']),style['BodyText']),Spacer(1,4),
                 Paragraph(f"Rule: {escape(f['rule_id'])} v{f['rule_version']} (SAMPLE / DEMO)",style['FinePrint']),
                 Paragraph('Evidence A: '+src(a),style['FinePrint']),Paragraph('Evidence B: '+src(b),style['FinePrint']),
                 Paragraph('Next action: '+escape(f['next_action']),style['BodyText']),
                 Paragraph(escape(f"OFFICIAL VERIFICATION: {f['official_status']} | INTERNAL CONSISTENCY: {f['consistency_status']} | AI SUSPICION: {f['ai_status']} | MANUAL REVIEW: {f['manual_status']}"),style['FinePrint']),Spacer(1,13)]
        story.append(KeepTogether(content))
    story.append(Paragraph('Historical changes',style['Heading2']))
    for c in case['changes']:
        story.append(Paragraph(escape(f"{c['key']}: {c['old_value']} -> {c['new_value']} | {'Evidence attached, review required' if c['explained'] else 'Unexplained, review required'}"),style['BodyText']))
    story.append(Spacer(1,4))
    story.append(Paragraph('Officer review and authorization required before release. No automatic enforcement or regulatory conclusion is authorized by this prototype.',style['FinePrint']))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#667085'))
        canvas.drawString(42,27,'Binary Battalion | SIH26263 | Synthetic ProofGraph prototype')
        canvas.drawRightString(552,27,f'Page {doc.page}')
    document.build(story,onFirstPage=footer,onLaterPages=footer)
    return buffer.getvalue()
