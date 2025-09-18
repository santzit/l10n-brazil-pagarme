# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging
import time

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentProvider(models.Model):
    _inherit = "payment.provider"

    code = fields.Selection(
        selection_add=[("pagarme", "Pagarme")], ondelete={"pagarme": "set default"}
    )
    pagarme_public_key = fields.Char(
        string="PagarMe Public Key",
        help="The public key provided by PagarMe",
        groups="base.group_system",
    )
    pagarme_secret_key = fields.Char(
        string="PagarMe Secret Key",
        help="The secret key provided by PagarMe",
        groups="base.group_system",
    )
    pagarme_use_orders_api = fields.Boolean(
        string="Use ORDERS API",
        default=True,
        help="Enable PagarMe ORDERS API integration for real payment processing. "
        "When disabled, uses simulation mode for testing.",
        groups="base.group_system",
    )

    # === COMPUTE METHODS ===#

    @api.depends("code")
    def _compute_view_configuration_fields(self):
        """Override of payment to show the credentials page for pagarme.

        :return: None
        """
        super()._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == "pagarme").show_credentials_page = True
        return

    def _compute_feature_support_fields(self):
        """Override of `payment` to enable additional features."""
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == "pagarme").update(
            {
                "support_fees": True,
                "support_manual_capture": True,
                "support_refund": "partial",
                "support_tokenization": True,
            }
        )
        return

    # === BUSINESS METHODS ===#

    def _get_processing_values(self, processing_values):
        """Override to add partner name to processing values.

        :param dict processing_values: The processing values of the transaction.
        :return: The updated processing values.
        :rtype: dict
        """
        res = super()._get_processing_values(processing_values)
        if self.code == "pagarme":
            # Try to get partner information from transaction
            tx_sudo = (
                self.env["payment.transaction"]
                .sudo()
                .search(
                    [
                        ("reference", "=", processing_values.get("reference")),
                        ("provider_id", "=", self.id),
                    ],
                    limit=1,
                )
            )

            if tx_sudo and tx_sudo.partner_id:
                res["partner_name"] = tx_sudo.partner_id.name or ""
                _logger.info(
                    "PagarMe: Added partner_name to processing_values: %s",
                    tx_sudo.partner_id.name,
                )
            else:
                _logger.info(
                    "PagarMe: No transaction or partner found for processing_values"
                )

        return res

    # Note: Partner name population is also handled by JavaScript in _prepareInlineForm
    # This ensures the name is available both server-side and client-side

    # === CONSTRAINT METHODS ===#

    @api.constrains("pagarme_secret_key", "state")
    def _check_pagarme_secret_key_format(self):
        """Validate PagarMe secret key format based on provider state."""
        for provider in self.filtered(
            lambda p: p.code == "pagarme" and p.pagarme_secret_key
        ):
            if provider.state == "test" and not provider.pagarme_secret_key.startswith(
                "sk_test_"
            ):
                raise ValidationError(
                    _("In test mode, PagarMe secret key must start with 'sk_test_'.")
                )

    @api.constrains("state", "code")
    def _check_provider_state(self):
        if self.filtered(
            lambda p: p.code == "pagarme" and p.state not in ("test", "disabled")
        ):
            raise UserError(_("Pagarme providers should never be enabled."))

    # === ACTION METHODS ===#

    def action_test_pagarme_connection(self):
        """Test connection to PagarMe API using the secret key."""
        self.ensure_one()
        if not self.pagarme_secret_key:
            raise UserError(_("Please configure the PagarMe secret key first."))

        try:
            # Test different endpoints based on configuration
            if self.pagarme_use_orders_api:
                # Test ORDERS API capabilities
                self._test_orders_api_connection()
            else:
                # Test basic API connection
                self._test_basic_api_connection()

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Connection Test"),
                    "message": _("Successfully connected to PagarMe API!"),
                    "type": "success",
                },
            }

        except requests.exceptions.Timeout:
            raise UserError(
                _("Connection timeout. Please check your internet connection.")
            ) from None
        except requests.exceptions.RequestException as e:
            _logger.error("PagarMe connection error: %s", str(e))
            raise UserError(_("Connection error: %(error)s") % {"error": str(e)}) from e

    def _test_basic_api_connection(self):
        """Test basic API connection using customers endpoint.

        :raise: UserError if connection fails
        """
        url = "https://api.pagar.me/core/v5/customers?size=2"

        # PagarMe API expects Basic auth with secret_key: (key with colon)
        # Encode "secret_key:" to base64 for Basic authentication
        auth_string = f"{self.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
        }

        _logger.info("Testing PagarMe basic connection to URL: %s", url)
        _logger.info(
            "Using secret key prefix: %s",
            self.pagarme_secret_key[:10] + "...",
        )
        _logger.info("Authorization header: Basic %s", encoded_auth[:20] + "...")

        response = requests.get(url, headers=headers, timeout=10)

        _logger.info(
            "PagarMe API response: status=%s, content=%s",
            response.status_code,
            response.text[:200],
        )

        if response.status_code != 200:
            raise UserError(
                _("Connection failed with status %(status)s: %(text)s")
                % {"status": response.status_code, "text": response.text}
            ) from None

    def _test_orders_api_connection(self):
        """Test ORDERS API connection by creating a test order structure.

        :raise: UserError if connection fails
        """
        # Create a minimal test order structure to validate API capabilities
        test_order_data = {
            "code": f"test-{self.id}-{int(time.time())}",
            "amount": 100,  # R$ 1.00 in cents
            "currency": "BRL",
            "customer": {
                "name": "Test Customer",
                "email": "test@example.com",
                "type": "individual",
            },
            "items": [
                {
                    "code": "test-item",
                    "description": "Test connection item",
                    "amount": 100,
                    "quantity": 1,
                    "category": "test",
                }
            ],
            "metadata": {
                "test": "true",
                "provider_id": str(self.id),
                "connection_test": "true",
            },
        }

        url = "https://api.pagar.me/core/v5/orders"

        # Prepare authentication header
        auth_string = f"{self.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        _logger.info("Testing PagarMe ORDERS API connection to URL: %s", url)
        _logger.info(
            "Using secret key prefix: %s",
            self.pagarme_secret_key[:10] + "...",
        )

        # Note: This is a dry-run test without payment methods
        # We expect this to fail with a validation error, which confirms API connectivity
        response = requests.post(
            url, data=json.dumps(test_order_data), headers=headers, timeout=10
        )

        _logger.info(
            "PagarMe ORDERS API response: status=%s, content=%s",
            response.status_code,
            response.text[:200] if response.text else "No content",
        )

        # For ORDERS API test, we accept both 200 (success) and 422 (validation error)
        # A 422 error indicates the API is reachable and processing requests
        if response.status_code not in [200, 422]:
            error_msg = "Unknown error"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
                elif "errors" in error_data:
                    error_msg = "; ".join([str(err) for err in error_data["errors"]])
            except (ValueError, KeyError):
                error_msg = response.text

            raise UserError(
                _("ORDERS API connection failed with status %(status)s: %(message)s")
                % {"status": response.status_code, "message": error_msg}
            ) from None

        # Log successful connection
        if response.status_code == 200:
            _logger.info("ORDERS API test successful - order structure accepted")
        else:  # 422
            _logger.info(
                "ORDERS API test successful - API reachable (validation error expected without payment method)"
            )
