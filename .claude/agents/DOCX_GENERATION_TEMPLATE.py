"""
REFERENCE TEMPLATE for QA Understanding Document Creator Agent

This Python script shows the REQUIRED approach for generating .docx files.
The agent MUST use python-docx library to generate Word documents directly.
DO NOT create Markdown files and convert them.
"""

import json
import os
from qa_workflow.paths import OutputPaths
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def create_qa_understanding_document(pbi_number):
    """
    Generate QA Understanding Document in Word format (.docx)

    Args:
        pbi_number: PBI number (e.g., "645352")

    Returns:
        Path to created .docx file
    """

    # Step 0: Resolve the standard output structure. Never hand-build a path —
    # every location comes from qa_workflow.paths so all agents agree.
    paths = OutputPaths.from_context(pbi_number).ensure()

    # Step 1: Load input files
    pbi_file = paths.pbi_data
    integration_file = paths.integration_docs

    if not os.path.exists(pbi_file):
        raise FileNotFoundError(f"PBI data not found: {pbi_file}")
    if not os.path.exists(integration_file):
        raise FileNotFoundError(f"Integration docs not found: {integration_file}")

    with open(pbi_file, 'r', encoding='utf-8') as f:
        pbi_data = json.load(f)
    with open(integration_file, 'r', encoding='utf-8') as f:
        integration_docs = json.load(f)

    # Step 2: Extract data
    title = pbi_data.get('title', '')
    description = pbi_data.get('description', '')
    acceptance_criteria = pbi_data.get('acceptanceCriteria', [])

    # Step 3: Create Word document
    doc = Document()

    # Title
    title_para = doc.add_heading('QA UNDERSTANDING DOCUMENT', level=0)
    title_para.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Subtitle
    subtitle = doc.add_paragraph(f'Feature: {title}')
    subtitle.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    subtitle.runs[0].font.size = Pt(14)
    subtitle.runs[0].font.bold = True

    doc.add_paragraph()  # Blank line

    # Section 1: User Story
    doc.add_heading('1. User Story', level=1)

    # Derive user story from description
    user_story = f"As a user, I want {title.lower()}, so that I can improve operational efficiency."
    doc.add_paragraph(user_story)

    doc.add_paragraph()  # Blank line

    # Section 2: Acceptance Criteria → QA Interpretation
    doc.add_heading('2. Acceptance Criteria → QA Interpretation', level=1)

    for idx, ac in enumerate(acceptance_criteria, 1):
        # AC heading
        ac_title = f"AC{idx} — {ac.get('title', f'Acceptance Criterion {idx}')}"
        doc.add_heading(ac_title, level=2)

        # Given/When/Then (extract from AC text or create)
        gwt_para = doc.add_paragraph()
        gwt_para.add_run('Given ').bold = True
        gwt_para.add_run(f"{ac.get('given', 'condition')}\n")
        gwt_para.add_run('When ').bold = True
        gwt_para.add_run(f"{ac.get('when', 'action')}\n")
        gwt_para.add_run('Then ').bold = True
        gwt_para.add_run(f"{ac.get('then', 'outcome')}")

        # QA Interpretation
        qa_para = doc.add_paragraph()
        qa_para.add_run('QA interpretation: ').bold = True

        # CRITICAL: Use SPECIFIC data from integration_docs
        # Example: Reference actual table names, API endpoints
        apis = integration_docs.get('apis', [])
        database = integration_docs.get('database', [])

        qa_interpretation = f"Verify that... [USE ACTUAL TABLE/API NAMES FROM integration_docs]"
        qa_para.add_run(qa_interpretation)

        # Concrete Example
        ex_para = doc.add_paragraph()
        ex_para.add_run('Example: ').bold = True

        # CRITICAL: Use CONCRETE data - real POD names, timestamps, etc.
        example = "POD 'CNP_POD123' with forecast_id = 98765... [USE REAL DATA]"
        ex_para.add_run(example)

        doc.add_paragraph()  # Blank line

    # Section 3: Business Rule → Data Mapping
    doc.add_heading('3. Business Rule → Data Mapping (Consolidated)', level=1)

    # Create table
    table = doc.add_table(rows=1, cols=5)
    table.style = 'Light Grid Accent 1'

    # Table headers
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = 'Area'
    hdr_cells[1].text = 'Business Rule'
    hdr_cells[2].text = 'Source / Data Needed'
    hdr_cells[3].text = 'Expected Behavior'
    hdr_cells[4].text = 'AC'

    # Make header bold
    for cell in hdr_cells:
        cell.paragraphs[0].runs[0].font.bold = True

    # Add data rows (extract from integration_docs)
    # CRITICAL: Map to ACTUAL data sources
    business_rules = [
        {
            'area': 'POD Details Table',
            'rule': 'Display Last Forecasted Date',
            'source': 'forecast_model.last_forecasted_date',  # ACTUAL table.column
            'expected': 'Display timestamp in user timezone',
            'ac': 'AC1'
        },
        # Add more rules...
    ]

    for rule in business_rules:
        row_cells = table.add_row().cells
        row_cells[0].text = rule['area']
        row_cells[1].text = rule['rule']
        row_cells[2].text = rule['source']
        row_cells[3].text = rule['expected']
        row_cells[4].text = rule['ac']

    doc.add_paragraph()  # Blank line

    # Section 4: Functional Flow
    doc.add_heading('4. Functional Flow', level=1)

    # CRITICAL: Use ACTUAL component names, API endpoints, DB queries
    flow_steps = [
        "User navigates to POD Details page for POD 'CNP_POD123'",
        "Frontend calls GET /pod-details/{pod}",
        "Backend queries: SELECT best_forecast_id FROM pod_header WHERE pod = 'CNP_POD123'",
        # Add more steps...
    ]

    for idx, step in enumerate(flow_steps, 1):
        doc.add_paragraph(f'{idx}. {step}', style='List Number')

    doc.add_paragraph()  # Blank line

    # Section 5: Constraints
    doc.add_heading('5. Constraints', level=1)

    # CRITICAL: List SPECIFIC gaps, not generic statements
    constraints = [
        "The PBI does not specify the exact database table name (assumed 'forecast_model')",
        "Auto-refresh mechanism technology (WebSocket/SSE/polling) not specified",
        # Add more constraints...
    ]

    for constraint in constraints:
        doc.add_paragraph(constraint, style='List Bullet')

    # Step 4: Save document
    output_path = paths.qa_understanding_document
    doc.save(output_path)

    # Step 5: Verify NO .md file was created
    md_path = paths.deliverable_file('QA_Understanding_Document.md')
    if os.path.exists(md_path):
        os.remove(md_path)
        print(f"WARNING: Deleted unwanted .md file: {md_path}")

    print(f"SUCCESS: Created {output_path}")
    return output_path


if __name__ == '__main__':
    # Example usage
    pbi_number = "645352"
    output_file = create_qa_understanding_document(pbi_number)
    print(f"Document created: {output_file}")