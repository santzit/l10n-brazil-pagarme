# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import logging

import requests

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    capture_manually = fields.Boolean(related="provider_id.capture_manually")

    # === ACTION METHODS ===#

    # === BUSINESS METHODS ===#

    def _send_payment_request(self):
        """Override of payment to send payment request to PagarMe ORDERS API.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_payment_request()
        if self.provider_code != "pagarme":
            return

        if not self.token_id:
            raise UserError(_("Pagarme: The transaction is not linked to a token."))

        # Always use PagarMe ORDERS API for real payment processing
        self._send_payment_request_to_pagarme_api()

    def _send_refund_request(self, **kwargs):
        """Override of payment to send refund request to PagarMe API.

        Note: self.ensure_one()

        :param dict kwargs: The keyword arguments.
        :return: The refund transaction created to process the refund request.
        :rtype: recordset of `payment.transaction`
        """
        refund_tx = super()._send_refund_request(**kwargs)
        if self.provider_code != "pagarme":
            return refund_tx

        # Send real refund request to PagarMe API
        try:
            self._send_pagarme_refund_request(refund_tx)
        except Exception as e:
            _logger.error("PagarMe refund request failed: %s", str(e))
            refund_tx._set_error(_("Refund failed: %(error)s") % {"error": str(e)})

        return refund_tx

    def _send_payment_request_to_pagarme_api(self):
        """Send payment request to PagarMe ORDERS API.

        Note: self.ensure_one()

        :return: None
        :raise: UserError if the API request fails
        """
        self.ensure_one()

        if not self.provider_id.pagarme_secret_key:
            raise UserError(_("PagarMe secret key is not configured."))

        # Prepare the order data for PagarMe API
        order_data = self._prepare_pagarme_order_data()

        try:
            # Make the API request to create an order
            response = self._make_pagarme_api_request(order_data)

            # Process the API response
            self._process_pagarme_api_response(response)

        except requests.exceptions.RequestException as e:
            _logger.error("PagarMe API request failed: %s", str(e))
            raise UserError(
                _("Payment processing failed: %(error)s") % {"error": str(e)}
            ) from e

    def _prepare_pagarme_order_data(self):
        """Prepare order data for PagarMe ORDERS API.

        :return: Dictionary containing order data for API
        :rtype: dict
        """
        # Basic order structure following PagarMe ORDERS API format
        order_data = {
            "code": self.reference,
            "amount": int(self.amount * 100),  # Convert to cents
            "currency": self.currency_id.name,
            "customer": self._prepare_customer_data(),
            "items": self._prepare_order_items(),
            "payments": self._prepare_payment_data(),
            "metadata": {
                "odoo_transaction_id": str(self.id),
                "odoo_reference": self.reference,
                "provider_id": str(self.provider_id.id),
            },
        }

        # Add shipping info if available
        if self.partner_id:
            shipping_data = self._prepare_shipping_data()
            if shipping_data:
                order_data["shipping"] = shipping_data

        return order_data

    def _prepare_customer_data(self):
        """Prepare customer data for PagarMe API.

        :return: Dictionary containing customer data
        :rtype: dict
        """
        partner = self.partner_id
        customer_data = {
            "name": partner.name or "",
            "email": partner.email or "",
            "type": "individual",  # Default to individual
        }

        # Add phone if available
        if partner.phone:
            customer_data["phones"] = {"mobile_phone": partner.phone}
        elif partner.mobile:
            customer_data["phones"] = {"mobile_phone": partner.mobile}

        # Add document if available (CPF/CNPJ for Brazilian customers)
        if hasattr(partner, "vat") and partner.vat:
            # Determine if it's CPF (individual) or CNPJ (company)
            document_number = (
                partner.vat.replace(".", "").replace("-", "").replace("/", "")
            )
            if len(document_number) == 11:
                customer_data["type"] = "individual"
                customer_data["document"] = document_number
                customer_data["document_type"] = "CPF"
            elif len(document_number) == 14:
                customer_data["type"] = "company"
                customer_data["document"] = document_number
                customer_data["document_type"] = "CNPJ"

        # Add address if available
        if partner.street:
            customer_data["address"] = {
                "line_1": partner.street or "",
                "line_2": partner.street2 or "",
                "zip_code": partner.zip or "",
                "city": partner.city or "",
                "state": partner.state_id.code if partner.state_id else "",
                "country": partner.country_id.code if partner.country_id else "BR",
            }

        return customer_data

    def _prepare_order_items(self):
        """Prepare order items for PagarMe API.

        :return: List of order items
        :rtype: list
        """
        # For payment transactions, create a generic item representing the payment
        return [
            {
                "code": f"payment-{self.id}",
                "description": f"Payment transaction {self.reference}",
                "amount": int(self.amount * 100),  # Convert to cents
                "quantity": 1,
                "category": "payment",
                "metadata": {
                    "transaction_id": str(self.id),
                    "reference": self.reference,
                },
            }
        ]

    def _prepare_payment_data(self):
        """Prepare payment data for PagarMe API.

        :return: List of payment methods
        :rtype: list
        """
        payment_data = []

        if self.token_id and getattr(self.token_id, "provider_ref", None):
            # Use existing token/card
            payment_data.append(
                {
                    "payment_method": "credit_card",
                    "amount": int(self.amount * 100),  # Convert to cents
                    "credit_card": {
                        "card_id": self.token_id.provider_ref,
                        "installments": 1,  # Default to single payment
                    },
                    "metadata": {
                        "token_id": str(self.token_id.id),
                        "payment_details": self.token_id.payment_details or "",
                    },
                }
            )
        elif self.token_id:
            # Token exists but no provider_ref - create a test payment method
            payment_data.append(
                {
                    "payment_method": "credit_card",
                    "amount": int(self.amount * 100),  # Convert to cents
                    "credit_card": {
                        "card_id": f"test_card_{self.token_id.id}",
                        "installments": 1,  # Default to single payment
                    },
                    "metadata": {
                        "token_id": str(self.token_id.id),
                        "payment_details": self.token_id.payment_details or "",
                        "test_mode": "true",
                    },
                }
            )
        else:
            # For new payments without existing token, we'll need card data
            # This should be handled by the frontend/tokenization process
            raise UserError(
                _(
                    "Payment token is required for PagarMe ORDERS API. "
                    "Please ensure proper tokenization is configured."
                )
            )

        return payment_data

    def _prepare_shipping_data(self):
        """Prepare shipping data for PagarMe API.

        :return: Dictionary containing shipping data or None
        :rtype: dict or None
        """
        partner = self.partner_id
        if not partner or not partner.street:
            return None

        return {
            "amount": 0,  # No shipping cost for payment transactions
            "description": "Standard shipping",
            "recipient_name": partner.name or "",
            "recipient_phone": partner.phone or partner.mobile or "",
            "address": {
                "line_1": partner.street or "",
                "line_2": partner.street2 or "",
                "zip_code": partner.zip or "",
                "city": partner.city or "",
                "state": partner.state_id.code if partner.state_id else "",
                "country": partner.country_id.code if partner.country_id else "BR",
            },
        }

    def _make_pagarme_api_request(self, order_data):
        """Make API request to PagarMe ORDERS endpoint.

        :param dict order_data: Order data to send to API
        :return: API response
        :rtype: requests.Response
        :raise: requests.exceptions.RequestException if request fails
        """
        url = "https://api.pagar.me/core/v5/orders"

        # Prepare authentication header
        auth_string = f"{self.provider_id.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        _logger.info(
            "PagarMe ORDERS API request: URL=%s, Order Code=%s, Amount=%s",
            url,
            order_data.get("code"),
            order_data.get("amount"),
        )

        response = requests.post(
            url, data=json.dumps(order_data), headers=headers, timeout=30
        )

        _logger.info(
            "PagarMe ORDERS API response: Status=%s, Order ID=%s",
            response.status_code,
            response.json().get("id") if response.status_code == 200 else "N/A",
        )

        # Check for API errors
        if response.status_code != 200:
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
                _("PagarMe API error (%(status)s): %(message)s")
                % {"status": response.status_code, "message": error_msg}
            )

        return response

    def _process_pagarme_api_response(self, response):
        """Process the response from PagarMe ORDERS API.

        :param requests.Response response: API response
        :return: None
        """
        try:
            response_data = response.json()
        except ValueError as e:
            _logger.error("Failed to parse PagarMe API response: %s", str(e))
            raise UserError(_("Invalid response from PagarMe API")) from e

        # Extract order information
        order_id = response_data.get("id")
        order_status = response_data.get("status")
        payments = response_data.get("charges", [])

        # Update transaction with PagarMe order information
        self.provider_reference = order_id

        # Process payment status
        if order_status == "paid":
            self._set_done()
            _logger.info(
                "PagarMe order %s completed successfully for transaction %s",
                order_id,
                self.reference,
            )
        elif order_status == "pending":
            self._set_pending()
            _logger.info(
                "PagarMe order %s is pending for transaction %s",
                order_id,
                self.reference,
            )
        elif order_status in ["failed", "canceled"]:
            self._set_error(
                _("PagarMe order %(order_id)s failed with status: %(status)s")
                % {"order_id": order_id, "status": order_status}
            )
            _logger.warning(
                "PagarMe order %s failed with status %s for transaction %s",
                order_id,
                order_status,
                self.reference,
            )
        else:
            # Handle other statuses as pending
            self._set_pending()
            _logger.info(
                "PagarMe order %s has status %s for transaction %s",
                order_id,
                order_status,
                self.reference,
            )

        # Process individual charges/payments
        for charge in payments:
            charge_id = charge.get("id")
            charge_status = charge.get("status")
            amount = charge.get("amount", 0) / 100  # Convert from cents

            _logger.info(
                "PagarMe charge %s has status %s with amount %s for transaction %s",
                charge_id,
                charge_status,
                amount,
                self.reference,
            )

            # Store charge information in metadata or logs for audit trail
            self.sudo().message_post(
                body=_(
                    "PagarMe charge %(charge_id)s: Status %(status)s, "
                    "Amount %(amount)s %(currency)s"
                )
                % {
                    "charge_id": charge_id,
                    "status": charge_status,
                    "amount": amount,
                    "currency": self.currency_id.name,
                }
            )

    def _send_pagarme_refund_request(self, refund_tx):
        """Send refund request to PagarMe API.

        :param refund_tx: The refund transaction
        :return: None
        """
        if not self.provider_reference:
            raise UserError(_("Cannot refund: No PagarMe order reference found."))

        url = f"https://api.pagar.me/core/v5/orders/{self.provider_reference}/refunds"
        
        # Prepare authentication header
        auth_string = f"{self.provider_id.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        refund_data = {
            "amount": int(refund_tx.amount * 100),  # Convert to cents
            "metadata": {
                "odoo_refund_transaction_id": str(refund_tx.id),
                "odoo_original_transaction_id": str(self.id),
                "refund_reason": "Customer request",
            },
        }

        _logger.info(
            "PagarMe refund request: Order=%s, Amount=%s",
            self.provider_reference,
            refund_data["amount"],
        )

        response = requests.post(
            url, data=json.dumps(refund_data), headers=headers, timeout=30
        )

        if response.status_code == 200:
            refund_tx._set_done()
            _logger.info("PagarMe refund successful for transaction %s", refund_tx.reference)
        else:
            error_msg = response.text
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except (ValueError, KeyError):
                pass
            raise UserError(
                _("PagarMe refund failed (%(status)s): %(message)s")
                % {"status": response.status_code, "message": error_msg}
            )

    def _send_pagarme_capture_request(self):
        """Send capture request to PagarMe API.

        :return: None
        """
        if not self.provider_reference:
            raise UserError(_("Cannot capture: No PagarMe order reference found."))

        url = f"https://api.pagar.me/core/v5/orders/{self.provider_reference}/charges"
        
        # Prepare authentication header
        auth_string = f"{self.provider_id.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Get charges for the order to capture them
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            charges = response.json().get("data", [])
            for charge in charges:
                if charge.get("status") == "pending":
                    charge_id = charge.get("id")
                    capture_url = f"https://api.pagar.me/core/v5/charges/{charge_id}/capture"
                    
                    capture_response = requests.post(
                        capture_url, 
                        data=json.dumps({"amount": charge.get("amount")}), 
                        headers=headers, 
                        timeout=30
                    )
                    
                    if capture_response.status_code == 200:
                        self._set_done()
                        _logger.info("PagarMe capture successful for transaction %s", self.reference)
                    else:
                        raise UserError(_("PagarMe capture failed"))
        else:
            raise UserError(_("Failed to get charges for capture"))

    def _send_pagarme_void_request(self):
        """Send void request to PagarMe API.

        :return: None
        """
        if not self.provider_reference:
            raise UserError(_("Cannot void: No PagarMe order reference found."))

        url = f"https://api.pagar.me/core/v5/orders/{self.provider_reference}"
        
        # Prepare authentication header
        auth_string = f"{self.provider_id.pagarme_secret_key}:"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Cancel the order
        cancel_data = {
            "status": "canceled",
            "metadata": {
                "void_reason": "Customer request",
                "odoo_transaction_id": str(self.id),
            },
        }

        response = requests.patch(
            url, data=json.dumps(cancel_data), headers=headers, timeout=30
        )

        if response.status_code == 200:
            self._set_canceled()
            _logger.info("PagarMe void successful for transaction %s", self.reference)
        else:
            error_msg = response.text
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except (ValueError, KeyError):
                pass
            raise UserError(
                _("PagarMe void failed (%(status)s): %(message)s")
                % {"status": response.status_code, "message": error_msg}
            )

    def _send_capture_request(self):
        """Override of payment to send capture request to PagarMe API.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_capture_request()
        if self.provider_code != "pagarme":
            return

        # Send real capture request to PagarMe API
        try:
            self._send_pagarme_capture_request()
        except Exception as e:
            _logger.error("PagarMe capture request failed: %s", str(e))
            self._set_error(_("Capture failed: %(error)s") % {"error": str(e)})

    def _send_void_request(self):
        """Override of payment to send void request to PagarMe API.

        Note: self.ensure_one()

        :return: None
        """
        super()._send_void_request()
        if self.provider_code != "pagarme":
            return

        # Send real void request to PagarMe API
        try:
            self._send_pagarme_void_request()
        except Exception as e:
            _logger.error("PagarMe void request failed: %s", str(e))
            self._set_error(_("Void failed: %(error)s") % {"error": str(e)})

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override of payment to find the transaction based on pagarme data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The pagarme notification data
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "pagarme" or len(tx) == 1:
            return tx

        reference = notification_data.get("reference")
        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "pagarme")]
        )
        if not tx:
            raise ValidationError(
                _("Pagarme: No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """Override of payment to process the transaction based on PagarMe webhook data.

        Note: self.ensure_one()

        :param dict notification_data: The PagarMe webhook notification data
        :return: None
        :raise: ValidationError if inconsistent data were received
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "pagarme":
            return

        # Extract order ID from webhook data
        order_id = notification_data.get("order_id") or notification_data.get("id")
        if order_id:
            self.provider_reference = order_id

        if self.tokenize:
            # Create a token from the payment data if tokenization is requested
            self._pagarme_tokenize_from_notification_data(notification_data)

        # Process the webhook status to determine transaction state
        status = notification_data.get("status", "").lower()
        
        if status == "pending":
            self._set_pending()
        elif status in ["paid", "authorized"]:
            if self.capture_manually and status == "authorized":
                self._set_authorized()
            else:
                self._set_done()
                # Immediately post-process the transaction if it is a refund, as the
                # post-processing will not be triggered by a customer browsing the
                # transaction from the portal.
                if self.operation == "refund":
                    self.env.ref("payment.cron_post_process_payment_tx")._trigger()
        elif status in ["canceled", "failed"]:
            self._set_canceled()
        elif status == "error":
            error_msg = notification_data.get("error_message", "Payment failed")
            self._set_error(_("PagarMe payment error: %s", error_msg))
        else:
            # Unknown status - log and set as error
            _logger.warning("Unknown PagarMe status received: %s", status)
            self._set_error(_("Unknown payment status received: %s", status))

    def _pagarme_tokenize_from_notification_data(self, notification_data):
        """Create a new token based on the notification data.

        Note: self.ensure_one()

        :param dict notification_data: The fake notification data to tokenize from.
        :return: None
        """
        self.ensure_one()

    def _pagarme_tokenize_from_notification_data(self, notification_data):
        """Create a new token based on the PagarMe webhook notification data.

        Note: self.ensure_one()

        :param dict notification_data: The PagarMe webhook notification data.
        :return: None
        """
        self.ensure_one()

        # Extract payment details from webhook
        payment_details = notification_data.get("payment_details", "Card ending in ****")
        card_id = notification_data.get("card_id")
        
        token = self.env["payment.token"].create(
            {
                "provider_id": self.provider_id.id,
                "payment_details": payment_details,
                "partner_id": self.partner_id.id,
                "provider_ref": card_id or f"token_{self.id}",
                "verified": True,
            }
        )
        self.write(
            {
                "token_id": token,
                "tokenize": False,
            }
        )
        _logger.info(
            "Created token with id %s for partner with id %s.",
            token.id,
            self.partner_id.id,
        )
