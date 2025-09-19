# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.addons.payment.tests.common import PaymentCommon


class PaymentPagarmeCommon(PaymentCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.provider = cls._prepare_provider(code="pagarme")
        # Configure provider with test secret key for API testing
        cls.provider.pagarme_secret_key = "sk_test_12345678901234567890"

        cls.notification_data = {
            "reference": cls.reference,
            "payment_details": "1234",
            "order_id": "order_test_123",
            "status": "paid",
        }
