import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../constants/api_constants.dart';
import '../../theme/app_theme.dart';
import '../../theme/app_styles.dart';
import '../../providers/product_provider.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../widgets/section_header.dart';
import '../../widgets/category_card.dart';
import '../../widgets/site_header.dart';
import '../../widgets/site_footer.dart';
import '../../widgets/product_grid_section.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _heroIndex = 0;
  final CarouselSliderController _carouselController = CarouselSliderController();

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await context.read<ProductProvider>().fetchHomeData();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SiteHeader(),
        Expanded(
          child: RefreshIndicator(
            color: AppColors.accent,
            onRefresh: _loadData,
            child: Consumer<ProductProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading && provider.categories.isEmpty) {
                  return const Center(
                    child: CircularProgressIndicator(color: AppColors.accent),
                  );
                }

                return ListView(
                  children: [
                    _buildHeroBanner(),
                    if (provider.categories.isNotEmpty) ...[
                      SectionHeader(
                        title: 'SHOP BY AGE',
                        onViewAll: () => Navigator.pushNamed(context, '/shop'),
                        showAccentLine: true,
                      ),
                      _buildCategories(provider.categories),
                    ],
                    _buildPromoCards(),
                    if (provider.newArrivals.isNotEmpty) ...[
                      SectionHeader(
                        title: 'NEW ARRIVALS',
                        onViewAll: () => Navigator.pushNamed(
                          context,
                          '/shop',
                          arguments: {'sort': 'newest'},
                        ),
                      ),
                      ProductGridSection(products: provider.newArrivals.take(6).toList()),
                      const SizedBox(height: 24),
                    ],
                    if (provider.trendingProducts.isNotEmpty) ...[
                      SectionHeader(
                        title: 'TRENDING NOW',
                        onViewAll: () => Navigator.pushNamed(
                          context,
                          '/shop',
                          arguments: {'sort': 'popular'},
                        ),
                      ),
                      ProductGridSection(products: provider.trendingProducts.take(6).toList()),
                      const SizedBox(height: 24),
                    ],
                    if (provider.featuredProducts.isNotEmpty) ...[
                      SectionHeader(
                        title: 'FEATURED COLLECTION',
                        onViewAll: () => Navigator.pushNamed(context, '/shop'),
                      ),
                      ProductGridSection(products: provider.featuredProducts.take(6).toList()),
                      const SizedBox(height: 24),
                    ],
                    _buildTrustBadges(),
                    const SiteFooter(),
                  ],
                );
              },
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildHeroBanner() {
    final base = ApiConstants.baseUrl;
    final banners = [
      {
        'gradient': AppStyles.saleHeroGradient,
        'eyebrow': 'Limited Time Only',
        'pre': 'End of Season',
        'display': 'SALE',
        'displayWhite': true,
        'subtitle': 'UP TO 50% OFF*',
        'cta': 'Shop Sale',
        'image': '$base/static/images/lifestyle/hero-sale-indian-girl.jpg',
      },
      {
        'gradient': AppStyles.newHeroGradient,
        'eyebrow': 'Spring Summer 2026',
        'pre': null,
        'display': 'Soft Styles\nFor Little Stars',
        'displayWhite': false,
        'subtitle': 'Premium cotton · Skin-safe · 0–18 years',
        'cta': 'New Arrivals',
        'image': '$base/static/images/lifestyle/hero-collection-indian-kids.jpg',
      },
      {
        'gradient': AppStyles.babyHeroGradient,
        'eyebrow': 'Newborn & Infant',
        'pre': null,
        'display': 'Gentle\nFrom Day One',
        'displayWhite': false,
        'subtitle': 'Rompers, bodysuits & gift sets',
        'cta': 'Shop Baby',
        'image': '$base/static/images/lifestyle/hero-baby-indian.jpg',
      },
    ];

    return Column(
      children: [
        CarouselSlider(
          carouselController: _carouselController,
          items: banners.map((banner) {
            final whiteText = banner['displayWhite'] as bool;
            final textColor = whiteText ? AppColors.white : AppColors.primary;
            return Container(
              width: double.infinity,
              height: 340,
              decoration: BoxDecoration(gradient: banner['gradient'] as Gradient),
              child: Stack(
                children: [
                  Positioned(
                    right: -20,
                    bottom: 0,
                    top: 20,
                    width: 180,
                    child: ClipRRect(
                      borderRadius: const BorderRadius.only(topLeft: Radius.circular(20)),
                      child: CachedNetworkImage(
                        imageUrl: banner['image'] as String,
                        fit: BoxFit.cover,
                        alignment: Alignment.topCenter,
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 32, 24, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          banner['eyebrow'] as String,
                          style: GoogleFonts.inter(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            letterSpacing: 1.2,
                            color: textColor.withOpacity(0.85),
                          ),
                        ),
                        if (banner['pre'] != null) ...[
                          const SizedBox(height: 8),
                          Text(
                            banner['pre'] as String,
                            style: GoogleFonts.inter(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: textColor,
                            ),
                          ),
                        ],
                        const SizedBox(height: 6),
                        Text(
                          banner['display'] as String,
                          style: GoogleFonts.inter(
                            fontSize: whiteText ? 52 : 28,
                            fontWeight: FontWeight.w900,
                            height: 0.95,
                            letterSpacing: whiteText ? -1.5 : -0.5,
                            color: textColor,
                          ),
                        ),
                        const SizedBox(height: 10),
                        Text(
                          banner['subtitle'] as String,
                          style: GoogleFonts.inter(
                            fontSize: 13,
                            fontWeight: FontWeight.w500,
                            color: textColor.withOpacity(0.8),
                          ),
                        ),
                        const Spacer(),
                        ElevatedButton(
                          onPressed: () => Navigator.pushNamed(context, '/shop'),
                          style: whiteText
                              ? AppStyles.primaryPillButton
                              : AppStyles.accentPillButton,
                          child: Text((banner['cta'] as String).toUpperCase()),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          options: CarouselOptions(
            height: 340,
            autoPlay: true,
            autoPlayInterval: const Duration(seconds: 5),
            viewportFraction: 1.0,
            onPageChanged: (i, _) => setState(() => _heroIndex = i),
          ),
        ),
        const SizedBox(height: 12),
        AnimatedSmoothIndicator(
          activeIndex: _heroIndex,
          count: banners.length,
          effect: const WormEffect(
            dotHeight: 4,
            dotWidth: 24,
            spacing: 6,
            activeDotColor: AppColors.accent,
            dotColor: AppColors.lightGrey,
          ),
          onDotClicked: (i) => _carouselController.animateToPage(i),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _buildCategories(List<Category> categories) {
    return SizedBox(
      height: 165,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: categories.length,
        itemBuilder: (_, i) => Padding(
          padding: const EdgeInsets.only(right: 20),
          child: CategoryCard(category: categories[i]),
        ),
      ),
    );
  }

  Widget _buildPromoCards() {
    final base = ApiConstants.baseUrl;
    final promos = [
      {
        'tag': 'LIMITED TIME',
        'title': 'End of Season\nSale',
        'image': '$base/static/images/lifestyle/hero-sale-indian-girl.jpg',
      },
      {
        'tag': 'EVERYDAY WEAR',
        'title': 'Comfort for\nActive Kids',
        'image': '$base/static/images/lifestyle/lifestyle-everyday-boy.jpg',
      },
      {
        'tag': 'ETHNIC & FESTIVE',
        'title': 'Celebrate in\nStyle',
        'image': '$base/static/images/lifestyle/lifestyle-ethnic-boy.jpg',
      },
    ];

    return Column(
      children: [
        SizedBox(
          height: 220,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: promos.length,
            itemBuilder: (_, index) {
              final promo = promos[index];
              return GestureDetector(
                onTap: () => Navigator.pushNamed(context, '/shop'),
                child: Container(
                  width: 200,
                  margin: const EdgeInsets.only(right: 12),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.12),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      CachedNetworkImage(imageUrl: promo['image'] as String, fit: BoxFit.cover),
                      Container(decoration: const BoxDecoration(gradient: AppStyles.promoGradient)),
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Text(
                              promo['tag'] as String,
                              style: GoogleFonts.inter(
                                fontSize: 9,
                                fontWeight: FontWeight.w700,
                                letterSpacing: 1.2,
                                color: AppColors.accentLight,
                              ),
                            ),
                            const SizedBox(height: 6),
                            Text(
                              promo['title'] as String,
                              style: GoogleFonts.inter(
                                fontSize: 17,
                                fontWeight: FontWeight.w800,
                                color: AppColors.white,
                                height: 1.2,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'SHOP NOW →',
                              style: GoogleFonts.inter(
                                fontSize: 10,
                                fontWeight: FontWeight.w700,
                                color: AppColors.accentLight,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildTrustBadges() {
    final badges = [
      {'icon': Icons.local_shipping_outlined, 'title': 'FREE SHIPPING', 'subtitle': 'On orders above ₹999'},
      {'icon': Icons.refresh, 'title': 'EASY RETURNS', 'subtitle': 'Hassle-free returns'},
      {'icon': Icons.shield_outlined, 'title': 'SECURE PAYMENTS', 'subtitle': '100% secure checkout'},
      {'icon': Icons.verified_outlined, 'title': 'QUALITY GUARANTEE', 'subtitle': 'Premium quality products'},
    ];

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 8, 16, 24),
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.accentSoft,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.lightGrey),
      ),
      child: Column(
        children: [
          for (int i = 0; i < badges.length; i += 2) ...[
            Row(
              children: [
                Expanded(child: _trustItem(badges[i])),
                Expanded(child: _trustItem(badges[i + 1])),
              ],
            ),
            if (i + 2 < badges.length) const SizedBox(height: 20),
          ],
        ],
      ),
    );
  }

  Widget _trustItem(Map<String, dynamic> b) {
    return Row(
      children: [
        Icon(b['icon'] as IconData, color: AppColors.primary, size: 26),
        const SizedBox(width: 10),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(b['title'] as String, style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.w700, letterSpacing: 0.5)),
              Text(b['subtitle'] as String, style: GoogleFonts.inter(fontSize: 9, color: AppColors.muted)),
            ],
          ),
        ),
      ],
    );
  }
}
