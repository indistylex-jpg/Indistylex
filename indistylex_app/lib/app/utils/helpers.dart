import 'package:flutter/material.dart';

import '../theme/app_theme.dart';
import '../constants/app_constants.dart';

/// Shows a snackbar message
void showMessage(BuildContext context, String message, {bool isError = false}) {
  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Text(message),
      backgroundColor: isError ? AppColors.error : AppColors.success,
      behavior: SnackBarBehavior.floating,
      margin: const EdgeInsets.all(16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
  );
}

/// Format currency amount
String formatCurrency(double amount) {
  return '${AppConstants.currency}${amount.toStringAsFixed(0)}';
}

/// Capitalize first letter
String capitalize(String text) {
  if (text.isEmpty) return text;
  return text[0].toUpperCase() + text.substring(1);
}

/// Validate email
bool isValidEmail(String email) {
  return RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(email);
}

/// Validate phone number (Indian)
bool isValidPhone(String phone) {
  return RegExp(r'^[6-9]\d{9}$').hasMatch(phone);
}

/// Validate pincode (Indian)
bool isValidPincode(String pincode) {
  return RegExp(r'^\d{6}$').hasMatch(pincode);
}
