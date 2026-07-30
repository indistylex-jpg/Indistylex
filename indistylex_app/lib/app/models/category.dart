class Category {
  final int id;
  final String name;
  final String slug;
  final String? image;
  final String? description;
  final int productCount;

  Category({
    required this.id,
    required this.name,
    this.slug = '',
    this.image,
    this.description,
    this.productCount = 0,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'] ?? 0,
      name: json['name'] ?? '',
      slug: json['slug'] ?? '',
      image: json['image'] ?? json['image_url'],
      description: json['description'],
      productCount: json['product_count'] ?? 0,
    );
  }
}
