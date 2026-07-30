import 'product.dart';

class CartItem {
  final int id;
  final Product product;
  int quantity;
  final String? size;
  final String? color;

  CartItem({
    required this.id,
    required this.product,
    this.quantity = 1,
    this.size,
    this.color,
  });

  double get total => product.displayPrice * quantity;

  factory CartItem.fromJson(Map<String, dynamic> json) {
    return CartItem(
      id: json['id'] ?? 0,
      product: Product.fromJson(json['product']),
      quantity: json['quantity'] ?? 1,
      size: json['size'],
      color: json['color'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': product.id,
      'quantity': quantity,
      'size': size,
      'color': color,
    };
  }
}

class Cart {
  final List<CartItem> items;
  final double subtotal;
  final double discount;
  final double shipping;
  final double total;
  final String? couponCode;

  Cart({
    this.items = const [],
    this.subtotal = 0,
    this.discount = 0,
    this.shipping = 0,
    this.total = 0,
    this.couponCode,
  });

  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  factory Cart.fromJson(Map<String, dynamic> json) {
    return Cart(
      items: (json['items'] as List? ?? [])
          .map((item) => CartItem.fromJson(item))
          .toList(),
      subtotal: (json['subtotal'] ?? 0).toDouble(),
      discount: (json['discount'] ?? 0).toDouble(),
      shipping: (json['shipping'] ?? 0).toDouble(),
      total: (json['total'] ?? 0).toDouble(),
      couponCode: json['coupon_code'],
    );
  }
}
