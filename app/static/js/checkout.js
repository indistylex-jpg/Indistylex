/* ============================================
   Indistylex — Checkout / Payment JS
   Razorpay integration helpers
   ============================================ */

document.addEventListener('DOMContentLoaded', function () {

  var payBtn = document.getElementById('payNowBtn');
  if (!payBtn) return;

  payBtn.addEventListener('click', function () {
    var orderId = payBtn.dataset.orderId;
    var amount  = payBtn.dataset.amount;
    var key     = payBtn.dataset.key;
    var name    = payBtn.dataset.customerName || '';
    var email   = payBtn.dataset.customerEmail || '';
    var phone   = payBtn.dataset.customerPhone || '';

    if (!orderId || !amount || !key) {
      alert('Payment configuration error. Please try again.');
      return;
    }

    var options = {
      key: key,
      amount: amount,
      currency: 'INR',
      name: 'Indistylex',
      description: 'Order Payment',
      order_id: orderId,
      prefill: { name: name, email: email, contact: phone },
      theme: { color: '#1A56DB' },
      handler: function (response) {
        /* Submit verification form */
        var form = document.getElementById('paymentVerifyForm');
        if (!form) return;
        document.getElementById('razorpay_payment_id').value = response.razorpay_payment_id;
        document.getElementById('razorpay_order_id').value   = response.razorpay_order_id;
        document.getElementById('razorpay_signature').value  = response.razorpay_signature;
        form.submit();
      },
      modal: {
        ondismiss: function () {
          showToast('Payment cancelled. You can try again.', 'warning');
        }
      }
    };

    var rzp = new Razorpay(options);
    rzp.on('payment.failed', function (response) {
      showToast('Payment failed: ' + (response.error.description || 'Unknown error'), 'danger');
    });
    rzp.open();
  });

  /* --- Shipping form validation --- */
  var shippingForm = document.getElementById('shippingForm');
  if (shippingForm) {
    shippingForm.addEventListener('submit', function (e) {
      if (!shippingForm.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      shippingForm.classList.add('was-validated');
    });
  }

});
