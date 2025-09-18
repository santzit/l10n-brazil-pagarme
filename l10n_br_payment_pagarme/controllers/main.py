# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class PaymentPagarmeController(http.Controller):
    _webhook_url = "/payment/pagarme/webhook"

    @http.route(_webhook_url, type="json", auth="public", csrf=False)
    def pagarme_webhook(self, **data):
        """Handle PagarMe webhook notifications.

        :param dict data: The webhook notification data from PagarMe.
        :return: Empty response to acknowledge receipt
        """
        _logger.info("PagarMe webhook received: %s", data)
        
        try:
            # Process the webhook data
            request.env["payment.transaction"].sudo()._handle_notification_data(
                "pagarme", data
            )
            return {}
        except Exception as e:
            _logger.error("Error processing PagarMe webhook: %s", str(e))
            return {"error": "Processing failed"}
