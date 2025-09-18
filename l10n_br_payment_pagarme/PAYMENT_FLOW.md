# PagarMe Payment Provider Integration Flow

This document describes the integration flow between Odoo and PagarMe payment provider
using the ORDERS API.

## Payment Processing Flow

```mermaid
flowchart TD
    A[Customer initiates payment] --> B{Payment provider configured?}
    B -->|No| X[Error: Provider not configured]
    B -->|Yes| C[Create payment transaction]

    C --> D{Use ORDERS API?}
    D -->|No| E[Simulation mode]
    D -->|Yes| F[Real API mode]

    E --> E1[Use simulated state from token]
    E1 --> E2[Process notification data]
    E2 --> Z[Update transaction state]

    F --> F1[Validate API credentials]
    F1 --> F2{Credentials valid?}
    F2 -->|No| X1[Error: Invalid credentials]
    F2 -->|Yes| F3[Prepare order data]

    F3 --> F4[Prepare customer data]
    F4 --> F5[Prepare order items]
    F5 --> F6[Prepare payment data]
    F6 --> F7[Add shipping info if available]

    F7 --> G[Send ORDERS API request]
    G --> H{API response successful?}
    H -->|No| I[Handle API error]
    H -->|Yes| J[Process API response]

    I --> I1[Log error details]
    I1 --> I2[Set transaction to error state]
    I2 --> Z

    J --> J1[Extract order ID and status]
    J1 --> J2{Order status?}
    J2 -->|paid| K[Set transaction to done]
    J2 -->|pending| L[Set transaction to pending]
    J2 -->|failed/canceled| M[Set transaction to error]
    J2 -->|other| N[Set transaction to pending]

    K --> O[Post success message]
    L --> P[Post pending message]
    M --> Q[Post error message]
    N --> R[Post status message]

    O --> Z
    P --> Z
    Q --> Z
    R --> Z

    Z --> S[Trigger post-processing if needed]
    S --> T[End]
```

## ODOO Payment Framework Integration

```mermaid
flowchart LR
    subgraph "Odoo Core"
        A[payment.provider] --> B[payment.transaction]
        B --> C[payment.token]
    end

    subgraph "PagarMe Module"
        D[PaymentProvider] --> E[PaymentTransaction]
        E --> F[PaymentToken]

        D -.extends.-> A
        E -.extends.-> B
        F -.extends.-> C
    end

    subgraph "PagarMe API"
        G[ORDERS Endpoint]
        H[Customers Endpoint]
        I[Charges Endpoint]
    end

    E -->|Create Order| G
    E -->|Customer Data| H
    E -->|Process Charges| I

    G -->|Order Response| E
    H -->|Customer Response| E
    I -->|Charge Response| E
```

## Method Flow Diagram

```mermaid
sequenceDiagram
    participant Customer
    participant Odoo
    participant PaymentProvider
    participant PaymentTransaction
    participant PagarMeAPI

    Customer->>Odoo: Initiate payment
    Odoo->>PaymentProvider: Get processing values
    PaymentProvider->>PaymentProvider: Add partner name to values

    Odoo->>PaymentTransaction: Create transaction
    PaymentTransaction->>PaymentTransaction: Validate token exists

    alt ORDERS API enabled
        PaymentTransaction->>PaymentTransaction: _send_payment_request_to_pagarme_api()
        PaymentTransaction->>PaymentTransaction: _prepare_pagarme_order_data()
        PaymentTransaction->>PaymentTransaction: _prepare_customer_data()
        PaymentTransaction->>PaymentTransaction: _prepare_order_items()
        PaymentTransaction->>PaymentTransaction: _prepare_payment_data()
        PaymentTransaction->>PaymentTransaction: _prepare_shipping_data()

        PaymentTransaction->>PagarMeAPI: POST /core/v5/orders
        PagarMeAPI-->>PaymentTransaction: Order response (JSON)

        PaymentTransaction->>PaymentTransaction: _process_pagarme_api_response()
        PaymentTransaction->>PaymentTransaction: Update transaction state
        PaymentTransaction->>PaymentTransaction: Post charge messages
    else Simulation mode
        PaymentTransaction->>PaymentTransaction: Use simulated state
        PaymentTransaction->>PaymentTransaction: _handle_notification_data()
    end

    PaymentTransaction-->>Odoo: Transaction updated
    Odoo-->>Customer: Payment result
```

## API Data Flow

```mermaid
flowchart TD
    subgraph "Order Data Preparation"
        A[Transaction Data] --> B[Order Structure]
        B --> C[Customer Info]
        B --> D[Order Items]
        B --> E[Payment Methods]
        B --> F[Shipping Info]
        B --> G[Metadata]
    end

    subgraph "Customer Data"
        C --> C1[Name & Email]
        C --> C2[Phone Numbers]
        C --> C3[CPF/CNPJ Document]
        C --> C4[Address]
    end

    subgraph "Payment Data"
        E --> E1[Credit Card Token]
        E --> E2[Amount in cents]
        E --> E3[Installments]
        E --> E4[Payment Metadata]
    end

    subgraph "API Request"
        B --> H[JSON Payload]
        H --> I[Authorization Header]
        H --> J[Content-Type: application/json]
        I --> K[Basic Auth with secret key]
    end

    subgraph "API Response Processing"
        L[PagarMe Response] --> M[Order ID]
        L --> N[Order Status]
        L --> O[Charges Array]

        N --> N1{Status Type}
        N1 -->|paid| P[Set Done]
        N1 -->|pending| Q[Set Pending]
        N1 -->|failed/canceled| R[Set Error]

        O --> O1[Process Each Charge]
        O1 --> O2[Log Charge Details]
        O1 --> O3[Post Audit Messages]
    end
```

## Error Handling Flow

```mermaid
flowchart TD
    A[API Request] --> B{Request Success?}
    B -->|No| C[Network/Connection Error]
    B -->|Yes| D{HTTP Status 200?}

    C --> C1[Log connection error]
    C1 --> C2[Raise UserError with details]

    D -->|No| E[API Error Response]
    D -->|Yes| F{Valid JSON Response?}

    E --> E1[Parse error message]
    E1 --> E2[Log API error]
    E2 --> E3[Raise UserError with API details]

    F -->|No| G[Invalid response format]
    F -->|Yes| H[Process successful response]

    G --> G1[Log parse error]
    G1 --> G2[Raise UserError - Invalid response]

    H --> I[Update transaction state]
    I --> J[Log success details]
    J --> K[Post audit messages]
```

## Configuration Flow

```mermaid
flowchart LR
    subgraph "Provider Configuration"
        A[PagarMe Public Key] --> D[Connection Test]
        B[PagarMe Secret Key] --> D
        C[Use ORDERS API] --> E{API Mode}
    end

    E -->|True| F[Real API Integration]
    E -->|False| G[Simulation Mode]

    F --> F1[Validate secret key format]
    F1 --> F2[Test API connection]
    F2 --> F3{Connection OK?}
    F3 -->|Yes| F4[Enable provider]
    F3 -->|No| F5[Show error message]

    G --> G1[Use token simulated state]
    G1 --> G2[Process notification data]
    G2 --> G3[Update transaction state]

    D --> H[GET /core/v5/customers]
    H --> I{Response 200?}
    I -->|Yes| J[Show success notification]
    I -->|No| K[Show error notification]
```

## Integration Points

### 1. Provider Configuration

- **Fields**: `pagarme_public_key`, `pagarme_secret_key`, `pagarme_use_orders_api`
- **Validation**: Secret key format validation for test/production modes
- **Connection Test**: API connectivity verification

### 2. Transaction Processing

- **Method**: `_send_payment_request()` - Entry point for payment processing
- **API Integration**: `_send_payment_request_to_pagarme_api()` - ORDERS API integration
- **Data Preparation**: Multiple helper methods for API payload construction
- **Response Processing**: `_process_pagarme_api_response()` - Handle API responses

### 3. Backward Compatibility

- **Simulation Mode**: Preserved for existing tests and development
- **Token Support**: Works with both simulated tokens and real API tokens
- **Configuration Toggle**: `pagarme_use_orders_api` setting controls behavior

### 4. Error Handling

- **API Errors**: Structured error processing with detailed logging
- **Network Issues**: Timeout and connection error handling
- **Data Validation**: Input validation before API calls
- **User Feedback**: Clear error messages for administrators and users

### 5. Audit Trail

- **Transaction Logs**: Detailed logging of API interactions
- **Charge Messages**: Posted messages for charge status updates
- **Reference Tracking**: PagarMe order ID stored as provider reference
- **Metadata**: Rich metadata for debugging and audit purposes
