"""Readable, evidence-linked PDF for human screening; never an official approval."""
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable

NAVY=colors.HexColor('#142d45')
TEAL=colors.HexColor('#0b8d86')
GRAY=colors.HexColor('#5a6b7a')
AMBER=colors.HexColor('#946114')

def build_report(case,kind='evidence',approved=False):
    stream=BytesIO()
    style=getSampleStyleSheet()
    style.add(ParagraphStyle(name='PGTitle',parent=style['Heading1'],fontName='Helvetica-Bold',fontSize=21,leading=26,textColor=NAVY,spaceAfter=9))
    style.add(ParagraphStyle(name='PGBody',parent=style['BodyText'],fontSize=10,leading=15,spaceAfter=6))
    style.add(ParagraphStyle(name='PGSmall',parent=style['BodyText'],fontSize=8.5,leading=12,textColor=GRAY,spaceAfter=4))
    style.add(ParagraphStyle(name='PGHeading',parent=style['Heading2'],fontSize=13,leading=18,textColor=NAVY,spaceBefore=13,spaceAfter=9))
    style.add(ParagraphStyle(name='PGIssue',parent=style['Heading3'],fontSize=12,leading=16,textColor=NAVY,spaceAfter=6))
    style.add(ParagraphStyle(name='PGValue',parent=style['BodyText'],fontSize=9,leading=13,textColor=NAVY,spaceAfter=4))
    doc=SimpleDocTemplate(stream,pagesize=A4,leftMargin=43,rightMargin=43,topMargin=42,bottomMargin=43,title='ProofGraph - Document Check Report')
    E=lambda v:escape(str(v if v is not None else ''))
    active=[f for f in case.get('findings',[]) if f.get('manual_status')!='SUPERSEDED']
    missing=[c for c in case.get('checklist',[]) if not c.get('present')]
    good=len(active)==0 and not missing and bool(case.get('documents'))
    status=('No differences found in checked fields' if good else f'{len(active)+len(missing)} items need human review')
    story=[Paragraph('DOCUMENT CHECK REPORT',style['PGTitle']),
           Paragraph('ProofGraph  |  Evidence-linked screening',style['PGSmall']),
           Paragraph('SYNTHETIC DEMONSTRATION DATA — NOT VALID AS OFFICIAL EVIDENCE',style['PGSmall']),
           HRFlowable(width='100%',thickness=1,color=TEAL),Spacer(1,12),
           Paragraph(E(case.get('institution','Institution')),style['PGHeading']),
           Paragraph(f"Application #{E(case.get('id'))}  |  {E(case.get('category'))}  |  {E(case.get('year'))}",style['PGSmall']),
           Spacer(1,8),
           Paragraph('<b>RESULT: '+E(status)+'</b>',style['PGBody']),
           Paragraph(f"{len(case.get('documents',[]))} uploaded documents checked  |  {len(active)} active findings  |  {len(missing)} missing document types",style['PGSmall']),
           Paragraph('Results are preliminary consistency and sample-rule checks, NOT an issuing-authority authentication or institutional approval.',style['PGSmall']),
           Spacer(1,12)]
    if kind=='deficiency':
        story+=[Paragraph('Draft clarification request',style['PGHeading']),Paragraph('The following items require clarification or supporting evidence. This notice must be approved by an authorized officer before issue.',style['PGBody'])]
    story.append(Paragraph('Documents reviewed',style['PGHeading']))
    if case.get('documents'):
        for d in case['documents']:
            story.append(Paragraph('• '+E(d.get('kind','Document'))+' — '+E(d.get('name','')),style['PGSmall']))
    else: story.append(Paragraph('No source documents uploaded.',style['PGBody']))
    story.append(Paragraph('Items to review',style['PGHeading']))
    if not active and not missing: story.append(Paragraph('No discrepancies were detected by the configured checks. This is not an authenticity certificate.',style['PGBody']))
    for i,f in enumerate(active,1):
        evidence=[]
        for tag,s in [('Source 1',f.get('source_a') or {}),('Source 2',f.get('source_b') or {})]:
            if not (s.get('document_name') or s.get('value')):continue
            evidence.append(Paragraph(f"<b>{tag}:</b> {E(s.get('document_name') or 'Record')} | Page {E(s.get('page') or '—')} | {E(s.get('field') or 'Field')} = <b>{E(s.get('value') or 'Not supplied')}</b>",style['PGValue']))
        story.append(KeepTogether([
            Paragraph(f"{i}. {E(f.get('title','Finding'))}",style['PGIssue']),
            Paragraph(E(f.get('reason','')),style['PGBody']),
            *evidence,
            Paragraph('<b>What to do:</b> '+E(f.get('next_action','Review original source evidence')),style['PGBody']),
            Paragraph(f"Rule {E(f.get('rule_id'))} version {E(f.get('rule_version'))}  |  Officer review: {E(f.get('manual_status'))}",style['PGSmall']),Spacer(1,7)
        ]))
    if missing:
        story.append(Paragraph('Not yet uploaded',style['PGHeading']))
        for c in missing:story.append(Paragraph('• '+E(c.get('type','Required document')),style['PGBody']))
    if case.get('changes'):
        story.append(Paragraph('Changes compared with earlier records',style['PGHeading']))
        for change in case['changes']:
            story.append(Paragraph(f"{E(change.get('key'))}: {E(change.get('old_value'))} → {E(change.get('new_value'))}. {'Supporting evidence still requires review.' if change.get('explained') else 'Reason or evidence required.'}",style['PGBody']))
    story.append(Spacer(1,12))
    story.append(HRFlowable(width='100%',thickness=.7,color=colors.HexColor('#d7e2e8')))
    story.append(Paragraph('VERIFICATION AND DECISION STATUS',style['PGHeading']))
    story.append(Paragraph('Official source verification: <b>Not established by this report.</b> Document consistency does not prove authenticity. AI anomaly indications, if any, are preliminary. Any regulatory action requires a recorded human review.',style['PGSmall']))
    story.append(Paragraph('REPORT STATUS: '+('Approved for prototype workflow review only — not official' if approved else 'DRAFT — human approval required before external release'),style['PGSmall']))
    def footer(c,d):
        c.setFont('Helvetica',8);c.setFillColor(GRAY)
        c.drawString(43,28,'ProofGraph · Synthetic training workflow · Not an official AICTE document')
        c.drawRightString(A4[0]-43,28,f'Page {d.page}')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    return stream.getvalue()
