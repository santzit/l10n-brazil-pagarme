odoo.define("l10n_br_payment_pagarme.payment_form", (require) => {
  "use strict";

  const checkoutForm = require("payment.checkout_form");
  const manageForm = require("payment.manage_form");

  const paymentPagarmeMixin = {
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Simulate a feedback from a payment provider and redirect the customer to the status page.
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the provider
     * @param {number} providerId - The id of the provider handling the transaction
     * @param {object} processingValues - The processing values of the transaction
     * @return {Promise}
     */
    _processDirectPayment: function (code, providerId, processingValues) {
      if (code !== "pagarme") {
        return this._super(...arguments);
      }

      const customerInput = document.getElementById("customer_input").value;
      const simulatedPaymentState = document.getElementById(
        "simulated_payment_state"
      ).value;

      // Collect enhanced form data with safety checks
      const cardHolderElement = document.getElementById("card_holder_name");
      const cardDocumentElement = document.getElementById("cardholder_document");
      const cardExpiryElement = document.getElementById("card_expiry");
      const cardCvvElement = document.getElementById("card_cvv");

      const cardHolderName = cardHolderElement ? cardHolderElement.value : "";
      const cardholderDocument = cardDocumentElement ? cardDocumentElement.value : "";
      const cardExpiry = cardExpiryElement ? cardExpiryElement.value : "";
      const cardCvv = cardCvvElement ? cardCvvElement.value : "";

      return this._rpc({
        route: "/payment/pagarme/simulate_payment",
        params: {
          reference: processingValues.reference,
          payment_details: customerInput,
          card_holder_name: cardHolderName,
          cardholder_document: cardholderDocument,
          card_expiry: cardExpiry,
          card_cvv: cardCvv,
          simulated_state: simulatedPaymentState,
        },
      }).then(() => {
        window.location = "/payment/status";
      });
    },

    /**
     * Prepare the inline form of Pagarme for direct payment.
     *
     * @override method from payment.payment_form_mixin
     * @private
     * @param {string} code - The code of the selected payment option's provider
     * @param {integer} paymentOptionId - The id of the selected payment option
     * @param {string} flow - The online payment flow of the selected payment option
     * @return {Promise}
     */
    _prepareInlineForm: function (code, paymentOptionId, flow) {
      if (code !== "pagarme") {
        return this._super(...arguments);
      } else if (flow === "token") {
        return Promise.resolve();
      }
      this._setPaymentFlow("direct");
      return Promise.resolve();
    },
  };
  checkoutForm.include(paymentPagarmeMixin);
  manageForm.include(paymentPagarmeMixin);
});
