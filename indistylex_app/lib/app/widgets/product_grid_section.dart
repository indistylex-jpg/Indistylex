import 'package:flutter/material.dart';

import '../models/product.dart';
import 'product_card.dart';

/// 2-column product grid matching the website layout.
class ProductGridSection extends StatelessWidget {
  final List<Product> products;
  final bool shrinkWrap;

  const ProductGridSection({
    super.key,
    required this.products,
    this.shrinkWrap = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: GridView.builder(
        shrinkWrap: shrinkWrap,
        physics: shrinkWrap ? const NeverScrollableScrollPhysics() : null,
        gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
          crossAxisCount: 2,
          childAspectRatio: 0.58,
          crossAxisSpacing: 12,
          mainAxisSpacing: 16,
        ),
        itemCount: products.length,
        itemBuilder: (_, index) => ProductCard(
          product: products[index],
          showWishlistButton: true,
        ),
      ),
    );
  }
}
