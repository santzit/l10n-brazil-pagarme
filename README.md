# l10n-brazil-pagarme
OCA PagarMe module for Brazil Localization

## Description

This repository contains an ODOO 16 OCA module for the Pagarme payment provider, designed specifically for Brazilian localization.

## Features

The `l10n_br_payment_pagarme` module provides:

- Direct payment flow simulation
- Tokenization with or without payment
- Manual capture support
- Full and partial refunds
- Customer fees
- Selectable payment outcome for testing

## Module Structure

- **l10n_br_payment_pagarme/**: Main module directory containing the Pagarme payment provider implementation
  - **controllers/**: HTTP controllers for payment simulation
  - **models/**: Payment provider, token, and transaction models
  - **views/**: XML templates and view definitions
  - **data/**: Data files for payment provider configuration
  - **static/**: JavaScript files for frontend integration
  - **tests/**: Unit tests for the module
  - **i18n/**: Translation files

## Installation

1. Clone this repository
2. Add the repository path to your Odoo addons path
3. Install the `l10n_br_payment_pagarme` module

## Testing

This module includes comprehensive tests and is configured with GitHub Actions for continuous integration:

- **pre-commit**: Code quality checks and formatting
- **tests**: Unit tests using OCA testing infrastructure

## License

This module is licensed under AGPL-3.0.

## Contributing

Please follow the OCA development guidelines and ensure all tests pass before submitting pull requests.
