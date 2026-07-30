import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../theme/app_theme.dart';
import '../services/app_info_service.dart';

class AppVersionBadge extends StatelessWidget {
  final bool centered;
  final Color? color;

  const AppVersionBadge({super.key, this.centered = true, this.color});

  @override
  Widget build(BuildContext context) {
    final info = AppInfoService();
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: centered ? MainAxisAlignment.center : MainAxisAlignment.start,
        children: [
          Icon(Icons.verified_user_outlined, size: 14, color: color ?? AppColors.muted),
          const SizedBox(width: 6),
          Text(
            '${info.displayVersion} • Build ${info.buildNumber}',
            style: GoogleFonts.inter(
              fontSize: 11,
              color: color ?? AppColors.muted,
            ),
          ),
        ],
      ),
    );
  }
}
