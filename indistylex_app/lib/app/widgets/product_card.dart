import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../theme/app_theme.dart';
import '../models/product.dart';
import '../providers/wishlist_provider.dart';
import '../constants/api_constants.dart';
import '../constants/app_constants.dart';

class ProductCard extends StatelessWidget {
  final Product product;
  final bool showWishlistButton;

  const ProductCard({
    super.key,
    required this.product,
    this.showWishlistButton = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.pushNamed(
        context,
        '/product',
        arguments: product.slug.isNotEmpty ? product.slug : product.id,
      ),
      child: Card(
        clipBehavior: Clip.antiAlias,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: AppColors.lightGrey.withOpacity(0.5)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              flex: 3,
              child: Stack(
                children: [
                  SizedBox(
                    width: double.infinity,
                    child: product.image != null && product.image!.isNotEmpty
                        ? CachedNetworkImage(
                            imageUrl: ApiConstants.resolveImageUrl(product.image),
                            fit: BoxFit.cover,
                            placeholder: (_, __) => Container(
                              color: AppColors.lightGrey,
                              child: const Center(
                                child: Icon(Icons.image,
                                    color: AppColors.muted),
                              ),
                            ),
                            errorWidget: (_, __, ___) => Container(
                              color: AppColors.lightGrey,
                              child: const Center(
                                child: Icon(Icons.image,
                                    color: AppColors.muted),
                              ),
                            ),
                          )
                        : Container(
                            color: AppColors.lightGrey,
                            child: const Center(
                              child:
                                  Icon(Icons.image, color: AppColors.muted),
                            ),
                          ),
                  ),
                  // Sale badge
                  if (product.isOnSale)
                    Positioned(
                      top: 8,
                      left: 8,
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: AppColors.accent,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          '${product.discountPercent.round()}% OFF',
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                    ),
                  // Wishlist button
                  if (showWishlistButton)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Consumer<WishlistProvider>(
                        builder: (_, wishlist, __) {
                          final isWishlisted =
                              wishlist.isInWishlist(product.id);
                          return GestureDetector(
                            onTap: () =>
                                wishlist.toggleWishlist(product),
                            child: Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: AppColors.white,
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color:
                                        Colors.black.withOpacity(0.1),
                                    blurRadius: 4,
                                  ),
                                ],
                              ),
                              child: Icon(
                                isWishlisted
                                    ? Icons.favorite
                                    : Icons.favorite_border,
                                size: 18,
                                color: isWishlisted
                                    ? Colors.red
                                    : AppColors.muted,
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                ],
              ),
            ),
            // Info
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      product.category.toUpperCase(),
                      style: const TextStyle(
                        fontSize: 10,
                        color: AppColors.accent,
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Expanded(
                      child: Text(
                        product.name,
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.w600,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Text(
                          '${AppConstants.currency}${product.displayPrice.toStringAsFixed(0)}',
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (product.isOnSale) ...[
                          const SizedBox(width: 6),
                          Text(
                            '${AppConstants.currency}${product.price.toStringAsFixed(0)}',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.muted,
                              decoration: TextDecoration.lineThrough,
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
