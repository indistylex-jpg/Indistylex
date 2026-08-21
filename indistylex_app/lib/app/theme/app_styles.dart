import 'package:flutter/material.dart';

import 'app_theme.dart';

/// Shared gradients and decorations from indistylex.com home.css
class AppStyles {
  static const saleHeroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFDBEAFE), Color(0xFF93C5FD), Color(0xFF2563EB)],
    stops: [0.0, 0.45, 1.0],
  );

  static const newHeroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFEFF6FF), Color(0xFFBFDBFE), Color(0xFF93C5FD)],
    stops: [0.0, 0.5, 1.0],
  );

  static const babyHeroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFFDBEAFE), Color(0xFFBFDBFE), Color(0xFF60A5FA)],
    stops: [0.0, 0.55, 1.0],
  );

  static const promoGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Colors.transparent, Color(0xCC1E4D8C)],
    stops: [0.2, 1.0],
  );

  static BoxDecoration cardDecoration = BoxDecoration(
    color: AppColors.white,
    borderRadius: BorderRadius.circular(12),
    border: Border.all(color: AppColors.lightGrey),
    boxShadow: [
      BoxShadow(
        color: AppColors.primary.withOpacity(0.06),
        blurRadius: 12,
        offset: const Offset(0, 4),
      ),
    ],
  );

  static ButtonStyle primaryPillButton = ElevatedButton.styleFrom(
    backgroundColor: AppColors.primary,
    foregroundColor: AppColors.white,
    elevation: 0,
    padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
    textStyle: const TextStyle(fontWeight: FontWeight.w800, letterSpacing: 0.8),
  );

  static ButtonStyle accentPillButton = ElevatedButton.styleFrom(
    backgroundColor: AppColors.accent,
    foregroundColor: AppColors.white,
    elevation: 0,
    padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 14),
    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
    textStyle: const TextStyle(fontWeight: FontWeight.w800, letterSpacing: 0.8),
  );
}
