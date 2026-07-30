class ApiConstants {
  static const String baseUrl = 'https://indistylex.com';
  static const String apiUrl = '$baseUrl/api/v1';

  // Auth
  static const String login = '$apiUrl/auth/login';
  static const String register = '$apiUrl/auth/register';
  static const String googleAuth = '$apiUrl/auth/google';
  static const String facebookAuth = '$apiUrl/auth/facebook';
  static const String profile = '$apiUrl/auth/me';
  static const String updateProfile = '$apiUrl/profile';
  static const String changePassword = '$apiUrl/profile/change-password';

  // Home (combined endpoint)
  static const String homeData = '$apiUrl/home';

  // Products
  static const String products = '$apiUrl/products';
  static const String categories = '$apiUrl/categories';
  // Product detail: GET /products/<slug>
  // Product search: GET /products?q=<query>
  // Featured: GET /products?featured=1
  // New arrivals: sorted by newest by default

  // Cart
  static const String cart = '$apiUrl/cart';
  static const String addToCart = '$apiUrl/cart/add';
  static const String updateCart = '$apiUrl/cart/update';
  static const String removeFromCart = '$apiUrl/cart/remove';

  // Wishlist
  static const String wishlist = '$apiUrl/wishlist';
  static const String toggleWishlist = '$apiUrl/wishlist/toggle';

  // Orders
  static const String orders = '$apiUrl/orders';
  static const String createOrder = '$apiUrl/orders/create';
  // Order detail: GET /orders/<order_number>

  // Coupons
  static const String validateCoupon = '$apiUrl/coupons/validate';

  // Auth extras
  static const String forgotPassword = '$apiUrl/auth/forgot-password';

  // Payment
  static const String verifyPayment = '$apiUrl/orders/verify-payment';

  // Addresses
  static const String addresses = '$apiUrl/addresses';

  // Images
  static String resolveImageUrl(String? path) {
    if (path == null || path.isEmpty) return '';
    if (path.startsWith('http')) return path;
    if (path.startsWith('/')) return '$baseUrl$path';
    return '$baseUrl/static/uploads/$path';
  }

  static String productImage(String filename) => resolveImageUrl(filename);
  static String categoryImage(String filename) => resolveImageUrl(filename);
}
