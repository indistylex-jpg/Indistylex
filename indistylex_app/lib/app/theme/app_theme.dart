import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Brand colors aligned with indistylex.com (style.css).
class AppColors {
  static const Color primary = Color(0xFF1E4D8C);
  static const Color accent = Color(0xFF2563EB);
  static const Color accentHover = Color(0xFF1D4ED8);
  static const Color accentSoft = Color(0xFFEFF6FF);
  static const Color accentLight = Color(0xFFDBEAFE);
  static const Color accentWarm = Color(0xFFE85D04);
  static const Color white = Color(0xFFFFFFFF);
  static const Color background = Color(0xFFF8FAFC);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color cardBg = Color(0xFFEEF4FC);
  static const Color muted = Color(0xFF64748B);
  static const Color lightGrey = Color(0xFFE2E8F0);
  static const Color error = Color(0xFFE53935);
  static const Color success = Color(0xFF43A047);
  static const Color cardShadow = Color(0x0D1E4D8C);
}

class AppTheme {
  static TextStyle _inter({
    required double size,
    FontWeight weight = FontWeight.w400,
    Color color = AppColors.primary,
    double? letterSpacing,
    double? height,
  }) {
    return GoogleFonts.inter(
      fontSize: size,
      fontWeight: weight,
      color: color,
      letterSpacing: letterSpacing,
      height: height,
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      colorScheme: const ColorScheme.light(
        primary: AppColors.primary,
        secondary: AppColors.accent,
        surface: AppColors.surface,
        error: AppColors.error,
        onPrimary: AppColors.white,
        onSecondary: AppColors.white,
        onSurface: AppColors.primary,
      ),
      scaffoldBackgroundColor: AppColors.background,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.white,
        foregroundColor: AppColors.primary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: _inter(size: 18, weight: FontWeight.w700),
      ),
      textTheme: TextTheme(
        displayLarge: _inter(size: 32, weight: FontWeight.w800),
        displayMedium: _inter(size: 24, weight: FontWeight.w700),
        headlineMedium: _inter(size: 20, weight: FontWeight.w700),
        titleLarge: _inter(size: 18, weight: FontWeight.w600),
        titleMedium: _inter(size: 16, weight: FontWeight.w600),
        bodyLarge: _inter(size: 16),
        bodyMedium: _inter(size: 14),
        bodySmall: _inter(size: 12, color: AppColors.muted),
        labelLarge: _inter(size: 14, weight: FontWeight.w600, color: AppColors.white),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.accent,
          foregroundColor: AppColors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(999)),
          textStyle: _inter(size: 14, weight: FontWeight.w700, color: AppColors.white),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.primary,
          side: const BorderSide(color: AppColors.primary),
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: AppColors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.lightGrey),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.lightGrey),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.accent, width: 2),
        ),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        hintStyle: _inter(size: 14, color: AppColors.muted),
      ),
      cardTheme: CardThemeData(
        color: AppColors.white,
        elevation: 2,
        shadowColor: AppColors.cardShadow,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: AppColors.white,
        selectedItemColor: AppColors.accent,
        unselectedItemColor: AppColors.muted,
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
    );
  }

  static ThemeData get darkTheme => lightTheme;
}
