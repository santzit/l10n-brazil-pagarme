# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import patch

from odoo.tests import tagged

from odoo.addons.l10n_br_payment_pagarme.controllers.main import (
    PaymentPagarmeController,
)
from odoo.addons.l10n_br_payment_pagarme.tests.common import PaymentPagarmeCommon
from odoo.addons.payment.tests.http_common import PaymentHttpCommon


@tagged("-at_install", "post_install")
class TestProcessingFlows(PaymentPagarmeCommon, PaymentHttpCommon):
    def test_portal_payment_triggers_processing(self):
        """Test that paying from the frontend triggers the processing of the
        notification data."""
        self._create_transaction(flow="direct")
        url = self._build_url(PaymentPagarmeController._simulation_url)
        with patch(
            "odoo.addons.payment.models.payment_transaction.PaymentTransaction"
            "._handle_notification_data"
        ) as handle_notification_data_mock:
            self._make_json_rpc_request(url, data=self.notification_data)
        self.assertEqual(handle_notification_data_mock.call_count, 1)

    def test_payment_with_extended_card_data(self):
        """Test that payment processing works with extended card holder fields."""
        self._create_transaction(flow="direct")
        url = self._build_url(PaymentPagarmeController._simulation_url)

        # Extended notification data with new card fields
        extended_data = {
            "reference": self.reference,
            "payment_details": "4111 1111 1111 1111",
            "card_holder_name": "João Silva",
            "cardholder_document": "123.456.789-00",
            "card_expiry": "12/26",
            "card_cvv": "123",
            "simulated_state": "done",
        }

        with patch(
            "odoo.addons.payment.models.payment_transaction.PaymentTransaction"
            "._handle_notification_data"
        ) as handle_notification_data_mock:
            self._make_json_rpc_request(url, data=extended_data)

        # Verify the notification data was processed
        self.assertEqual(handle_notification_data_mock.call_count, 1)

        # Verify the extended data was passed to the handler
        args, kwargs = handle_notification_data_mock.call_args
        self.assertEqual(args[0], "pagarme")
        notification_data = args[1]
        self.assertEqual(notification_data["card_holder_name"], "João Silva")
        self.assertEqual(notification_data["cardholder_document"], "123.456.789-00")
        self.assertEqual(notification_data["card_expiry"], "12/26")
        self.assertEqual(notification_data["card_cvv"], "123")

    def test_tokenization_with_extended_card_data(self):
        """Test that tokenization works with extended card holder fields."""
        # Create a transaction that will be tokenized
        self._create_transaction(flow="direct", tokenize=True)

        extended_data = {
            "reference": self.reference,
            "payment_details": "4111 1111 1111 1111",
            "card_holder_name": "Maria Santos",
            "cardholder_document": "98.765.432/0001-10",
            "card_expiry": "06/25",
            "card_cvv": "456",
            "simulated_state": "done",
        }

        # Process the notification data directly
        transaction = self.env["payment.transaction"].search(
            [("reference", "=", self.reference)]
        )
        transaction._handle_notification_data("pagarme", extended_data)

        # Verify the transaction was tokenized
        self.assertTrue(transaction.token_id)

        # Verify the token contains the payment details
        token = transaction.token_id
        self.assertEqual(token.payment_details, "4111 1111 1111 1111")
        self.assertEqual(token.pagarme_simulated_state, "done")
