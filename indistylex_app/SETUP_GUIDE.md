# Indistylex Flutter App - Setup & Build Guide

## Overview
Complete e-commerce mobile application for **Indistylex** (Premium Kids Fashion) built with Flutter for Android & iOS. Connects to the existing Flask backend at `https://indistylex.com`.

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Setup Steps](#setup-steps)
4. [Running the App](#running-the-app)
5. [Building for Production](#building-for-production)
6. [API Integration](#api-integration)
7. [Features](#features)
8. [Customization](#customization)

---

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Flutter SDK | 3.24+ | Cross-platform framework |
| Dart SDK | 3.0+ | Comes with Flutter |
| Android Studio | Latest | Android build tools, emulator |
| Xcode | 15+ | iOS builds (macOS only) |
| VS Code | Latest | IDE with Flutter extension |
| Git | Latest | Version control |

---

## Project Structure

```
indistylex_app/
├── lib/
│   ├── main.dart                 # App entry point
│   └── app/
│       ├── app.dart              # App widget, routing
│       ├── constants/
│       │   ├── api_constants.dart    # API endpoints
│       │   └── app_constants.dart    # App-wide constants
│       ├── models/
│       │   ├── product.dart      # Product model
│       │   ├── category.dart     # Category model
│       │   ├── cart.dart         # Cart & CartItem models
│       │   ├── order.dart        # Order & OrderItem models
│       │   └── user.dart         # User model
│       ├── providers/
│       │   ├── auth_provider.dart     # Authentication state
│       │   ├── cart_provider.dart     # Cart state
│       │   ├── order_provider.dart    # Orders state
│       │   ├── product_provider.dart  # Products state
│       │   └── wishlist_provider.dart # Wishlist state
│       ├── screens/
│       │   ├── splash_screen.dart     # Splash/loading screen
│       │   ├── home/home_screen.dart  # Home with banners, featured
│       │   ├── auth/
│       │   │   ├── login_screen.dart
│       │   │   └── register_screen.dart
│       │   ├── shop/shop_screen.dart  # Product listing with filters
│       │   ├── product/product_detail_screen.dart
│       │   ├── cart/cart_screen.dart
│       │   ├── checkout/checkout_screen.dart
│       │   ├── order/
│       │   │   ├── orders_screen.dart
│       │   │   └── order_detail_screen.dart
│       │   ├── profile/profile_screen.dart
│       │   ├── wishlist/wishlist_screen.dart
│       │   └── search/search_screen.dart
│       ├── services/
│       │   └── api_service.dart   # HTTP client with auth
│       ├── theme/
│       │   └── app_theme.dart     # Colors, typography, theme
│       └── widgets/
│           ├── bottom_nav.dart    # Bottom navigation bar
│           ├── category_card.dart # Category circle card
│           ├── product_card.dart  # Product grid card
│           └── section_header.dart
├── assets/
│   ├── fonts/                    # Playfair Display font files
│   ├── images/                   # App images, logo
│   └── icons/                    # Custom icons
├── android/                      # Android platform code
├── ios/                          # iOS platform code
├── pubspec.yaml                  # Dependencies
└── README.md
```

---

## Setup Steps

### Step 1: Install Flutter SDK

**Windows:**
```powershell
# Option A: Download from https://docs.flutter.dev/get-started/install/windows
# Extract to D:\flutter and add D:\flutter\bin to PATH

# Option B: Using Chocolatey
choco install flutter

# Option C: Using winget (if available)
winget install Flutter.Flutter
```

**Verify installation:**
```bash
flutter doctor
```

### Step 2: Clone / Navigate to Project
```bash
cd D:\indistylex_app
```

### Step 3: Install Dependencies
```bash
flutter pub get
```

### Step 4: Add Font Assets
Download Playfair Display font files and place in `assets/fonts/`:
- PlayfairDisplay-Regular.ttf
- PlayfairDisplay-Bold.ttf
- PlayfairDisplay-SemiBold.ttf

### Step 5: Configure Android
1. Open `android/app/build.gradle`
2. Ensure `minSdkVersion` is 21+
3. Add internet permission in `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.INTERNET"/>
```

### Step 6: Configure iOS (macOS only)
1. Open `ios/Runner.xcworkspace` in Xcode
2. Set minimum iOS deployment target to 12.0
3. Add to `ios/Runner/Info.plist`:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

### Step 7: Setup Razorpay (Payment)
1. Get Razorpay API keys from https://dashboard.razorpay.com
2. Update `lib/app/constants/app_constants.dart`:
```dart
static const String razorpayKey = 'rzp_live_YOUR_KEY';
```

### Step 8: Setup Firebase (Push Notifications)
1. Create Firebase project at https://console.firebase.google.com
2. Add Android app with package name `com.indistylex.app`
3. Download `google-services.json` → `android/app/`
4. Add iOS app, download `GoogleService-Info.plist` → `ios/Runner/`

---

## Running the App

### Android
```bash
# List available devices
flutter devices

# Run on connected device/emulator
flutter run

# Run on specific device
flutter run -d <device_id>
```

### iOS (macOS only)
```bash
flutter run -d iphone
```

### Web (for testing)
```bash
flutter run -d chrome
```

---

## Building for Production

### Android APK
```bash
# Debug APK
flutter build apk --debug

# Release APK (single file)
flutter build apk --release

# Split APKs (smaller downloads)
flutter build apk --split-per-abi
```
Output: `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (for Play Store)
```bash
flutter build appbundle --release
```
Output: `build/app/outputs/bundle/release/app-release.aab`

### iOS (macOS only)
```bash
flutter build ios --release
```
Then archive in Xcode for App Store submission.

---

## API Integration

The app connects to the Flask backend at `https://indistylex.com/api/`.

### Endpoints Used:
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/auth/login` | POST | User login |
| `/api/auth/register` | POST | User registration |
| `/api/user/profile` | GET/PUT | Get/update profile |
| `/api/products` | GET | List products (with filters) |
| `/api/products/{id}` | GET | Product detail |
| `/api/products/featured` | GET | Featured products |
| `/api/products/new-arrivals` | GET | New arrivals |
| `/api/products/search` | GET | Search products |
| `/api/categories` | GET | All categories |
| `/api/cart` | GET | Get cart |
| `/api/cart/add` | POST | Add to cart |
| `/api/cart/update` | PUT | Update quantity |
| `/api/cart/remove` | POST | Remove item |
| `/api/wishlist` | GET | Get wishlist |
| `/api/wishlist/add` | POST | Add to wishlist |
| `/api/wishlist/remove` | POST | Remove from wishlist |
| `/api/orders` | GET | List orders |
| `/api/orders/create` | POST | Place order |
| `/api/checkout/apply-coupon` | POST | Apply coupon |
| `/api/checkout/verify-payment` | POST | Verify Razorpay payment |

### Authentication:
- JWT Bearer token stored in secure storage
- Sent via `Authorization: Bearer <token>` header
- Auto-redirect to login on 401

---

## Features

### Implemented:
- [x] Splash screen with brand animation
- [x] Home screen (hero banner carousel, categories, featured, new arrivals)
- [x] Product browsing with category filters & sorting
- [x] Product detail (images, sizes, colors, quantity, reviews)
- [x] Shopping cart (add, update qty, remove, coupon code)
- [x] Wishlist (add/remove favorites)
- [x] User authentication (login, register)
- [x] Checkout (address, payment method selection)
- [x] Order history & order detail with status timeline
- [x] User profile management
- [x] Product search
- [x] Bottom navigation with cart badge
- [x] Pull-to-refresh
- [x] Infinite scroll pagination
- [x] Responsive grid layouts

### Brand Design:
- **Primary:** #1A1A1A (Black)
- **Accent:** #C8A962 (Gold)
- **Fonts:** Playfair Display (headings), Inter (body)
- **Style:** Premium, minimal, luxury kids fashion

---

## Customization

### Change API Base URL
Edit `lib/app/constants/api_constants.dart`:
```dart
static const String baseUrl = 'https://your-domain.com';
```

### Change Brand Colors
Edit `lib/app/theme/app_theme.dart`:
```dart
static const Color primary = Color(0xFF1A1A1A);
static const Color accent = Color(0xFFC8A962);
```

### Add New Screens
1. Create screen file in `lib/app/screens/`
2. Add route in `lib/app/app.dart`
3. Navigate using `Navigator.pushNamed(context, '/route')`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `flutter pub get` fails | Run `flutter clean` then retry |
| Android build fails | Run `flutter doctor` to check SDK |
| iOS build fails | Run `pod install` in `ios/` directory |
| API connection fails | Check internet & base URL |
| Images not loading | Verify image paths on server |

---

## Play Store / App Store Submission

### Android (Google Play):
1. Create keystore: `keytool -genkey -v -keystore indistylex-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias indistylex`
2. Configure signing in `android/app/build.gradle`
3. Build: `flutter build appbundle --release`
4. Upload `.aab` to Google Play Console

### iOS (App Store):
1. Configure signing in Xcode (Apple Developer account required)
2. Build: `flutter build ios --release`
3. Archive in Xcode → Upload to App Store Connect

---

## Contact & Support
- Website: https://indistylex.com
- Email: indistylex@gmail.com
- Phone: +91 6394142176
