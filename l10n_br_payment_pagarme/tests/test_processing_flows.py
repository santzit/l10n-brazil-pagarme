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
