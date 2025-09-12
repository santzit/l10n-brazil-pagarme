# GitHub Copilot Instructions for l10n-brazil-pagarme

**ALWAYS reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

This is an **Odoo 16.0 OCA (Odoo Community Association) module repository** for **Brazilian localization payment providers**. The primary module `l10n_br_payment_pagarme` implements PagarMe payment provider integration with Brazilian market-specific features.

## 🚨 MANDATORY COPILOT FIREWALL RULES 🚨

**THESE RULES MUST BE FOLLOWED WITHOUT EXCEPTION - NO CODE CHANGES ARE ALLOWED WITHOUT COMPLIANCE**

### Rule 1: MANDATORY Validation Before ANY Commit

**CRITICAL: pre-commit AND GitHub Actions CI MUST pass before ANY commit**

Following the OCA l10n-brazil test.yml reference workflow, these validation steps are MANDATORY:

```bash
# STEP 1: MANDATORY pre-commit validation (MUST PASS)
# TIMING: 40 seconds for full validation - NEVER CANCEL
pre-commit run --all-files

# STEP 2: MANDATORY Local OCA Testing (MUST PASS)
# Uses Docker Compose approach to mirror GitHub Actions container + services setup
# TIMING: 10-15 minutes for full OCA validation - NEVER CANCEL

# GitHub Actions runs these separated steps automatically:
# - Step 1: oca_install_addons
# - Step 2: manifestoo -d . check-licenses  
# - Step 3: manifestoo -d . check-dev-status --default-dev-status=Beta
# - Step 4: oca_init_test_database
# - Step 5: oca_run_tests

# All steps use INCLUDE/EXCLUDE environment variables:
export INCLUDE="l10n_br_payment_pagarme"
export EXCLUDE=""
```

**COMMIT ENFORCEMENT RULES:**
- **NO COMMITS** are allowed unless BOTH pre-commit AND local OCA Docker testing pass completely
- **NO ALTERNATIVE SOLUTIONS** are permitted - both validations are mandatory  
- **NO EXCEPTIONS** - if any validation fails, the commit MUST NOT proceed
- **ERROR REPORTING** - if validation fails, report the specific error and stop the process
- **PostgreSQL CONNECTIVITY** - MUST test database connection using Docker after oca_install_addons
- **SEPARATED STEPS** - Follow GitHub Actions pattern: install → connection test → init database → run tests

**ENFORCEMENT SEQUENCE:**
1. Execute `pre-commit run --all-files` - MUST PASS
2. Execute Docker-based OCA testing sequence (oca_install_addons → PostgreSQL connection test → oca_init_test_database → oca_run_tests) - MUST PASS
3. Only proceed with commit if BOTH validations pass
4. If any step fails: STOP, report error in comment, do NOT commit
5. Optional: Push changes to verify GitHub Actions CI also passes

**LOCAL OCA TESTING WITH DOCKER COMPOSE**
- GitHub Actions uses `container:` + `services:` approach - replicate locally with Docker Compose
- **MANDATORY**: Use Docker Compose for local OCA testing that mirrors GitHub Actions setup
- **SEPARATED STEPS**: Follow exact GitHub Actions pattern with individual Docker commands
- **CONNECTION TESTING**: Always test PostgreSQL connectivity using Docker after `oca_install_addons`

**Docker Compose Setup for Local Testing:**
```yaml
# docker-compose-oca-test.yml (create temporarily for testing)
version: '3.8'
services:
  postgres:
    image: postgres:14.0
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - oca-network

  oca-ci:
    image: ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/addons/custom
    working_dir: /opt/odoo/addons/custom
    environment:
      - INCLUDE=l10n_br_payment_pagarme
      - EXCLUDE=
      - PGHOST=postgres
      - PGUSER=odoo
      - PGPASSWORD=odoo
      - PGDATABASE=odoo
    networks:
      - oca-network

networks:
  oca-network:
    driver: bridge
```

**MANDATORY Local OCA Testing Sequence (Rule 1):**
```bash
# Step 1: Create Docker Compose file and start PostgreSQL
cat > docker-compose-oca-test.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:14.0
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - oca-network

  oca-ci:
    image: ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/addons/custom
    working_dir: /opt/odoo/addons/custom
    environment:
      - INCLUDE=l10n_br_payment_pagarme
      - EXCLUDE=
      - PGHOST=postgres
      - PGUSER=odoo
      - PGPASSWORD=odoo
      - PGDATABASE=odoo
    networks:
      - oca-network

networks:
  oca-network:
    driver: bridge
EOF

# Step 2: Start PostgreSQL service
docker compose -f docker-compose-oca-test.yml up -d postgres

# Step 3: Install addons using Docker Compose run
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_install_addons"

# Step 4: Test PostgreSQL connectivity using Docker (MANDATORY after oca_install_addons)
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "echo 'Testing PostgreSQL connectivity...' && timeout 30 bash -c 'until pg_isready -h postgres -p 5432 -U odoo; do echo \"Waiting for PostgreSQL...\"; sleep 2; done' && echo 'PostgreSQL connection verified ✅'"

# Step 5: Initialize test database using Docker Compose
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_init_test_database"

# Step 6: Run tests using Docker Compose  
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_run_tests"

# Step 7: Cleanup
docker compose -f docker-compose-oca-test.yml down
rm docker-compose-oca-test.yml
```

### Rule 2: Zero Tolerance for Formatting Violations

- **Python**: ONLY double quotes allowed - `"string"` ✅, `'string'` ❌
- **Line Length**: MAXIMUM 88 characters per line (E501 enforced by ruff)
- **Imports**: ONLY explicit re-exports in `__init__.py` -
  `from . import models as models` ✅
- **Files**: MUST end with single newline, NO trailing whitespace
- **XML/JS**: MUST pass prettier formatting validation
- **Docstrings**: Break long docstrings across multiple lines to stay under 88 chars

### Rule 3: File Modification Restrictions

**CRITICAL: Root and GitHub directory protection rules - NO EXCEPTIONS**

- **FORBIDDEN**: Do NOT modify any files in root directory (e.g.,
  `.pre-commit-config.yaml`, `.eslintrc.json`, `requirements.txt`, `setup.py`, etc.)
  unless EXPLICITLY requested by user
- **FORBIDDEN**: Do NOT modify any files in `.github/` directory (except
  `.github/copilot-instructions.md`) unless EXPLICITLY requested by user
- **REQUIRED**: Only modify module files within `l10n_br_payment_pagarme/` directory
  unless user specifically asks for root/github changes
- **EXCEPTION**: The `.github/copilot-instructions.md` file can be modified when
  updating documentation

---

## Working Effectively

### Quick Setup Commands - Execute These on Fresh Clone

```bash
# STEP 1: Install development tools (4 seconds)
pip install pre-commit
pre-commit install

# STEP 2: MANDATORY quality validation (40 seconds - NEVER CANCEL)
# Set timeout to 60+ seconds in any automation
pre-commit run --all-files
```

### OCA Environment Variables for Module Selection

Following OCA l10n-brazil test.yml reference, use INCLUDE/EXCLUDE environment variables:

```bash
# OCA Standard Practice - Module Selection Environment Variables
export INCLUDE="l10n_br_payment_pagarme"  # Target specific module for testing/installation
export EXCLUDE=""                         # Exclude specific modules (empty for single-module repo)

# Usage Pattern (following OCA l10n-brazil/test.yml):
export INCLUDE="l10n_br_payment_pagarme"
export EXCLUDE=""
oca_install_addons
oca_init_test_database
oca_run_tests
```

## Repository Overview

**Key Context:**
- **Module Type**: Single Odoo 16.0 OCA payment provider module  
- **Main Module**: `l10n_br_payment_pagarme` - PagarMe payment integration for Brazil
- **Dependencies**: Odoo 16.0 `payment` module (core payment framework)
- **Testing**: Uses Odoo's TransactionCase and HttpCase frameworks  
- **Location**: All development happens in `l10n_br_payment_pagarme/` directory

## Validation and Testing Scenarios

## Build and Test Timing Expectations

### Timing Reference (NEVER CANCEL - Wait for Completion)

| Operation | Expected Time | Timeout Setting | Notes |
|-----------|---------------|-----------------|-------|
| `pip install pre-commit` | 4 seconds | 60 seconds | Network dependent |
| `pre-commit install` | < 1 second | 30 seconds | Local operation |
| `pre-commit run --all-files` (first time) | 40 seconds | 90 seconds | Downloads environments |
| `pre-commit run --all-files` (subsequent) | 10 seconds | 60 seconds | Uses cached environments |
| PostgreSQL connectivity check | 2-5 seconds | 30 seconds | Network + service dependent |
| `python -m ruff format .` | < 1 second | 30 seconds | Fast formatter |
| `python -m ruff check --fix .` | < 1 second | 30 seconds | Fast linter |
| `npx prettier --write ...` | < 1 second | 30 seconds | Fast formatter |
| Python syntax validation | < 1 second | 30 seconds | Compilation check |
| XML syntax validation | < 1 second | 30 seconds | Parser check |
| OCA Docker addon install | 5+ minutes | 15 minutes | Network + Docker dependent |
| `pip install manifestoo` | 3 seconds | 60 seconds | Network dependent |

### CI Pipeline Expectations

**From `.github/workflows/test.yml`:**
- Uses `ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest` Docker container
- Requires PostgreSQL 14.0 service  
- Runs `oca_install_addons`, `oca_init_test_database`, `oca_run_tests`
- **Total CI time: 10-20 minutes** (NEVER CANCEL CI workflows)

## Repository Navigation and Module Structure

### Current Repository Structure (Validated)
```
l10n-brazil-pagarme/
├── .github/                      # GitHub workflows and copilot instructions  
│   ├── workflows/
│   │   ├── test.yml             # OCA CI testing workflow
│   │   └── pre-commit.yml       # Pre-commit validation workflow
│   └── copilot-instructions.md  # This file
├── l10n_br_payment_pagarme/     # MAIN MODULE DIRECTORY (focus here)
│   ├── __manifest__.py          # Module metadata and dependencies
│   ├── __init__.py              # Module initialization
│   ├── controllers/             # HTTP controllers for payment flows
│   │   ├── __init__.py
│   │   └── main.py              # PaymentPagarmeController
│   ├── models/                  # Business logic models
│   │   ├── __init__.py
│   │   ├── payment_provider.py  # Provider configuration  
│   │   ├── payment_token.py     # Token management
│   │   └── payment_transaction.py # Transaction processing
│   ├── tests/                   # Test cases (IMPORTANT for validation)
│   │   ├── __init__.py
│   │   ├── common.py            # PaymentPagarmeCommon test base
│   │   ├── test_payment_transaction.py # Transaction tests
│   │   └── test_processing_flows.py    # Flow integration tests
│   ├── views/                   # XML view definitions
│   │   ├── payment_pagarme_templates.xml
│   │   ├── payment_templates.xml
│   │   ├── payment_token_views.xml
│   │   └── payment_transaction_views.xml
│   ├── data/                    # Data records
│   │   └── payment_provider_data.xml
│   └── static/src/js/           # Frontend JavaScript
│       └── payment_form.js      # Payment form handling
├── .pre-commit-config.yaml      # Pre-commit hook configuration
├── .ruff.toml                   # Python code formatting rules
├── .eslintrc.json               # JavaScript linting rules
├── setup.py                     # Python package setup
├── test-requirements.txt        # Test dependencies
└── README.md                    # Project documentation
```

### Key Files to Know

#### Module Manifest (`l10n_br_payment_pagarme/__manifest__.py`)
- **Purpose**: Defines module metadata, dependencies, and load order
- **Dependencies**: `["payment"]` (Odoo core payment framework)
- **Version**: `16.0.6.2.0` (Odoo 16.0 compatible)
- **Data Files**: XML views, templates, and provider configuration

#### Test Files (`l10n_br_payment_pagarme/tests/`)
- **common.py**: `PaymentPagarmeCommon` - Test base class with provider setup
- **test_payment_transaction.py**: Transaction state and processing tests  
- **test_processing_flows.py**: End-to-end payment flow tests
- **Tags**: `@tagged("-at_install", "post_install")` - Standard OCA test pattern

#### Models (`l10n_br_payment_pagarme/models/`)
- **payment_provider.py**: Extends `payment.provider` with PagarMe configuration
- **payment_transaction.py**: Extends `payment.transaction` with PagarMe processing
- **payment_token.py**: Extends `payment.token` with PagarMe tokenization

### Navigation Commands

```bash
# See all Python files and their purpose
find l10n_br_payment_pagarme -name "*.py" -exec echo "=== {} ===" \; -exec head -5 {} \;

# See all XML view files
find l10n_br_payment_pagarme -name "*.xml" | sort

# Check module dependencies 
grep -A 5 -B 5 '"depends"' l10n_br_payment_pagarme/__manifest__.py

# See test structure
ls -la l10n_br_payment_pagarme/tests/

# Check static assets
find l10n_br_payment_pagarme/static -type f
```

## Common Development Tasks

### Adding New Payment Methods
1. **Modify payment_provider.py**: Add configuration fields
2. **Update payment_transaction.py**: Add processing logic
3. **Add/modify XML views**: Update provider configuration forms  
4. **Update tests**: Add test cases for new method
5. **ALWAYS validate**: Run full pre-commit validation

### Debugging Payment Flows
```bash
# Check payment controller routes
grep -r "@http.route" l10n_br_payment_pagarme/controllers/

# See transaction states and processing  
grep -r "simulated_state" l10n_br_payment_pagarme/

# Check notification data structure
grep -A 10 -B 5 "notification_data" l10n_br_payment_pagarme/tests/common.py
```

### Adding New Tests
1. **Extend PaymentPagarmeCommon**: Use common test base in `tests/common.py`
2. **Use standard tags**: `@tagged("-at_install", "post_install")`  
3. **Follow naming**: `test_descriptive_name_of_behavior`
4. **Test both flows**: Direct payment and tokenization scenarios

## Development Guidelines

### 1. ODOO OCA Standards Compliance

#### Manifest File Requirements

```python
{
    "name": "Descriptive Module Name",
    "version": "16.0.x.y.z",  # Follow OCA versioning
    "category": "Appropriate Category",
    "summary": "Brief module description",
    "depends": ["base", "required_modules"],  # Core dependencies
    "data": [
        "security/security.xml",  # If access control needed
        "views/view_files.xml",
        "data/data_files.xml",
    ],
    "license": "LGPL-3",  # OCA standard license
    "installable": True,
    "auto_install": False,
}
```

### 2. Python Development Standards

#### Code Style and Formatting Requirements

- Follow **PEP 8** and **OCA Python guidelines**
- **MANDATORY**: Use **double quotes** for all strings (enforced by ruff)
- **MANDATORY**: Use explicit re-exports in `__init__.py` files to avoid F401 errors
- **MANDATORY**: Ensure all files end with a newline
- Use the configured **pre-commit hooks** (setup in `.pre-commit-config.yaml`)
- **ALWAYS** run `pre-commit run --all-files` before committing

#### Critical Formatting Rules

```python
# ✅ CORRECT - Double quotes (REQUIRED)
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

# ✅ CORRECT - Explicit re-exports in __init__.py
from . import models as models
from . import controllers as controllers

# ❌ WRONG - Single quotes will fail pre-commit
from odoo.exceptions import UserError, ValidationError

# ❌ WRONG - Missing explicit re-export causes F401 errors
from . import models
from . import controllers
```

#### Model Development Patterns

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class ModelName(models.Model):
    _inherit = "existing.model"  # For extending existing models (double quotes!)
    # OR
    _name = "new.model.name"     # For new models (double quotes!)

    # Field definitions with proper types and attributes (double quotes!)
    field_name = fields.Char("Field Label", required=True)

    # Methods with proper decorators and documentation
    @api.depends("field_name")  # Double quotes!
    def _compute_something(self):
        """Compute method documentation."""
        for record in self:
            record.computed_field = self._calculate_value()

    @api.constrains("field_name")  # Double quotes!
    def _check_field_name(self):
        """Validation method documentation."""
        if self.filtered(lambda r: not r.field_name):
            raise ValidationError(_("Field is required"))  # Double quotes!
```

#### Brazilian Localization Patterns

- **Module naming**: Use `l10n_br_*` pattern for Brazilian localization
- **Document handling**: Consider CPF/CNPJ validation when dealing with customer data
- **Currency**: Default to BRL (Brazilian Real) when applicable
- **Regulatory compliance**: Follow Brazilian regulations and requirements
- **Payment systems**: Support Brazilian payment methods (PIX, installments, etc.)

### 3. Testing Framework

#### Test Structure

- Place all tests in `tests/` directory
- Use OCA testing base classes and patterns
- Follow the testing approach defined in `.github/workflows/test.yml`

#### Testing Patterns

```python
from odoo.tests import tagged, TransactionCase
from odoo.tests.common import HttpCase

@tagged("-at_install", "post_install")  # Standard OCA test tagging
class TestModuleFunctionality(TransactionCase):

    def setUp(self):
        super().setUp()
        # Test setup code

    def test_functionality(self):
        """Test method documentation."""
        # Test implementation
        self.assertEqual(expected, actual)
```

#### Running Tests

The repository uses OCA testing infrastructure as defined in
`.github/workflows/test.yml`:

```bash
# Tests are run automatically using OCA CI containers with GitHub Actions
# Following test.yml workflow pattern with containers and services:
# - container: ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest 
# - services: postgres:14.0 with proper environment variables
# - Separated steps: install addons → check licenses → init database → run tests

# GitHub Actions approach (from test.yml):
export INCLUDE="l10n_br_payment_pagarme"
export EXCLUDE=""

# Step 1: Install addons and dependencies
oca_install_addons

# Step 2: Check licenses  
manifestoo -d . check-licenses

# Step 3: Check development status
manifestoo -d . check-dev-status --default-dev-status=Beta

# Step 4: Initialize test database
oca_init_test_database

# Step 5: Run tests
oca_run_tests

# For local testing, replicate GitHub Actions environment:
# IMPORTANT: Use Docker Compose approach like test.yml, NOT direct docker run
```

### 4. Brazilian Market Specifics

#### Payment Provider Development

- Support Brazilian payment methods and regulations
- Implement proper document validation (CPF/CNPJ)
- Handle installment payments common in Brazilian market
- Support PIX instant payment system
- Follow Brazilian Central Bank regulations

#### Localization Requirements

- Brazilian tax system integration
- State and municipal tax handling
- SPED (Sistema Público de Escrituração Digital) compliance
- NFe (Nota Fiscal Eletrônica) support when applicable
- Brazilian fiscal document patterns

### 5. Advanced Integration

#### Controller Development

```python
from odoo import http
from odoo.http import request

class BrazilianController(http.Controller):

    @http.route("/brazilian/endpoint", type="json", auth="public", csrf=False)
    def endpoint_handler(self, **kwargs):
        """Handle Brazilian-specific requests."""
        # Implementation with proper error handling
        return {"status": "success"}
```

#### Playwright Testing Integration

For browser automation testing, integrate with Odoo's testing framework:

```python
from odoo.tests import HttpCase, tagged

@tagged("post_install", "-at_install")
class TestUIFunctionality(HttpCase):

    def test_user_interface(self):
        """Test UI functionality with Playwright patterns."""
        # Use Playwright for browser automation
        # Integrate with Odoo's HttpCase framework
        pass
```

Follow the testing patterns established in `.github/workflows/test.yml` for consistency
with CI/CD pipeline.

### 6. Pre-commit Configuration and Error Prevention

The repository includes comprehensive pre-commit hooks for code quality that **MUST** be
followed to prevent CI failures:

#### Available Hooks

- **OCA-specific**: Module validation, manifest checks, README generation
- **Code formatting**: Ruff for Python, Prettier for XML/JS
- **Code quality**: PyLint with Odoo extensions
- **General checks**: Encoding, merge conflicts, trailing whitespace

#### Critical Pre-commit Error Prevention Guidelines

##### Python Code Formatting (Ruff)

**ALWAYS use double quotes** - Ruff enforces double quote usage:

```python
# ✅ CORRECT - Use double quotes
setup_provider(cr, registry, "pagarme")
field_name = fields.Char("Field Label", required=True)

# ❌ WRONG - Single quotes will cause pre-commit failures
setup_provider(cr, registry, 'pagarme')
field_name = fields.Char('Field Label', required=True)
```

**Import Best Practices** - Avoid F401 "imported but unused" errors:

```python
# ✅ CORRECT - Explicit re-exports in __init__.py files
from . import controllers as controllers
from . import models as models

# ❌ WRONG - Will cause F401 errors
from . import controllers
from . import models
```

**Method and Class Formatting**:

```python
# ✅ CORRECT - Proper spacing and formatting
class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    def _compute_something(self):
        """Compute method documentation."""
        for record in self:
            record.field = self._calculate_value()

# ❌ WRONG - Inconsistent spacing
class PaymentProvider(models.Model):
    _inherit='payment.provider'
    def _compute_something(self):
        for record in self:
            record.field=self._calculate_value()
```

**Line Length Requirements (E501)** - MAXIMUM 88 characters per line:

```python
# ✅ CORRECT - Break long lines appropriately
def test_processing_notification_data_sets_transaction_pending(self):
    """Test that the transaction state is set to 'pending' when the
    notification data indicate a pending payment."""

# ✅ CORRECT - Break long comments
# The reasons why we immediately tokenize the transaction regardless of
# the state rather than waiting for the payment method to be validated
# ('authorized' or 'done') like the other payment providers do are:

# ❌ WRONG - Lines over 88 characters will cause E501 errors
def test_processing_notification_data_sets_transaction_pending(self):
    """Test that the transaction state is set to 'pending' when the notification data indicate a pending payment."""

# ❌ WRONG - Long comments over 88 characters
# The reasons why we immediately tokenize the transaction regardless of the state rather than waiting for the payment method to be validated ('authorized' or 'done') like the other payment providers do are:
```

##### XML Formatting (Prettier)

**Consistent indentation and formatting**:

```xml
<!-- ✅ CORRECT - Proper XML formatting -->
<?xml version="1.0" encoding="utf-8" ?>
<odoo>
    <template id="payment_form" name="Payment Form">
        <div class="payment-form">
            <input
                type="text"
                name="card_number"
                placeholder="Card Number"
                required="required"
            />
        </div>
    </template>
</odoo>

<!-- ❌ WRONG - Poor formatting will be auto-fixed by prettier -->
<odoo><template id="payment_form" name="Payment Form"><div class="payment-form"><input type="text" name="card_number" placeholder="Card Number" required="required"/></div></template></odoo>
```

##### JavaScript Formatting

**Quote consistency and proper formatting**:

```javascript
// ✅ CORRECT - Double quotes and proper formatting
const paymentForm = {
  selector: ".payment-form",
  init: function () {
    this.setupEventHandlers();
  },
};

// ❌ WRONG - Mixed quotes and poor formatting
const paymentForm = {
  selector: ".payment-form",
  init: function () {
    this.setupEventHandlers();
  },
};
```

##### File Requirements

**ALWAYS ensure files end with a newline**:

```python
# ✅ CORRECT - File ends with newline
def my_function():
    return "value"

# ❌ WRONG - Missing newline at end will cause pre-commit failure
```

**Remove trailing whitespace** - No spaces at the end of lines.

#### Mandatory Pre-commit Workflow

**BEFORE making any code changes:**

```bash
# Install and setup pre-commit (REQUIRED)
pip install pre-commit
pre-commit install

# Run pre-commit on all files to check current state
pre-commit run --all-files
```

**AFTER making any code changes:**

```bash
# ALWAYS run pre-commit before committing
pre-commit run --all-files

# Fix any errors reported and re-run until all checks pass
# Common commands to fix specific issues:

# Fix Python formatting automatically
python -m ruff format .
python -m ruff check --fix .

# Fix XML/JS formatting automatically
npx prettier --write "**/*.{xml,js,css,json}"

# Check for trailing whitespace and missing newlines
git diff --check
```

#### Common Pre-commit Errors and Solutions

| Error Type                   | Description                       | Solution                                     |
| ---------------------------- | --------------------------------- | -------------------------------------------- |
| **Ruff format**              | Single quotes used                | Change all single quotes to double quotes    |
| **E501 Line too long**       | Lines exceed 88 characters        | Break long lines, docstrings, and comments   |
| **F401 imported but unused** | Import not explicitly re-exported | Use `from . import module as module`         |
| **end-of-file-fixer**        | Missing newline at end            | Add newline at end of file                   |
| **trailing-whitespace**      | Spaces at end of lines            | Remove trailing spaces                       |
| **prettier**                 | XML/JS formatting issues          | Run `npx prettier --write` on affected files |
| **check-xml**                | Invalid XML syntax                | Fix XML syntax errors                        |
| **oca-checks-odoo-module**   | OCA module compliance             | Fix manifest, structure, or naming issues    |

#### Error Prevention Checklist

Before submitting any changes, ensure:

- [ ] All Python strings use double quotes
- [ ] All lines are under 88 characters (E501 compliance)
- [ ] All `__init__.py` files use explicit re-exports (`as module`)
- [ ] All files end with a single newline
- [ ] No trailing whitespace in any files
- [ ] XML files are properly formatted with consistent indentation
- [ ] JavaScript follows consistent quote and formatting rules
- [ ] Pre-commit runs successfully: `pre-commit run --all-files`
- [ ] No ruff, prettier, or OCA validation errors

#### Usage

```bash
# Essential pre-commit setup (REQUIRED for all contributions)
pip install pre-commit
pre-commit install

# Run before every commit (MANDATORY)
pre-commit run --all-files

# Auto-fix common formatting issues
python -m ruff format .
python -m ruff check --fix .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"
```

#### OCA README Standards

When updating README.md files, follow OCA standards:

- **Include badges**: Runboat, Pre-commit Status, Build Status, codecov, Translation
  Status
- **Bilingual content**: Portuguese and English for Brazilian localization
- **Proper sections**: Features, Installation, Configuration, Development, Contributing
- **OCA footer**: Include OCA mission statement
- **Runboat integration**: Provide "Try it now" section with working Runboat links
- **Module table**: Use auto-generated addons table format

Example OCA-compliant README structure:

```markdown
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=org/repo&target_branch=16.0)
[![Pre-commit Status](https://github.com/org/repo/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/org/repo/actions/workflows/pre-commit.yml?query=branch%3A16.0)

<!-- /!\ do not modify above this line -->

# Title in English and Portuguese

Description in both languages...

## Features / Características

Bilingual feature list...

## :arrow_forward: **Try it now! / Teste agora!**

Runboat instructions...

<!-- /!\ do not modify below this line -->

[//]: # "addons"
[//]: # "end addons"

## License / Licença

OCA footer...
```

### 7. Continuous Integration

The repository uses GitHub Actions workflows defined in `.github/workflows/`:

#### Test Workflow (test.yml)

- **OCA CI containers**: Uses official OCA testing infrastructure
- **Database**: PostgreSQL 14.0 with Odoo and OCB testing
- **Commands**: `oca_install_addons`, `oca_init_test_database`, `oca_run_tests` (with INCLUDE/EXCLUDE env vars)
- **Quality checks**: License validation, development status checks
- **Coverage**: Codecov integration for test coverage reporting

#### Local Testing Setup

**LOCAL DOCKER COMPOSE APPROACH**: Replicate GitHub Actions `container:` + `services:` pattern locally

1. **Use pre-commit for immediate validation**:
```bash
# Quick local validation (MANDATORY first step)
pre-commit run --all-files
```

2. **Use Docker Compose for full OCA validation locally**:
```bash
# Create temporary Docker Compose file with proper networking
cat > docker-compose-oca-test.yml << 'EOF'
version: '3.8'
services:
  postgres:
    image: postgres:14.0
    environment:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U odoo"]
      interval: 5s
      timeout: 5s
      retries: 5
    networks:
      - oca-network

  oca-ci:
    image: ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - .:/opt/odoo/addons/custom
    working_dir: /opt/odoo/addons/custom
    environment:
      - INCLUDE=l10n_br_payment_pagarme
      - EXCLUDE=
      - PGHOST=postgres
      - PGUSER=odoo
      - PGPASSWORD=odoo
      - PGDATABASE=odoo
    networks:
      - oca-network

networks:
  oca-network:
    driver: bridge
EOF

# Step 1: Start PostgreSQL service with health check
docker compose -f docker-compose-oca-test.yml up -d postgres

# Step 2: Install addons with INCLUDE/EXCLUDE using Docker Compose run
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_install_addons"

# Step 3: Test PostgreSQL connectivity using Docker (MANDATORY after oca_install_addons)
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "echo 'Testing PostgreSQL connectivity...' && timeout 30 bash -c 'until pg_isready -h postgres -p 5432 -U odoo; do echo \"Waiting for PostgreSQL...\"; sleep 2; done' && echo 'PostgreSQL connection verified ✅'"

# Step 4: Initialize test database using Docker Compose
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_init_test_database"

# Step 5: Run tests using Docker Compose
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_run_tests"

# Step 6: Cleanup
docker compose -f docker-compose-oca-test.yml down
rm docker-compose-oca-test.yml
```

3. **GitHub Actions CI validation** (automatic on push):
   - Mirrors the exact same steps with `container:` + `services:` setup
   - Provides backup validation and CI/CD integration
   - Uses same INCLUDE/EXCLUDE environment variables

**GitHub Actions Environment (from test.yml)**:
```yaml
runs-on: ubuntu-22.04
container: ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest
services:
  postgres:
    image: postgres:14.0
    env:
      POSTGRES_USER: odoo
      POSTGRES_PASSWORD: odoo
      POSTGRES_DB: odoo
    ports:
      - 5432:5432
```

**All OCA steps use INCLUDE/EXCLUDE environment variables**:
```bash
export INCLUDE="l10n_br_payment_pagarme"
export EXCLUDE=""
```

**LOCAL TESTING REQUIREMENTS**: 
- **Step 1**: Pre-commit validation (local, fast feedback)
- **Step 2**: Docker Compose OCA testing (local, full validation)
- **Step 3**: GitHub Actions CI (automatic, backup validation)
```

### 8. Development Workflow

#### 🚨 MANDATORY PRE-COMMIT ENFORCEMENT WORKFLOW 🚨

**EVERY development task MUST follow this enforcement sequence:**

```bash
# Step 1: MANDATORY setup (execute once per environment)
pip install pre-commit
pre-commit install

# Step 2: MANDATORY after EVERY code change (NO EXCEPTIONS)
pre-commit run --all-files

# Step 3: If pre-commit fails due to network, execute emergency protocols:
python -m ruff format . && python -m ruff check --fix .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"
find . -name "*.py" -exec python -m py_compile {} \;

# Step 4: MANDATORY validation before any commit
git diff --check  # Check for whitespace errors
echo "✅ All firewall rules passed - proceeding with development"
```

#### New Module Development

1. **Create module directory**: Follow `l10n_br_*` naming pattern
2. **Structure module**: Use OCA-compliant directory structure
3. **Implement functionality**: Follow Brazilian localization patterns
4. **🚨 FIREWALL CHECKPOINT**: Execute pre-commit validation
5. **Add tests**: Comprehensive testing using OCA framework
6. **🚨 FIREWALL CHECKPOINT**: Execute pre-commit validation
7. **Quality checks**: Run pre-commit hooks and OCA validation
8. **Update manifest**: Proper versioning and metadata
9. **🚨 FINAL FIREWALL CHECK**: Execute complete validation suite

#### Bug Fixes and Improvements

1. **Identify issue**: Check existing functionality and tests
2. **Create tests**: Add tests that reproduce the issue
3. **🚨 FIREWALL CHECKPOINT**: Execute pre-commit validation
4. **Implement fix**: Minimal changes following OCA patterns
5. **🚨 FIREWALL CHECKPOINT**: Execute pre-commit validation
6. **Validate**: Ensure tests pass and no regressions
7. **Documentation**: Update as needed
8. **🚨 FINAL FIREWALL CHECK**: Execute complete validation suite

### 9. OCA Specific Guidelines

#### Dependencies Management

- **Odoo dependencies**: List in `depends` field of manifest
- **External dependencies**: Document in `external_dependencies` if needed
- **Version compatibility**: Ensure Odoo 16.0 compatibility

#### Translation Support

- Use Odoo's translation system: `_("Translatable string")`
- Generate .pot files using OCA tools
- Support Portuguese (Brazil) as primary language

#### Documentation Standards

- Keep module descriptions clear and concise
- Add comprehensive docstrings to methods
- Follow OCA documentation guidelines

### 10. Best Practices

#### Code Organization

- **Logical separation**: One model per file when possible
- **Proper inheritance**: Use `_inherit` for extensions, `_name` for new models
- **Security**: Implement proper access controls in `security/` directory

#### Error Handling

```python
from odoo.exceptions import UserError, ValidationError

# User-facing errors
raise UserError(_("User-friendly error message"))

# Validation errors
raise ValidationError(_("Validation failed: specific reason"))
```

#### Logging

```python
import logging
_logger = logging.getLogger(__name__)

# Appropriate log levels
_logger.info("Information message")
_logger.warning("Warning message")
_logger.error("Error message: %s", error_details)
```

---

## Quick Reference Commands

Following the consolidation in Rule 1, these are the essential commands:

```bash
# Fresh repository setup (execute once)
pip install pre-commit && pre-commit install

# MANDATORY validation after EVERY code change (Rule 1)
pre-commit run --all-files

# MANDATORY OCA testing (Rule 1) - Docker Compose approach following test.yml pattern
# Step 1: Start PostgreSQL service
docker compose -f docker-compose-oca-test.yml up -d postgres

# Step 2: Install addons with INCLUDE/EXCLUDE using Docker Compose run
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_install_addons"

# Step 3: Test PostgreSQL connectivity (MANDATORY after oca_install_addons)
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "timeout 30 bash -c 'until pg_isready -h postgres -p 5432 -U odoo; do echo \"Waiting for PostgreSQL...\"; sleep 2; done'"

# Step 4: Initialize database
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_init_test_database"

# Step 5: Run tests
docker compose -f docker-compose-oca-test.yml run --rm oca-ci bash -c "oca_run_tests"

# Step 6: Cleanup
docker compose -f docker-compose-oca-test.yml down

# Repository exploration
find l10n_br_payment_pagarme -name "*.py" | head -10    # See Python files
find l10n_br_payment_pagarme -name "*.xml" | head -10   # See XML files  
grep -r "class.*Model" l10n_br_payment_pagarme/models/  # See model classes
```

---

This repository maintains high OCA standards while focusing on Brazilian localization requirements. Always prioritize code quality, comprehensive testing, regulatory compliance, and maintainability when developing new modules or features.

**Remember: Rule 1 requires BOTH pre-commit AND local Docker-based OCA testing to pass before ANY commit - no exceptions.**

