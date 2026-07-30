import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_theme.dart';
import '../providers/cart_provider.dart';
import '../providers/auth_provider.dart';
import 'app_logo.dart';

class SiteHeader extends StatelessWidget {
  final bool showAnnouncement;
  final VoidCallback? onShop;
  final VoidCallback? onNewArrivals;
  final VoidCallback? onSale;

  const SiteHeader({
    super.key,
    this.showAnnouncement = true,
    this.onShop,
    this.onNewArrivals,
    this.onSale,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: AppColors.white,
      elevation: 0,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (showAnnouncement) _AnnouncementBar(),
          Container(
            height: 56,
            padding: const EdgeInsets.symmetric(horizontal: 8),
            decoration: const BoxDecoration(
              border: Border(bottom: BorderSide(color: AppColors.lightGrey)),
            ),
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.menu, size: 24),
                  onPressed: () => Scaffold.of(context).openDrawer(),
                  tooltip: 'Menu',
                ),
                Expanded(
                  child: GestureDetector(
                    onTap: () => _navigateHome(context),
                    child: const Center(child: AppLogo(monogramSize: 30)),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.search, size: 22),
                  onPressed: () => Navigator.pushNamed(context, '/search'),
                ),
                Consumer<AuthProvider>(
                  builder: (_, auth, __) {
                    return IconButton(
                      icon: Icon(
                        auth.isLoggedIn ? Icons.person : Icons.person_outline,
                        size: 22,
                      ),
                      onPressed: () {
                        if (auth.isLoggedIn) {
                          Navigator.pushNamed(context, '/profile');
                        } else {
                          Navigator.pushNamed(context, '/login');
                        }
                      },
                    );
                  },
                ),
                Stack(
                  clipBehavior: Clip.none,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.shopping_bag_outlined, size: 22),
                      onPressed: () => Navigator.pushNamed(context, '/cart'),
                    ),
                    Consumer<CartProvider>(
                      builder: (_, cart, __) {
                        if (cart.itemCount == 0) return const SizedBox.shrink();
                        return Positioned(
                          right: 6,
                          top: 6,
                          child: Container(
                            padding: const EdgeInsets.all(4),
                            constraints: const BoxConstraints(minWidth: 16, minHeight: 16),
                            decoration: const BoxDecoration(
                              color: AppColors.accent,
                              shape: BoxShape.circle,
                            ),
                            child: Text(
                              cart.itemCount.toString(),
                              style: GoogleFonts.inter(
                                fontSize: 9,
                                fontWeight: FontWeight.bold,
                                color: AppColors.primary,
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ),
                        );
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
          _NavChips(
            onShop: onShop,
            onNewArrivals: onNewArrivals,
            onSale: onSale,
          ),
        ],
      ),
    );
  }

  void _navigateHome(BuildContext context) {
    Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
  }
}

class _AnnouncementBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
      color: AppColors.primary,
      child: Text(
        'FREE SHIPPING ON ORDERS ABOVE ₹999  |  EASY RETURNS',
        textAlign: TextAlign.center,
        style: GoogleFonts.inter(
          fontSize: 10,
          color: AppColors.white,
          letterSpacing: 0.4,
        ),
      ),
    );
  }
}

class _NavChips extends StatelessWidget {
  final VoidCallback? onShop;
  final VoidCallback? onNewArrivals;
  final VoidCallback? onSale;

  const _NavChips({this.onShop, this.onNewArrivals, this.onSale});

  @override
  Widget build(BuildContext context) {
    final items = [
      ('HOME', () => Navigator.pushNamedAndRemoveUntil(context, '/home', (r) => false)),
      ('SHOP', onShop ?? () => Navigator.pushNamed(context, '/shop')),
      ('NEW', onNewArrivals ?? () => Navigator.pushNamed(context, '/shop', arguments: {'sort': 'newest'})),
      ('SALE', onSale ?? () => Navigator.pushNamed(context, '/shop', arguments: {'sort': 'popular'})),
      ('CONTACT', () => Navigator.pushNamed(context, '/contact')),
    ];

    return SizedBox(
      height: 40,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        itemCount: items.length,
        separatorBuilder: (_, __) => const SizedBox(width: 4),
        itemBuilder: (context, index) {
          final (label, onTap) = items[index];
          return ActionChip(
            label: Text(
              label,
              style: GoogleFonts.inter(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                letterSpacing: 0.8,
              ),
            ),
            backgroundColor: AppColors.background,
            side: BorderSide(color: AppColors.lightGrey.withOpacity(0.8)),
            padding: const EdgeInsets.symmetric(horizontal: 4),
            visualDensity: VisualDensity.compact,
            onPressed: onTap,
          );
        },
      ),
    );
  }
}
