import 'package:flutter/material.dart';

import '../models/order.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';

class OrderProvider extends ChangeNotifier {
  final ApiService _api = ApiService();

  List<Order> _orders = [];
  bool _isLoading = false;
  String? _error;

  List<Order> get orders => _orders;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> fetchOrders() async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.get(ApiConstants.orders);
    _isLoading = false;

    if (response['success']) {
      _orders = (response['data'] as List? ?? [])
          .map((o) => Order.fromJson(o))
          .toList();
    } else {
      _error = response['message'];
    }
    notifyListeners();
  }

  Future<Order?> fetchOrderDetail(int orderId) async {
    final response = await _api.get('${ApiConstants.orders}/$orderId');
    if (response['success']) {
      return Order.fromJson(response['data']);
    }
    return null;
  }

  Future<Map<String, dynamic>> createOrder({
    required String address,
    required String city,
    required String state,
    required String pincode,
    required String phone,
    String paymentMethod = 'online',
  }) async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.post(ApiConstants.createOrder, body: {
      'address': address,
      'city': city,
      'state': state,
      'pincode': pincode,
      'phone': phone,
      'payment_method': paymentMethod,
    });

    _isLoading = false;
    notifyListeners();

    if (response['success']) {
      return {'success': true, 'data': response['data']};
    }
    return {'success': false, 'message': response['message']};
  }

  Future<bool> verifyPayment(String paymentId, String orderId, String signature) async {
    final response = await _api.post(ApiConstants.verifyPayment, body: {
      'payment_id': paymentId,
      'order_id': orderId,
      'signature': signature,
    });
    return response['success'];
  }
}
