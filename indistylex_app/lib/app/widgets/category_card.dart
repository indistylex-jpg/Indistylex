import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_theme.dart';
import '../models/category.dart';
import '../constants/api_constants.dart';

class CategoryCard extends StatelessWidget {
  final Category category;

  const CategoryCard({super.key, required this.category});

  static const _fallbackImages = {
    'newborn': 'https://images.unsplash.com/photo-1519689680058-324335c77eba?w=400&q=80',
    'toddler': 'https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&q=80',
    'boys': 'https://images.unsplash.com/photo-1542652694-40abf526446e?w=400&q=80',
    'girls': 'https://images.unsplash.com/photo-1476234251651-f353703a034d?w=400&q=80',
  };

  String _imageUrl() {
    if (category.image != null) {
      return ApiConstants.categoryImage(category.image!);
    }
    final slugKey = category.slug.isNotEmpty
        ? category.slug.split('-').first.toLowerCase()
        : category.name.split(' ').first.toLowerCase();
    return _fallbackImages[slugKey] ??
        'https://images.unsplash.com/photo-1596870230751-ebdfce98ec42?w=400&q=80';
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => Navigator.pushNamed(context, '/shop',
          arguments: category.slug.isNotEmpty ? {'category': category.slug} : null),
      child: SizedBox(
        width: 110,
        child: Column(
          children: [
            Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                border: Border.all(color: AppColors.accent, width: 3),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: ClipOval(
                child: CachedNetworkImage(
                  imageUrl: _imageUrl(),
                  fit: BoxFit.cover,
                  placeholder: (_, __) => Container(
                    color: AppColors.background,
                    child: const Icon(Icons.category, color: AppColors.accent),
                  ),
                  errorWidget: (_, __, ___) => Container(
                    color: AppColors.background,
                    child: const Icon(Icons.category, color: AppColors.accent),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 10),
            Text(
              category.name.toUpperCase(),
              style: GoogleFonts.inter(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 1.2,
              ),
              textAlign: TextAlign.center,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            Text(
              'VIEW ALL →',
              style: GoogleFonts.inter(
                fontSize: 9,
                color: AppColors.accent,
                fontWeight: FontWeight.w500,
                letterSpacing: 0.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
