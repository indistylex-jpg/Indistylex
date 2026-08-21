import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../theme/app_theme.dart';
import '../../models/product.dart';
import '../../providers/product_provider.dart';
import '../../providers/cart_provider.dart';
import '../../providers/wishlist_provider.dart';
import '../../constants/api_constants.dart';
import '../../constants/app_constants.dart';

class ProductDetailScreen extends StatefulWidget {
  final dynamic slugOrId;

  const ProductDetailScreen({super.key, required this.slugOrId});

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  Product? _product;
  bool _isLoading = true;
  String? _selectedSize;
  String? _selectedColor;
  int _quantity = 1;
  int _currentImageIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadProduct();
  }

  Future<void> _loadProduct() async {
    final product = await context
        .read<ProductProvider>()
        .fetchProductDetail(widget.slugOrId);
    if (mounted) {
      setState(() {
        _product = product;
        _isLoading = false;
        if (product != null && product.sizes.isNotEmpty) {
          _selectedSize = product.sizes.first;
        }
        if (product != null && product.colors.isNotEmpty) {
          _selectedColor = product.colors.first;
        }
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

    if (_product == null) {
      return Scaffold(
        appBar: AppBar(),
        body: const Center(child: Text('Product not found')),
      );
    }

    final product = _product!;

    return Scaffold(
      body: CustomScrollView(
        slivers: [
          // Image gallery
          SliverAppBar(
            expandedHeight: 400,
            pinned: true,
            actions: [
              Consumer<WishlistProvider>(
                builder: (_, wishlist, __) {
                  final isWishlisted = wishlist.isInWishlist(product.id);
                  return IconButton(
                    icon: Icon(
                      isWishlisted ? Icons.favorite : Icons.favorite_border,
                      color: isWishlisted ? Colors.red : null,
                    ),
                    onPressed: () => wishlist.toggleWishlist(product),
                  );
                },
              ),
              IconButton(
                icon: const Icon(Icons.share),
                onPressed: () {
                  // TODO: Share product
                },
              ),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: product.image != null
                  ? CachedNetworkImage(
                      imageUrl: ApiConstants.resolveImageUrl(product.image),
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: AppColors.lightGrey,
                        child: const Center(
                            child: Icon(Icons.image, size: 64,
                                color: AppColors.muted)),
                      ),
                    )
                  : Container(
                      color: AppColors.lightGrey,
                      child: const Center(
                          child: Icon(Icons.image, size: 64,
                              color: AppColors.muted)),
                    ),
            ),
          ),

          // Product details
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Category
                  Text(
                    product.category.toUpperCase(),
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.accent,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1,
                    ),
                  ),
                  const SizedBox(height: 8),

                  // Name
                  Text(
                    product.name,
                    style: GoogleFonts.inter(
                      fontSize: 22,
                      fontWeight: FontWeight.w800,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 12),

                  // Price
                  Row(
                    children: [
                      Text(
                        '${AppConstants.currency}${product.displayPrice.toStringAsFixed(0)}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: AppColors.accent,
                        ),
                      ),
                      if (product.isOnSale) ...[
                        const SizedBox(width: 12),
                        Text(
                          '${AppConstants.currency}${product.price.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 16,
                            color: AppColors.muted,
                            decoration: TextDecoration.lineThrough,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: AppColors.accent.withOpacity(0.1),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            '${product.discountPercent.round()}% OFF',
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.accent,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Rating
                  if (product.rating > 0)
                    Row(
                      children: [
                        ...List.generate(5, (i) {
                          return Icon(
                            i < product.rating.round()
                                ? Icons.star
                                : Icons.star_border,
                            size: 18,
                            color: AppColors.accent,
                          );
                        }),
                        const SizedBox(width: 8),
                        Text(
                          '${product.rating} (${product.reviewCount} reviews)',
                          style: const TextStyle(
                              color: AppColors.muted, fontSize: 13),
                        ),
                      ],
                    ),
                  const SizedBox(height: 20),

                  // Sizes
                  if (product.sizes.isNotEmpty) ...[
                    const Text('Size',
                        style: TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: product.sizes.map((size) {
                        final isSelected = _selectedSize == size;
                        return GestureDetector(
                          onTap: () =>
                              setState(() => _selectedSize = size),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 10),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppColors.primary
                                  : AppColors.white,
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.primary
                                    : AppColors.lightGrey,
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              size,
                              style: TextStyle(
                                color: isSelected
                                    ? AppColors.white
                                    : AppColors.primary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Colors
                  if (product.colors.isNotEmpty) ...[
                    const Text('Color',
                        style: TextStyle(fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      children: product.colors.map((color) {
                        final isSelected = _selectedColor == color;
                        return GestureDetector(
                          onTap: () =>
                              setState(() => _selectedColor = color),
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 10),
                            decoration: BoxDecoration(
                              color: isSelected
                                  ? AppColors.primary
                                  : AppColors.white,
                              border: Border.all(
                                color: isSelected
                                    ? AppColors.primary
                                    : AppColors.lightGrey,
                              ),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              color,
                              style: TextStyle(
                                color: isSelected
                                    ? AppColors.white
                                    : AppColors.primary,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 20),
                  ],

                  // Quantity
                  Row(
                    children: [
                      const Text('Quantity',
                          style: TextStyle(fontWeight: FontWeight.w600)),
                      const Spacer(),
                      Container(
                        decoration: BoxDecoration(
                          border: Border.all(color: AppColors.lightGrey),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.remove, size: 18),
                              onPressed: _quantity > 1
                                  ? () => setState(() => _quantity--)
                                  : null,
                            ),
                            Text('$_quantity',
                                style: const TextStyle(
                                    fontWeight: FontWeight.w600)),
                            IconButton(
                              icon: const Icon(Icons.add, size: 18),
                              onPressed: _quantity < product.stock
                                  ? () => setState(() => _quantity++)
                                  : null,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Description
                  const Text('Description',
                      style: TextStyle(
                          fontWeight: FontWeight.w600, fontSize: 16)),
                  const SizedBox(height: 8),
                  Text(
                    product.description,
                    style: const TextStyle(
                        color: AppColors.muted, height: 1.6),
                  ),
                  const SizedBox(height: 100),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
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
        child: Row(
          children: [
            Expanded(
              child: SizedBox(
                height: 50,
                child: ElevatedButton(
                  onPressed: product.inStock
                      ? () async {
                          final success = await context
                              .read<CartProvider>()
                              .addToCart(
                                product.id,
                                quantity: _quantity,
                                size: _selectedSize,
                                color: _selectedColor,
                              );
                          if (!mounted) return;
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(success
                                  ? 'Added to cart!'
                                  : 'Failed to add to cart'),
                              backgroundColor: success
                                  ? AppColors.success
                                  : AppColors.error,
                            ),
                          );
                        }
                      : null,
                  child: Text(product.inStock
                      ? 'Add to Cart'
                      : 'Out of Stock'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
