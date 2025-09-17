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

      // Collect enhanced form data with null safety
      let cardHolderName = "";
      let cardholderDocument = "";
      let cardExpiry = "";
      let cardCvv = "";

      try {
        const cardHolderElement = document.getElementById("card_holder_name");
        if (cardHolderElement) cardHolderName = cardHolderElement.value;

        const cardDocumentElement = document.getElementById("cardholder_document");
        if (cardDocumentElement) cardholderDocument = cardDocumentElement.value;

        const cardExpiryElement = document.getElementById("card_expiry");
        if (cardExpiryElement) cardExpiry = cardExpiryElement.value;

        const cardCvvElement = document.getElementById("card_cvv");
        if (cardCvvElement) cardCvv = cardCvvElement.value;
      } catch (error) {
        // Silently continue if elements are not found
      }

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

      // Populate card holder name from partner data with a delay to ensure DOM is ready
      setTimeout(() => {
        this._populateCardHolderName();
      }, 100);

      return Promise.resolve();
    },

    /**
     * Populate the card holder name field with partner name if available.
     *
     * @private
     */
    _populateCardHolderName: function () {
      console.log("PagarMe: _populateCardHolderName called");

      // Try multiple ways to find partner_id
      let partnerIdElement = document.getElementById("partner_id");
      if (!partnerIdElement) {
        partnerIdElement = document.querySelector("input[name=partner_id]");
      }
      if (!partnerIdElement) {
        partnerIdElement = document.querySelector("[name=partner_id]");
      }

      console.log("PagarMe: partnerIdElement found:", partnerIdElement);

      if (!partnerIdElement || !partnerIdElement.value) {
        console.log("PagarMe: No partner_id found for card holder name");

        // Try to get partner info from global variables or page context
        if (window.odoo && window.odoo.payment && window.odoo.payment.partner_id) {
          this._fetchAndSetPartnerName(window.odoo.payment.partner_id);
          return;
        }

        return;
      }

      const partnerId = partnerIdElement.value;
      console.log("PagarMe: Found partner_id:", partnerId);
      this._fetchAndSetPartnerName(partnerId);
    },

    /**
     * Fetch partner name and set it in the card holder field.
     *
     * @private
     * @param {string|number} partnerId - The partner ID
     */
    _fetchAndSetPartnerName: function (partnerId) {
      // Use RPC to get partner name
      this._rpc({
        model: "res.partner",
        method: "read",
        args: [[parseInt(partnerId)], ["name"]],
      })
        .then((result) => {
          console.log("PagarMe: RPC result:", result);
          if (result && result.length > 0 && result[0].name) {
            const cardHolderElement = document.getElementById("card_holder_name");
            console.log("PagarMe: cardHolderElement found:", cardHolderElement);
            if (cardHolderElement) {
              cardHolderElement.value = result[0].name;
              // Also trigger input event to ensure any listeners are notified
              cardHolderElement.dispatchEvent(new Event("input", {bubbles: true}));
              console.log("PagarMe: Set card holder name to:", result[0].name);
            }
          }
        })
        .catch((error) => {
          console.warn("PagarMe: Failed to fetch partner name:", error);
        });
    },
  };
  checkoutForm.include(paymentPagarmeMixin);
  manageForm.include(paymentPagarmeMixin);
});
