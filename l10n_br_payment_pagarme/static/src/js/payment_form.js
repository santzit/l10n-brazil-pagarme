odoo.define("l10n_br_payment_pagarme.payment_form", (require) => {
  "use strict";

  const checkoutForm = require("payment.checkout_form");
  const manageForm = require("payment.manage_form");

  const paymentPagarmeMixin = {
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Format card number with spaces for better readability
     * @private
     * @param {string} value - The card number
     * @return {string} Formatted card number
     */
    _formatCardNumber: function (value) {
      const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
      const matches = v.match(/\d{4,16}/g);
      const match = (matches && matches[0]) || "";
      const parts = [];
      for (let i = 0, len = match.length; i < len; i += 4) {
        parts.push(match.substring(i, i + 4));
      }
      if (parts.length) {
        return parts.join(" ");
      } else {
        return v;
      }
    },

    /**
     * Format expiry date as MM/AA
     * @private
     * @param {string} value - The expiry date
     * @return {string} Formatted expiry date
     */
    _formatExpiryDate: function (value) {
      const v = value.replace(/\s+/g, "").replace(/[^0-9]/gi, "");
      if (v.length >= 2) {
        return v.substring(0, 2) + "/" + v.substring(2, 4);
      }
      return v;
    },

    /**
     * Format CVV to numeric only
     * @private
     * @param {string} value - The CVV
     * @return {string} Formatted CVV
     */
    _formatCVV: function (value) {
      return value.replace(/[^0-9]/gi, "");
    },

    /**
     * Populate partner data in the form fields
     * @private
     */
    _populatePartnerData: function () {
      const partnerIdInput = document.getElementById("partner_id");
      if (!partnerIdInput || !partnerIdInput.value) {
        return;
      }

      const partnerId = partnerIdInput.value;

      // Fetch partner data and populate the form
      this._rpc({
        model: "res.partner",
        method: "read",
        args: [parseInt(partnerId), ["name", "vat"]],
      })
        .then((partnerData) => {
          if (partnerData && partnerData.length > 0) {
            const partner = partnerData[0];

            // Populate card holder name if empty
            const holderNameInput = document.getElementById("card_holder_name");
            if (holderNameInput && !holderNameInput.value && partner.name) {
              holderNameInput.value = partner.name;
            }

            // Populate CPF/CNPJ if empty
            const documentInput = document.getElementById("cardholder_document");
            if (documentInput && !documentInput.value && partner.vat) {
              documentInput.value = partner.vat;
            }
          }
        })
        .catch(() => {
          // Silently ignore errors - partner data is just a convenience
        });
    },
    _setupInputFormatting: function () {
      const cardNumberInput = document.getElementById("customer_input");
      const expiryInput = document.getElementById("card_expiry");
      const cvvInput = document.getElementById("card_cvv");

      if (cardNumberInput) {
        cardNumberInput.addEventListener("input", (e) => {
          e.target.value = this._formatCardNumber(e.target.value);
        });
      }

      if (expiryInput) {
        expiryInput.addEventListener("input", (e) => {
          e.target.value = this._formatExpiryDate(e.target.value);
        });
      }

      if (cvvInput) {
        cvvInput.addEventListener("input", (e) => {
          e.target.value = this._formatCVV(e.target.value);
        });
      }
    },

    /**
     * Validate payment form fields
     * @private
     * @return {boolean} True if valid, false otherwise
     */
    _validatePaymentForm: function () {
      const cardNumber = document
        .getElementById("customer_input")
        .value.replace(/\s/g, "");
      const holderName = document.getElementById("card_holder_name").value.trim();
      const expiryDate = document.getElementById("card_expiry").value;
      const cvv = document.getElementById("card_cvv").value;

      // Basic validation
      if (!cardNumber || cardNumber.length < 13) {
        alert("Please enter a valid card number");
        return false;
      }

      if (!holderName) {
        alert("Please enter the card holder name");
        return false;
      }

      if (!expiryDate || !expiryDate.match(/^\d{2}\/\d{2}$/)) {
        alert("Please enter a valid expiry date (MM/AA)");
        return false;
      }

      if (!cvv || cvv.length < 3) {
        alert("Please enter a valid CVV");
        return false;
      }

      return true;
    },

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

      // Validate form before processing
      if (!this._validatePaymentForm()) {
        return Promise.reject("Validation failed");
      }

      // Collect all form data
      const customerInput = document.getElementById("customer_input").value;
      const cardHolderName = document.getElementById("card_holder_name").value;
      const cardholderDocument = document.getElementById("cardholder_document").value;
      const cardExpiry = document.getElementById("card_expiry").value;
      const cardCvv = document.getElementById("card_cvv").value;
      const simulatedPaymentState = document.getElementById(
        "simulated_payment_state"
      ).value;

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

      // Set up input formatting and populate partner data after DOM is ready
      setTimeout(() => {
        this._setupInputFormatting();
        this._populatePartnerData();
      }, 100);

      return Promise.resolve();
    },
  };
  checkoutForm.include(paymentPagarmeMixin);
  manageForm.include(paymentPagarmeMixin);
});
