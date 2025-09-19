# PagarMe ORDERS API Integration - Payment Flow Documentation

This document provides comprehensive Mermaid flowcharts showing the integration between ODOO and PagarMe payment provider using the ORDERS API.

## 1. Payment Processing Flow

```mermaid
flowchart TD
    A[Customer Initiates Payment] --> B[ODOO Payment Form]
    B --> C{Payment Method?}
    
    C -->|Credit Card| D[Enter Card Details<br/>- Card Number<br/>- Holder Name<br/>- Expiry<br/>- CVV<br/>- CPF/CNPJ<br/>- Installments]
    
    D --> E[Submit Payment Form]
    E --> F[ODOO Creates Payment Transaction]
    F --> G[_send_payment_request Method]
    
    G --> H[_send_payment_request_to_pagarme_api]
    H --> I[_prepare_pagarme_order_data]
    
    I --> J[Prepare Order Components:<br/>- Customer Data<br/>- Order Items<br/>- Payment Data<br/>- Shipping Data]
    
    J --> K[_make_pagarme_api_request]
    K --> L[HTTP POST to<br/>api.pagar.me/core/v5/orders]
    
    L --> M{API Response?}
    
    M -->|Success 200/201| N[_process_pagarme_api_response]
    M -->|Error 4xx/5xx| O[Handle API Error<br/>Log Error Details<br/>Update Transaction State]
    
    N --> P[Extract Order ID & Status]
    P --> Q[Update Transaction in ODOO]
    Q --> R[Set Transaction State<br/>- pending<br/>- authorized<br/>- done<br/>- error]
    
    R --> S[Webhook Endpoint<br/>/payment/pagarme/webhook]
    S --> T[Process Payment Status Updates]
    T --> U[Final Transaction State]
    
    O --> V[Display Error to Customer]
    U --> W[Payment Complete]
    V --> X[Payment Failed]

    F --> F1[Validate API credentials]
    F1 --> F2{Credentials valid?}
    F2 -->|No| X1[Error: Invalid credentials]
    F2 -->|Yes| F3[Prepare order data]

    F3 --> F4[Prepare customer data]
    F4 --> F5[Prepare order items]
```

## 2. ODOO Payment Framework Integration

```mermaid
flowchart TD
    A[payment.provider Model] --> B[PaymentProvider Class<br/>l10n_br_payment_pagarme]
    
    B --> C[Configuration Fields:<br/>- pagarme_public_key<br/>- pagarme_secret_key<br/>- state (test/enabled)]
    
    C --> D[Connection Testing:<br/>- action_test_pagarme_connection<br/>- _test_orders_api_connection]
    
    A --> E[payment.transaction Model] --> F[PaymentTransaction Class<br/>l10n_br_payment_pagarme]
    
    F --> G[Payment Methods:<br/>- _send_payment_request<br/>- _send_refund_request<br/>- _send_capture_request<br/>- _send_void_request]
    
    G --> H[PagarMe API Integration:<br/>- _send_payment_request_to_pagarme_api<br/>- _prepare_pagarme_order_data<br/>- _make_pagarme_api_request<br/>- _process_pagarme_api_response]
    
    A --> I[payment.token Model] --> J[PaymentToken Class<br/>l10n_br_payment_pagarme]
    
    J --> K[Token Storage:<br/>- Card Brand<br/>- Last 4 Digits<br/>- Expiry Date<br/>- Provider Reference]
    
    L[Controller<br/>PaymentPagarmeController] --> M[Webhook Endpoint:<br/>/payment/pagarme/webhook]
    
    M --> N[Process Real-time<br/>Payment Notifications]
    N --> O[Update Transaction Status]
```

## 3. Method Sequence Flow

```mermaid
sequenceDiagram
    participant C as Customer
    participant O as ODOO
    participant P as PaymentTransaction
    participant A as PagarMe API
    participant W as Webhook
    
    C->>O: Submit Payment Form
    O->>P: Create Transaction Record
    P->>P: _send_payment_request()
    P->>P: _send_payment_request_to_pagarme_api()
    
    P->>P: _prepare_pagarme_order_data()
    Note over P: Prepare customer, items, payment data
    
    P->>P: _prepare_customer_data()
    Note over P: CPF/CNPJ, address, phone
    
    P->>P: _prepare_order_items()
    Note over P: Transaction amount, description
    
    P->>P: _prepare_payment_data()
    Note over P: Credit card, installments
    
    P->>P: _prepare_shipping_data()
    Note over P: Brazilian address format
    
    P->>P: _make_pagarme_api_request()
    P->>A: POST /core/v5/orders
    Note over A: Process payment with<br/>Brazilian regulations
    
    A->>P: Response (order_id, status)
    P->>P: _process_pagarme_api_response()
    P->>O: Update Transaction State
    
    A->>W: Webhook Notification
    W->>P: Update Payment Status
    P->>O: Final State Update
    O->>C: Payment Result
```

## 4. API Data Flow

```mermaid
flowchart LR
    A[ODOO Transaction Data] --> B[Data Preparation]
    
    B --> C[Customer Data:<br/>- name<br/>- email<br/>- phones<br/>- documents (CPF/CNPJ)<br/>- address]
    
    B --> D[Order Items:<br/>- code<br/>- description<br/>- amount (centavos)<br/>- quantity<br/>- category]
    
    B --> E[Payment Data:<br/>- payment_method<br/>- credit_card token<br/>- installments<br/>- amount]
    
    B --> F[Shipping Data:<br/>- address<br/>- recipient_name<br/>- recipient_phone]
    
    C --> G[PagarMe Order JSON]
    D --> G
    E --> G
    F --> G
    
    G --> H[HTTP POST<br/>api.pagar.me/core/v5/orders<br/>Authorization: Basic base64(secret_key:)]
    
    H --> I[PagarMe Response:<br/>- id (order_id)<br/>- status<br/>- charges array<br/>- customer data<br/>- metadata]
    
    I --> J[ODOO Transaction Update:<br/>- provider_reference<br/>- state mapping<br/>- status message]
```

## 5. Error Handling Flow

```mermaid
flowchart TD
    A[API Request] --> B{Response Status}
    
    B -->|200/201 Success| C[Process Response Data]
    B -->|401 Unauthorized| D[Invalid API Key Error]
    B -->|422 Validation Error| E[Invalid Request Data]
    B -->|500 Server Error| F[PagarMe System Error]
    B -->|Network Timeout| G[Connection Timeout]
    B -->|Connection Error| H[Network Error]
    
    C --> I[Extract Order Information<br/>Update Transaction State]
    
    D --> J[Log Authentication Error<br/>Display User-Friendly Message]
    E --> K[Log Validation Details<br/>Show Field Errors]
    F --> L[Log Server Error<br/>Retry or Fallback]
    G --> M[Log Timeout Error<br/>Suggest Retry]
    H --> N[Log Network Error<br/>Check Connectivity]
    
    J --> O[Set Transaction to Error State]
    K --> O
    L --> O
    M --> O
    N --> O
    
    I --> P[Transaction Complete]
    O --> Q[Payment Failed]
```

## 6. Configuration Flow

```mermaid
flowchart TD
    A[Administrator Access] --> B[Payment Settings]
    B --> C[Create PagarMe Provider]
    
    C --> D[Configure Credentials:<br/>- Public Key<br/>- Secret Key<br/>- Environment (test/prod)]
    
    D --> E[Test Connection]
    E --> F[action_test_pagarme_connection]
    F --> G[_test_orders_api_connection]
    
    G --> H[Create Test Order Structure]
    H --> I[Send to PagarMe API]
    I --> J{Connection Test Result}
    
    J -->|Success| K[Enable Provider<br/>Ready for Payments]
    J -->|Failure| L[Show Error Message<br/>Check Credentials]
    
    K --> M[Provider Available<br/>for Customer Payments]
    L --> N[Fix Configuration<br/>Retry Test]
    
    N --> E
```

## Key Implementation Features

### Real API Integration
- **Complete ORDERS API**: Full integration with PagarMe's core payment API
- **Brazilian Compliance**: CPF/CNPJ document handling, BRL currency, installments
- **Authentication**: Secure Basic authentication with secret key
- **Error Handling**: Comprehensive API error processing with detailed logging

### ODOO Framework Integration
- **Provider Model Extension**: Inherits from `payment.provider`
- **Transaction Model Extension**: Inherits from `payment.transaction`
- **Token Model Extension**: Inherits from `payment.token`
- **Controller Integration**: Real webhook endpoint for notifications

### Data Flow Architecture
- **Preparation Layer**: Multiple specialized methods for data formatting
- **API Communication**: Dedicated HTTP client with proper headers
- **Response Processing**: Status mapping and error handling
- **State Management**: Transaction lifecycle management

### Brazilian Market Features
- **Document Support**: CPF/CNPJ automatic detection and formatting
- **Address Format**: Brazilian postal codes and state handling
- **Payment Methods**: Credit card with installment options (1x to 12x)
- **Currency**: BRL with centavo conversion (amount * 100)

This integration provides a production-ready foundation for Brazilian e-commerce payments using PagarMe's robust payment infrastructure.
