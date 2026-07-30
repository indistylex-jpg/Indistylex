import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'app/app.dart';
import 'app/providers/auth_provider.dart';
import 'app/providers/cart_provider.dart';
import 'app/providers/product_provider.dart';
import 'app/providers/wishlist_provider.dart';
import 'app/providers/order_provider.dart';
import 'app/services/app_info_service.dart';
import 'app/services/security_service.dart';
import 'app/services/api_service.dart';
import 'app/screens/security/security_blocked_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await AppInfoService().init();
  final securityReport = await SecurityService().runChecks();

  if (!securityReport.isSecure) {
    runApp(SecurityBlockedApp(threats: securityReport.threats));
    return;
  }

  final authProvider = AuthProvider();
  ApiService().onUnauthorized = () => authProvider.logout();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider.value(value: authProvider),
        ChangeNotifierProvider(create: (_) => ProductProvider()),
        ChangeNotifierProvider(create: (_) => CartProvider()),
        ChangeNotifierProvider(create: (_) => WishlistProvider()),
        ChangeNotifierProvider(create: (_) => OrderProvider()),
      ],
      child: const IndistylexApp(),
    ),
  );
}

/// Minimal app shown when device fails security checks.
class SecurityBlockedApp extends StatelessWidget {
  final List<String> threats;

  const SecurityBlockedApp({super.key, required this.threats});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: SecurityBlockedScreen(threats: threats),
    );
  }
}
