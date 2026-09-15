# BA Agent Documentation

⚠️ **NOTE: BA agents have been moved to `.claude/agents/`**

This README provides documentation for the Business Analyst (BA) agents used for work item analysis, requirements writing, acceptance criteria, effort estimation, and test case generation.

All BA agent files are now located in **`.claude/agents/`** directory.

## 1. Purpose of this folder

Use this folder when you want to move from a work item to a clear BA deliverable. The agents here help with:

- impact analysis
- requirement writing
- acceptance criteria drafting
- effort estimation
- test case generation
- test case verification

---

## 2. Agent Files

All BA agents are now in **`.claude/agents/`**:

- **ba-workflow.md** - Main workflow orchestrator that runs the full BA process
- **impact_analysis.md** - Impact analysis agent
- **requirement_writing.md** - Requirements documentation agent
- **acceptance_criteria_writer.md** - Acceptance criteria agent
- **pbi_eta_estimator.md** - Effort estimation agent
- **test_case_generator.md** - Test case generation agent
- **test_case_verification_based_on_requirements.md** - Requirements-based test verification
- **test_case_verification_against_code_implementation_based_on_implementation.md** - Code-based test verification

Each file represents one part of the BA workflow. The full BA orchestrator flow uses these agents together, not just one of them.

---

## 3. Prerequisites

Before starting the BA orchestrator workflow, make sure these are ready:

- the Azure DevOps MCP connection is installed, enabled, and working
- the PostgreSQL MCP connection is installed, enabled, and working if database access is needed
- access to the relevant Azure DevOps work item
- the work item ID ready
- the repository opened in Claude Code
- the required PAT token available if Azure DevOps authentication is required
- the required environment variables configured if your setup uses them

---

## 4. Full BA orchestrator flow

The ba-workflow is a step-by-step BA workflow. It is not just one agent. It runs a sequence of BA specialist agents and pauses for human approval at important checkpoints.

### Phase 1: Fetch the work item
- Use the Azure DevOps MCP tool only to fetch the work item.
- Use the correct project context, which is the team Azure DevOps project used for these work items.
- Save the raw work item details into the analysis folder.
- Ask the BA for approval before continuing.

### Phase 2: Impact analysis
- Run impact_analysis.md to review:
  - affected components
  - risks
  - dependencies
  - gaps between the request and the current implementation
- Save the output as 01-impact-analysis.md.
- Ask the BA to review and approve before moving on.

### Phase 3: Requirements writing
- Run requirement_writing.md to turn the request into clear, structured requirements.
- Save the output as 02-requirements.md.
- Ask the BA to review and approve the requirements.

### Phase 4: Acceptance criteria writing
- Run acceptance_criteria_writer.md to define testable acceptance criteria.
- Save the output as 03-acceptance-criteria.md.
- Ask the BA whether to continue to estimation or skip it.

### Phase 5: ETA estimation (optional)
- Run pbi_eta_estimator.md only if the BA explicitly asks for effort estimation.
- Save the output as 04-eta-estimation.md.
- This step is optional and should not run automatically unless requested.

### Phase 6: Update Azure DevOps
- Create a summary file named 00-SUMMARY.md.
- Update the Azure DevOps work item description and add a comment through the Azure DevOps MCP tools.
- Optionally update any available BA-related custom fields.
- Ask the BA for final confirmation before finishing.

### Phase 7: Completion
- Finalize the workflow.
- Share the location of the generated analysis files.
- The BA can review, edit, or re-run any phase later.

### Which agents are involved in the full flow
The full BA orchestrator flow usually includes all of these agents:

- impact_analysis.md for impact and risk review
- requirement_writing.md for business requirements
- acceptance_criteria_writer.md for clear acceptance criteria
- pbi_eta_estimator.md for effort estimation
- test_case_generator.md for test case creation
- test_case_verification_based_on_requirements.md for checking against written requirements
- test_case_verification_against_code_implementation_based_on_implementation.md for checking against actual implementation

### Important rules from the orchestrator
- Only fetch work items through the Azure DevOps MCP tool.
- Do not use Bash, ADO CLI, REST API calls, or other manual methods to fetch work items.
- Wait for BA approval at each checkpoint.
- Save all outputs inside ba-analysis/<work-item-id>/.
- ETA estimation is optional.
- If the work item is missing or the MCP connection fails, stop and report the issue.
- If the setup uses an environment variable for the PAT token, make sure it is available before starting.

---

## 5. MCP setup required

The BA workflow depends on MCP connections. Both MCPs should be working before you start the analysis.

### 4.1 Azure DevOps MCP
Use the Azure DevOps MCP connection to:

- fetch work items
- update work items
- add comments

#### Setup steps for Azure DevOps MCP
1. Open Claude Code.
2. Make sure the Azure DevOps MCP integration is installed and enabled.
3. Sign in with the account that has access to the Azure DevOps project.
4. Confirm that you can open the project and see work items.
5. Connect the Azure DevOps MCP server or extension.
6. Select the correct organization and project.
7. Test the connection by trying to fetch a sample work item.

#### PAT token setup for Azure DevOps
If Azure DevOps asks for authentication, create a Personal Access Token (PAT).

Use these steps:
1. Open Azure DevOps.
2. Go to your profile settings.
3. Open Personal access tokens.
4. Click New Token.
5. Give it a clear name, such as "Claude BA MCP".
6. Choose the required scopes.
   - Recommended: Work Items (Read & write)
   - Recommended: Project and Team (Read)
   - If your environment is restricted, use the minimum scopes needed.
7. Create the token and copy it immediately.

Where to store it:
- If your setup uses an authentication prompt, paste the PAT token into that prompt.
- If your setup uses environment variables, store the PAT token in the required environment variable.
- Do not paste the PAT token into the repository or into chat messages.

### 4.2 PostgreSQL MCP
Use the PostgreSQL MCP connection if the analysis needs database access.

#### Setup steps for PostgreSQL MCP
1. Make sure the PostgreSQL MCP integration is installed and enabled.
2. Confirm that you have the correct database host, port, database name, username, and password.
3. Store database credentials securely in the required environment variables if your setup uses them.
4. Connect the PostgreSQL MCP server or extension.
5. Test the connection with a simple database check.

If the PostgreSQL MCP connection is missing, any database-related analysis may not work properly.

---

## 6. How to use the files in this folder

Each file is meant for a specific BA task:

- impact_analysis.md: identify affected systems, risks, gaps, and dependencies
- requirement_writing.md: turn a request into clear, structured requirements
- acceptance_criteria_writer.md: define acceptance criteria in a testable format
- pbi_eta_estimator.md: estimate level of effort
- test_case_generator.md: create test cases from the requirements
- test_case_verification_based_on_requirements.md: verify the implementation against the written requirements
- test_case_verification_against_code_implementation_based_on_implementation.md: verify the implementation against the coded behavior

---

## 7. Example starting prompt

Use a prompt like this:

```text
Analyze work item 279788.
First review the impact, then write requirements and acceptance criteria, and finally estimate effort.
```

---

## 8. Quick checklist

1. Make sure the Azure DevOps MCP connection is active.
2. Make sure the PostgreSQL MCP connection is active if database access is needed.
3. Confirm the PAT token is available and stored securely.
4. Open the relevant BA file for the task you need.
5. Follow the workflow from impact analysis to test case verification.

---

## 9. Final note

This folder is meant to make the BA workflow simple, structured, and repeatable. Use the files in order for the clearest results.
