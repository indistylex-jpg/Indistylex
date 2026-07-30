class Product {
  final int id;
  final String name;
  final String slug;
  final String description;
  final double price;
  final double? compareAtPrice;
  final String? image;
  final List<String> images;
  final String category;
  final String? categorySlug;
  final int? categoryId;
  final List<ProductVariant> variants;
  final int stock;
  final double rating;
  final int reviewCount;
  final bool isFeatured;
  final bool isTrending;
  final String? brand;
  final String? gender;
  final DateTime? createdAt;
  final double? _apiDiscountPercent;

  Product({
    required this.id,
    required this.name,
    this.slug = '',
    required this.description,
    required this.price,
    this.compareAtPrice,
    this.image,
    this.images = const [],
    required this.category,
    this.categorySlug,
    this.categoryId,
    this.variants = const [],
    this.stock = 0,
    this.rating = 0.0,
    this.reviewCount = 0,
    this.isFeatured = false,
    this.isTrending = false,
    this.brand,
    this.gender,
    this.createdAt,
    double? apiDiscountPercent,
  }) : _apiDiscountPercent = apiDiscountPercent;

  bool get isOnSale =>
      (_apiDiscountPercent ?? 0) > 0 ||
      (compareAtPrice != null && compareAtPrice! > price);
  double get displayPrice => price;
  double get discountPercent {
    if (_apiDiscountPercent != null && _apiDiscountPercent! > 0) {
      return _apiDiscountPercent!;
    }
    return isOnSale && compareAtPrice != null
        ? ((compareAtPrice! - price) / compareAtPrice! * 100)
        : 0;
  }
  bool get inStock => stock > 0;

  List<String> get sizes => variants
      .where((v) => v.size != null && v.size!.isNotEmpty)
      .map((v) => v.size!)
      .toSet()
      .toList();

  List<String> get colors => variants
      .where((v) => v.color != null && v.color!.isNotEmpty)
      .map((v) => v.color!)
      .toSet()
      .toList();

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      description: json['description'] ?? '',
      price: (json['price'] ?? 0).toDouble(),
      compareAtPrice: json['compare_at_price'] != null
          ? (json['compare_at_price']).toDouble()
          : null,
      image: json['primary_image'] ?? json['image'] ?? json['image_url'],
      images: json['images'] != null
          ? List<String>.from(json['images'])
          : [],
      category: json['category_name'] ??
          (json['category'] is Map ? json['category']['name'] : json['category']) ??
          json['brand'] ??
          '',
      categorySlug: json['category_slug'] ??
          (json['category'] is Map ? json['category']['slug'] : null),
      categoryId: json['category_id'],
      variants: json['variants'] != null
          ? (json['variants'] as List).map((v) => ProductVariant.fromJson(v)).toList()
          : [],
      stock: json['stock'] ?? json['total_stock'] ?? 0,
      rating: (json['average_rating'] ?? json['rating'] ?? 0).toDouble(),
      reviewCount: json['review_count'] ?? 0,
      isFeatured: json['is_featured'] ?? false,
      isTrending: json['is_trending'] ?? false,
      brand: json['brand'],
      gender: json['gender'],
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'])
          : null,
      apiDiscountPercent: json['discount_percent'] != null
          ? (json['discount_percent'] as num).toDouble()
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'slug': slug,
      'description': description,
      'price': price,
      'compare_at_price': compareAtPrice,
      'image': image,
      'category': category,
    };
  }
}

class ProductVariant {
  final int id;
  final String? size;
  final String? color;
  final int stockQuantity;
  final bool isActive;

  ProductVariant({
    required this.id,
    this.size,
    this.color,
    this.stockQuantity = 0,
    this.isActive = true,
  });

  factory ProductVariant.fromJson(Map<String, dynamic> json) {
    return ProductVariant(
      id: json['id'] ?? 0,
      size: json['size'],
      color: json['color'],
      stockQuantity: json['stock_quantity'] ?? json['stock'] ?? 0,
      isActive: json['is_active'] ?? true,
    );
  }
}
