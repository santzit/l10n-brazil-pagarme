[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=santzit/l10n-brazil-pagarme&target_branch=16.0)
[![Pre-commit Status](https://github.com/santzit/l10n-brazil-pagarme/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/santzit/l10n-brazil-pagarme/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/santzit/l10n-brazil-pagarme/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/santzit/l10n-brazil-pagarme/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/santzit/l10n-brazil-pagarme/branch/16.0/graph/badge.svg)](https://codecov.io/gh/santzit/l10n-brazil-pagarme)

<!-- /!\ do not modify above this line -->

# Odoo Brazilian Localization - PagarMe Payment Provider / Localização Brasileira do Odoo - Provedor de Pagamento PagarMe

Este repositório contém um módulo Odoo 16.0 OCA que implementa o provedor de pagamento PagarMe, projetado especificamente para a localização brasileira. O módulo oferece integração completa com os serviços de pagamento PagarMe, suportando as necessidades específicas do mercado brasileiro.

This repository contains an Odoo 16.0 OCA module that implements the PagarMe payment provider, designed specifically for Brazilian localization. The module provides complete integration with PagarMe payment services, supporting the specific needs of the Brazilian market.

## Características Principais / Key Features

O módulo `l10n_br_payment_pagarme` oferece / The `l10n_br_payment_pagarme` module provides:

- **Simulação de fluxo de pagamento direto** / Direct payment flow simulation
- **Tokenização com ou sem pagamento** / Tokenization with or without payment
- **Suporte à captura manual** / Manual capture support
- **Reembolsos totais e parciais** / Full and partial refunds
- **Taxas do cliente** / Customer fees
- **Resultado de pagamento selecionável para testes** / Selectable payment outcome for testing
- **Integração com métodos de pagamento brasileiros** / Integration with Brazilian payment methods
- **Conformidade com regulamentações locais** / Compliance with local regulations

## :arrow_forward: **Teste o Módulo Agora! / Try the Module Now!**

Experimente o módulo PagarMe em um ambiente de demonstração / Try the PagarMe module in a demo environment:

1. Clique no botão abaixo para iniciar um container no Runboat / Click the button below to start a container on Runboat:

   [![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=santzit/l10n-brazil-pagarme&target_branch=16.0)

2. Aguarde até o container ficar disponível (indicador verde) / Wait until the container is available (green indicator)
3. Clique em **Live** para acessar o Odoo / Click **Live** to access Odoo
4. Entre com `admin/admin` / Login with `admin/admin`
5. Instale o módulo `l10n_br_payment_pagarme` e explore as funcionalidades de pagamento / Install the `l10n_br_payment_pagarme` module and explore payment functionalities

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[l10n_br_payment_pagarme](l10n_br_payment_pagarme/) | 16.0.1.0.0 |  | PagarMe Payment Provider for Brazilian Localization

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Instalação / Installation

### Pré-requisitos / Prerequisites

- Odoo 16.0
- Módulos da localização brasileira OCA / OCA Brazilian localization modules
- Conta PagarMe ativa / Active PagarMe account

### Passos de Instalação / Installation Steps

1. **Clone este repositório / Clone this repository:**

   ```bash
   git clone https://github.com/santzit/l10n-brazil-pagarme.git
   ```

2. **Adicione o caminho ao addons_path do Odoo / Add the path to Odoo's addons_path:**

   ```ini
   addons_path = /path/to/odoo/addons,/path/to/l10n-brazil-pagarme
   ```

3. **Atualize a lista de módulos / Update module list:**
   - Acesse o Odoo / Access Odoo
   - Vá para Apps / Go to Apps
   - Clique em "Update Apps List" / Click "Update Apps List"

4. **Instale o módulo / Install the module:**
   - Procure por "PagarMe" / Search for "PagarMe"
   - Instale `l10n_br_payment_pagarme` / Install `l10n_br_payment_pagarme`

## Configuração / Configuration

1. **Configure o provedor de pagamento / Configure the payment provider:**
   - Vá para Invoicing > Configuration > Payment Providers
   - Selecione PagarMe
   - Configure suas credenciais da API / Configure your API credentials

2. **Configure métodos de pagamento / Configure payment methods:**
   - Cartão de crédito / Credit card
   - PIX (sistema de pagamento instantâneo brasileiro / Brazilian instant payment system)
   - Boleto bancário / Bank slip

## Desenvolvimento / Development

### Executando Testes / Running Tests

```bash
# Execute todos os testes / Run all tests
python -m pytest l10n_br_payment_pagarme/tests/

# Execute verificações de qualidade / Run quality checks
pre-commit run --all-files
```

### Contribuindo / Contributing

1. Faça um fork do repositório / Fork the repository
2. Crie uma branch para sua feature / Create a feature branch
3. Implemente suas mudanças / Implement your changes
4. Execute os testes / Run tests
5. Submeta um pull request / Submit a pull request

Por favor, siga as diretrizes de desenvolvimento da OCA e garanta que todos os testes passem antes de submeter pull requests.

Please follow OCA development guidelines and ensure all tests pass before submitting pull requests.

## Licenças / Licenses

Este repositório está licenciado sob [AGPL-3.0](LICENSE).

This repository is licensed under [AGPL-3.0](LICENSE).

Entretanto, cada módulo pode ter uma licença totalmente diferente, desde que aderem à política da Odoo Community Association (OCA). Consulte o arquivo `__manifest__.py` de cada módulo, que contém uma chave `license` que explica sua licença.

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA) policy. Consult each module's `__manifest__.py` file, which contains a `license` key that explains its license.

---

OCA, ou a [Odoo Community Association](http://odoo-community.org/), é uma organização sem fins lucrativos cuja missão é apoiar o desenvolvimento colaborativo de recursos do Odoo e promover seu uso generalizado.

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.
