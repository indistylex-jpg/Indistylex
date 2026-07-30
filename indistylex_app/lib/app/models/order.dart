class Order {
  final int id;
  final String orderNumber;
  final String status;
  final double total;
  final double subtotal;
  final double discount;
  final double shipping;
  final String? couponCode;
  final String paymentMethod;
  final String? paymentId;
  final String shippingAddress;
  final String? trackingNumber;
  final List<OrderItem> items;
  final DateTime createdAt;
  final DateTime? updatedAt;

  Order({
    required this.id,
    required this.orderNumber,
    required this.status,
    required this.total,
    this.subtotal = 0,
    this.discount = 0,
    this.shipping = 0,
    this.couponCode,
    this.paymentMethod = 'online',
    this.paymentId,
    required this.shippingAddress,
    this.trackingNumber,
    this.items = const [],
    required this.createdAt,
    this.updatedAt,
  });

  String get statusLabel {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'confirmed':
        return 'Confirmed';
      case 'processing':
        return 'Processing';
      case 'shipped':
        return 'Shipped';
      case 'delivered':
        return 'Delivered';
      case 'cancelled':
        return 'Cancelled';
      default:
        return status;
    }
  }

  factory Order.fromJson(Map<String, dynamic> json) {
    return Order(
      id: json['id'] ?? 0,
      orderNumber: json['order_number'] ?? '',
      status: json['status'] ?? 'pending',
      total: (json['total'] ?? 0).toDouble(),
      subtotal: (json['subtotal'] ?? 0).toDouble(),
      discount: (json['discount'] ?? 0).toDouble(),
      shipping: (json['shipping'] ?? 0).toDouble(),
      couponCode: json['coupon_code'],
      paymentMethod: json['payment_method'] ?? 'online',
      paymentId: json['payment_id'],
      shippingAddress: json['shipping_address'] ?? '',
      trackingNumber: json['tracking_number'],
      items: (json['items'] as List? ?? [])
          .map((item) => OrderItem.fromJson(item))
          .toList(),
      createdAt: DateTime.parse(
          json['created_at'] ?? DateTime.now().toIso8601String()),
      updatedAt: json['updated_at'] != null
          ? DateTime.parse(json['updated_at'])
          : null,
    );
  }
}

class OrderItem {
  final int id;
  final String productName;
  final String? productImage;
  final double price;
  final int quantity;
  final String? size;
  final String? color;

  OrderItem({
    required this.id,
    required this.productName,
    this.productImage,
    required this.price,
    required this.quantity,
    this.size,
    this.color,
  });

  double get total => price * quantity;

  factory OrderItem.fromJson(Map<String, dynamic> json) {
    return OrderItem(
      id: json['id'] ?? 0,
      productName: json['product_name'] ?? '',
      productImage: json['product_image'],
      price: (json['price'] ?? 0).toDouble(),
      quantity: json['quantity'] ?? 1,
      size: json['size'],
      color: json['color'],
    );
  }
}
