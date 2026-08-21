import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';

import '../theme/app_theme.dart';
import '../providers/auth_provider.dart';
import '../providers/product_provider.dart';
import '../constants/app_constants.dart';
import 'app_logo.dart';

class AppDrawer extends StatelessWidget {
  final int currentTab;

  const AppDrawer({super.key, this.currentTab = 0});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(20),
              child: const AppLogo(height: 38),
            ),
            const Divider(height: 1),
            Expanded(
              child: ListView(
                padding: EdgeInsets.zero,
                children: [
                  _item(context, Icons.home_outlined, 'Home', 0, '/home'),
                  _item(context, Icons.grid_view_outlined, 'Shop', 1, '/shop'),
                  _categoriesSection(context),
                  _item(context, Icons.fiber_new_outlined, 'New Arrivals', 1,
                      '/shop', args: {'sort': 'newest'}),
                  _item(context, Icons.local_offer_outlined, 'Sale', 1, '/shop',
                      args: {'sort': 'popular'}),
                  _item(context, Icons.shopping_bag_outlined, 'Cart', 2, '/home'),
                  _item(context, Icons.favorite_outline, 'Wishlist', 3, '/home'),
                  const Divider(),
                  _link(context, 'About Us', AppConstants.websiteAbout),
                  _link(context, 'Contact', AppConstants.websiteContact),
                  _link(context, 'FAQs', AppConstants.websiteFaq),
                  _link(context, 'Privacy Policy', AppConstants.websitePrivacy),
                  _link(context, 'Terms of Service', AppConstants.websiteTerms),
                ],
              ),
            ),
            const Divider(height: 1),
            Consumer<AuthProvider>(
              builder: (_, auth, __) {
                if (auth.isLoggedIn) {
                  return ListTile(
                    leading: const Icon(Icons.logout, color: AppColors.error),
                    title: Text('Sign Out', style: GoogleFonts.inter(color: AppColors.error)),
                    onTap: () async {
                      Navigator.pop(context);
                      await auth.logout();
                    },
                  );
                }
                return Column(
                  children: [
                    ListTile(
                      leading: const Icon(Icons.login),
                      title: Text('Sign In', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                      onTap: () {
                        Navigator.pop(context);
                        Navigator.pushNamed(context, '/login');
                      },
                    ),
                    ListTile(
                      leading: const Icon(Icons.person_add_outlined),
                      title: Text('Create Account', style: GoogleFonts.inter()),
                      onTap: () {
                        Navigator.pop(context);
                        Navigator.pushNamed(context, '/register');
                      },
                    ),
                  ],
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _item(BuildContext context, IconData icon, String title, int tab,
      String route,
      {Map<String, dynamic>? args}) {
    final selected = currentTab == tab && args == null;
    return ListTile(
      leading: Icon(icon, color: selected ? AppColors.accent : AppColors.primary),
      title: Text(
        title,
        style: GoogleFonts.inter(
          fontWeight: selected ? FontWeight.w600 : FontWeight.w500,
          color: selected ? AppColors.accent : AppColors.primary,
        ),
      ),
      onTap: () {
        Navigator.pop(context);
        if (route == '/home') {
          Navigator.pushNamedAndRemoveUntil(context, '/home', (r) => false);
        } else if (args != null) {
          Navigator.pushNamed(context, route, arguments: args);
        } else {
          Navigator.pushNamed(context, route);
        }
      },
    );
  }

  Widget _categoriesSection(BuildContext context) {
    return Consumer<ProductProvider>(
      builder: (_, provider, __) {
        if (provider.categories.isEmpty) return const SizedBox.shrink();
        return ExpansionTile(
          leading: const Icon(Icons.category_outlined),
          title: Text('Categories', style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
          children: provider.categories.map((cat) {
            return ListTile(
              title: Text(cat.name, style: GoogleFonts.inter(fontSize: 14)),
              dense: true,
              onTap: () {
                Navigator.pop(context);
                Navigator.pushNamed(context, '/shop',
                    arguments: {'category': cat.slug});
              },
            );
          }).toList(),
        );
      },
    );
  }

  Widget _link(BuildContext context, String title, String url) {
    return ListTile(
      leading: const Icon(Icons.open_in_new, size: 18),
      title: Text(title, style: GoogleFonts.inter(fontSize: 14)),
      onTap: () async {
        Navigator.pop(context);
        final uri = Uri.parse(url);
        if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
      },
    );
  }
}
