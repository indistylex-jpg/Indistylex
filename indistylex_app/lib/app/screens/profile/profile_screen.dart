import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../theme/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../constants/app_constants.dart';
import '../../widgets/app_version_badge.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: Consumer<AuthProvider>(
        builder: (context, auth, _) {
          if (!auth.isLoggedIn) {
            return _buildGuestView(context);
          }
          return _buildUserProfile(context, auth);
        },
      ),
    );
  }

  Widget _buildGuestView(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.person_outline,
                size: 80, color: AppColors.lightGrey),
            const SizedBox(height: 16),
            const Text('Sign in to view your profile',
                style: TextStyle(fontSize: 16)),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pushNamed(context, '/login'),
                child: const Text('Sign In'),
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              width: double.infinity,
              child: OutlinedButton(
                onPressed: () =>
                    Navigator.pushNamed(context, '/register'),
                child: const Text('Create Account'),
              ),
            ),
            const SizedBox(height: 32),
            const AppVersionBadge(),
          ],
        ),
      ),
    );
  }

  Widget _buildUserProfile(BuildContext context, AuthProvider auth) {
    final user = auth.user;

    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // User info card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: AppColors.accent,
                child: Text(
                  (user?.name.isNotEmpty == true)
                      ? user!.name[0].toUpperCase()
                      : 'U',
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      user?.name ?? 'User',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: AppColors.white,
                      ),
                    ),
                    Text(
                      user?.email ?? '',
                      style: TextStyle(
                        color: AppColors.white.withOpacity(0.7),
                        fontSize: 13,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Menu items
        _buildMenuItem(
          icon: Icons.shopping_bag_outlined,
          title: 'My Orders',
          onTap: () => Navigator.pushNamed(context, '/orders'),
        ),
        _buildMenuItem(
          icon: Icons.favorite_outline,
          title: 'Wishlist',
          onTap: () => Navigator.pushNamed(context, '/wishlist'),
        ),
        _buildMenuItem(
          icon: Icons.location_on_outlined,
          title: 'Addresses',
          onTap: () {
            // TODO: Manage addresses
          },
        ),
        _buildMenuItem(
          icon: Icons.headset_mic_outlined,
          title: 'Help & Support',
          onTap: () {
            // TODO: Help screen
          },
        ),
        _buildMenuItem(
          icon: Icons.shield_outlined,
          title: 'Secure Connection',
          subtitle: 'HTTPS encrypted • Anti-tamper enabled',
          onTap: () {},
        ),
        _buildMenuItem(
          icon: Icons.info_outline,
          title: 'About Us',
          subtitle: AppConstants.website,
          onTap: () {
            // TODO: About screen
          },
        ),
        const SizedBox(height: 24),
        _buildMenuItem(
          icon: Icons.logout,
          title: 'Sign Out',
          isDestructive: true,
          onTap: () async {
            await auth.logout();
            if (context.mounted) {
              Navigator.pushNamedAndRemoveUntil(
                  context, '/home', (route) => false);
            }
          },
        ),
        const SizedBox(height: 16),
        const AppVersionBadge(),
      ],
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    String? subtitle,
    bool isDestructive = false,
    required VoidCallback onTap,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
      leading: Icon(icon,
          color: isDestructive ? AppColors.error : AppColors.primary),
      title: Text(
        title,
        style: TextStyle(
          fontWeight: FontWeight.w500,
          color: isDestructive ? AppColors.error : AppColors.primary,
        ),
      ),
      subtitle: subtitle != null
          ? Text(subtitle, style: const TextStyle(fontSize: 12))
          : null,
      trailing: const Icon(Icons.chevron_right, color: AppColors.muted),
      onTap: onTap,
    );
  }
}
