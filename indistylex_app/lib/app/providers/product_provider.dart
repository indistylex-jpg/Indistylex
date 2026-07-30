import 'package:flutter/material.dart';

import '../models/product.dart';
import '../models/category.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';

class ProductProvider extends ChangeNotifier {
  final ApiService _api = ApiService();

  List<Product> _products = [];
  List<Product> _featuredProducts = [];
  List<Product> _trendingProducts = [];
  List<Product> _newArrivals = [];
  List<Category> _categories = [];
  bool _isLoading = false;
  String? _error;
  int _currentPage = 1;
  bool _hasMore = true;

  List<Product> get products => _products;
  List<Product> get featuredProducts => _featuredProducts;
  List<Product> get trendingProducts => _trendingProducts;
  List<Product> get newArrivals => _newArrivals;
  List<Category> get categories => _categories;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get hasMore => _hasMore;

  Future<void> fetchProducts({
    int? categoryId,
    String? categorySlug,
    String? sort,
    double? minPrice,
    double? maxPrice,
    bool featured = false,
    bool trending = false,
    bool refresh = false,
  }) async {
    if (refresh) {
      _currentPage = 1;
      _hasMore = true;
      _products = [];
    }

    if (!_hasMore || _isLoading) return;

    _isLoading = true;
    notifyListeners();

    final params = <String, String>{
      'page': _currentPage.toString(),
      'per_page': '20',
    };

    if (categorySlug != null && categorySlug.isNotEmpty) {
      params['category'] = categorySlug;
    } else if (categoryId != null) {
      final matches = _categories.where((c) => c.id == categoryId);
      if (matches.isNotEmpty && matches.first.slug.isNotEmpty) {
        params['category'] = matches.first.slug;
      }
    }

    if (sort != null) params['sort'] = sort;
    if (minPrice != null) params['min_price'] = minPrice.toString();
    if (maxPrice != null) params['max_price'] = maxPrice.toString();
    if (featured) params['featured'] = '1';
    if (trending) params['trending'] = '1';

    final response = await _api.get(ApiConstants.products, queryParams: params);

    _isLoading = false;

    if (response['success']) {
      final data = response['data'];
      final List<Product> newProducts = (data['products'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();

      _products.addAll(newProducts);
      _hasMore = data['has_next'] == true || newProducts.length >= 20;
      _currentPage++;
    } else {
      _error = response['message'];
    }
    notifyListeners();
  }

  Future<void> fetchFeaturedProducts() async {
    final response =
        await _api.get(ApiConstants.products, queryParams: {'featured': '1', 'per_page': '12'});
    if (response['success']) {
      _featuredProducts = (response['data']['products'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      notifyListeners();
    }
  }

  Future<void> fetchTrendingProducts() async {
    final response =
        await _api.get(ApiConstants.products, queryParams: {'trending': '1', 'per_page': '12'});
    if (response['success']) {
      _trendingProducts = (response['data']['products'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      notifyListeners();
    }
  }

  Future<void> fetchNewArrivals() async {
    final response = await _api.get(ApiConstants.products,
        queryParams: {'sort': 'newest', 'per_page': '12'});
    if (response['success']) {
      _newArrivals = (response['data']['products'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      notifyListeners();
    }
  }

  Future<void> fetchHomeData() async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.get(ApiConstants.homeData);
    _isLoading = false;

    if (response['success']) {
      final data = response['data'];
      _featuredProducts = (data['featured'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      _trendingProducts = (data['trending'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      _newArrivals = (data['new_arrivals'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
      _categories = (data['categories'] as List? ?? [])
          .map((c) => Category.fromJson(c))
          .toList();
      notifyListeners();
    } else {
      await Future.wait([
        fetchFeaturedProducts(),
        fetchTrendingProducts(),
        fetchNewArrivals(),
        fetchCategories(),
      ]);
    }
  }

  Future<void> fetchCategories() async {
    final response = await _api.get(ApiConstants.categories);
    if (response['success']) {
      final data = response['data'];
      _categories = (data['categories'] as List? ?? data as List? ?? [])
          .map((c) => Category.fromJson(c))
          .toList();
      notifyListeners();
    }
  }

  Future<Product?> fetchProductDetail(dynamic slugOrId) async {
    final response = await _api.get('${ApiConstants.products}/$slugOrId');
    if (response['success']) {
      final productData = response['data']['product'] ?? response['data'];
      return Product.fromJson(productData);
    }
    return null;
  }

  Future<List<Product>> searchProducts(String query) async {
    final response = await _api.get(
      ApiConstants.products,
      queryParams: {'q': query},
    );
    if (response['success']) {
      return (response['data']['products'] as List? ?? [])
          .map((p) => Product.fromJson(p))
          .toList();
    }
    return [];
  }
}
