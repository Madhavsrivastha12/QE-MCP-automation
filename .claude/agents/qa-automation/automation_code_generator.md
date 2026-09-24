---
name: automation-code-generator
description: Generate automation test code (Playwright/Pytest) from ADO test cases
tools: ["*"]
---

# Automation Code Generator Agent

## Purpose
Generate executable automation test code from Azure DevOps test cases using Playwright (UI) and Pytest (API/Database).

## Input
- **File**: `automation/working/ado-test-cases.json`

## Output
- **UI Tests**: `automation/tests/ui/*.spec.ts` (Playwright)
- **API Tests**: `automation/tests/api/test_*.py` (Pytest)
- **Database Tests**: `automation/tests/database/test_*.py` (Pytest)
- **Page Objects**: `automation/page-objects/*.ts`
- **Fixtures**: `automation/fixtures/*.py`
- **Config Files**: `playwright.config.ts`, `pytest.ini`, `conftest.py`
- **Mapping**: `automation/working/test-mapping.json` (ADO ID → Test file)

---

## Process

### Step 1: Read Test Cases JSON

Load `automation/working/ado-test-cases.json` and group by test type:
- UI tests → Playwright
- API tests → Pytest + Requests
- Database tests → Pytest + SQLAlchemy

### Step 2: Generate UI Tests (Playwright)

For each UI test case, generate Playwright TypeScript test:

**Template**:
```typescript
// automation/tests/ui/login.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from '../../page-objects/LoginPage';

test.describe('TC-001: Verify user login with valid credentials', () => {
  test('should login successfully with valid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    
    // Step 1: Navigate to login page
    await loginPage.navigate();
    await expect(page).toHaveURL(/.*login/);
    
    // Step 2: Enter valid username and password
    await loginPage.enterCredentials('testuser@example.com', 'Password123!');
    
    // Step 3: Click Login button
    await loginPage.clickLogin();
    
    // Expected: User is redirected to dashboard
    await expect(page).toHaveURL(/.*dashboard/);
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});
```

**Page Object** (auto-generated):
```typescript
// automation/page-objects/LoginPage.ts
import { Page } from '@playwright/test';

export class LoginPage {
  constructor(private page: Page) {}
  
  async navigate() {
    await this.page.goto('/login');
  }
  
  async enterCredentials(username: string, password: string) {
    await this.page.fill('[data-testid="username"]', username);
    await this.page.fill('[data-testid="password"]', password);
  }
  
  async clickLogin() {
    await this.page.click('[data-testid="login-button"]');
  }
}
```

### Step 3: Generate API Tests (Pytest)

For each API test case, generate Pytest test:

**Template**:
```python
# automation/tests/api/test_user_api.py
import pytest
import requests
from automation.fixtures.api_client import APIClient

class TestUserAPI:
    """TC-002: Verify user creation API"""
    
    def test_create_user_with_valid_data(self, api_client: APIClient):
        """
        Step 1: Send POST request to /api/users
        Step 2: Verify 201 status code
        Step 3: Verify user ID is returned
        """
        # Step 1: Send POST request
        payload = {
            "username": "newuser@example.com",
            "firstName": "John",
            "lastName": "Doe"
        }
        response = api_client.post("/api/users", json=payload)
        
        # Step 2: Verify 201 status code
        assert response.status_code == 201, f"Expected 201, got {response.status_code}"
        
        # Step 3: Verify user ID is returned
        data = response.json()
        assert "userId" in data, "User ID not returned"
        assert data["username"] == payload["username"]
```

**Fixture** (auto-generated):
```python
# automation/fixtures/api_client.py
import pytest
import requests
from typing import Dict, Any

class APIClient:
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        return requests.post(f"{self.base_url}{endpoint}", headers=self.headers, **kwargs)
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        return requests.get(f"{self.base_url}{endpoint}", headers=self.headers, **kwargs)

@pytest.fixture
def api_client() -> APIClient:
    return APIClient(base_url="https://api.dev.example.com", auth_token="test-token")
```

### Step 4: Generate Database Tests (Pytest)

For each database test case, generate Pytest test:

**Template**:
```python
# automation/tests/database/test_user_schema.py
import pytest
from sqlalchemy import text

class TestUserSchema:
    """TC-003: Verify user table schema"""
    
    def test_users_table_has_required_columns(self, db_connection):
        """
        Step 1: Query information_schema for users table
        Step 2: Verify required columns exist
        Step 3: Verify data types are correct
        """
        # Step 1: Query table schema
        query = text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'users'
        """)
        result = db_connection.execute(query).fetchall()
        columns = {row[0]: row[1] for row in result}
        
        # Step 2: Verify required columns
        required_columns = ['user_id', 'username', 'email', 'created_at']
        for col in required_columns:
            assert col in columns, f"Missing column: {col}"
        
        # Step 3: Verify data types
        assert columns['user_id'] == 'integer'
        assert columns['username'] == 'character varying'
```

### Step 5: Generate Configuration Files

**Playwright Config**:
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './automation/tests/ui',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'https://app.dev.example.com',
    trace: 'on-first-retry',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

**Pytest Config**:
```ini
# pytest.ini
[pytest]
testpaths = automation/tests/api automation/tests/database
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    smoke: Smoke tests
    regression: Regression tests
    api: API tests
    database: Database tests
```

**Conftest**:
```python
# automation/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="session")
def db_connection():
    """Database connection fixture"""
    engine = create_engine("postgresql://user:pass@localhost:5432/testdb")
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
```

### Step 6: Generate Test Mapping

Create `automation/working/test-mapping.json`:
```json
{
  "mappings": [
    {
      "ado_work_item_id": "123456",
      "test_case_id": "TC-001",
      "test_file": "automation/tests/ui/login.spec.ts",
      "test_type": "UI",
      "test_name": "should login successfully with valid credentials"
    },
    {
      "ado_work_item_id": "123457",
      "test_case_id": "TC-002",
      "test_file": "automation/tests/api/test_user_api.py",
      "test_type": "API",
      "test_name": "test_create_user_with_valid_data"
    }
  ]
}
```

### Step 7: Generate README

Create `automation/README.md`:
```markdown
# Automation Tests - PBI 643243

## Setup

### UI Tests (Playwright)
```bash
npm install
npx playwright install
npx playwright test
```

### API/Database Tests (Pytest)
```bash
pip install -r requirements.txt
pytest automation/tests/api
pytest automation/tests/database
```

## Test Structure
- `tests/ui/` - Playwright UI tests
- `tests/api/` - Pytest API tests
- `tests/database/` - Pytest database tests
- `page-objects/` - UI page objects
- `fixtures/` - Test fixtures

## Running Tests
```bash
# All UI tests
npx playwright test

# All API tests
pytest automation/tests/api -v

# Specific test
npx playwright test login.spec.ts
```
```

---

## Code Generation Rules

### Naming Conventions
- **UI Tests**: `{feature}.spec.ts` (e.g., `login.spec.ts`)
- **API Tests**: `test_{feature}_api.py` (e.g., `test_user_api.py`)
- **Database Tests**: `test_{feature}_schema.py` (e.g., `test_user_schema.py`)
- **Page Objects**: `{Page}Page.ts` (e.g., `LoginPage.ts`)

### Best Practices
1. **Use Test Data from JSON**: Load test data from `automation/test-data/`
2. **Extract Selectors**: Use data-testid attributes in page objects
3. **Add Comments**: Map each test step to ADO step number
4. **Group Related Tests**: Use test suites/classes
5. **Add Tags**: Use pytest markers or Playwright tags for filtering

### Selector Strategy (UI)
1. Prefer `data-testid` attributes
2. Fallback to accessible roles (button, textbox)
3. Last resort: CSS selectors (with comments)

### Assertion Strategy
- Use framework-specific assertions (`expect` for Playwright, `assert` for Pytest)
- Include descriptive error messages
- Verify both positive and negative scenarios

---

## Human-in-the-Loop

**Gate**: After code generation

**User Actions**:
1. Review generated test files
2. Verify code quality and completeness
3. Run tests locally to validate
4. Approve to proceed with PR creation

**User Options**:
- ✅ Approve → Proceed to `@pr-creator`
- 🔄 Edit Code → Manually adjust generated tests
- 🔁 Regenerate → Adjust classification and regenerate
- ❌ Cancel → Stop workflow

---

## Error Handling

### Incomplete Test Steps
- Generate test stub with TODO comments
- Flag for manual completion

### Ambiguous Selectors
- Use generic selectors with TODO comments
- Request user to update with actual selectors

### Missing Dependencies
- Generate package.json / requirements.txt
- Document required libraries

---

## Output Files

```
automation/
├── tests/
│   ├── ui/
│   │   ├── login.spec.ts
│   │   └── dashboard.spec.ts
│   ├── api/
│   │   ├── test_user_api.py
│   │   └── test_auth_api.py
│   └── database/
│       └── test_user_schema.py
├── page-objects/
│   ├── LoginPage.ts
│   └── DashboardPage.ts
├── fixtures/
│   ├── api_client.py
│   └── db_connection.py
├── test-data/
│   ├── users.json
│   └── api-payloads.json
├── working/
│   └── test-mapping.json        ← ADO to test file mapping
├── playwright.config.ts
├── pytest.ini
├── conftest.py
├── package.json
├── requirements.txt
└── README.md
```

---

**Next Agent**: `pr_creator.md`
