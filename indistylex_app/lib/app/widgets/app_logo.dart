import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_theme.dart';

/// Brand logo — same SVG assets as indistylex.com navbar.
class AppLogo extends StatelessWidget {
  final double height;
  final bool iconOnly;
  final bool white;

  const AppLogo({
    super.key,
    this.height = 40,
    this.iconOnly = false,
    this.white = false,
  });

  @override
  Widget build(BuildContext context) {
    final asset = white
        ? 'assets/images/logo-white.svg'
        : iconOnly
            ? 'assets/images/logo-icon.svg'
            : 'assets/images/logo.svg';
    return SvgPicture.asset(
      asset,
      height: height,
      fit: BoxFit.contain,
    );
  }
}

/// Splash screen logo — icon + wordmark matching website brand.
class SplashLogo extends StatelessWidget {
  const SplashLogo({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: AppColors.accent.withOpacity(0.35),
                blurRadius: 28,
                offset: const Offset(0, 10),
              ),
            ],
          ),
          child: SvgPicture.asset(
            'assets/images/logo-icon.svg',
            height: 96,
          ),
        ),
        const SizedBox(height: 28),
        Text(
          'INDISTYLEX',
          style: GoogleFonts.inter(
            fontSize: 30,
            fontWeight: FontWeight.w800,
            color: AppColors.white,
            letterSpacing: 4,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: 72,
          height: 3,
          decoration: BoxDecoration(
            color: AppColors.accentLight,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'Premium Kids Fashion',
          style: GoogleFonts.inter(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: AppColors.accentLight.withOpacity(0.95),
            letterSpacing: 1.5,
          ),
        ),
      ],
    );
  }
}
