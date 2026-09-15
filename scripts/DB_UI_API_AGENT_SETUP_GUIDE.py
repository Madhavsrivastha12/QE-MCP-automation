"""
DB/UI/API QA Agent Setup Guide Generator
Creates a comprehensive Word document for setting up the QA Agent system on a new Windows laptop
"""

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def add_heading_with_style(doc, text, level=1):
    """Add a heading with custom styling"""
    heading = doc.add_heading(text, level=level)
    heading_format = heading.runs[0].font
    heading_format.color.rgb = RGBColor(0, 51, 102)  # Navy blue
    return heading

def add_code_block(doc, code_text, language=""):
    """Add a formatted code block"""
    paragraph = doc.add_paragraph()
    paragraph.style = 'Normal'
    run = paragraph.add_run(code_text)
    run.font.name = 'Consolas'
    run.font.size = Pt(9)

    # Add gray background
    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'F0F0F0')
    paragraph._element.get_or_add_pPr().append(shading_elm)

    # Add border
    paragraph.paragraph_format.left_indent = Inches(0.5)
    paragraph.paragraph_format.right_indent = Inches(0.5)
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(6)

    return paragraph

def add_table_from_data(doc, headers, rows):
    """Add a formatted table"""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Light Grid Accent 1'

    # Header row
    hdr_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        hdr_cells[i].text = header
        for paragraph in hdr_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

        # Navy background for header
        shading_elm = OxmlElement('w:shd')
        shading_elm.set(qn('w:fill'), '003366')
        hdr_cells[i]._element.get_or_add_tcPr().append(shading_elm)

    # Data rows
    for row_idx, row_data in enumerate(rows, start=1):
        row_cells = table.rows[row_idx].cells
        for col_idx, cell_data in enumerate(row_data):
            row_cells[col_idx].text = str(cell_data)

    return table

def add_warning_box(doc, text):
    """Add a warning/important box"""
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(f"⚠️ IMPORTANT: {text}")
    run.font.bold = True
    run.font.color.rgb = RGBColor(204, 0, 0)

    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'FFF3CD')
    paragraph._element.get_or_add_pPr().append(shading_elm)

    paragraph.paragraph_format.left_indent = Inches(0.25)
    paragraph.paragraph_format.right_indent = Inches(0.25)
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(6)

    return paragraph

def add_success_box(doc, text):
    """Add a success/checkmark box"""
    paragraph = doc.add_paragraph()
    run = paragraph.add_run(f"✅ {text}")
    run.font.color.rgb = RGBColor(0, 102, 0)

    shading_elm = OxmlElement('w:shd')
    shading_elm.set(qn('w:fill'), 'D4EDDA')
    paragraph._element.get_or_add_pPr().append(shading_elm)

    paragraph.paragraph_format.left_indent = Inches(0.25)
    paragraph.paragraph_format.right_indent = Inches(0.25)
    paragraph.paragraph_format.space_before = Pt(6)
    paragraph.paragraph_format.space_after = Pt(6)

    return paragraph

def create_setup_guide():
    """Create the complete setup guide Word document"""
    doc = Document()

    # =========================================================================
    # TITLE PAGE
    # =========================================================================
    title = doc.add_heading('QA Agent System Setup Guide', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.runs[0].font.color.rgb = RGBColor(0, 51, 102)

    subtitle = doc.add_paragraph('Complete Installation Guide for DB/UI/API Testing Agents')
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.runs[0].font.size = Pt(14)
    subtitle.runs[0].font.color.rgb = RGBColor(102, 102, 102)

    subtitle2 = doc.add_paragraph('Windows 10/11 Enterprise Environment')
    subtitle2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle2.runs[0].font.size = Pt(12)
    subtitle2.runs[0].italic = True

    doc.add_paragraph()
    version_para = doc.add_paragraph('Version 2.0.0')
    version_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    date_para = doc.add_paragraph('Last Updated: September 2026')
    date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_page_break()

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    add_heading_with_style(doc, 'Table of Contents', level=1)

    toc_items = [
        "1. Overview",
        "2. What Needs to Be Copied/Shared",
        "3. Prerequisites",
        "4. New Laptop Step-by-Step Installation",
        "5. Claude Code + Vertex AI Setup",
        "6. Azure DevOps Authentication",
        "7. MCP Server Configuration",
        "8. DB Agent Setup",
        "9. UI Agent Setup",
        "10. API Agent Setup",
        "11. Integrated QA Workflow",
        "12. Validation Checklist",
        "13. Troubleshooting",
        "14. Security Best Practices"
    ]

    for item in toc_items:
        doc.add_paragraph(item, style='List Number')

    doc.add_page_break()

    # =========================================================================
    # 1. OVERVIEW
    # =========================================================================
    add_heading_with_style(doc, '1. Overview', level=1)

    doc.add_paragraph(
        'This guide provides complete step-by-step instructions for setting up the QA Agent '
        'system on a new Windows laptop. The system automates QA testing workflows from '
        'PBI (Product Backlog Item) requirements to test case generation.'
    )

    doc.add_paragraph()
    add_heading_with_style(doc, '1.1 System Components', level=2)

    components_data = [
        ['Component', 'Purpose'],
        ['Claude Code', 'AI-powered code assistant with agent capabilities'],
        ['Azure DevOps MCP', 'Fetches PBIs from Azure DevOps'],
        ['Usage Empire MCP', 'Database and API testing integration'],
        ['DB Agent', 'Database schema analysis and test generation'],
        ['UI Agent', 'UI test execution guide and screenshot validation'],
        ['API Agent', 'API endpoint testing and validation'],
        ['QA Workflow Orchestrator', 'Coordinates all agents with checkpoints']
    ]

    add_table_from_data(doc, components_data[0], components_data[1:])

    doc.add_paragraph()
    add_heading_with_style(doc, '1.2 Workflow Overview', level=2)

    workflow_steps = [
        "Phase 1: Fetch PBI from Azure DevOps + Collect user context → pbi-data.json + user-context.json",
        "Phase 2: Read integration documentation → integration-docs.json",
        "Phase 3: Create QA Understanding Document → QA_Understanding_Document.docx (Word)",
        "Phase 4: Map test scenarios to AC → Test-Scenarios-Mapped-to-AC.xlsx",
        "Phase 5: Generate test cases → Test_Cases_PBI_<number>.xlsx",
        "Optional: Execute DB/UI/API agents based on selected test types"
    ]

    for step in workflow_steps:
        doc.add_paragraph(step, style='List Bullet')

    doc.add_page_break()

    # =========================================================================
    # 2. WHAT NEEDS TO BE COPIED/SHARED
    # =========================================================================
    add_heading_with_style(doc, '2. What Needs to Be Copied/Shared', level=1)

    add_heading_with_style(doc, '2.1 Required Folders and Files', level=2)

    doc.add_paragraph('The following folders and files from the QE_MCP_automation project must be included:')

    required_items = [
        ".claude/ — All agent definitions and skills",
        ".agents/ — MCP configuration templates",
        "docs/ — Integration documentation (API, DB, Business Logic)",
        "*.py — All Python scripts for document/Excel generation",
        "*.js — JavaScript utilities (if any)",
        "package.json — Node.js dependencies",
        "requirements.txt — Python dependencies",
        ".gitignore — Git ignore rules",
        ".mcp.json — MCP server configuration (template)",
        "README.md — Project documentation",
        "ENVIRONMENT_SETUP.md — Environment variable setup guide"
    ]

    for item in required_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '2.2 Files to EXCLUDE from ZIP', level=2)

    add_warning_box(doc, "NEVER include these files/folders in the shared ZIP:")

    excluded_items = [
        "outputs/ — Contains PBI-specific output files",
        "node_modules/ — Will be regenerated via npm install",
        "__pycache__/ — Python bytecode cache",
        "*.log — Log files",
        ".env — Environment variable file (MUST NOT be shared)",
        ".env.* — Any environment variable files",
        "*.pyc, *.pyo, *.pyd — Python compiled files",
        "Any files containing PAT tokens, API keys, or credentials"
    ]

    for item in excluded_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '2.3 Folder Structure After Extraction', level=2)

    doc.add_paragraph('After extracting the ZIP file, the structure should be:')

    add_code_block(doc, """C:\\UE_Automation\\
├── QE_MCP_automation\\         (This project)
│   ├── .claude\\
│   │   ├── agents\\
│   │   ├── skills\\
│   │   └── settings.json
│   ├── .agents\\
│   ├── docs\\
│   │   └── integrations\\
│   ├── *.py
│   ├── package.json
│   ├── requirements.txt
│   └── .mcp.json
└── usage-empire\\              (Parent repo - separate setup)
    ├── ue-api\\
    └── .nrg\\
        └── keys\\              (Service account keys - NOT shared)""")

    doc.add_paragraph()
    add_warning_box(doc,
        "The usage-empire repository is a SEPARATE project. It is NOT included in the "
        "QE_MCP_automation ZIP. It must be cloned separately and configured with its own "
        "authentication (Google Cloud service account keys)."
    )

    doc.add_page_break()

    # =========================================================================
    # 3. PREREQUISITES
    # =========================================================================
    add_heading_with_style(doc, '3. Prerequisites', level=1)

    add_heading_with_style(doc, '3.1 Software Requirements', level=2)

    software_reqs = [
        ['Software', 'Version', 'Purpose'],
        ['Windows 10/11 Pro', '10.0.26200+', 'Operating system'],
        ['VS Code', 'Latest', 'IDE for Claude Code extension'],
        ['Git + Git Bash', '2.40+', 'Version control and shell'],
        ['Python', '3.10+', 'Python scripts for document generation'],
        ['Node.js', '18+', 'Azure DevOps MCP server'],
        ['Claude Code', 'Latest', 'AI agent orchestration'],
        ['Google Cloud SDK', 'Latest', 'For usage-empire MCP (if DB/API testing)']
    ]

    add_table_from_data(doc, software_reqs[0], software_reqs[1:])

    doc.add_paragraph()
    add_heading_with_style(doc, '3.2 Required VS Code Extensions', level=2)

    extensions = [
        "Claude Code (Official) — com.anthropic.claude-code",
        "Python — ms-python.python (optional, for editing Python scripts)",
        "GitLens — eamodio.gitlens (optional, for Git integration)"
    ]

    for ext in extensions:
        doc.add_paragraph(ext, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '3.3 Required Access/Permissions', level=2)

    access_reqs = [
        "Azure DevOps Account — Access to digital-it-apps organization",
        "NRG-Business-CI Project Access — Read permissions for work items",
        "Azure DevOps PAT Creation Rights — To create personal access token",
        "VPN/Network Access — Connection to NRG internal network (if required)",
        "Google Cloud Access — For usage-empire project (if DB/API testing needed)",
        "Vertex AI API Access — For Claude Code authentication"
    ]

    for req in access_reqs:
        doc.add_paragraph(req, style='List Bullet')

    doc.add_page_break()

    # =========================================================================
    # 4. NEW LAPTOP STEP-BY-STEP INSTALLATION
    # =========================================================================
    add_heading_with_style(doc, '4. New Laptop Step-by-Step Installation', level=1)

    doc.add_paragraph(
        'Follow these steps in order on a completely fresh Windows laptop. '
        'Commands are provided for PowerShell and Git Bash where applicable.'
    )

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 1: Install Git + Git Bash', level=2)

    doc.add_paragraph('1. Download Git for Windows from: https://git-scm.com/download/win')
    doc.add_paragraph('2. Run the installer with default settings')
    doc.add_paragraph('3. Verify installation:')

    add_code_block(doc, """# Git Bash
git --version
# Expected: git version 2.40.0 (or higher)""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 2: Install Node.js', level=2)

    doc.add_paragraph('1. Download Node.js LTS from: https://nodejs.org/')
    doc.add_paragraph('2. Run the installer (include npm package manager)')
    doc.add_paragraph('3. Verify installation:')

    add_code_block(doc, """# PowerShell or Git Bash
node --version
# Expected: v18.x.x or higher

npm --version
# Expected: 9.x.x or higher""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 3: Install Python', level=2)

    doc.add_paragraph('1. Download Python 3.10+ from: https://www.python.org/downloads/')
    doc.add_paragraph('2. IMPORTANT: Check "Add Python to PATH" during installation')
    doc.add_paragraph('3. Verify installation:')

    add_code_block(doc, """# PowerShell or Git Bash
python --version
# Expected: Python 3.10.x or higher

python -m pip --version
# Expected: pip version info""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 4: Install VS Code', level=2)

    doc.add_paragraph('1. Download VS Code from: https://code.visualstudio.com/')
    doc.add_paragraph('2. Run the installer')
    doc.add_paragraph('3. Launch VS Code')

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 5: Extract QE_MCP_automation Project', level=2)

    doc.add_paragraph('1. Extract the QE_MCP_automation.zip to:')

    add_code_block(doc, """C:\\UE_Automation\\QE_MCP_automation\\""")

    doc.add_paragraph('2. Verify folder structure:')

    add_code_block(doc, """# Git Bash
cd /c/UE_Automation/QE_MCP_automation
ls -la

# Should show:
# .claude/
# .agents/
# docs/
# *.py files
# package.json
# requirements.txt""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 6: Install Python Dependencies', level=2)

    doc.add_paragraph('1. Navigate to project directory:')

    add_code_block(doc, """# Git Bash
cd /c/UE_Automation/QE_MCP_automation""")

    doc.add_paragraph('2. Install Python packages:')

    add_code_block(doc, """# Git Bash
python -m pip install python-docx openpyxl

# Verify installation
python -c "import docx; import openpyxl; print('Success')"
# Expected: Success""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Step 7: Install Node.js Dependencies', level=2)

    add_code_block(doc, """# Git Bash
cd /c/UE_Automation/QE_MCP_automation
npm install

# Expected: Creates node_modules/ and installs exceljs""")

    doc.add_page_break()

    # =========================================================================
    # 5. CLAUDE CODE + VERTEX AI SETUP
    # =========================================================================
    add_heading_with_style(doc, '5. Claude Code + Vertex AI Setup', level=1)

    add_heading_with_style(doc, '5.1 Install Claude Code Extension', level=2)

    doc.add_paragraph('1. Open VS Code')
    doc.add_paragraph('2. Go to Extensions (Ctrl+Shift+X)')
    doc.add_paragraph('3. Search for "Claude Code"')
    doc.add_paragraph('4. Install the official Anthropic Claude Code extension')
    doc.add_paragraph('5. Restart VS Code')

    doc.add_paragraph()
    add_heading_with_style(doc, '5.2 Authenticate with Vertex AI', level=2)

    add_warning_box(doc,
        "Claude Code uses Vertex AI for authentication. You MUST have Google Cloud SDK "
        "installed and configured with proper access to the Vertex AI API."
    )

    doc.add_paragraph()
    doc.add_paragraph('1. Install Google Cloud SDK from: https://cloud.google.com/sdk/docs/install')
    doc.add_paragraph('2. Initialize gcloud:')

    add_code_block(doc, """# PowerShell
gcloud init

# Follow prompts:
# - Login with your NRG Google account
# - Select the appropriate GCP project""")

    doc.add_paragraph('3. Verify authentication:')

    add_code_block(doc, """# PowerShell
gcloud auth list
# Your account should show ACTIVE

gcloud config list
# Should show your project and account""")

    doc.add_paragraph()
    add_heading_with_style(doc, '5.3 Configure Claude Code', level=2)

    doc.add_paragraph('1. Open VS Code Command Palette (Ctrl+Shift+P)')
    doc.add_paragraph('2. Type: "Claude Code: Sign In"')
    doc.add_paragraph('3. Follow authentication prompts')
    doc.add_paragraph('4. Verify connection:')

    add_success_box(doc, 'Claude Code should show "Connected" status in VS Code')

    doc.add_page_break()

    # =========================================================================
    # 6. AZURE DEVOPS AUTHENTICATION
    # =========================================================================
    add_heading_with_style(doc, '6. Azure DevOps Authentication', level=1)

    add_heading_with_style(doc, '6.1 Create Azure DevOps Personal Access Token (PAT)', level=2)

    doc.add_paragraph('1. Navigate to: https://dev.azure.com/digital-it-apps')
    doc.add_paragraph('2. Click your profile icon (top right) → Personal Access Tokens')
    doc.add_paragraph('3. Click "+ New Token"')
    doc.add_paragraph('4. Configure the token:')

    pat_config = [
        ['Setting', 'Value'],
        ['Name', 'Claude Code MCP - QE Automation'],
        ['Organization', 'digital-it-apps'],
        ['Expiration', '90 days (or per your policy)'],
        ['Scopes', 'Custom defined (see below)']
    ]

    add_table_from_data(doc, pat_config[0], pat_config[1:])

    doc.add_paragraph()
    doc.add_paragraph('5. Required Scopes:')

    scopes = [
        "Work Items: Read & Write",
        "Code: Read",
        "Test Management: Read & Write",
        "Build: Read"
    ]

    for scope in scopes:
        doc.add_paragraph(scope, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph('6. Click "Create"')
    doc.add_paragraph('7. COPY THE TOKEN IMMEDIATELY — It is only shown once!')

    doc.add_paragraph()
    add_heading_with_style(doc, '6.2 Set PAT as Windows Environment Variable', level=2)

    add_warning_box(doc,
        "The PAT MUST be stored as a Windows System Environment Variable, "
        "NOT in a .env file or hardcoded in any project file."
    )

    doc.add_paragraph()
    doc.add_paragraph('Option 1: PowerShell (Recommended)')

    add_code_block(doc, """# PowerShell (run as regular user, admin NOT required)
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-actual-pat-token-here', 'User')

# Verify it was set
[System.Environment]::GetEnvironmentVariable('AZURE_DEVOPS_PAT', 'User')
# Expected: Shows your PAT token""")

    doc.add_paragraph()
    doc.add_paragraph('Option 2: Windows GUI')

    gui_steps = [
        "Press Win+R, type sysdm.cpl, press Enter",
        "Go to Advanced tab → Environment Variables",
        "Under User variables, click New",
        "Variable name: AZURE_DEVOPS_PAT",
        "Variable value: <your-pat-token>",
        "Click OK on all dialogs"
    ]

    for step in gui_steps:
        doc.add_paragraph(step, style='List Number')

    doc.add_paragraph()
    add_heading_with_style(doc, '6.3 Restart Applications', level=2)

    add_warning_box(doc,
        "After setting the environment variable, you MUST restart all terminals, "
        "VS Code, and Claude Code for the variable to be available."
    )

    restart_steps = [
        "Close all Git Bash terminals",
        "Close all PowerShell windows",
        "Close VS Code completely",
        "Reopen VS Code",
        "Open a new Git Bash terminal in VS Code"
    ]

    for step in restart_steps:
        doc.add_paragraph(step, style='List Number')

    doc.add_paragraph()
    add_heading_with_style(doc, '6.4 Verify PAT Environment Variable', level=2)

    add_code_block(doc, """# Git Bash (after restart)
echo $AZURE_DEVOPS_PAT
# Expected: Shows your PAT token (52 characters)

# PowerShell (after restart)
$env:AZURE_DEVOPS_PAT
# Expected: Shows your PAT token""")

    doc.add_paragraph()

    add_warning_box(doc,
        "If the variable is blank or shows 'AZURE_DEVOPS_PAT' literally, the environment "
        "variable was not set correctly. Repeat Step 6.2 and restart applications."
    )

    doc.add_page_break()

    # =========================================================================
    # 7. MCP SERVER CONFIGURATION
    # =========================================================================
    add_heading_with_style(doc, '7. MCP Server Configuration', level=1)

    add_heading_with_style(doc, '7.1 Understanding .mcp.json', level=2)

    doc.add_paragraph(
        'The .mcp.json file configures MCP (Model Context Protocol) servers that provide '
        'tools for Claude Code agents. This project uses two MCP servers:'
    )

    doc.add_paragraph()

    mcp_servers = [
        ['MCP Server', 'Purpose', 'Used By'],
        ['azure-devops', 'Fetch PBIs from Azure DevOps', 'Phase 1: PBI Fetcher'],
        ['usage-empire-dev', 'Database and API testing', 'DB/API Agents'],
        ['postgres', 'PostgreSQL database queries', 'DB Agent']
    ]

    add_table_from_data(doc, mcp_servers[0], mcp_servers[1:])

    doc.add_paragraph()
    add_heading_with_style(doc, '7.2 Current .mcp.json Configuration', level=2)

    doc.add_paragraph('The project includes a pre-configured .mcp.json file:')

    add_code_block(doc, """{
  "mcpServers": {
    "azure-devops": {
      "command": "npx",
      "args": ["-y", "@azure-devops/mcp", "digital-it-apps"],
      "env": {
        "AZURE_DEVOPS_PAT": "${AZURE_DEVOPS_PAT}",
        "ADO_DEFAULT_PROJECT": "NRG-Business-CI"
      }
    },
    "usage-empire-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\\\UE_Automation\\\\usage-empire\\\\ue-api",
        "run",
        "src/mcp/server.py",
        "--env",
        "env/dev.yml"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "c:\\\\UE_Automation\\\\usage-empire\\\\.nrg\\\\keys\\\\dev.json"
      }
    },
    "postgres": {
      "command": "uv",
      "args": [
        "--directory",
        "c:\\\\UE_Automation\\\\usage-empire\\\\ue-api",
        "run",
        "src/mcp/run_postgres_mcp.py",
        "--env",
        "env/dev.yml"
      ],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "c:\\\\UE_Automation\\\\usage-empire\\\\.nrg\\\\keys\\\\dev.json",
        "NODE_TLS_REJECT_UNAUTHORIZED": "0"
      }
    }
  }
}""")

    doc.add_paragraph()
    add_heading_with_style(doc, '7.3 Azure DevOps MCP Setup', level=2)

    doc.add_paragraph('The azure-devops MCP server is automatically configured. Verify:')

    add_code_block(doc, """# Git Bash
cd /c/UE_Automation/QE_MCP_automation

# Test Azure DevOps MCP connection
npx -y @azure-devops/mcp digital-it-apps --help

# If successful, the MCP server help will display""")

    doc.add_paragraph()
    add_success_box(doc,
        'No additional configuration needed for Azure DevOps MCP. It uses the '
        'AZURE_DEVOPS_PAT environment variable set in Step 6.'
    )

    doc.add_paragraph()
    add_heading_with_style(doc, '7.4 Usage Empire MCP Setup (For DB/API Testing)', level=2)

    add_warning_box(doc,
        "The usage-empire MCP servers require the usage-empire repository to be cloned "
        "separately and configured with Google Cloud service account keys. This is ONLY "
        "needed if you plan to use DB or API testing agents."
    )

    doc.add_paragraph()
    doc.add_paragraph('Skip this section if you are ONLY using:')

    skip_items = [
        "Phase 1-5 (PBI fetch → Test cases generation)",
        "UI testing only"
    ]

    for item in skip_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph(
        'If you need DB/API testing, the usage-empire repository setup is beyond the scope '
        'of this document. Contact your team lead for the separate usage-empire setup guide.'
    )

    doc.add_page_break()

    # =========================================================================
    # 8. DB AGENT SETUP
    # =========================================================================
    add_heading_with_style(doc, '8. DB Agent Setup', level=1)

    add_heading_with_style(doc, '8.1 DB Agent Files', level=2)

    doc.add_paragraph('The DB Agent is defined in:')

    add_code_block(doc, """.claude/agents/db_research_planner.md""")

    doc.add_paragraph()
    add_heading_with_style(doc, '8.2 DB Agent Dependencies', level=2)

    doc.add_paragraph('The DB Agent requires:')

    db_deps = [
        "PostgreSQL MCP server (usage-empire)",
        "Google Cloud service account keys",
        "Database connection credentials",
        "Integration documentation in docs/integrations/database/"
    ]

    for dep in db_deps:
        doc.add_paragraph(dep, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '8.3 How DB Agent Works', level=2)

    doc.add_paragraph(
        'The DB Agent analyzes database schema and generates test scenarios. It:')

    db_process = [
        "Reads user-context.json to check if 'Database' is in selected_types",
        "If Database not selected → Skips execution (clean no-op)",
        "If Database selected → Loads PBI data and DB details",
        "Searches integration documentation for schema info",
        "Identifies tables, columns, constraints, relationships",
        "Generates db-analysis.md with test scenarios",
        "Creates db-test-scripts.sql (if applicable)"
    ]

    for step in db_process:
        doc.add_paragraph(step, style='List Number')

    doc.add_paragraph()
    add_heading_with_style(doc, '8.4 DB Agent Scope Guard', level=2)

    add_warning_box(doc,
        "The DB Agent has a MANDATORY scope guard. It will ABORT if user-context.json "
        "does not exist or if 'Database' is not in selected_types. This prevents "
        "generating database analysis for unrelated PBIs."
    )

    doc.add_paragraph()
    add_heading_with_style(doc, '8.5 Verifying DB Agent', level=2)

    doc.add_paragraph('To verify the DB Agent is configured correctly:')

    add_code_block(doc, """# In VS Code with Claude Code
# Open the project: C:\\UE_Automation\\QE_MCP_automation

# In Claude Code chat:
List available agents

# Expected output should include:
# - db-research-planner""")

    doc.add_paragraph()
    doc.add_paragraph('For full DB testing, ensure:')

    db_checklist = [
        "usage-empire repository is cloned and configured",
        "PostgreSQL MCP server is running",
        "Database credentials are set",
        "Integration docs exist in docs/integrations/database/"
    ]

    for item in db_checklist:
        doc.add_paragraph(f"☐ {item}")

    doc.add_page_break()

    # =========================================================================
    # 9. UI AGENT SETUP
    # =========================================================================
    add_heading_with_style(doc, '9. UI Agent Setup', level=1)

    add_heading_with_style(doc, '9.1 UI Agent Files', level=2)

    doc.add_paragraph('The UI Agent is defined in:')

    add_code_block(doc, """.claude/agents/ui_test_executor.md""")

    doc.add_paragraph()
    add_heading_with_style(doc, '9.2 UI Agent Purpose', level=2)

    doc.add_paragraph(
        'The UI Agent generates UI test execution guides and validates screenshot capture. '
        'It does NOT automate browser testing directly. Instead, it:'
    )

    ui_features = [
        "Generates detailed step-by-step execution guide",
        "Creates screenshots directory structure",
        "Provides screenshot naming conventions",
        "Validates that all screenshots are captured",
        "Records test results as PASS/FAIL/BLOCKED"
    ]

    for feature in ui_features:
        doc.add_paragraph(feature, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '9.3 UI Agent Scope Guard', level=2)

    add_warning_box(doc,
        "The UI Agent has a MANDATORY scope guard. It will SKIP execution if "
        "user-context.json does not exist or if 'UI' is not in selected_types. "
        "This prevents generating UI test guides for API/DB-only PBIs."
    )

    doc.add_paragraph()
    add_heading_with_style(doc, '9.4 UI Test Execution Workflow', level=2)

    doc.add_paragraph('When the UI Agent runs:')

    ui_workflow = [
        "Loads UI test cases from Test_Cases_PBI_<number>.xlsx",
        "Filters test cases using 'Test Type Map' sheet (Type = UI)",
        "Generates ui-test-execution-guide.md",
        "Creates outputs/<PBI>/deliverables/ui/screenshots/ directory",
        "QA tester manually executes tests and captures screenshots",
        "UI Agent validates screenshot existence",
        "Saves results to ui-test-results.json"
    ]

    for idx, step in enumerate(ui_workflow, 1):
        doc.add_paragraph(f"{idx}. {step}")

    doc.add_paragraph()
    add_heading_with_style(doc, '9.5 Screenshot Naming Convention', level=2)

    doc.add_paragraph('Screenshots must follow this naming pattern:')

    add_code_block(doc, """tc-<test-number>-step-<step-number>.png

Examples:
tc-001-step-1.png  → Test case 1, step 1
tc-001-step-2.png  → Test case 1, step 2
tc-002-step-1.png  → Test case 2, step 1""")

    doc.add_paragraph()
    add_heading_with_style(doc, '9.6 Verifying UI Agent', level=2)

    add_code_block(doc, """# In Claude Code
List available agents

# Expected output should include:
# - ui-test-executor

# To invoke the UI Agent:
@ui-test-executor <pbi-number>""")

    doc.add_paragraph()
    add_success_box(doc,
        'UI Agent requires NO additional tools or dependencies beyond the base Python '
        'packages (python-docx, openpyxl) already installed.'
    )

    doc.add_page_break()

    # =========================================================================
    # 10. API AGENT SETUP
    # =========================================================================
    add_heading_with_style(doc, '10. API Agent Setup', level=1)

    add_warning_box(doc,
        "The API Agent is part of the usage-empire MCP server. It is NOT a standalone "
        "agent in this project. API testing uses MCP tools from usage-empire."
    )

    doc.add_paragraph()
    add_heading_with_style(doc, '10.1 API Testing Overview', level=2)

    doc.add_paragraph(
        'API testing in this system works differently than DB/UI agents. Instead of a '
        'dedicated agent, API testing:'
    )

    api_features = [
        "Uses test cases generated in Phase 5",
        "Filters test cases by Type = 'API' from Test Type Map sheet",
        "Relies on integration documentation in docs/integrations/apis/",
        "Can use MCP tools from usage-empire for execution (if configured)"
    ]

    for feature in api_features:
        doc.add_paragraph(feature, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '10.2 API Integration Documentation', level=2)

    doc.add_paragraph('API documentation should be maintained in:')

    add_code_block(doc, """docs/integrations/apis/

Example structure:
docs/integrations/apis/
├── pod-forecast-batch-results.md
├── forecast-model-api.md
└── therm-integration.md

Each API doc should include:
- Endpoint URL and HTTP method
- Request headers, parameters, body
- Response schema and status codes
- Validation rules
- Example requests/responses
- Error scenarios""")

    doc.add_paragraph()
    add_heading_with_style(doc, '10.3 Verifying API Setup', level=2)

    doc.add_paragraph(
        'API testing does not require a separate agent verification. Verify that:'
    )

    api_checklist = [
        "Integration docs exist in docs/integrations/apis/",
        "Test cases are generated with Type = 'API'",
        "usage-empire MCP is configured (if automated execution needed)"
    ]

    for item in api_checklist:
        doc.add_paragraph(f"☐ {item}")

    doc.add_page_break()

    # =========================================================================
    # 11. INTEGRATED QA WORKFLOW
    # =========================================================================
    add_heading_with_style(doc, '11. Integrated QA Workflow', level=1)

    add_heading_with_style(doc, '11.1 Complete Workflow Overview', level=2)

    doc.add_paragraph('The complete QA workflow consists of 5 phases:')

    phases = [
        ['Phase', 'Agent', 'Output'],
        ['1', 'ado-pbi-fetcher + user input', 'pbi-data.json + user-context.json'],
        ['2', 'md-file-reader', 'integration-docs.json'],
        ['3', 'qa-understanding-doc-creator', 'QA_Understanding_Document.docx'],
        ['4', 'test-scenario-ac-mapper', 'Test-Scenarios-Mapped-to-AC.xlsx'],
        ['5', 'qa-test-cases-generator', 'Test_Cases_PBI_<number>.xlsx']
    ]

    add_table_from_data(doc, phases[0], phases[1:])

    doc.add_paragraph()
    add_heading_with_style(doc, '11.2 How to Run the Workflow', level=2)

    doc.add_paragraph('Use the qa-workflow skill:')

    add_code_block(doc, """# In Claude Code chat:
@qa-workflow <PBI_NUMBER>

Example:
@qa-workflow 643243""")

    doc.add_paragraph()
    add_heading_with_style(doc, '11.3 User Checkpoints', level=2)

    doc.add_paragraph('The workflow includes 2 user checkpoints:')

    checkpoints = [
        ['Checkpoint', 'After Phase', 'Review Document', 'Actions'],
        [
            '1',
            '3',
            'QA_Understanding_Document.docx',
            'Approve / Request Changes / Cancel'
        ],
        [
            '2',
            '4',
            'Test-Scenarios-Mapped-to-AC.xlsx',
            'Approve / Add More Scenarios / Cancel'
        ]
    ]

    add_table_from_data(doc, checkpoints[0], checkpoints[1:])

    doc.add_paragraph()
    add_heading_with_style(doc, '11.4 Test Type Selection and Scope Control', level=2)

    add_warning_box(doc,
        "CRITICAL: Test type selection controls which agents execute and which test cases "
        "are generated. The selected_types list in user-context.json is the authoritative "
        "scope contract."
    )

    doc.add_paragraph()
    doc.add_paragraph('During Phase 1, the user is asked:')

    add_code_block(doc, """Question 1: What type of testing are you performing?
Options:
  - API/Endpoint Testing
  - UI/Frontend Testing
  - Database Testing
  - Business Logic Testing
  - Integration Testing
  - Mixed Testing (select multiple)

If "Mixed" is selected:
  Question 1a: Which test types? (multi-select)
    - API
    - UI
    - Database
    - BusinessLogic""")

    doc.add_paragraph()
    doc.add_paragraph('This creates user-context.json with:')

    add_code_block(doc, """{
  "pbi_number": "643243",
  "selected_types": ["UI", "API"],  // Authoritative scope
  "primary_type": "UI",
  "components": {
    "UI": "POD Details Page - Last Forecasted Date column",
    "API": "POST /pod-forecast-batch-results"
  }
}""")

    doc.add_paragraph()
    add_heading_with_style(doc, '11.5 Execution Scenarios', level=2)

    doc.add_paragraph('API-only scenario:')

    add_code_block(doc, """selected_types: ["API"]
→ Phase 5 generates test cases with Type = "API"
→ DB Agent skips (Database not in selected_types)
→ UI Agent skips (UI not in selected_types)""")

    doc.add_paragraph()
    doc.add_paragraph('UI-only scenario:')

    add_code_block(doc, """selected_types: ["UI"]
→ Phase 5 generates test cases with Type = "UI"
→ DB Agent skips
→ API-related test cases not generated
→ UI Agent executes after Phase 5""")

    doc.add_paragraph()
    doc.add_paragraph('Mixed scenario (UI + Database):')

    add_code_block(doc, """selected_types: ["UI", "Database"]
→ Phase 5 generates test cases with Type = "UI" and Type = "Database"
→ DB Agent executes after Phase 5
→ UI Agent executes after Phase 5
→ API-related test cases NOT generated (API not selected)""")

    doc.add_paragraph()
    add_warning_box(doc,
        "Agents use the Test Type Map sheet in Test_Cases_PBI_<number>.xlsx to filter "
        "test cases by type. Only test cases matching the agent's type are processed."
    )

    doc.add_page_break()

    # =========================================================================
    # 12. VALIDATION CHECKLIST
    # =========================================================================
    add_heading_with_style(doc, '12. Validation Checklist', level=1)

    doc.add_paragraph('Use this checklist to verify the complete setup:')

    doc.add_paragraph()
    add_heading_with_style(doc, '12.1 Software Installation', level=2)

    software_checks = [
        "Git Bash installed and accessible",
        "Node.js and npm installed (node --version, npm --version)",
        "Python 3.10+ installed (python --version)",
        "VS Code installed",
        "Claude Code extension installed in VS Code"
    ]

    for check in software_checks:
        doc.add_paragraph(f"☐ {check}")

    doc.add_paragraph()
    add_heading_with_style(doc, '12.2 Authentication', level=2)

    auth_checks = [
        "Google Cloud SDK installed and authenticated (gcloud auth list)",
        "Vertex AI access verified",
        "Claude Code connected in VS Code",
        "Azure DevOps PAT created with correct scopes",
        "AZURE_DEVOPS_PAT environment variable set",
        "Environment variable persists after restarting terminals"
    ]

    for check in auth_checks:
        doc.add_paragraph(f"☐ {check}")

    doc.add_paragraph()
    add_heading_with_style(doc, '12.3 Project Setup', level=2)

    project_checks = [
        "QE_MCP_automation extracted to C:\\UE_Automation\\QE_MCP_automation",
        "Python packages installed (python-docx, openpyxl)",
        "Node.js packages installed (npm install completed)",
        ".mcp.json exists in project root",
        ".claude/agents/ folder contains all agent definitions",
        "docs/integrations/ folder exists with API/DB/business-logic subdirs"
    ]

    for check in project_checks:
        doc.add_paragraph(f"☐ {check}")

    doc.add_paragraph()
    add_heading_with_style(doc, '12.4 MCP Servers', level=2)

    add_code_block(doc, """# Verify Azure DevOps MCP
npx -y @azure-devops/mcp digital-it-apps --help
# Should show help text

# Verify environment variable is accessible
echo $AZURE_DEVOPS_PAT
# Should show your PAT (52 characters)""")

    mcp_checks = [
        "Azure DevOps MCP server responds to --help",
        "AZURE_DEVOPS_PAT visible in terminal (echo $AZURE_DEVOPS_PAT)",
        "usage-empire MCP configured (if DB/API testing needed)"
    ]

    for check in mcp_checks:
        doc.add_paragraph(f"☐ {check}")

    doc.add_paragraph()
    add_heading_with_style(doc, '12.5 Agent Verification', level=2)

    add_code_block(doc, """# In Claude Code:
List available agents

# Expected agents:
# - ado-pbi-fetcher
# - md-file-reader
# - qa-understanding-doc-creator
# - test-scenario-ac-mapper
# - qa-test-cases-generator
# - qa-workflow-orchestrator
# - db-research-planner
# - ui-test-executor""")

    doc.add_paragraph()
    add_heading_with_style(doc, '12.6 End-to-End Workflow Test', level=2)

    doc.add_paragraph('Run a simple workflow test:')

    add_code_block(doc, """# In Claude Code:
@qa-workflow 643243

# Expected:
# 1. Fetches PBI from Azure DevOps
# 2. Asks for test type and component
# 3. Generates user-context.json
# 4. Reads integration docs
# 5. Creates QA_Understanding_Document.docx
# 6. Asks for checkpoint 1 approval
# 7. Generates Test-Scenarios-Mapped-to-AC.xlsx
# 8. Asks for checkpoint 2 approval
# 9. Generates Test_Cases_PBI_643243.xlsx
# 10. Executes DB/UI agents if applicable""")

    doc.add_paragraph()

    workflow_checks = [
        "PBI fetched successfully from Azure DevOps",
        "User context collected (test type, component)",
        "QA Understanding Document generated in Word format",
        "Test scenarios mapped to AC in Excel",
        "Test cases generated in Azure DevOps format",
        "All files saved to outputs/<PBI>/ directory"
    ]

    for check in workflow_checks:
        doc.add_paragraph(f"☐ {check}")

    doc.add_page_break()

    # =========================================================================
    # 13. TROUBLESHOOTING
    # =========================================================================
    add_heading_with_style(doc, '13. Troubleshooting', level=1)

    add_heading_with_style(doc, '13.1 Claude Code Connection Issues', level=2)

    doc.add_paragraph('Problem: Claude Code not connecting or authentication failing')

    doc.add_paragraph()
    doc.add_paragraph('Solutions:')

    claude_solutions = [
        "Verify Google Cloud SDK is installed: gcloud --version",
        "Check authentication: gcloud auth list (should show ACTIVE account)",
        "Re-authenticate: gcloud auth login",
        "Verify Vertex AI API access in your GCP project",
        "Restart VS Code after authentication",
        "Check Claude Code extension is latest version"
    ]

    for sol in claude_solutions:
        doc.add_paragraph(sol, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '13.2 Azure DevOps PAT Issues', level=2)

    doc.add_paragraph('Problem: "AZURE_DEVOPS_PAT environment variable NOT set"')

    doc.add_paragraph()
    doc.add_paragraph('Solutions:')

    pat_solutions = [
        "Verify variable is set: echo $AZURE_DEVOPS_PAT (Git Bash) or $env:AZURE_DEVOPS_PAT (PowerShell)",
        "If empty, set again using PowerShell method from Section 6.2",
        "Restart ALL terminals and VS Code after setting",
        "Verify persistence: Close and reopen terminal, check again",
        "If using GUI method, ensure it's in User variables, not System variables",
        "Check PAT hasn't expired in Azure DevOps"
    ]

    for sol in pat_solutions:
        doc.add_paragraph(sol, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '13.3 PowerShell Execution Policy Issues', level=2)

    doc.add_paragraph('Problem: "Scripts are disabled on this system"')

    doc.add_paragraph()
    doc.add_paragraph('Solution:')

    add_code_block(doc, """# PowerShell (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify
Get-ExecutionPolicy
# Expected: RemoteSigned""")

    doc.add_paragraph()
    add_heading_with_style(doc, '13.4 MCP Connection Failures', level=2)

    doc.add_paragraph('Problem: "azure-devops: not connected" or MCP server failed')

    doc.add_paragraph()
    doc.add_paragraph('Solutions:')

    mcp_solutions = [
        "Verify AZURE_DEVOPS_PAT is set (echo $AZURE_DEVOPS_PAT)",
        "Test MCP manually: npx -y @azure-devops/mcp digital-it-apps --help",
        "Check network/proxy settings",
        "Verify PAT has correct scopes (Work Items, Code, Test Management)",
        "Restart Claude Code session",
        "Check .mcp.json file exists and is valid JSON"
    ]

    for sol in mcp_solutions:
        doc.add_paragraph(sol, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '13.5 Python Dependency Issues', level=2)

    doc.add_paragraph('Problem: "ModuleNotFoundError: No module named \'docx\'"')

    doc.add_paragraph()
    doc.add_paragraph('Solution:')

    add_code_block(doc, """# Git Bash
cd /c/UE_Automation/QE_MCP_automation
python -m pip install --upgrade python-docx openpyxl

# Verify
python -c "import docx; import openpyxl; print('Success')"
# Expected: Success""")

    doc.add_paragraph()
    add_heading_with_style(doc, '13.6 Git Bash Not Found', level=2)

    doc.add_paragraph('Problem: Git Bash terminal not available in VS Code')

    doc.add_paragraph()
    doc.add_paragraph('Solutions:')

    bash_solutions = [
        "Install Git for Windows from https://git-scm.com/download/win",
        "Restart VS Code after Git installation",
        "In VS Code, press Ctrl+Shift+P → 'Terminal: Select Default Profile' → Git Bash",
        "Verify Git Bash path: C:\\Program Files\\Git\\bin\\bash.exe"
    ]

    for sol in bash_solutions:
        doc.add_paragraph(sol, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '13.7 Vertex AI Timeout or Auth Issues', level=2)

    doc.add_paragraph('Problem: Vertex AI API timeouts or 403 Forbidden errors')

    doc.add_paragraph()
    doc.add_paragraph('Solutions:')

    vertex_solutions = [
        "Verify gcloud account has Vertex AI API access",
        "Check GCP project has Vertex AI API enabled",
        "Re-authenticate: gcloud auth application-default login",
        "Verify network connectivity to Google Cloud APIs",
        "Check if VPN is required and connected",
        "Contact GCP admin to verify API permissions"
    ]

    for sol in vertex_solutions:
        doc.add_paragraph(sol, style='List Bullet')

    doc.add_page_break()

    # =========================================================================
    # 14. SECURITY BEST PRACTICES
    # =========================================================================
    add_heading_with_style(doc, '14. Security Best Practices', level=1)

    add_heading_with_style(doc, '14.1 Credential Management', level=2)

    add_warning_box(doc,
        "NEVER commit credentials, PAT tokens, API keys, or service account JSON files "
        "to Git repositories or share them in documentation."
    )

    doc.add_paragraph()
    doc.add_paragraph('✅ DO:')

    do_items = [
        "Store PAT in Windows User environment variables",
        "Use minimum required scopes when creating PAT",
        "Set reasonable expiration dates (30-90 days)",
        "Rotate PAT tokens regularly",
        "Keep service account keys in .nrg/keys/ (gitignored)",
        "Use .gitignore to prevent credential files from being committed"
    ]

    for item in do_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    doc.add_paragraph('❌ DO NOT:')

    dont_items = [
        "Commit PAT tokens to git repositories",
        "Share PAT tokens with others",
        "Store PAT in .env files",
        "Hardcode credentials in code or config files",
        "Use PAT tokens with 'Full access' scope",
        "Email or Slack credentials",
        "Store credentials in shared drives unencrypted"
    ]

    for item in dont_items:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '14.2 Files That Should Never Be Shared', level=2)

    never_share = [
        ".env — Environment variable files",
        ".nrg/keys/*.json — Google Cloud service account keys",
        "Any file containing PAT tokens",
        "Any file containing API keys or passwords",
        "Database connection strings with credentials",
        "SSH private keys"
    ]

    for item in never_share:
        doc.add_paragraph(item, style='List Bullet')

    doc.add_paragraph()
    add_heading_with_style(doc, '14.3 Verifying No Secrets in ZIP', level=2)

    doc.add_paragraph('Before sharing the project ZIP, verify:')

    add_code_block(doc, """# Search for potential secrets
grep -r "password\\|secret\\|api_key\\|token" . --exclude-dir=node_modules --exclude-dir=.git

# Check for .env files
find . -name ".env*" -type f

# Verify .gitignore is working
git status --ignored

# Expected: No .env files, no keys/*.json files listed""")

    doc.add_paragraph()
    add_heading_with_style(doc, '14.4 PAT Token Renewal', level=2)

    doc.add_paragraph('When your PAT expires:')

    renewal_steps = [
        "Go to Azure DevOps → Personal Access Tokens",
        "Click on the expired token",
        "Click 'Regenerate'",
        "Copy the new token",
        "Update environment variable: [System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'new-token', 'User')",
        "Restart terminals and VS Code"
    ]

    for idx, step in enumerate(renewal_steps, 1):
        doc.add_paragraph(f"{idx}. {step}")

    doc.add_page_break()

    # =========================================================================
    # APPENDIX
    # =========================================================================
    add_heading_with_style(doc, 'Appendix A: Quick Reference Commands', level=1)

    add_heading_with_style(doc, 'Environment Variable Management', level=2)

    add_code_block(doc, """# Set PAT (PowerShell)
[System.Environment]::SetEnvironmentVariable('AZURE_DEVOPS_PAT', 'your-token', 'User')

# Check PAT (PowerShell)
$env:AZURE_DEVOPS_PAT

# Check PAT (Git Bash)
echo $AZURE_DEVOPS_PAT""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'MCP Verification', level=2)

    add_code_block(doc, """# Test Azure DevOps MCP
npx -y @azure-devops/mcp digital-it-apps --help

# Check MCP config
cat .mcp.json""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Agent Invocation', level=2)

    add_code_block(doc, """# Complete workflow
@qa-workflow <PBI_NUMBER>

# Individual agents (advanced use only)
@ado-pbi-fetcher <PBI_NUMBER>
@ui-test-executor <PBI_NUMBER>
@db-research-planner <PBI_NUMBER>""")

    doc.add_paragraph()
    add_heading_with_style(doc, 'Common File Paths', level=2)

    paths = [
        ['Purpose', 'Path'],
        ['Project Root', 'C:\\UE_Automation\\QE_MCP_automation'],
        ['Agent Definitions', '.claude\\agents\\'],
        ['Skills', '.claude\\skills\\'],
        ['MCP Config', '.mcp.json'],
        ['Integration Docs', 'docs\\integrations\\'],
        ['Output Files', 'outputs\\<PBI>\\'],
        ['Python Scripts', '*.py (project root)']
    ]

    add_table_from_data(doc, paths[0], paths[1:])

    doc.add_page_break()

    # =========================================================================
    # FINAL PAGE
    # =========================================================================
    add_heading_with_style(doc, 'Support and Contact', level=1)

    doc.add_paragraph(
        'For questions or issues with this setup guide, contact your team lead or '
        'QA automation team.'
    )

    doc.add_paragraph()

    support_info = [
        ['Item', 'Resource'],
        ['Project Documentation', 'README.md in project root'],
        ['Environment Setup', 'ENVIRONMENT_SETUP.md'],
        ['MCP Setup', 'README_MCP_SETUP.md'],
        ['Azure DevOps', 'https://dev.azure.com/digital-it-apps'],
        ['Claude Code Docs', 'https://claude.ai/code']
    ]

    add_table_from_data(doc, support_info[0], support_info[1:])

    doc.add_paragraph()
    doc.add_paragraph()

    footer = doc.add_paragraph(
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
    )
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    end_note = doc.add_paragraph('End of Setup Guide')
    end_note.alignment = WD_ALIGN_PARAGRAPH.CENTER
    end_note.runs[0].font.bold = True

    # Save the document
    output_path = 'DB_UI_API_AGENT_SETUP_GUIDE.docx'
    doc.save(output_path)

    return output_path

if __name__ == '__main__':
    import sys
    # Set UTF-8 encoding for console output
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

    output_file = create_setup_guide()
    print(f"Success: Setup guide created: {output_file}")
    print(f"Total pages: ~40+")
    print(f"Sections: 14 + Appendix")
