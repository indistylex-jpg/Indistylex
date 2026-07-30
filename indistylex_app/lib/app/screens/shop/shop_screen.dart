import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../theme/app_theme.dart';
import '../../providers/product_provider.dart';
import '../../widgets/product_card.dart';
import '../../widgets/site_header.dart';
import '../../widgets/site_footer.dart';

class ShopScreen extends StatefulWidget {
  const ShopScreen({super.key});

  @override
  State<ShopScreen> createState() => _ShopScreenState();
}

class _ShopScreenState extends State<ShopScreen> {
  String? _selectedCategorySlug;
  String _sortBy = 'newest';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) => _initFromArgs());
  }

  void _initFromArgs() {
    final args = ModalRoute.of(context)?.settings.arguments;
    if (args is Map) {
      if (args['category'] != null) _selectedCategorySlug = args['category'] as String;
      if (args['sort'] != null) _sortBy = args['sort'] as String;
    }
    _loadProducts(refresh: true);
    context.read<ProductProvider>().fetchCategories();
  }

  void _loadProducts({bool refresh = false}) {
    context.read<ProductProvider>().fetchProducts(
          refresh: refresh,
          categorySlug: _selectedCategorySlug,
          sort: _sortBy,
        );
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const SiteHeader(),
        Expanded(
          child: Consumer<ProductProvider>(
            builder: (context, provider, _) {
              return Column(
                children: [
                  _buildToolbar(provider),
                  if (provider.categories.isNotEmpty) _buildCategoryChips(provider),
                  Expanded(
                    child: provider.isLoading && provider.products.isEmpty
                        ? const Center(child: CircularProgressIndicator(color: AppColors.accent))
                        : provider.products.isEmpty
                            ? Center(
                                child: Text('No products found', style: GoogleFonts.inter(color: AppColors.muted)),
                              )
                            : NotificationListener<ScrollNotification>(
                                onNotification: (n) {
                                  if (n is ScrollEndNotification && n.metrics.extentAfter < 300) {
                                    _loadProducts();
                                  }
                                  return false;
                                },
                                child: ListView(
                                  children: [
                                    Padding(
                                      padding: const EdgeInsets.fromLTRB(16, 8, 16, 0),
                                      child: Text(
                                        '${provider.products.length} Products',
                                        style: GoogleFonts.inter(fontSize: 12, color: AppColors.muted),
                                      ),
                                    ),
                                    GridView.builder(
                                      shrinkWrap: true,
                                      physics: const NeverScrollableScrollPhysics(),
                                      padding: const EdgeInsets.all(16),
                                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                                        crossAxisCount: 2,
                                        childAspectRatio: 0.58,
                                        crossAxisSpacing: 12,
                                        mainAxisSpacing: 16,
                                      ),
                                      itemCount: provider.products.length,
                                      itemBuilder: (_, i) => ProductCard(
                                        product: provider.products[i],
                                        showWishlistButton: true,
                                      ),
                                    ),
                                    if (provider.isLoading)
                                      const Padding(
                                        padding: EdgeInsets.all(16),
                                        child: Center(child: CircularProgressIndicator(color: AppColors.accent)),
                                      ),
                                    const SiteFooter(),
                                  ],
                                ),
                              ),
                  ),
                ],
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildToolbar(ProductProvider provider) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
      child: Row(
        children: [
          Text('SHOP', style: GoogleFonts.playfairDisplay(fontSize: 22, fontWeight: FontWeight.w600)),
          const Spacer(),
          IconButton(icon: const Icon(Icons.tune, size: 20), onPressed: _showFilterSheet),
          IconButton(icon: const Icon(Icons.sort, size: 20), onPressed: _showSortSheet),
        ],
      ),
    );
  }

  Widget _buildCategoryChips(ProductProvider provider) {
    return SizedBox(
      height: 44,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          _chip('All', _selectedCategorySlug == null, () {
            setState(() => _selectedCategorySlug = null);
            _loadProducts(refresh: true);
          }),
          ...provider.categories.map((c) => _chip(c.name, _selectedCategorySlug == c.slug, () {
            setState(() => _selectedCategorySlug = c.slug);
            _loadProducts(refresh: true);
          })),
        ],
      ),
    );
  }

  Widget _chip(String label, bool selected, VoidCallback onTap) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label, style: GoogleFonts.inter(fontSize: 12)),
        selected: selected,
        selectedColor: AppColors.accent,
        labelStyle: TextStyle(color: selected ? AppColors.primary : AppColors.muted, fontWeight: selected ? FontWeight.w600 : FontWeight.normal),
        onSelected: (_) => onTap(),
      ),
    );
  }

  void _showSortSheet() {
    showModalBottomSheet(
      context: context,
      builder: (_) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text('Sort By', style: GoogleFonts.playfairDisplay(fontSize: 18, fontWeight: FontWeight.w600)),
          ),
          _sortTile('newest', 'Newest First'),
          _sortTile('price_low', 'Price: Low to High'),
          _sortTile('price_high', 'Price: High to Low'),
          _sortTile('popular', 'Most Popular'),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _sortTile(String value, String label) {
    return ListTile(
      title: Text(label),
      trailing: _sortBy == value ? const Icon(Icons.check, color: AppColors.accent) : null,
      onTap: () {
        setState(() => _sortBy = value);
        Navigator.pop(context);
        _loadProducts(refresh: true);
      },
    );
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => const _FilterSheet(),
    );
  }
}

class _FilterSheet extends StatefulWidget {
  const _FilterSheet();

  @override
  State<_FilterSheet> createState() => _FilterSheetState();
}

class _FilterSheetState extends State<_FilterSheet> {
  RangeValues _priceRange = const RangeValues(0, 5000);

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Filters', style: GoogleFonts.playfairDisplay(fontSize: 18, fontWeight: FontWeight.w600)),
          const SizedBox(height: 24),
          const Text('Price Range', style: TextStyle(fontWeight: FontWeight.w500)),
          RangeSlider(
            values: _priceRange,
            min: 0,
            max: 10000,
            divisions: 100,
            activeColor: AppColors.accent,
            labels: RangeLabels('₹${_priceRange.start.round()}', '₹${_priceRange.end.round()}'),
            onChanged: (v) => setState(() => _priceRange = v),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                context.read<ProductProvider>().fetchProducts(
                      refresh: true,
                      minPrice: _priceRange.start,
                      maxPrice: _priceRange.end,
                    );
              },
              child: const Text('Apply Filters'),
            ),
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
