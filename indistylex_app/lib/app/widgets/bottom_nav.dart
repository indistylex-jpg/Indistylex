import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../theme/app_theme.dart';
import '../providers/cart_provider.dart';

class BottomNav extends StatelessWidget {
  final int currentIndex;
  final Function(int) onTap;

  const BottomNav({
    super.key,
    required this.currentIndex,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
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
      child: BottomNavigationBar(
        currentIndex: currentIndex,
        onTap: onTap,
        items: [
          const BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Home',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.grid_view_outlined),
            activeIcon: Icon(Icons.grid_view),
            label: 'Shop',
          ),
          BottomNavigationBarItem(
            icon: Consumer<CartProvider>(
              builder: (_, cart, child) {
                return Badge(
                  isLabelVisible: cart.itemCount > 0,
                  label: Text(
                    cart.itemCount.toString(),
                    style: const TextStyle(fontSize: 10),
                  ),
                  backgroundColor: AppColors.accent,
                  child: child!,
                );
              },
              child: const Icon(Icons.shopping_bag_outlined),
            ),
            activeIcon: Consumer<CartProvider>(
              builder: (_, cart, child) {
                return Badge(
                  isLabelVisible: cart.itemCount > 0,
                  label: Text(
                    cart.itemCount.toString(),
                    style: const TextStyle(fontSize: 10),
                  ),
                  backgroundColor: AppColors.accent,
                  child: child!,
                );
              },
              child: const Icon(Icons.shopping_bag),
            ),
            label: 'Cart',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.favorite_outline),
            activeIcon: Icon(Icons.favorite),
            label: 'Wishlist',
          ),
          const BottomNavigationBarItem(
            icon: Icon(Icons.person_outlined),
            activeIcon: Icon(Icons.person),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
