# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

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
            url = "https://api.pagar.me/core/v5/customers?size=2"

            # PagarMe API expects Basic auth with secret_key: (key with colon)
            # Encode "secret_key:" to base64 for Basic authentication
            auth_string = f"{self.pagarme_secret_key}:"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()

            headers = {
                "authorization": f"Basic {encoded_auth}",
                "Content-Type": "application/json",
            }

            _logger.info("Testing PagarMe connection to URL: %s", url)
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

            if response.status_code == 200:
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "title": _("Connection Test"),
                        "message": _("Successfully connected to PagarMe API!"),
                        "type": "success",
                    },
                }
            else:
                raise UserError(
                    _("Connection failed with status %(status)s: %(text)s")
                    % {"status": response.status_code, "text": response.text}
                ) from None
        except requests.exceptions.Timeout:
            raise UserError(
                _("Connection timeout. Please check your internet connection.")
            ) from None
        except requests.exceptions.RequestException as e:
            _logger.error("PagarMe connection error: %s", str(e))
            raise UserError(_("Connection error: %(error)s") % {"error": str(e)}) from e
