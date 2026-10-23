"""Concise, source-linked document check and clarification PDF.

Only current actionable discrepancies appear in the main report. Detailed histories,
internal graph data, dismissed/superseded findings and successful comparisons stay
in the application workbench and audit trail instead of cluttering this summary.
"""
from datetime import datetime, timezone
from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer,
    Table, TableStyle,
)

NAVY = colors.HexColor('#142D45')
TEAL = colors.HexColor('#087E79')
TEXT = colors.HexColor('#233745')
MUTED = colors.HexColor('#627483')
BORDER = colors.HexColor('#DEE7EC')
PALE = colors.HexColor('#F4F7F9')
AMBER = colors.HexColor('#825412')
AMBER_BG = colors.HexColor('#FFF5DE')
GREEN = colors.HexColor('#166044')
GREEN_BG = colors.HexColor('#EAF7F0')

# A dismissed result is not an outstanding issue. Its original evidence and review
# decision are preserved in the application's append-only audit history.
EXCLUDED_STATUSES = {'SUPERSEDED', 'DISMISSED_WITH_REASON'}


def readable_title(finding):
    """Use plain-English titles rather than internal detection-engine names."""
    title = str(finding.get('title') or 'Document discrepancy')
    low = title.lower()
    if 'laborator' in low and 'conflict' in low:
        return 'Laboratory counts do not match'
    if low.startswith('expired:'):
        return 'Document has expired'
    if 'cross-institution similar' in low or 'duplicate' in low:
        return 'Similar document appears in another application'
    if 'unexplained change' in low:
        return 'A value changed since the previous application'
    if 'conflict' in low or 'mismatch' in low:
        return 'Information differs between documents'
    return title


def plain_explanation(finding):
    """Explain the specific outcome; keep source citations separate from prose."""
    title = str(finding.get('title') or '').lower()
    a, b = finding.get('source_a') or {}, finding.get('source_b') or {}
    if 'laborator' in title and 'conflict' in title and a.get('value') is not None and b.get('value') is not None:
        return f"The application and supporting record show different laboratory counts: {a['value']} versus {b['value']}."
    if title.startswith('expired:'):
        return 'The stated validity date has passed. An updated document or clarification is needed.'
    if 'duplicate' in title or 'cross-institution similar' in title:
        return 'A matching or similar file was found in another application. Similarity is not proof of misuse.'
    if 'unexplained change' in title:
        return 'The reported value differs from an earlier submission. Supporting evidence may be needed.'
    return str(finding.get('reason') or 'A difference was found that needs checking.')


def source_line(source):
    """Return a short traceable source without dumping bounding boxes or metadata."""
    if not source or not (source.get('document_name') or source.get('value') is not None):
        return ''
    name = str(source.get('document_name') or 'Previous record')
    val = source.get('value')
    page = source.get('page')
    label = name
    if page is not None and str(page).strip():
        label += f' (page {page})'
    if val is not None and str(val).strip():
        label += f': {val}'
    return label


def build_report(case, kind='evidence', approved=False):
    """Generate a simple PDF with outcome, actionable issues and evidence only.

    No global fraud/pass score, claims of official verification or complete
    institutional compliance are made. The report intentionally summarizes only
    outstanding detected results, while audit history remains accessible in-app.
    """
    out = BytesIO()
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='ReportTitle', parent=styles['Heading1'],
                               fontName='Helvetica-Bold', fontSize=19, leading=23,
                               textColor=NAVY, spaceAfter=5))
    styles.add(ParagraphStyle(name='ReportHeading', parent=styles['Heading2'],
                               fontName='Helvetica-Bold', fontSize=11.4, leading=15,
                               textColor=NAVY, spaceBefore=10, spaceAfter=7))
    styles.add(ParagraphStyle(name='ReportBody', parent=styles['BodyText'],
                               fontName='Helvetica', fontSize=9.2, leading=13.8,
                               textColor=TEXT, spaceAfter=6))
    styles.add(ParagraphStyle(name='ReportSmall', parent=styles['BodyText'],
                               fontSize=8, leading=11.5, textColor=MUTED, spaceAfter=5))
    styles.add(ParagraphStyle(name='ReportIssue', parent=styles['BodyText'],
                               fontName='Helvetica-Bold', fontSize=10.5, leading=14,
                               textColor=NAVY, spaceAfter=6))
    styles.add(ParagraphStyle(name='ReportSummary', parent=styles['BodyText'],
                               fontName='Helvetica-Bold', fontSize=13.5, leading=18,
                               textColor=NAVY, spaceAfter=3))
    styles.add(ParagraphStyle(name='ReportSummarySub', parent=styles['BodyText'],
                               fontSize=9.1, leading=13, textColor=TEXT))

    e = lambda value: escape(str(value if value is not None else ''))
    documents = case.get('documents') or []
    findings = [f for f in case.get('findings', [])
                if f.get('manual_status') not in EXCLUDED_STATUSES]
    missing = [c for c in case.get('checklist', []) if not c.get('present')]
    open_count = len(findings) + len(missing)

    is_empty = not documents
    is_clear = bool(documents) and open_count == 0
    result_title = ('No documents checked' if is_empty else
                    'No issues found in the checked fields' if is_clear else
                    f'{open_count} item{"s" if open_count != 1 else ""} need attention')
    result_desc = ('Upload the required application documents to begin checking.' if is_empty else
                   'The uploaded information is consistent under the configured sample checks.' if is_clear else
                   'Review the items below and the cited source documents before deciding what to do.')
    banner_fill = PALE if is_empty else GREEN_BG if is_clear else AMBER_BG
    banner_edge = BORDER if is_empty else colors.HexColor('#C5E4D4') if is_clear else colors.HexColor('#F0DBA3')
    header = 'CLARIFICATION REQUEST' if kind == 'deficiency' else 'DOCUMENT CHECK RESULT'

    pdf = SimpleDocTemplate(out, pagesize=A4, leftMargin=44, rightMargin=44,
                            topMargin=42, bottomMargin=46,
                            title='ProofGraph - ' + ('Clarification Request' if kind == 'deficiency' else 'Document Check Result'))
    story = [
        Paragraph(header, styles['ReportTitle']),
        Paragraph('ProofGraph  |  Evidence-based document comparison', styles['ReportSmall']),
        HRFlowable(width='100%', thickness=1.3, color=TEAL), Spacer(1, 13),
        Paragraph(e(case.get('institution') or 'Institution'), styles['ReportHeading']),
        Paragraph(f"Application #{e(case.get('id', '-'))}  |  {e(case.get('category') or 'Application')}  |  {e(case.get('year') or '-')}", styles['ReportSmall']),
        Spacer(1, 7),
    ]

    summary = Table([
        [Paragraph(e(result_title), styles['ReportSummary'])],
        [Paragraph(e(result_desc), styles['ReportSummarySub'])],
        [Paragraph(f'<b>{len(documents)} document{"s" if len(documents) != 1 else ""} checked</b>', styles['ReportSmall'])],
    ], colWidths=[A4[0] - 88 - 27], hAlign='LEFT')
    summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), banner_fill),
        ('BOX', (0, 0), (-1, -1), 0.7, banner_edge),
        ('LEFTPADDING', (0, 0), (-1, -1), 13),
        ('RIGHTPADDING', (0, 0), (-1, -1), 13),
        ('TOPPADDING', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, -1), (-1, -1), 9),
    ]))
    story += [summary, Spacer(1, 12)]

    if findings:
        story.append(Paragraph('What needs attention', styles['ReportHeading']))
        for number, finding in enumerate(findings, 1):
            block = [
                Paragraph(f'{number}. {e(readable_title(finding))}', styles['ReportIssue']),
                Paragraph(e(plain_explanation(finding)), styles['ReportBody']),
            ]
            a = source_line(finding.get('source_a'))
            b = source_line(finding.get('source_b'))
            if a or b:
                source_text = ' <b>Compared documents:</b> ' if a and b else ' <b>Source:</b> '
                lines = ([a] if a else []) + ([b] if b and b != a else [])
                block.append(Paragraph(source_text + '<br/>'.join(e(x) for x in lines), styles['ReportSmall']))
            action = str(finding.get('next_action') or '').strip()
            if action:
                block.append(Paragraph('<b>Next step:</b> ' + e(action), styles['ReportBody']))
            if finding.get('manual_status') not in (None, '', 'PENDING', 'PENDING_REVIEW'):
                # Human decisions matter, but internal status codes do not help readers.
                decisions = {
                    'CONFIRMED_BY_OFFICER': 'Confirmed for follow-up',
                    'EVIDENCE_REQUESTED': 'Additional evidence requested',
                    'ESCALATED_FOR_INSPECTION': 'Referred for inspection',
                }
                state = decisions.get(finding.get('manual_status'))
                if state:
                    block.append(Paragraph('<b>Review update:</b> ' + e(state), styles['ReportSmall']))
            block.append(Paragraph(f"Reference: {e(finding.get('rule_id') or 'Sample check')}"
                                   f" · v{e(finding.get('rule_version') or 1)}", styles['ReportSmall']))
            block.append(Spacer(1, 9))
            story.append(KeepTogether(block))

    if missing:
        story.append(Paragraph('Documents still needed', styles['ReportHeading']))
        for record in missing:
            story.append(Paragraph('- ' + e(record.get('type') or 'Supporting document'), styles['ReportBody']))

    # Do not duplicate every uploaded filename, historical change, review log, AI
    # status or check that passed. The source PDF is directly traceable per finding.
    if kind == 'deficiency' and not is_clear and not is_empty:
        story.append(Paragraph('Clarification to request', styles['ReportHeading']))
        story.append(Paragraph('Please provide the missing records or explain the differences listed above. An authorized officer must review this draft before it is released.', styles['ReportBody']))

    story += [Spacer(1, 12), HRFlowable(width='100%', thickness=.7, color=BORDER),
              Spacer(1, 8), Paragraph(
                  '<b>Important:</b> This is a preliminary comparison of uploaded information using sample rules. '
                  'It does not authenticate documents with their issuing authorities or approve the institution. '
                  'Any decision requires human review.', styles['ReportSmall']),
              Paragraph('SYNTHETIC DEMONSTRATION DATA - NOT OFFICIAL EVIDENCE', styles['ReportSmall']),
              Paragraph('Report: ' + ('Reviewed in the prototype workflow - not an official approval' if approved else
                                     'DRAFT - requires authorized officer approval before release'),
                        styles['ReportSmall'])]

    def footer(canvas, doc):
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(44, 26, 'ProofGraph | Document comparison, not official verification')
        canvas.drawRightString(A4[0]-44, 26, f'Page {doc.page}')

    pdf.build(story, onFirstPage=footer, onLaterPages=footer)
    return out.getvalue()
