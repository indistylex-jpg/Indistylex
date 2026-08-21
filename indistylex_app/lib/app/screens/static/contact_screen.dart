import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../theme/app_theme.dart';
import '../../constants/app_constants.dart';
import '../../widgets/site_header.dart';
import '../../widgets/site_footer.dart';
import '../../widgets/app_drawer.dart';

class ContactScreen extends StatelessWidget {
  const ContactScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: const AppDrawer(),
      body: Column(
        children: [
          const SiteHeader(showAnnouncement: false),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(24),
              children: [
                Text('Contact Us', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.w800, color: AppColors.primary)),
                const SizedBox(height: 8),
                Text('We\'d love to hear from you.', style: GoogleFonts.inter(color: AppColors.muted)),
                const SizedBox(height: 32),
                _tile(Icons.location_on_outlined, 'Address', AppConstants.address),
                _tile(Icons.email_outlined, 'Email', AppConstants.email, isLink: true),
                _tile(Icons.phone_outlined, 'Phone', AppConstants.phone, isLink: true),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () async {
                    final uri = Uri.parse(AppConstants.websiteContact);
                    if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
                  },
                  child: const Text('Visit Contact Page'),
                ),
                const SizedBox(height: 32),
                const SiteFooter(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _tile(IconData icon, String title, String value, {bool isLink = false}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: AppColors.accent),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: GoogleFonts.inter(fontWeight: FontWeight.w600)),
                const SizedBox(height: 4),
                Text(value, style: GoogleFonts.inter(color: AppColors.muted, fontSize: 14)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
