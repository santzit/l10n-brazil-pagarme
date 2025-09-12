import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-santzit-l10n-brazil-pagarme",
    description="Meta package for santzit-l10n-brazil-pagarme Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-l10n_br_payment_pagarme>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)