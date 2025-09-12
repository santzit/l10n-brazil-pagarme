# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Provider: Pagarme',
    'version': '2.0',
    'category': 'Hidden',
    'sequence': 350,
    'summary': "A payment provider for running fake payment flows for pagarme purposes.",
    'description': " ",  # Non-empty string to avoid loading the README file.
    'depends': ['payment'],
    'data': [
        'views/payment_pagarme_templates.xml',
        'views/payment_templates.xml',
        'views/payment_token_views.xml',
        'views/payment_transaction_views.xml',
        'data/payment_provider_data.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'assets': {
        'web.assets_frontend': [
            'l10n_br_payment_pagarme/static/src/js/**/*',
        ],
    },
    'license': 'LGPL-3',
}