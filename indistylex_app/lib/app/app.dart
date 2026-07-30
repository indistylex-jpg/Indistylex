import 'package:flutter/material.dart';

import 'theme/app_theme.dart';
import 'screens/splash_screen.dart';
import 'screens/home/home_screen.dart';
import 'screens/auth/login_screen.dart';
import 'screens/auth/register_screen.dart';
import 'screens/shop/shop_screen.dart';
import 'screens/product/product_detail_screen.dart';
import 'screens/cart/cart_screen.dart';
import 'screens/checkout/checkout_screen.dart';
import 'screens/order/orders_screen.dart';
import 'screens/order/order_detail_screen.dart';
import 'screens/profile/profile_screen.dart';
import 'screens/wishlist/wishlist_screen.dart';
import 'screens/search/search_screen.dart';
import 'screens/static/contact_screen.dart';
import 'widgets/bottom_nav.dart';
import 'widgets/app_drawer.dart';

class IndistylexApp extends StatelessWidget {
  const IndistylexApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Indistylex',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.light,
      home: const SplashScreen(),
      routes: {
        '/home': (context) => const MainScreen(),
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const RegisterScreen(),
        '/shop': (context) => Scaffold(
              drawer: const AppDrawer(currentTab: 1),
              body: const ShopScreen(),
            ),
        '/cart': (context) => const CartScreen(),
        '/checkout': (context) => const CheckoutScreen(),
        '/orders': (context) => const OrdersScreen(),
        '/profile': (context) => const ProfileScreen(),
        '/wishlist': (context) => const WishlistScreen(),
        '/search': (context) => const SearchScreen(),
        '/contact': (context) => const ContactScreen(),
      },
      onGenerateRoute: (settings) {
        if (settings.name == '/product') {
          final slugOrId = settings.arguments;
          return MaterialPageRoute(
            builder: (_) => ProductDetailScreen(slugOrId: slugOrId),
          );
        }
        if (settings.name == '/order-detail') {
          final orderId = settings.arguments as int;
          return MaterialPageRoute(
            builder: (_) => OrderDetailScreen(orderId: orderId),
          );
        }
        return null;
      },
    );
  }
}

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: AppDrawer(currentTab: _currentIndex),
      body: IndexedStack(
        index: _currentIndex,
        children: [
          const HomeScreen(),
          const ShopScreen(),
          const CartScreen(),
          const WishlistScreen(),
          const ProfileScreen(),
        ],
      ),
      bottomNavigationBar: BottomNav(
        currentIndex: _currentIndex,
        onTap: (index) => setState(() => _currentIndex = index),
      ),
    );
  }
}
