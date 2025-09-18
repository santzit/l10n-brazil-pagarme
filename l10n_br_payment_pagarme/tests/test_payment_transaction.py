# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import Mock, patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.l10n_br_payment_pagarme.tests.common import PaymentPagarmeCommon
from odoo.addons.payment.tests.http_common import PaymentHttpCommon


@tagged("-at_install", "post_install")
class TestPaymentTransaction(PaymentPagarmeCommon, PaymentHttpCommon):
    def test_processing_notification_data_sets_transaction_pending(self):
        """Test that the transaction state is set to 'pending' when the
        notification data indicate a pending payment."""
        tx = self._create_transaction("direct")
        tx._process_notification_data(
            dict(self.notification_data, status="pending")
        )
        self.assertEqual(tx.state, "pending")

    def test_processing_notification_data_authorizes_transaction(self):
        """Test that the transaction state is set to 'authorize' when the
        notification data indicate a successful payment and manual capture is
        enabled."""
        self.provider.capture_manually = True
        tx = self._create_transaction("direct")
        tx._process_notification_data(self.notification_data)
        self.assertEqual(tx.state, "authorized")

    def test_processing_notification_data_confirms_transaction(self):
        """Test that the transaction state is set to 'done' when the notification
        data indicate a successful payment."""
        tx = self._create_transaction("direct")
        tx._process_notification_data(self.notification_data)
        self.assertEqual(tx.state, "done")

    def test_processing_notification_data_cancels_transaction(self):
        """Test that the transaction state is set to 'cancel' when the notification
        data indicate an unsuccessful payment."""
        tx = self._create_transaction("direct")
        tx._process_notification_data(
            dict(self.notification_data, status="canceled")
        )
        self.assertEqual(tx.state, "cancel")

    def test_processing_notification_data_sets_transaction_in_error(self):
        """Test that the transaction state is set to 'error' when the notification
        data indicate an error during the payment."""
        tx = self._create_transaction("direct")
        tx._process_notification_data(
            dict(self.notification_data, status="error", error_message="Payment failed")
        )
        self.assertEqual(tx.state, "error")

    def test_processing_notification_data_tokenizes_transaction(self):
        """Test that the transaction is tokenized when it was requested and the
        notification data include token data."""
        tx = self._create_transaction("direct", tokenize=True)
        with patch(
            "odoo.addons.l10n_br_payment_pagarme.models.payment_transaction.PaymentTransaction"
            "._pagarme_tokenize_from_notification_data"
        ) as tokenize_mock:
            tx._process_notification_data(self.notification_data)
        self.assertEqual(tokenize_mock.call_count, 1)

    @patch(
        "odoo.addons.l10n_br_payment_pagarme.models.payment_transaction.requests.post"
    )
    def test_orders_api_payment_request_success(self, mock_post):
        """Test successful ORDERS API payment request."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "order_123",
            "status": "paid",
            "charges": [
                {
                    "id": "charge_456",
                    "status": "paid",
                    "amount": 10000,  # R$ 100.00 in cents
                }
            ],
        }
        mock_post.return_value = mock_response

        # Configure provider for API testing
        self.provider.pagarme_secret_key = "sk_test_123456789"  # Add test secret key
        tx = self._create_transaction("direct")
        tx.token_id = self._create_token()

        tx._send_payment_request()

        # Verify API was called
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertIn("/core/v5/orders", call_args[0][0])

        # Verify transaction state was updated
        self.assertEqual(tx.state, "done")
        self.assertEqual(tx.provider_reference, "order_123")

    @patch(
        "odoo.addons.l10n_br_payment_pagarme.models.payment_transaction.requests.post"
    )
    def test_orders_api_payment_request_pending(self, mock_post):
        """Test ORDERS API payment request with pending status."""
        # Mock pending API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "order_456",
            "status": "pending",
            "charges": [],
        }
        mock_post.return_value = mock_response

        # Configure provider for API testing
        self.provider.pagarme_secret_key = "sk_test_123456789"  # Add test secret key
        tx = self._create_transaction("direct")
        tx.token_id = self._create_token()

        tx._send_payment_request()

        # Verify transaction state was updated to pending
        self.assertEqual(tx.state, "pending")
        self.assertEqual(tx.provider_reference, "order_456")

    @patch(
        "odoo.addons.l10n_br_payment_pagarme.models.payment_transaction.requests.post"
    )
    def test_orders_api_payment_request_failure(self, mock_post):
        """Test ORDERS API payment request failure."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {"message": "Invalid payment data"}
        mock_post.return_value = mock_response

        # Configure provider for API testing
        self.provider.pagarme_secret_key = "sk_test_123456789"  # Add test secret key
        tx = self._create_transaction("direct")
        tx.token_id = self._create_token()

        with self.assertRaises(UserError) as cm:
            tx._send_payment_request()
        self.assertIn("PagarMe API error (400)", str(cm.exception))

    def test_orders_api_data_preparation(self):
        """Test ORDERS API data preparation methods."""
        # Configure provider for API testing
        self.provider.pagarme_secret_key = "sk_test_123456789"  # Add test secret key
        tx = self._create_transaction("direct")
        tx.token_id = self._create_token()

        # Test order data preparation
        order_data = tx._prepare_pagarme_order_data()

        self.assertEqual(order_data["code"], tx.reference)
        self.assertEqual(order_data["amount"], int(tx.amount * 100))
        self.assertEqual(order_data["currency"], tx.currency_id.name)
        self.assertIn("customer", order_data)
        self.assertIn("items", order_data)
        self.assertIn("payments", order_data)
        self.assertIn("metadata", order_data)

        # Test customer data
        customer_data = tx._prepare_customer_data()
        self.assertEqual(customer_data["name"], tx.partner_id.name)
        self.assertEqual(customer_data["email"], tx.partner_id.email)

        # Test order items
        items = tx._prepare_order_items()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["amount"], int(tx.amount * 100))

    def test_orders_api_customer_data_with_vat(self):
        """Test customer data preparation with CPF/CNPJ."""
        # Test with CPF (11 digits)
        self.partner.vat = "123.456.789-00"
        tx = self._create_transaction("direct")
        customer_data = tx._prepare_customer_data()

        self.assertEqual(customer_data["type"], "individual")
        self.assertEqual(customer_data["document"], "12345678900")
        self.assertEqual(customer_data["document_type"], "CPF")

        # Test with CNPJ (14 digits)
        self.partner.vat = "12.345.678/0001-90"
        customer_data = tx._prepare_customer_data()

        self.assertEqual(customer_data["type"], "company")
        self.assertEqual(customer_data["document"], "12345678000190")
        self.assertEqual(customer_data["document_type"], "CNPJ")
