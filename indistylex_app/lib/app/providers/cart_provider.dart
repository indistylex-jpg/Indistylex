import 'package:flutter/material.dart';

import '../models/cart.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';

class CartProvider extends ChangeNotifier {
  final ApiService _api = ApiService();

  Cart _cart = Cart();
  bool _isLoading = false;
  String? _error;
  String? _couponMessage;

  Cart get cart => _cart;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get couponMessage => _couponMessage;
  int get itemCount => _cart.itemCount;
  double get total => _cart.total;

  Future<void> fetchCart() async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.get(ApiConstants.cart);
    _isLoading = false;

    if (response['success']) {
      _cart = Cart.fromJson(response['data']);
    }
    notifyListeners();
  }

  Future<bool> addToCart(int productId, {int quantity = 1, String? size, String? color}) async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.post(ApiConstants.addToCart, body: {
      'product_id': productId,
      'quantity': quantity,
      if (size != null) 'size': size,
      if (color != null) 'color': color,
    });

    _isLoading = false;

    if (response['success']) {
      _cart = Cart.fromJson(response['data']);
      notifyListeners();
      return true;
    }
    _error = response['message'] ?? response['data']?['error'];
    notifyListeners();
    return false;
  }

  Future<bool> updateQuantity(int cartItemId, int quantity) async {
    final response = await _api.put(ApiConstants.updateCart, body: {
      'item_id': cartItemId,
      'quantity': quantity,
    });

    if (response['success']) {
      await fetchCart();
      return true;
    }
    return false;
  }

  Future<bool> removeItem(int cartItemId) async {
    final response = await _api.delete('${ApiConstants.removeFromCart}?item_id=$cartItemId');

    if (response['success']) {
      _cart = Cart.fromJson(response['data']);
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<bool> applyCoupon(String code) async {
    final response = await _api.post(ApiConstants.validateCoupon, body: {
      'code': code,
    });

    if (response['success']) {
      await fetchCart();
      return true;
    }
    _error = response['message'];
    notifyListeners();
    return false;
  }

  void clear() {
    _cart = Cart();
    notifyListeners();
  }
}
