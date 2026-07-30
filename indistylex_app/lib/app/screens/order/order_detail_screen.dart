import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';

import '../../theme/app_theme.dart';
import '../../providers/order_provider.dart';
import '../../models/order.dart';
import '../../constants/app_constants.dart';

class OrderDetailScreen extends StatefulWidget {
  final int orderId;

  const OrderDetailScreen({super.key, required this.orderId});

  @override
  State<OrderDetailScreen> createState() => _OrderDetailScreenState();
}

class _OrderDetailScreenState extends State<OrderDetailScreen> {
  Order? _order;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadOrder();
  }

  Future<void> _loadOrder() async {
    final order = await context
        .read<OrderProvider>()
        .fetchOrderDetail(widget.orderId);
    if (mounted) {
      setState(() {
        _order = order;
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(
            child: CircularProgressIndicator(color: AppColors.accent)),
      );
    }

    if (_order == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Order not found')),
      );
    }

    final order = _order!;

    return Scaffold(
      appBar: AppBar(title: Text('Order #${order.orderNumber}')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status timeline
            _buildStatusTimeline(order),
            const SizedBox(height: 24),

            // Items
            const Text('Items',
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 12),
            ...order.items.map((item) => _buildItemRow(item)),
            const SizedBox(height: 24),

            // Shipping address
            const Text('Shipping Address',
                style: TextStyle(
                    fontSize: 16, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Text(order.shippingAddress,
                style: const TextStyle(color: AppColors.muted)),
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
                      '${AppConstants.currency}${order.subtotal.toStringAsFixed(0)}'),
                  if (order.discount > 0)
                    _row('Discount',
                        '-${AppConstants.currency}${order.discount.toStringAsFixed(0)}'),
                  _row('Shipping',
                      order.shipping == 0 ? 'Free' : '${AppConstants.currency}${order.shipping.toStringAsFixed(0)}'),
                  const Divider(height: 24),
                  _row('Total',
                      '${AppConstants.currency}${order.total.toStringAsFixed(0)}',
                      bold: true),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Order info
            Text(
              'Placed on ${DateFormat('dd MMMM yyyy').format(order.createdAt)}',
              style: const TextStyle(color: AppColors.muted, fontSize: 13),
            ),
            if (order.paymentId != null)
              Text(
                'Payment ID: ${order.paymentId}',
                style: const TextStyle(color: AppColors.muted, fontSize: 13),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusTimeline(Order order) {
    final statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered'];
    final currentIndex = statuses.indexOf(order.status);

    return Column(
      children: List.generate(statuses.length, (index) {
        final isActive = index <= currentIndex;
        final isCurrent = index == currentIndex;
        return Row(
          children: [
            Column(
              children: [
                Container(
                  width: 24,
                  height: 24,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: isActive ? AppColors.accent : AppColors.lightGrey,
                  ),
                  child: isActive
                      ? const Icon(Icons.check, size: 14, color: AppColors.primary)
                      : null,
                ),
                if (index < statuses.length - 1)
                  Container(
                    width: 2,
                    height: 30,
                    color: isActive ? AppColors.accent : AppColors.lightGrey,
                  ),
              ],
            ),
            const SizedBox(width: 12),
            Text(
              statuses[index][0].toUpperCase() + statuses[index].substring(1),
              style: TextStyle(
                fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                color: isActive ? AppColors.primary : AppColors.muted,
              ),
            ),
          ],
        );
      }),
    );
  }

  Widget _buildItemRow(OrderItem item) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.productName,
                    style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(
                  'Qty: ${item.quantity}${item.size != null ? " | ${item.size}" : ""}',
                  style: const TextStyle(
                      color: AppColors.muted, fontSize: 12),
                ),
              ],
            ),
          ),
          Text('${AppConstants.currency}${item.total.toStringAsFixed(0)}',
              style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
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
