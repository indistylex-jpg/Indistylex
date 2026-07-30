import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';

import '../theme/app_theme.dart';
import '../constants/app_constants.dart';
import '../providers/product_provider.dart';
import 'app_logo.dart';
import 'app_version_badge.dart';

class SiteFooter extends StatefulWidget {
  const SiteFooter({super.key});

  @override
  State<SiteFooter> createState() => _SiteFooterState();
}

class _SiteFooterState extends State<SiteFooter> {
  final _emailController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        _newsletterSection(),
        _footerMain(),
        _footerBottom(),
      ],
    );
  }

  Widget _newsletterSection() {
    return Container(
      width: double.infinity,
      color: AppColors.primary,
      padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 24),
      child: Column(
        children: [
          Text(
            'STAY IN THE LOOP',
            style: GoogleFonts.inter(
              fontSize: 10,
              letterSpacing: 2,
              color: AppColors.white.withOpacity(0.7),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Get 10% Off Your First Order',
            style: GoogleFonts.playfairDisplay(
              fontSize: 22,
              fontWeight: FontWeight.w600,
              color: AppColors.white,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'Subscribe for exclusive offers, early access & new arrivals.',
            style: GoogleFonts.inter(fontSize: 12, color: AppColors.white.withOpacity(0.8)),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: _emailController,
                  style: const TextStyle(color: AppColors.white),
                  decoration: InputDecoration(
                    hintText: 'Enter your email',
                    hintStyle: TextStyle(color: AppColors.white.withOpacity(0.5)),
                    filled: true,
                    fillColor: Colors.white.withOpacity(0.1),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(0)),
                    enabledBorder: OutlineInputBorder(
                      borderSide: BorderSide(color: AppColors.white.withOpacity(0.3)),
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                  ),
                  keyboardType: TextInputType.emailAddress,
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  if (_emailController.text.contains('@')) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Thanks for subscribing!')),
                    );
                    _emailController.clear();
                  }
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppColors.accent,
                  foregroundColor: AppColors.primary,
                  shape: const RoundedRectangleBorder(),
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                ),
                child: Text('SUBSCRIBE', style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w700, letterSpacing: 1)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _footerMain() {
    return Container(
      color: AppColors.primary,
      padding: const EdgeInsets.fromLTRB(24, 32, 24, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const AppLogo(monogramSize: 32, lightMode: false),
          const SizedBox(height: 12),
          Text(
            'Premium fashion for everyone.\nQuality fabrics, trendy designs.',
            style: GoogleFonts.inter(fontSize: 12, color: AppColors.white.withOpacity(0.7), height: 1.6),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _socialIcon(Icons.facebook, AppConstants.facebook),
              _socialIcon(Icons.camera_alt_outlined, AppConstants.instagram),
            ],
          ),
          const SizedBox(height: 24),
          _footerColumn('SHOP', _shopLinks()),
          const SizedBox(height: 20),
          _footerColumn('CUSTOMER CARE', [
            _FooterLink('Contact Us', AppConstants.websiteContact),
            _FooterLink('FAQs', AppConstants.websiteFaq),
            _FooterLink('Shipping & Returns', AppConstants.websiteTerms),
          ]),
          const SizedBox(height: 20),
          _footerColumn('HELP', [
            _FooterText(Icons.location_on_outlined, AppConstants.address),
            _FooterText(Icons.email_outlined, AppConstants.email),
            _FooterText(Icons.phone_outlined, AppConstants.phone),
          ]),
        ],
      ),
    );
  }

  List<Widget> _shopLinks() {
    return [
      Consumer<ProductProvider>(
        builder: (_, provider, __) {
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              ...provider.categories.take(4).map((c) => _FooterLink(
                    c.name,
                    '${AppConstants.website}/shop?category=${c.slug}',
                  )),
              _FooterLink('New Arrivals', '${AppConstants.website}/shop?sort=newest'),
              _FooterLink('Best Sellers', '${AppConstants.website}/shop?sort=popular'),
            ],
          );
        },
      ),
    ];
  }

  Widget _footerColumn(String title, List<Widget> children) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: GoogleFonts.inter(
            fontSize: 11,
            fontWeight: FontWeight.w700,
            letterSpacing: 1.2,
            color: AppColors.accent,
          ),
        ),
        const SizedBox(height: 10),
        ...children,
      ],
    );
  }

  Widget _socialIcon(IconData icon, String url) {
    return Padding(
      padding: const EdgeInsets.only(right: 12),
      child: InkWell(
        onTap: () async {
          final uri = Uri.parse(url);
          if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
        },
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            border: Border.all(color: AppColors.white.withOpacity(0.2)),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Icon(icon, color: AppColors.white, size: 18),
        ),
      ),
    );
  }

  Widget _footerBottom() {
    return Container(
      color: AppColors.primary,
      padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
      child: Column(
        children: [
          Container(height: 1, color: AppColors.white.withOpacity(0.15)),
          const SizedBox(height: 16),
          Text(
            '© 2026 Indistylex. All rights reserved.',
            style: GoogleFonts.inter(fontSize: 11, color: AppColors.white.withOpacity(0.6)),
          ),
          const SizedBox(height: 12),
          const AppVersionBadge(color: Colors.white54),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: ['VISA', 'Mastercard', 'UPI', 'RuPay', 'Paytm'].map((p) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  border: Border.all(color: AppColors.white.withOpacity(0.2)),
                  borderRadius: BorderRadius.circular(2),
                ),
                child: Text(p, style: GoogleFonts.inter(fontSize: 9, color: AppColors.white.withOpacity(0.7))),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _FooterLink extends StatelessWidget {
  final String label;
  final String url;

  const _FooterLink(this.label, this.url);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: InkWell(
        onTap: () async {
          final uri = Uri.parse(url);
          if (await canLaunchUrl(uri)) await launchUrl(uri, mode: LaunchMode.externalApplication);
        },
        child: Text(
          label,
          style: GoogleFonts.inter(fontSize: 12, color: AppColors.white.withOpacity(0.75)),
        ),
      ),
    );
  }
}

class _FooterText extends StatelessWidget {
  final IconData icon;
  final String text;

  const _FooterText(this.icon, this.text);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 14, color: AppColors.accent),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              text,
              style: GoogleFonts.inter(fontSize: 12, color: AppColors.white.withOpacity(0.75)),
            ),
          ),
        ],
      ),
    );
  }
}
