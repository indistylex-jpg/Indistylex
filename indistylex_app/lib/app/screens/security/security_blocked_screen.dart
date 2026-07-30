import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter/services.dart';

import '../../theme/app_theme.dart';
import '../../services/security_service.dart';
import '../../widgets/app_logo.dart';

class SecurityBlockedScreen extends StatelessWidget {
  final List<String> threats;

  const SecurityBlockedScreen({super.key, required this.threats});

  @override
  Widget build(BuildContext context) {
    final message = SecurityService().threatMessage(threats);

    return Scaffold(
      backgroundColor: AppColors.primary,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.security, size: 72, color: AppColors.accent),
              const SizedBox(height: 24),
              const AppLogo(monogramSize: 40, lightMode: false),
              const SizedBox(height: 32),
              Text(
                'Security Alert',
                style: GoogleFonts.playfairDisplay(
                  fontSize: 26,
                  fontWeight: FontWeight.w600,
                  color: AppColors.white,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                message,
                textAlign: TextAlign.center,
                style: GoogleFonts.inter(
                  fontSize: 14,
                  color: AppColors.white.withOpacity(0.8),
                  height: 1.6,
                ),
              ),
              const SizedBox(height: 32),
              OutlinedButton(
                onPressed: () => SystemNavigator.pop(),
                style: OutlinedButton.styleFrom(
                  foregroundColor: AppColors.accent,
                  side: const BorderSide(color: AppColors.accent),
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 14),
                ),
                child: const Text('Exit App'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
