# Copilot Instructions for l10n-brazil-pagarme

## 🚨 MANDATORY COPILOT FIREWALL RULES 🚨

**THESE RULES MUST BE FOLLOWED WITHOUT EXCEPTION - NO CODE CHANGES ARE ALLOWED WITHOUT
COMPLIANCE**

### Rule 1: Pre-commit Execution is MANDATORY

```bash
# ABSOLUTE REQUIREMENT: Execute these commands after EVERY code change
pre-commit run --all-files

# If pre-commit fails due to network issues, use alternative validation:
python -m ruff format .
python -m ruff check --fix .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"
find . -name "*.py" -exec python -m py_compile {} \;
```

### Rule 2: Zero Tolerance for Formatting Violations

- **Python**: ONLY double quotes allowed - `"string"` ✅, `'string'` ❌
- **Line Length**: MAXIMUM 88 characters per line (E501 enforced by ruff)
- **Imports**: ONLY explicit re-exports in `__init__.py` -
  `from . import models as models` ✅
- **Files**: MUST end with single newline, NO trailing whitespace
- **XML/JS**: MUST pass prettier formatting validation
- **Docstrings**: Break long docstrings across multiple lines to stay under 88 chars

### Rule 3: Validation Before ANY Code Submission

```bash
# MANDATORY pre-submission checklist execution:
pre-commit run --all-files                    # Primary validation
python -m ruff format . && python -m ruff check --fix .    # Python validation
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"  # Format validation
find . -name "*.py" -exec python -m py_compile {} \;       # Syntax validation
```

### Rule 4: Emergency Protocols for Network Issues

When pre-commit installation fails due to network issues, execute these commands
immediately:

```bash
# Install tools directly if pre-commit network fails
pip install ruff
npm install prettier @prettier/plugin-xml

# Execute manual validation (substitute for pre-commit)
ruff check --fix . && ruff format .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}" --ignore-unknown
find . -name "*.py" -exec python -m py_compile {} \;
find . -name "*.xml" -exec python -c "import xml.etree.ElementTree as ET; ET.parse('{}'); print('{}: OK')" \;
```

**FAILURE TO COMPLY WITH THESE FIREWALL RULES WILL RESULT IN CI PIPELINE FAILURES**

---

## Repository Overview

This is an **ODOO 16.0 OCA (Odoo Community Association) repository** for **Brazilian
localization modules**, with a focus on payment providers and Brazilian market
requirements.

**Key Context:**

- **Purpose**: Brazilian localization modules for Odoo, including payment providers and
  market-specific features
- **Odoo Version**: 16.0 (follow version-specific patterns and APIs)
- **OCA Compliance**: Strict adherence to OCA standards for community modules
- **Localization Focus**: Brazilian market requirements, regulations, and payment
  systems
- **Module Pattern**: `l10n_br_*` naming convention for Brazilian localization modules

The repository follows OCA standards and best practices for Odoo module development with
specific focus on Brazilian market requirements.

## Repository Structure

This repository contains Brazilian localization modules following OCA directory
standards:

```
l10n_br_module_name/              # Module directory (l10n_br_* pattern)
├── __manifest__.py               # Module manifest (required)
├── __init__.py                   # Module initialization
├── controllers/                  # HTTP controllers (if needed)
├── models/                       # Business logic models
├── views/                        # XML view definitions
├── data/                         # Data files and records
├── static/                       # Static assets (JS, CSS, images)
├── tests/                        # Unit and integration tests
├── security/                     # Access control files
└── i18n/                        # Translation files (auto-generated)
```

## Development Guidelines

### 1. ODOO OCA Standards Compliance

#### Module Structure

- **ALWAYS** follow the OCA module structure pattern
- **REQUIRED**: Each module must have `__manifest__.py` with proper OCA metadata
- **REQUIRED**: Include `__init__.py` files in all Python directories
- Use descriptive names following OCA naming conventions (`l10n_br_*` for Brazilian
  localization)

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
# Tests are run automatically using OCA CI containers
# Commands from test.yml workflow:
oca_install_addons       # Install dependencies
oca_init_test_database   # Initialize test database
oca_run_tests           # Run all tests

# For local development with Docker:
docker run --rm -v $(pwd):/opt/odoo/addons/custom \
  ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest \
  oca_run_tests
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

#### Network Issues and Alternative Validation

If pre-commit encounters network issues during installation, use these alternative
validation methods:

```bash
# Install core tools directly
pip install ruff
npm install prettier @prettier/plugin-xml

# Manual validation commands
ruff check --fix .                    # Python linting
ruff format .                         # Python formatting
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}" --ignore-unknown

# Check Python syntax compilation
find . -name "*.py" -exec python -m py_compile {} \;

# Check XML syntax with Python
find . -name "*.xml" -exec python -c "import xml.etree.ElementTree as ET; ET.parse('{}'); print('{}: OK')" \;

# Check for trailing whitespace
find . -name "*.py" -exec grep -l "[[:space:]]$" {} \;

# Check for missing newlines at end of files
find . -name "*.py" -exec sh -c 'if [ "$(tail -c1 "$1")" != "" ]; then echo "$1"; fi' _ {} \;
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
- **Commands**: `oca_install_addons`, `oca_init_test_database`, `oca_run_tests`
- **Quality checks**: License validation, development status checks
- **Coverage**: Codecov integration for test coverage reporting

#### Local Testing

```bash
# Use the same OCA containers as CI
docker run --rm -v $(pwd):/opt/odoo/addons/custom \
  ghcr.io/oca/oca-ci/py3.10-odoo16.0:latest \
  oca_run_tests

# Check module compliance (as per test.yml)
manifestoo -d . check-licenses
manifestoo -d . check-dev-status --default-dev-status=Beta
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

## Quick Reference

### 🚨 FIREWALL RULES - EXECUTE AFTER EVERY CODE CHANGE 🚨

```bash
# PRIMARY FIREWALL COMMAND (execute after every code change)
pre-commit run --all-files

# EMERGENCY FIREWALL (if pre-commit fails due to network issues)
python -m ruff format . && python -m ruff check --fix .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"
find . -name "*.py" -exec python -m py_compile {} \;
find . -name "*.xml" -exec python -c "import xml.etree.ElementTree as ET; ET.parse('{}'); print('{}: OK')" \;

# VALIDATION FIREWALL (before any commit/push)
git diff --check && echo "✅ FIREWALL PASSED - Safe to proceed"
```

### Setup and Development

```bash
# Clone and setup repository
git clone https://github.com/santzit/l10n-brazil-pagarme.git
cd l10n-brazil-pagarme

# MANDATORY: Install development tools and setup pre-commit
pip install pre-commit
pre-commit install

# MANDATORY: Quality checks (following .pre-commit-config.yaml)
# Run this before every commit to prevent CI failures
pre-commit run --all-files

# Auto-fix common formatting issues
python -m ruff format .                    # Fix Python formatting (double quotes, etc.)
python -m ruff check --fix .             # Fix Python linting issues
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"  # Fix XML/JS formatting

# Testing (following .github/workflows/test.yml patterns)
oca_install_addons
oca_init_test_database
oca_run_tests

# Module validation
manifestoo -d . check-licenses
manifestoo -d . check-dev-status --default-dev-status=Beta
```

### Development Checklist

#### 🚨 FIREWALL VALIDATION CHECKLIST (MANDATORY) 🚨

- [ ] **FIREWALL RULE 1**: Execute `pre-commit run --all-files` after EVERY code change
- [ ] **FIREWALL RULE 2**: All Python strings use double quotes (ruff enforced)
- [ ] **FIREWALL RULE 3**: All `__init__.py` use explicit re-exports
      (`from . import module as module`)
- [ ] **FIREWALL RULE 4**: All files end with single newline, no trailing whitespace
- [ ] **FIREWALL RULE 5**: Execute emergency protocols if pre-commit network fails

#### Standard Development Requirements

- [ ] Follow `l10n_br_*` naming convention for Brazilian modules
- [ ] Implement proper `__manifest__.py` with OCA metadata using **double quotes**
- [ ] Add models in `models/` directory with proper inheritance using **double quotes**
- [ ] Create views in `views/` directory with properly formatted XML structure
- [ ] Add tests in `tests/` directory using OCA patterns with **double quotes**
- [ ] Include security definitions in `security/` if needed
- [ ] Use translation markers `_()` for user-facing strings with **double quotes**
- [ ] Use explicit re-exports in all `__init__.py` files
      (`from . import module as module`)
- [ ] Ensure all files end with a single newline
- [ ] Remove all trailing whitespace from files
- [ ] Follow Brazilian localization requirements
- [ ] **README.md**: Follow OCA standards with badges, bilingual content, and proper
      structure
- [ ] **README.md**: Include Runboat links, installation instructions, and OCA footer
- [ ] **README.md**: Use auto-generated addons table format with proper comments

#### Final Validation (MANDATORY BEFORE COMMIT)

- [ ] **MANDATORY**: Run pre-commit hooks and ensure ALL checks pass:
      `pre-commit run --all-files`
- [ ] **MANDATORY**: Fix any ruff formatting errors (especially quote standardization)
- [ ] **MANDATORY**: Fix any prettier formatting errors for XML/JS files
- [ ] **MANDATORY**: Validate Python syntax compilation:
      `find . -name "*.py" -exec python -m py_compile {} \;`
- [ ] **MANDATORY**: Validate XML syntax:
      `find . -name "*.xml" -exec python -c "import xml.etree.ElementTree as ET; ET.parse('{}'); print('{}: OK')" \;`
- [ ] Test with OCA infrastructure using `oca_run_tests`
- [ ] Validate module compliance with manifestoo tools

### Environment Requirements

- **Python**: 3.10 (as per OCA CI configuration)
- **Odoo**: 16.0 compatibility required
- **Database**: PostgreSQL 14.0+ for testing
- **Tools**: Docker (for OCA testing), pre-commit, manifestoo
- **Brazilian Context**: Understanding of Brazilian market and regulatory requirements

This repository maintains high OCA standards while focusing on Brazilian localization
requirements. Always prioritize code quality, comprehensive testing, regulatory
compliance, and maintainability when developing new modules or features.

---

## 🚨 FINAL REMINDER: FIREWALL RULES ENFORCEMENT 🚨

**These commands MUST be executed after EVERY code change - NO EXCEPTIONS:**

```bash
# Execute this after every code modification
pre-commit run --all-files

# Emergency fallback if network issues occur
python -m ruff format . && python -m ruff check --fix .
npx prettier --write "**/*.{xml,js,css,json,md,yml,yaml}"
find . -name "*.py" -exec python -m py_compile {} \;
```

**Failure to execute these firewall rules will result in CI pipeline failures and
blocked merges.**

Remember: Pre-commit hooks are your first line of defense against formatting errors and
CI failures. The pre-commit environment shown in the successful execution indicates that
all necessary tools are properly installed and ready for validation.
