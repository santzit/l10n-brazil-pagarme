# Copilot Instructions for l10n-brazil-pagarme

## Repository Overview

This is an **ODOO 16.0 OCA (Odoo Community Association) repository** for **Brazilian localization modules**, with a focus on payment providers and Brazilian market requirements.

**Key Context:**
- **Purpose**: Brazilian localization modules for Odoo, including payment providers and market-specific features
- **Odoo Version**: 16.0 (follow version-specific patterns and APIs)
- **OCA Compliance**: Strict adherence to OCA standards for community modules
- **Localization Focus**: Brazilian market requirements, regulations, and payment systems
- **Module Pattern**: `l10n_br_*` naming convention for Brazilian localization modules

The repository follows OCA standards and best practices for Odoo module development with specific focus on Brazilian market requirements.

## Repository Structure

This repository contains Brazilian localization modules following OCA directory standards:

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
- Use descriptive names following OCA naming conventions (`l10n_br_*` for Brazilian localization)

#### Manifest File Requirements
```python
{
    'name': 'Descriptive Module Name',
    'version': '16.0.x.y.z',  # Follow OCA versioning
    'category': 'Appropriate Category',
    'summary': "Brief module description",
    'depends': ['base', 'required_modules'],  # Core dependencies
    'data': [
        'security/security.xml',  # If access control needed
        'views/view_files.xml',
        'data/data_files.xml',
    ],
    'license': 'LGPL-3',  # OCA standard license
    'installable': True,
    'auto_install': False,
}
```

### 2. Python Development Standards

#### Code Style
- Follow **PEP 8** and **OCA Python guidelines**
- Use the configured **pre-commit hooks** (setup in `.pre-commit-config.yaml`)
- Run `pre-commit run --all-files` before committing

#### Model Development Patterns
```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

class ModelName(models.Model):
    _inherit = 'existing.model'  # For extending existing models
    # OR
    _name = 'new.model.name'     # For new models
    
    # Field definitions with proper types and attributes
    field_name = fields.Char("Field Label", required=True)
    
    # Methods with proper decorators and documentation
    @api.depends('field_name')
    def _compute_something(self):
        """Compute method documentation."""
        for record in self:
            record.computed_field = self._calculate_value()
    
    @api.constrains('field_name')
    def _check_field_name(self):
        """Validation method documentation."""
        if self.filtered(lambda r: not r.field_name):
            raise ValidationError(_("Field is required"))
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

@tagged('-at_install', 'post_install')  # Standard OCA test tagging
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
The repository uses OCA testing infrastructure as defined in `.github/workflows/test.yml`:

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
    
    @http.route('/brazilian/endpoint', type='json', auth='public', csrf=False)
    def endpoint_handler(self, **kwargs):
        """Handle Brazilian-specific requests."""
        # Implementation with proper error handling
        return {'status': 'success'}
```

#### Playwright Testing Integration
For browser automation testing, integrate with Odoo's testing framework:

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestUIFunctionality(HttpCase):
    
    def test_user_interface(self):
        """Test UI functionality with Playwright patterns."""
        # Use Playwright for browser automation
        # Integrate with Odoo's HttpCase framework
        pass
```

Follow the testing patterns established in `.github/workflows/test.yml` for consistency with CI/CD pipeline.

### 6. Pre-commit Configuration

The repository includes comprehensive pre-commit hooks for code quality:

#### Available Hooks
- **OCA-specific**: Module validation, manifest checks, README generation
- **Code formatting**: Ruff for Python, Prettier for XML/JS
- **Code quality**: PyLint with Odoo extensions
- **General checks**: Encoding, merge conflicts, trailing whitespace

#### Usage
```bash
# Install and run pre-commit (essential for OCA compliance)
pip install pre-commit
pre-commit install
pre-commit run --all-files
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

#### New Module Development
1. **Create module directory**: Follow `l10n_br_*` naming pattern
2. **Structure module**: Use OCA-compliant directory structure
3. **Implement functionality**: Follow Brazilian localization patterns
4. **Add tests**: Comprehensive testing using OCA framework
5. **Quality checks**: Run pre-commit hooks and OCA validation
6. **Update manifest**: Proper versioning and metadata

#### Bug Fixes and Improvements
1. **Identify issue**: Check existing functionality and tests
2. **Create tests**: Add tests that reproduce the issue
3. **Implement fix**: Minimal changes following OCA patterns
4. **Validate**: Ensure tests pass and no regressions
5. **Documentation**: Update as needed

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

### Setup and Development
```bash
# Clone and setup repository
git clone https://github.com/santzit/l10n-brazil-pagarme.git
cd l10n-brazil-pagarme

# Install development tools
pip install pre-commit
pre-commit install

# Quality checks (following .pre-commit-config.yaml)
pre-commit run --all-files

# Testing (following .github/workflows/test.yml patterns)
oca_install_addons
oca_init_test_database  
oca_run_tests

# Module validation
manifestoo -d . check-licenses
manifestoo -d . check-dev-status --default-dev-status=Beta
```

### Development Checklist
- [ ] Follow `l10n_br_*` naming convention for Brazilian modules
- [ ] Implement proper `__manifest__.py` with OCA metadata
- [ ] Add models in `models/` directory with proper inheritance
- [ ] Create views in `views/` directory with XML structure
- [ ] Add tests in `tests/` directory using OCA patterns
- [ ] Include security definitions in `security/` if needed
- [ ] Use translation markers `_()` for user-facing strings
- [ ] Follow Brazilian localization requirements
- [ ] Run pre-commit hooks and ensure all checks pass
- [ ] Test with OCA infrastructure using `oca_run_tests`
- [ ] Validate module compliance with manifestoo tools

### Environment Requirements
- **Python**: 3.10 (as per OCA CI configuration)
- **Odoo**: 16.0 compatibility required
- **Database**: PostgreSQL 14.0+ for testing
- **Tools**: Docker (for OCA testing), pre-commit, manifestoo
- **Brazilian Context**: Understanding of Brazilian market and regulatory requirements

This repository maintains high OCA standards while focusing on Brazilian localization requirements. Always prioritize code quality, comprehensive testing, regulatory compliance, and maintainability when developing new modules or features.