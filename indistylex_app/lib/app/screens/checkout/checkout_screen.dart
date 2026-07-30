import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../theme/app_theme.dart';
import '../../providers/cart_provider.dart';
import '../../providers/order_provider.dart';
import '../../providers/auth_provider.dart';
import '../../constants/app_constants.dart';
import '../../widgets/secure_screen.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  final _formKey = GlobalKey<FormState>();
  final _addressController = TextEditingController();
  final _cityController = TextEditingController();
  final _stateController = TextEditingController();
  final _pincodeController = TextEditingController();
  final _phoneController = TextEditingController();
  String _paymentMethod = 'online';

  @override
  void initState() {
    super.initState();
    _prefillAddress();
  }

  void _prefillAddress() {
    final user = context.read<AuthProvider>().user;
    if (user != null) {
      _addressController.text = user.address ?? '';
      _cityController.text = user.city ?? '';
      _stateController.text = user.state ?? '';
      _pincodeController.text = user.pincode ?? '';
      _phoneController.text = user.phone ?? '';
    }
  }

  @override
  void dispose() {
    _addressController.dispose();
    _cityController.dispose();
    _stateController.dispose();
    _pincodeController.dispose();
    _phoneController.dispose();
    super.dispose();
  }

  Future<void> _placeOrder() async {
    if (!_formKey.currentState!.validate()) return;

    final orderProvider = context.read<OrderProvider>();
    final result = await orderProvider.createOrder(
      address: _addressController.text.trim(),
      city: _cityController.text.trim(),
      state: _stateController.text.trim(),
      pincode: _pincodeController.text.trim(),
      phone: _phoneController.text.trim(),
      paymentMethod: _paymentMethod,
    );

    if (!mounted) return;

    if (result['success']) {
      if (_paymentMethod == 'online') {
        _initiatePayment(result['data']);
      } else {
        _orderSuccess();
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(result['message'] ?? 'Failed to place order'),
          backgroundColor: AppColors.error,
        ),
      );
    }
  }

  void _initiatePayment(Map<String, dynamic> orderData) {
    // Razorpay integration - would be implemented with actual keys
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Redirecting to payment...'),
        backgroundColor: AppColors.accent,
      ),
    );
    // In production: use razorpay_flutter to open payment gateway
    _orderSuccess();
  }

  void _orderSuccess() {
    context.read<CartProvider>().clear();
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.check_circle,
                color: AppColors.success, size: 64),
            const SizedBox(height: 16),
            const Text(
              'Order Placed!',
              style: TextStyle(
                  fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              'Your order has been placed successfully.',
              textAlign: TextAlign.center,
              style: TextStyle(color: AppColors.muted),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  Navigator.pushNamedAndRemoveUntil(
                      context, '/home', (route) => false);
                },
                child: const Text('Continue Shopping'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cart = context.watch<CartProvider>().cart;

    return SecureScreen(
      child: Scaffold(
      appBar: AppBar(title: const Text('Checkout')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Shipping Address',
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _addressController,
                maxLines: 2,
                decoration: const InputDecoration(labelText: 'Address'),
                validator: (v) =>
                    v?.isEmpty == true ? 'Required' : null,
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _cityController,
                      decoration:
                          const InputDecoration(labelText: 'City'),
                      validator: (v) =>
                          v?.isEmpty == true ? 'Required' : null,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _stateController,
                      decoration:
                          const InputDecoration(labelText: 'State'),
                      validator: (v) =>
                          v?.isEmpty == true ? 'Required' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _pincodeController,
                      keyboardType: TextInputType.number,
                      decoration:
                          const InputDecoration(labelText: 'Pincode'),
                      validator: (v) {
                        if (v?.isEmpty == true) return 'Required';
                        if (v!.length != 6) return 'Invalid pincode';
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextFormField(
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      decoration:
                          const InputDecoration(labelText: 'Phone'),
                      validator: (v) {
                        if (v?.isEmpty == true) return 'Required';
                        if (v!.length != 10) return 'Invalid phone';
                        return null;
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 32),

              // Payment method
              const Text(
                'Payment Method',
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w600),
              ),
              const SizedBox(height: 12),
              RadioListTile(
                value: 'online',
                groupValue: _paymentMethod,
                activeColor: AppColors.accent,
                title: const Text('Pay Online (UPI/Card/Net Banking)'),
                onChanged: (v) =>
                    setState(() => _paymentMethod = v!),
              ),
              RadioListTile(
                value: 'cod',
                groupValue: _paymentMethod,
                activeColor: AppColors.accent,
                title: const Text('Cash on Delivery'),
                onChanged: (v) =>
                    setState(() => _paymentMethod = v!),
              ),
              const SizedBox(height: 24),

              // Order summary
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.white,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.lightGrey),
                ),
                child: Column(
                  children: [
                    _row('Subtotal',
                        '${AppConstants.currency}${cart.subtotal.toStringAsFixed(0)}'),
                    if (cart.discount > 0)
                      _row('Discount',
                          '-${AppConstants.currency}${cart.discount.toStringAsFixed(0)}'),
                    _row('Shipping',
                        cart.shipping == 0 ? 'Free' : '${AppConstants.currency}${cart.shipping.toStringAsFixed(0)}'),
                    const Divider(height: 24),
                    _row(
                      'Total',
                      '${AppConstants.currency}${cart.total.toStringAsFixed(0)}',
                      bold: true,
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              Consumer<OrderProvider>(
                builder: (_, orderProvider, __) {
                  return SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: ElevatedButton(
                      onPressed:
                          orderProvider.isLoading ? null : _placeOrder,
                      child: orderProvider.isLoading
                          ? const CircularProgressIndicator(
                              color: AppColors.white, strokeWidth: 2)
                          : const Text('Place Order'),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    ),
    );
  }

  Widget _row(String label, String value, {bool bold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: TextStyle(
                  fontWeight: bold ? FontWeight.bold : FontWeight.normal)),
          Text(value,
              style: TextStyle(
                  fontWeight: bold ? FontWeight.bold : FontWeight.normal)),
        ],
      ),
    );
  }
}
