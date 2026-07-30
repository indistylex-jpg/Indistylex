import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:carousel_slider/carousel_slider.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../theme/app_theme.dart';
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
    final banners = [
      {
        'badge': 'NEW COLLECTION 2026',
        'title': 'Style That Speaks,',
        'titleEm': 'Quality That Lasts.',
        'subtitle': 'Discover premium kids\' clothing crafted for comfort.',
        'image': 'https://images.unsplash.com/photo-1503944583220-79d8926ad5e2?w=1200&q=80',
      },
      {
        'badge': 'NEWBORN COLLECTION',
        'title': 'Soft & Gentle',
        'titleEm': 'For Your Little One.',
        'subtitle': 'Ultra-soft fabrics crafted for delicate skin.',
        'image': 'https://images.unsplash.com/photo-1522771930-78848d9293e8?w=1200&q=80',
      },
      {
        'badge': 'GIRLS\' COLLECTION',
        'title': 'Playful Styles',
        'titleEm': 'For Little Princesses.',
        'subtitle': 'Colorful, fun & comfortable outfits.',
        'image': 'https://images.unsplash.com/photo-1621452773781-0f992fd1f5cb?w=1200&q=80',
      },
      {
        'badge': 'LIMITED TIME OFFER',
        'title': 'Summer Sale',
        'titleEm': 'Up to 50% Off.',
        'subtitle': 'Adorable outfits at amazing prices.',
        'image': 'https://images.unsplash.com/photo-1471286174890-9c112ffca5b4?w=1200&q=80',
      },
      {
        'badge': 'PREMIUM QUALITY',
        'title': 'Crafted With Care,',
        'titleEm': 'Worn With Pride.',
        'subtitle': 'Safe, skin-friendly fabrics for your precious ones.',
        'image': 'https://images.unsplash.com/photo-1604917621956-10dfa7cce2e7?w=1200&q=80',
      },
    ];

    return Column(
      children: [
        CarouselSlider(
          carouselController: _carouselController,
          items: banners.map((banner) {
            return SizedBox(
              width: double.infinity,
              height: 300,
              child: Stack(
                fit: StackFit.expand,
                children: [
                  CachedNetworkImage(
                    imageUrl: banner['image'] as String,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => Container(color: AppColors.primary),
                  ),
                  Container(
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.centerLeft,
                        end: Alignment.centerRight,
                        colors: [Color(0x99000000), Color(0x33000000), Colors.transparent],
                        stops: [0.0, 0.55, 1.0],
                      ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.fromLTRB(24, 40, 24, 24),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          banner['badge'] as String,
                          style: GoogleFonts.inter(
                            fontSize: 10,
                            letterSpacing: 2,
                            color: AppColors.white.withOpacity(0.9),
                          ),
                        ),
                        const SizedBox(height: 10),
                        RichText(
                          text: TextSpan(
                            style: GoogleFonts.playfairDisplay(
                              fontSize: 26,
                              fontWeight: FontWeight.w700,
                              color: AppColors.white,
                              height: 1.2,
                            ),
                            children: [
                              TextSpan(text: '${banner['title']}\n'),
                              TextSpan(
                                text: banner['titleEm'] as String,
                                style: const TextStyle(fontStyle: FontStyle.italic, fontWeight: FontWeight.w400),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          banner['subtitle'] as String,
                          style: GoogleFonts.inter(fontSize: 12, color: AppColors.white.withOpacity(0.85)),
                        ),
                        const SizedBox(height: 18),
                        Row(
                          children: [
                            _heroBtn('SHOP NOW', filled: true),
                            const SizedBox(width: 10),
                            _heroBtn('EXPLORE', filled: false),
                          ],
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
          options: CarouselOptions(
            height: 300,
            autoPlay: true,
            autoPlayInterval: const Duration(seconds: 4),
            viewportFraction: 1.0,
            onPageChanged: (i, _) => setState(() => _heroIndex = i),
          ),
        ),
        const SizedBox(height: 12),
        AnimatedSmoothIndicator(
          activeIndex: _heroIndex,
          count: banners.length,
          effect: const WormEffect(
            dotHeight: 3,
            dotWidth: 28,
            spacing: 6,
            activeDotColor: AppColors.primary,
            dotColor: AppColors.lightGrey,
          ),
          onDotClicked: (i) => _carouselController.animateToPage(i),
        ),
        const SizedBox(height: 20),
      ],
    );
  }

  Widget _heroBtn(String label, {required bool filled}) {
    return ElevatedButton(
      onPressed: () => Navigator.pushNamed(context, '/shop'),
      style: ElevatedButton.styleFrom(
        backgroundColor: filled ? AppColors.white : Colors.transparent,
        foregroundColor: filled ? AppColors.primary : AppColors.white,
        elevation: 0,
        side: filled ? null : BorderSide(color: AppColors.white.withOpacity(0.6)),
        shape: const RoundedRectangleBorder(),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
        textStyle: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.w600, letterSpacing: 1),
      ),
      child: Text(label),
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
    final promos = [
      {'tag': 'LIMITED TIME OFFER', 'title': 'Spring / Summer\nCollection', 'discount': 'UP TO\n40% OFF', 'image': 'https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?w=600&q=80'},
      {'tag': 'BEST SELLERS', 'title': 'Top Picks\nFor Your Kids', 'image': 'https://images.unsplash.com/photo-1596870230751-ebdfce98ec42?w=600&q=80'},
      {'tag': 'PREMIUM QUALITY', 'title': 'Comfort\nThey Deserve', 'image': 'https://images.unsplash.com/photo-1604917621956-10dfa7cce2e7?w=600&q=80'},
    ];

    return Column(
      children: [
        SizedBox(
          height: 230,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: promos.length,
            itemBuilder: (_, index) {
              final promo = promos[index];
              return GestureDetector(
                onTap: () => Navigator.pushNamed(context, '/shop'),
                child: Container(
                  width: 210,
                  margin: const EdgeInsets.only(right: 12),
                  child: Stack(
                    fit: StackFit.expand,
                    children: [
                      CachedNetworkImage(imageUrl: promo['image'] as String, fit: BoxFit.cover),
                      Container(
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [Colors.transparent, Color(0xCC000000)],
                            stops: [0.25, 1.0],
                          ),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.end,
                          children: [
                            Text(promo['tag'] as String, style: GoogleFonts.inter(fontSize: 9, letterSpacing: 1.5, color: AppColors.white.withOpacity(0.8))),
                            const SizedBox(height: 6),
                            Text(promo['title'] as String, style: GoogleFonts.playfairDisplay(fontSize: 16, fontWeight: FontWeight.w600, color: AppColors.white, height: 1.3)),
                            if (promo['discount'] != null) ...[
                              const SizedBox(height: 4),
                              Text(promo['discount'] as String, style: GoogleFonts.inter(fontSize: 11, color: AppColors.white)),
                            ],
                            const SizedBox(height: 8),
                            Text('SHOP NOW →', style: GoogleFonts.inter(fontSize: 10, fontWeight: FontWeight.w600, color: AppColors.white, decoration: TextDecoration.underline)),
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
        color: AppColors.white,
        border: Border(top: BorderSide(color: AppColors.lightGrey), bottom: BorderSide(color: AppColors.lightGrey)),
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
        Icon(b['icon'] as IconData, color: AppColors.accent, size: 26),
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
