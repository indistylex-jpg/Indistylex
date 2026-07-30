import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_theme.dart';

/// Brand logo matching the Indistylex website navbar.
class AppLogo extends StatelessWidget {
  final double monogramSize;
  final bool showWordmark;
  final bool lightMode;
  final MainAxisAlignment alignment;

  const AppLogo({
    super.key,
    this.monogramSize = 34,
    this.showWordmark = true,
    this.lightMode = true,
    this.alignment = MainAxisAlignment.center,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: alignment,
      children: [
        BrandMonogram(size: monogramSize, lightMode: lightMode),
        if (showWordmark) ...[
          SizedBox(width: monogramSize * 0.3),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'INDISTYLEX',
                style: GoogleFonts.playfairDisplay(
                  fontSize: monogramSize * 0.4,
                  fontWeight: FontWeight.w700,
                  letterSpacing: 2.5,
                  color: lightMode ? AppColors.primary : AppColors.white,
                  height: 1.1,
                ),
              ),
              Container(
                width: monogramSize * 1.5,
                height: 1.5,
                margin: const EdgeInsets.only(top: 2),
                decoration: BoxDecoration(
                  color: AppColors.accent,
                  borderRadius: BorderRadius.circular(1),
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }
}

/// iX monogram mark — black square with gold accent underline.
class BrandMonogram extends StatelessWidget {
  final double size;
  final bool lightMode;

  const BrandMonogram({
    super.key,
    this.size = 34,
    this.lightMode = true,
  });

  @override
  Widget build(BuildContext context) {
    final bgColor = lightMode ? AppColors.primary : Colors.white.withOpacity(0.1);
    final textColor = lightMode ? AppColors.white : AppColors.white;

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(size * 0.12),
        border: Border(
          bottom: BorderSide(color: AppColors.accent, width: size * 0.06),
        ),
      ),
      alignment: Alignment.center,
      child: Text(
        'iX',
        style: GoogleFonts.playfairDisplay(
          fontSize: size * 0.42,
          fontWeight: FontWeight.w700,
          color: textColor,
          letterSpacing: 0.5,
          height: 1,
        ),
      ),
    );
  }
}

/// Large splash logo with tagline.
class SplashLogo extends StatelessWidget {
  const SplashLogo({super.key});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(16),
            border: Border(
              bottom: BorderSide(color: AppColors.accent, width: 3),
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.accent.withOpacity(0.25),
                blurRadius: 24,
                offset: const Offset(0, 8),
              ),
            ],
          ),
          alignment: Alignment.center,
          child: Text(
            'iX',
            style: GoogleFonts.playfairDisplay(
              fontSize: 48,
              fontWeight: FontWeight.w700,
              color: AppColors.accent,
              height: 1,
            ),
          ),
        ),
        const SizedBox(height: 28),
        Text(
          'INDISTYLEX',
          style: GoogleFonts.playfairDisplay(
            fontSize: 32,
            fontWeight: FontWeight.w700,
            color: AppColors.white,
            letterSpacing: 6,
          ),
        ),
        const SizedBox(height: 6),
        Container(
          width: 60,
          height: 2,
          decoration: BoxDecoration(
            color: AppColors.accent,
            borderRadius: BorderRadius.circular(1),
          ),
        ),
        const SizedBox(height: 12),
        Text(
          'Style That Speaks, Quality That Lasts',
          style: GoogleFonts.inter(
            fontSize: 13,
            color: AppColors.accent.withOpacity(0.85),
            letterSpacing: 0.5,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }
}
