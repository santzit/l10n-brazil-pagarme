# Part of Odoo. See LICENSE file for full copyright and licensing details.

from unittest.mock import Mock, patch

from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from odoo.addons.l10n_br_payment_pagarme.tests.common import PaymentPagarmeCommon


@tagged("-at_install", "post_install")
class TestPaymentProvider(PaymentPagarmeCommon):
    def test_pagarme_secret_key_constraint_test_mode(self):
        """Test that secret key validation works for test mode."""
        self.provider.state = "test"

        # Valid test key should not raise error
        self.provider.pagarme_secret_key = "sk_test_valid_key"
        # No exception should be raised

        # Invalid test key should raise error
        with self.assertRaises(ValidationError):
            self.provider.pagarme_secret_key = "sk_invalid_key"

    def test_pagarme_secret_key_constraint_disabled_mode(self):
        """Test that secret key validation doesn't apply for disabled mode."""
        self.provider.state = "disabled"

        # Any key should be allowed in disabled mode
        self.provider.pagarme_secret_key = "any_key_format"
        # No exception should be raised

    def test_credentials_page_visibility(self):
        """Test that credentials page is shown for pagarme providers."""
        self.provider.code = "pagarme"
        self.provider._compute_view_configuration_fields()
        self.assertTrue(self.provider.show_credentials_page)

    def test_connection_test_without_secret_key(self):
        """Test connection test fails without secret key."""
        self.provider.pagarme_secret_key = False
        with self.assertRaises(UserError) as cm:
            self.provider.action_test_pagarme_connection()
        self.assertIn(
            "Please configure the PagarMe secret key first", str(cm.exception)
        )

    @patch("odoo.addons.l10n_br_payment_pagarme.models.payment_provider.requests.get")
    def test_connection_test_success(self, mock_get):
        """Test successful connection test."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"data": []}'
        mock_get.return_value = mock_response

        self.provider.pagarme_secret_key = "sk_test_valid_key"
        result = self.provider.action_test_pagarme_connection()

        # Verify the correct authentication format is used
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        headers = call_args[1]["headers"]

        # Check that authorization header uses correct format (secret_key:)
        import base64

        expected_auth = base64.b64encode(b"sk_test_valid_key:").decode()
        self.assertEqual(headers["authorization"], f"Basic {expected_auth}")

        # Check that the notification action is returned
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertIn("Successfully connected", result["params"]["message"])

    @patch("odoo.addons.l10n_br_payment_pagarme.models.payment_provider.requests.get")
    def test_connection_test_failure(self, mock_get):
        """Test failed connection test."""
        # Mock failed API response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response

        self.provider.pagarme_secret_key = "sk_test_invalid_key"

        with self.assertRaises(UserError) as cm:
            self.provider.action_test_pagarme_connection()
        self.assertIn("Connection failed with status 401", str(cm.exception))

    @patch("odoo.addons.l10n_br_payment_pagarme.models.payment_provider.requests.get")
    def test_connection_test_timeout(self, mock_get):
        """Test connection test timeout handling."""
        # Mock timeout exception
        import requests

        mock_get.side_effect = requests.exceptions.Timeout()

        self.provider.pagarme_secret_key = "sk_test_valid_key"

        with self.assertRaises(UserError) as cm:
            self.provider.action_test_pagarme_connection()
        self.assertIn("Connection timeout", str(cm.exception))

    @patch("odoo.addons.l10n_br_payment_pagarme.models.payment_provider.requests.get")
    def test_connection_test_request_exception(self, mock_get):
        """Test connection test request exception handling."""
        # Mock request exception
        import requests

        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        self.provider.pagarme_secret_key = "sk_test_valid_key"

        with self.assertRaises(UserError) as cm:
            self.provider.action_test_pagarme_connection()
        self.assertIn("Connection error", str(cm.exception))

    def test_get_inline_form_values_with_partner(self):
        """Test that inline form values include partner name."""
        # Create a partner with a name
        partner = self.env["res.partner"].create({"name": "João Silva"})

        # Prepare values with partner_id
        values = {"partner_id": partner.id}

        # Get inline form values
        result = self.provider._get_inline_form_values(values)

        # Verify partner_name is included
        self.assertIn("partner_name", result)
        self.assertEqual(result["partner_name"], "João Silva")

    def test_get_inline_form_values_without_partner(self):
        """Test that inline form values handle missing partner gracefully."""
        # Prepare values without partner_id
        values = {}

        # Get inline form values
        result = self.provider._get_inline_form_values(values)

        # Verify partner_name is not set or empty
        self.assertNotIn("partner_name", result)

    def test_get_inline_form_values_non_pagarme_provider(self):
        """Test that non-pagarme providers don't get partner_name."""
        # Create a different provider
        other_provider = self._prepare_provider(code="other")
        partner = self.env["res.partner"].create({"name": "Test Partner"})
        values = {"partner_id": partner.id}

        # Get inline form values for non-pagarme provider
        result = other_provider._get_inline_form_values(values)

        # Verify partner_name is not added by pagarme logic
        self.assertNotIn("partner_name", result)
