import 'package:flutter/material.dart';

import '../models/product.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';

class WishlistProvider extends ChangeNotifier {
  final ApiService _api = ApiService();

  List<Product> _items = [];
  bool _isLoading = false;

  List<Product> get items => _items;
  bool get isLoading => _isLoading;
  int get itemCount => _items.length;

  bool isInWishlist(int productId) {
    return _items.any((p) => p.id == productId);
  }

  Future<void> fetchWishlist() async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.get(ApiConstants.wishlist);
    _isLoading = false;

    if (response['success']) {
      _items = (response['data'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
    }
    notifyListeners();
  }

  Future<bool> toggleWishlist(Product product) async {
    final response = await _api.post(ApiConstants.toggleWishlist, body: {
      'product_id': product.id,
    });

    if (response['success']) {
      final added = response['data']?['added'] ?? false;
      if (added) {
        if (!_items.any((p) => p.id == product.id)) {
          _items.add(product);
        }
      } else {
        _items.removeWhere((p) => p.id == product.id);
      }
      notifyListeners();
      return true;
    }
    return false;
  }

  Future<bool> addToWishlist(Product product) async {
    return toggleWishlist(product);
  }

  Future<bool> removeFromWishlist(int productId) async {
    final product = _items.firstWhere((p) => p.id == productId,
        orElse: () => Product(id: productId, name: '', description: '', price: 0, category: ''));
    return toggleWishlist(product);
  }
}
