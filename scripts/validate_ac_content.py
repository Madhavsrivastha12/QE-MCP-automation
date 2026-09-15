#!/usr/bin/env python3
"""Validate that each AC has unique QA Interpretation and Example"""

import sys
from pathlib import Path
from docx import Document

def validate_document(pbi_number):
    doc_path = Path(__file__).parent / 'outputs' / pbi_number / f'QA_Understanding_Document_PBI_{pbi_number}.docx'

    if not doc_path.exists():
        print(f"ERROR: Document not found: {doc_path}")
        return False

    doc = Document(str(doc_path))

    # Extract AC sections
    acs = []
    current_ac = None

    for para in doc.paragraphs:
        text = para.text.strip()

        # Detect AC heading
        if text.startswith('AC-') and ':' in text:
            if current_ac:
                acs.append(current_ac)
            current_ac = {
                'heading': text,
                'gwt': '',
                'qa_interp': '',
                'example': ''
            }
        elif current_ac:
            if text.startswith('Given:'):
                current_ac['gwt'] = text
            elif text.startswith('QA Interpretation:'):
                current_ac['qa_interp'] = text.replace('QA Interpretation:', '').strip()
            elif text.startswith('Example:'):
                current_ac['example'] = text.replace('Example:', '').strip()

    if current_ac:
        acs.append(current_ac)

    print(f"\n{'='*80}")
    print(f"PBI {pbi_number} - AC Content Validation")
    print(f"{'='*80}\n")

    # Display each AC
    for i, ac in enumerate(acs, 1):
        print(f"AC-{i}: {ac['heading']}")
        print(f"\nGiven/When/Then:")
        print(f"  {ac['gwt'][:100]}...")
        print(f"\nQA Interpretation:")
        print(f"  {ac['qa_interp'][:150]}...")
        print(f"\nExample:")
        print(f"  {ac['example'][:150]}...")
        print(f"\n{'-'*80}\n")

    # Check for duplicates
    qa_interps = [ac['qa_interp'] for ac in acs]
    examples = [ac['example'] for ac in acs]

    issues = []

    # Check QA Interpretation uniqueness
    for i in range(len(qa_interps)):
        for j in range(i+1, len(qa_interps)):
            if qa_interps[i] == qa_interps[j]:
                issues.append(f"DUPLICATE QA Interpretation: AC-{i+1} and AC-{j+1}")

    # Check Example uniqueness
    for i in range(len(examples)):
        for j in range(i+1, len(examples)):
            if examples[i] == examples[j]:
                issues.append(f"DUPLICATE Example: AC-{i+1} and AC-{j+1}")

    # Report results
    if issues:
        print(f"VALIDATION FAILED - {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print(f"VALIDATION PASSED - All {len(acs)} ACs have unique content")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python validate_ac_content.py <PBI_NUMBER>")
        sys.exit(1)

    pbi_number = sys.argv[1]
    success = validate_document(pbi_number)
    sys.exit(0 if success else 1)