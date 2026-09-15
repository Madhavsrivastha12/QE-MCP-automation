# QA Understanding Document - Permanent Formatting Standards

## Status: Applied to All Future PBIs

These formatting standards are **permanently applied** to all QA Understanding Documents generated for current and future PBIs.

---

## Core Principles

1. ✅ **Complete Text Preservation**: NO truncation with "..." or clipping
2. ✅ **Auto-Wrap Long Headings**: Long AC headings wrap across multiple lines automatically
3. ✅ **Professional Layout**: Clean, polished, visually consistent on every page
4. ✅ **No Overflow**: Tables, headings, code blocks never overflow or create awkward page breaks
5. ✅ **Proper Hierarchy**: Clear heading structure with consistent spacing
6. ✅ **Readable Typography**: Calibri font, appropriate sizes, proper line spacing
7. ✅ **Visual Consistency**: Navy blue color scheme matching reference template

---

## Document Structure

### Page Setup
- **Page Size**: Letter (8.5" x 11")
- **Margins**: 1 inch (2.54 cm) on all sides
- **Orientation**: Portrait
- **Line Spacing**: 1.15 (normal paragraphs)
- **Font**: Calibri throughout

### Headers and Footers
- **Header**: 
  - Text: "QA Understanding Document - PBI {number}"
  - Alignment: Center
  - Font: 9pt, bold, dark gray
  - Position: 0.5" from top

- **Footer**:
  - Text: "Page X of Y | Generated: YYYY-MM-DD"
  - Alignment: Center
  - Font: 9pt, dark gray
  - Position: 0.5" from bottom
  - Dynamic page numbers (auto-updates)

### Heading Hierarchy

#### Heading 1 (Major Sections)
- **Font**: Calibri, 16pt, Bold
- **Color**: Navy Blue (RGB 31, 73, 125)
- **Space Before**: 12pt
- **Space After**: 6pt
- **Keep With Next**: Yes (prevents orphan headings)
- **Examples**: "1. Feature Overview & Scope", "2. Acceptance Criteria -> QA Interpretation"

#### Heading 2 (Subsections)
- **Font**: Calibri, 13pt, Bold
- **Color**: Lighter Blue (RGB 79, 129, 189)
- **Space Before**: 10pt
- **Space After**: 4pt
- **Keep With Next**: Yes
- **Examples**: "1.1 Purpose & Problem Statement", "7.1 Environments"

#### Heading 3 (AC Headings and Details)
- **Font**: Calibri, 11pt, Bold
- **Color**: Lighter Blue (RGB 79, 129, 189)
- **Space Before**: 8pt
- **Space After**: 4pt
- **Keep With Next**: Yes
- **Text Wrapping**: **ENABLED** - long headings wrap across multiple lines
- **NO TRUNCATION**: Complete AC text preserved (never use "...")
- **Examples**: "AC1 - For Scalar forecast model, max_read_date should be retrieved from pod_scalar_meterread_clean table and should be the latest read_date"

### Normal Paragraphs
- **Font**: Calibri, 11pt
- **Color**: Black
- **Space After**: 6pt
- **Line Spacing**: 1.15
- **Justification**: Left-aligned
- **Widow/Orphan Control**: Enabled

---

## Special Formatting

### Given-When-Then Format

```
Given: <precondition text>
  - Label: Bold, Navy Blue, 11pt
  - Text: Regular, 11pt
  - Left Indent: 0.5 cm
  - Space After: 3pt

When: <action text>
  - Label: Bold, Navy Blue, 11pt
  - Text: Regular, 11pt
  - Left Indent: 0.5 cm
  - Space After: 3pt

Then: <expected outcome text>
  - Label: Bold, Navy Blue, 11pt
  - Text: Regular, 11pt
  - Left Indent: 0.5 cm
  - Space After: 8pt
```

### QA Interpretation

```
QA Interpretation: <dynamic implementation-focused explanation>
  - Label: Bold, Dark Red (RGB 192, 0, 0), 11pt
  - Text: Regular, 10pt, Black
  - Left Indent: 0.5 cm
  - Space After: 8pt
  - Content: Implementation-focused (HOW + WHAT + Evidence)
```

### Examples

```
Example: <concrete example with real dates/values>
  - Label: Bold, Blue (RGB 0, 112, 192), 11pt
  - Text: Italic, 10pt, Dark Gray (RGB 64, 64, 64)
  - Background: Light Gray (RGB 242, 242, 242)
  - Left Indent: 0.5 cm
  - Right Indent: 0.5 cm
  - Space After: 12pt
```

### Tables

#### Professional Table Format
- **Style**: Light Grid Accent 1
- **Header Row**:
  - Background: Navy Blue (RGB 31, 73, 125)
  - Text: White, Bold, 11pt
  - Alignment: Left
- **Data Rows**:
  - Text: Black, Regular, 10pt
  - Zebra Striping: Automatic (via table style)
  - Cell Padding: 5pt
- **Column Widths**: Optimized to prevent overflow
  - Business Rule: 2.5"
  - Source/Data: 2.5"
  - Expected Behavior: 2.0"
  - AC Reference: 0.5"
- **Row Splitting**: Disabled (prevents awkward breaks)
- **Keep With Next**: Enabled for table caption

#### Table Layout Rules
1. ✅ Always precede tables with a descriptive heading
2. ✅ Set explicit column widths to prevent overflow
3. ✅ Disable row splitting to keep rows together
4. ✅ Use white bold text on navy blue background for headers
5. ✅ Add 10pt spacing after tables

### Code Blocks

```
<code content in monospace font>
  - Font: Consolas, 9pt, Black
  - Background: Light Gray (RGB 231, 230, 230)
  - Border: 1pt solid gray on all sides
  - Left/Right Indent: 0.5 cm
  - Space Before/After: 6pt
  - Keep Together: Yes (prevents mid-block page breaks)
  - Optional Language Label: Italic, 9pt, Gray, above code block
```

### List Styles

#### Bulleted Lists
- **Bullet Character**: Standard round bullet (•)
- **Left Indent**: 1.27 cm
- **Hanging Indent**: 0.63 cm
- **Space After**: 0pt (tight spacing)
- **Use Cases**: In-scope items, out-of-scope items, risk lists

#### Numbered Lists
- **Number Format**: 1., 2., 3., ...
- **Left Indent**: 1.27 cm
- **Hanging Indent**: 0.63 cm
- **Space After**: 0pt
- **Use Cases**: Functional flow steps, process sequences

---

## Page Break Control

### Prevent Awkward Breaks

1. ✅ **Headings**: Never orphan at bottom of page
   - `keep_with_next = True` for all headings

2. ✅ **Tables**: Never split header from data rows
   - Disable row splitting (`cantSplit`)
   - Keep table heading with table

3. ✅ **Code Blocks**: Never break in middle
   - `keep_together = True`
   - `widow_control = True`

4. ✅ **AC Sections**: Keep Given-When-Then together
   - AC heading has `keep_with_next = True`
   - Prevents AC heading on one page, content on next

5. ✅ **Examples**: Keep complete
   - Example paragraph not split mid-sentence

### Manual Page Breaks

Only use explicit page breaks:
- After title page
- Between major sections (optional, only if logical)
- **NEVER** in middle of AC content

---

## Text Preservation Rules

### CRITICAL: No Truncation

❌ **WRONG**:
```
AC1 - For Scalar forecast model, max_read_date should be retr...
```

✅ **CORRECT**:
```
AC1 - For Scalar forecast model, max_read_date should be retrieved from 
pod_scalar_meterread_clean table and should be the latest read_date for the POD
```

### Auto-Wrap Implementation

1. ✅ Use **complete AC text** in heading
2. ✅ Enable paragraph wrapping (automatic)
3. ✅ Set appropriate line spacing (1.15)
4. ✅ Allow headings to span multiple lines
5. ✅ **NEVER** use `[:70]` or similar truncation
6. ✅ **NEVER** append "..." to headings

### Long Text Handling

For any text content (headings, paragraphs, table cells):
1. ✅ Preserve complete original text
2. ✅ Let Word handle wrapping automatically
3. ✅ Set column widths appropriately for tables
4. ✅ Use justified or left-aligned text (never center long text)

---

## Color Scheme

### Primary Colors
- **Navy Blue**: RGB(31, 73, 125) - H1 headings, primary emphasis
- **Lighter Blue**: RGB(79, 129, 189) - H2/H3 headings, labels
- **Dark Red**: RGB(192, 0, 0) - QA Interpretation label
- **Blue**: RGB(0, 112, 192) - Example label

### Secondary Colors
- **Black**: RGB(0, 0, 0) - Body text
- **Dark Gray**: RGB(64, 64, 64) - Example text, de-emphasized content
- **Medium Gray**: RGB(128, 128, 128) - Code language labels
- **White**: RGB(255, 255, 255) - Table header text

### Background Colors
- **Navy Blue**: RGB(31, 73, 125) - Table headers
- **Light Gray**: RGB(242, 242, 242) - Example blocks
- **Code Gray**: RGB(231, 230, 230) - Code blocks

---

## Spacing Standards

### Vertical Spacing (Space After)
- **H1**: 6pt
- **H2**: 4pt
- **H3**: 4pt
- **Normal Paragraph**: 6pt
- **Given/When (individual)**: 3pt
- **Then**: 8pt
- **QA Interpretation**: 8pt
- **Example**: 12pt
- **Table**: 10pt
- **Code Block**: 6pt
- **Between Sections**: 12pt

### Horizontal Spacing (Indentation)
- **Bulleted Lists**: 1.27 cm left indent
- **Numbered Lists**: 1.27 cm left indent
- **Given-When-Then**: 0.5 cm left indent
- **QA Interpretation**: 0.5 cm left indent
- **Example**: 0.5 cm left + 0.5 cm right indent
- **Code Blocks**: 0.5 cm left + 0.5 cm right indent

---

## Validation Checklist

Before finalizing any QA Understanding Document, verify:

### ✅ Text Preservation
- [ ] All AC headings show COMPLETE text (no "...")
- [ ] Long headings wrap across multiple lines properly
- [ ] No truncated table cell content
- [ ] All examples include full concrete details

### ✅ Layout Quality
- [ ] No orphan headings at bottom of pages
- [ ] Tables don't break between header and data rows
- [ ] Code blocks stay together (no mid-block breaks)
- [ ] Given-When-Then stays with AC heading
- [ ] Examples stay complete (no mid-sentence breaks)

### ✅ Visual Consistency
- [ ] Navy blue color on all H1 headings
- [ ] Lighter blue on all H2/H3 headings
- [ ] Table headers have navy background + white text
- [ ] Example blocks have light gray background
- [ ] Code blocks have gray background + border

### ✅ Professional Formatting
- [ ] Header shows PBI number
- [ ] Footer shows "Page X of Y | Generated: date"
- [ ] Margins are 1 inch on all sides
- [ ] Font is Calibri throughout (except code = Consolas)
- [ ] Line spacing is 1.15 for normal text
- [ ] Proper spacing between sections

### ✅ Content Quality
- [ ] All 10 sections present
- [ ] Every AC has Given-When-Then
- [ ] Every AC has implementation-focused QA Interpretation (not generic)
- [ ] Every AC has concrete example with real dates/values
- [ ] Business rules table populated
- [ ] No placeholder content left in final document

---

## Implementation Notes

### Python-docx Methods Used

1. **Paragraph Formatting**:
   ```python
   para.paragraph_format.space_before = Pt(12)
   para.paragraph_format.space_after = Pt(6)
   para.paragraph_format.keep_with_next = True
   para.paragraph_format.widow_control = True
   para.paragraph_format.left_indent = Cm(0.5)
   ```

2. **Run Formatting**:
   ```python
   run.font.bold = True
   run.font.color.rgb = RGBColor(31, 73, 125)
   run.font.size = Pt(12)
   run.font.italic = True
   ```

3. **Table Formatting**:
   ```python
   table = self.doc.add_table(rows=n, cols=m)
   table.style = 'Light Grid Accent 1'
   
   # Navy blue header
   shading = OxmlElement('w:shd')
   shading.set(qn('w:fill'), '1F497D')
   cell._element.get_or_add_tcPr().append(shading)
   
   # Prevent row splitting
   row._element.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
   ```

4. **Background Shading**:
   ```python
   shading = OxmlElement('w:shd')
   shading.set(qn('w:fill'), 'F2F2F2')
   para._element.get_or_add_pPr().append(shading)
   ```

5. **Page Numbers**:
   ```python
   fldChar = OxmlElement('w:fldChar')
   fldChar.set(qn('w:fldCharType'), 'begin')
   instrText = OxmlElement('w:instrText')
   instrText.text = "PAGE"
   # ... field construction
   ```

---

## Generator Script

**File**: `final_10_section_generator.py`

**Key Methods**:
- `setup_document()`: Applies all style and margin settings
- `setup_header_footer()`: Creates professional headers/footers with page numbers
- `add_professional_table()`: Creates tables with navy headers, no overflow
- `add_code_block()`: Formats code with monospace font and gray background
- `add_spacing()`: Adds consistent vertical spacing
- `prevent_page_break_before()`: Controls page break behavior

**Usage**:
```bash
python scripts/final_10_section_generator.py <PBI_NUMBER>
```

**Output**:
```
outputs/<PBI_NUMBER>/deliverables/QA_Understanding_Document.docx
```

---

## Future PBI Application

These standards are **locked in** for all future PBIs. Every new QA Understanding Document will automatically:

1. ✅ Use the professional Word template
2. ✅ Preserve complete AC text (no truncation)
3. ✅ Apply navy blue color scheme
4. ✅ Format tables professionally
5. ✅ Control page breaks intelligently
6. ✅ Include dynamic page numbers
7. ✅ Use implementation-focused QA interpretations
8. ✅ Provide concrete examples
9. ✅ Maintain visual consistency

**No manual formatting required** - the generator applies all standards automatically.

---

## Summary

**Status**: ✓ PERMANENT STANDARD

All QA Understanding Documents now follow professional formatting standards with:
- ✅ Complete text preservation (NO "..." truncation)
- ✅ Auto-wrapped long headings
- ✅ Professional layout with proper spacing
- ✅ No table/heading/code overflow
- ✅ Smart page break control
- ✅ Navy blue color scheme
- ✅ Headers/footers with page numbers
- ✅ Visually polished on every page

**Applied To**:
- Current PBIs: 634367, 643243
- All future PBIs automatically

**Generator**: `final_10_section_generator.py`
**Reference**: Radhika's QA template + Dynamic QA interpretation
**Quality**: Production-ready, stakeholder-approved format
