import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../theme/app_theme.dart';
import '../../providers/cart_provider.dart';
import '../../models/cart.dart';
import '../../constants/api_constants.dart';
import '../../constants/app_constants.dart';

class CartScreen extends StatefulWidget {
  const CartScreen({super.key});

  @override
  State<CartScreen> createState() => _CartScreenState();
}

class _CartScreenState extends State<CartScreen> {
  final _couponController = TextEditingController();

  @override
  void initState() {
    super.initState();
    context.read<CartProvider>().fetchCart();
  }

  @override
  void dispose() {
    _couponController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Shopping Cart')),
      body: Consumer<CartProvider>(
        builder: (context, cartProvider, _) {
          if (cartProvider.isLoading && cartProvider.cart.items.isEmpty) {
            return const Center(
                child: CircularProgressIndicator(color: AppColors.accent));
          }

          if (cartProvider.cart.items.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.shopping_bag_outlined,
                      size: 80, color: AppColors.lightGrey),
                  const SizedBox(height: 16),
                  const Text('Your cart is empty',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  const Text('Add items to start shopping',
                      style: TextStyle(color: AppColors.muted)),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () => Navigator.pushNamed(context, '/shop'),
                    child: const Text('Start Shopping'),
                  ),
                ],
              ),
            );
          }

          final cart = cartProvider.cart;

          return Column(
            children: [
              // Cart items
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: cart.items.length,
                  itemBuilder: (_, index) =>
                      _buildCartItem(cart.items[index], cartProvider),
                ),
              ),

              // Order summary
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Coupon
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _couponController,
                            decoration: const InputDecoration(
                              hintText: 'Coupon code',
                              isDense: true,
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        OutlinedButton(
                          onPressed: () {
                            if (_couponController.text.isNotEmpty) {
                              cartProvider.applyCoupon(_couponController.text);
                            }
                          },
                          child: const Text('Apply'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),

                    // Summary
                    _buildSummaryRow('Subtotal', cart.subtotal),
                    if (cart.discount > 0)
                      _buildSummaryRow('Discount', -cart.discount,
                          isDiscount: true),
                    _buildSummaryRow('Shipping',
                        cart.shipping == 0 ? null : cart.shipping,
                        freeText: 'Free'),
                    const Divider(height: 24),
                    _buildSummaryRow('Total', cart.total, isBold: true),
                    const SizedBox(height: 16),

                    SizedBox(
                      width: double.infinity,
                      height: 50,
                      child: ElevatedButton(
                        onPressed: () =>
                            Navigator.pushNamed(context, '/checkout'),
                        child: Text(
                            'Checkout (${AppConstants.currency}${cart.total.toStringAsFixed(0)})'),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  Widget _buildCartItem(CartItem item, CartProvider cartProvider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            // Image
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: item.product.image != null
                  ? CachedNetworkImage(
                      imageUrl:
                          ApiConstants.productImage(item.product.image!),
                      width: 80,
                      height: 80,
                      fit: BoxFit.cover,
                    )
                  : Container(
                      width: 80,
                      height: 80,
                      color: AppColors.lightGrey,
                      child: const Icon(Icons.image, color: AppColors.muted),
                    ),
            ),
            const SizedBox(width: 12),

            // Details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    item.product.name,
                    style: const TextStyle(fontWeight: FontWeight.w600),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 4),
                  if (item.size != null || item.color != null)
                    Text(
                      [if (item.size != null) 'Size: ${item.size}',
                       if (item.color != null) 'Color: ${item.color}']
                          .join(' | '),
                      style: const TextStyle(
                          fontSize: 12, color: AppColors.muted),
                    ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Text(
                        '${AppConstants.currency}${item.product.displayPrice.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                      const Spacer(),
                      // Quantity controls
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: AppColors.lightGrey),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            InkWell(
                              onTap: item.quantity > 1
                                  ? () => cartProvider.updateQuantity(
                                      item.id, item.quantity - 1)
                                  : null,
                              child: const Padding(
                                padding: EdgeInsets.all(6),
                                child: Icon(Icons.remove, size: 16),
                              ),
                            ),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 8),
                              child: Text('${item.quantity}',
                                  style: const TextStyle(
                                      fontWeight: FontWeight.w600)),
                            ),
                            InkWell(
                              onTap: () => cartProvider.updateQuantity(
                                  item.id, item.quantity + 1),
                              child: const Padding(
                                padding: EdgeInsets.all(6),
                                child: Icon(Icons.add, size: 16),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            // Delete
            IconButton(
              icon: const Icon(Icons.delete_outline,
                  color: AppColors.error, size: 20),
              onPressed: () => cartProvider.removeItem(item.id),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryRow(String label, double? amount,
      {bool isBold = false, bool isDiscount = false, String? freeText}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label,
              style: TextStyle(
                fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
                fontSize: isBold ? 16 : 14,
              )),
          Text(
            amount == null
                ? (freeText ?? '-')
                : '${isDiscount ? "-" : ""}${AppConstants.currency}${amount.abs().toStringAsFixed(0)}',
            style: TextStyle(
              fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
              fontSize: isBold ? 16 : 14,
              color: isDiscount ? AppColors.success : null,
            ),
          ),
        ],
      ),
    );
  }
}
