# Indistylex Flutter Mobile App - Complete Documentation

## Table of Contents
1. [Project Overview](#1-project-overview)
2. [Project Structure](#2-project-structure)
3. [Prerequisites & Environment Setup](#3-prerequisites--environment-setup)
4. [Android Build Guide](#4-android-build-guide)
5. [iOS Build Guide (Mac)](#5-ios-build-guide-mac)
6. [App Architecture](#6-app-architecture)
7. [API Integration](#7-api-integration)
8. [Features & Screens](#8-features--screens)
9. [Configuration](#9-configuration)
10. [Third-Party Services Setup](#10-third-party-services-setup)
11. [Customization](#11-customization)
12. [Play Store Submission](#12-play-store-submission)
13. [App Store Submission](#13-app-store-submission)
14. [Troubleshooting](#14-troubleshooting)

---

## 1. Project Overview

| Property | Value |
|----------|-------|
| App Name | Indistylex |
| Package ID | `com.indistylex.app` |
| Flutter SDK | 3.24.5 (stable) |
| Dart SDK | 3.5.4 |
| Min Android SDK | 21 (Android 5.0) |
| Target Android SDK | 35 (Android 15) |
| Min iOS | 12.0 |
| Backend | Flask API at `https://indistylex.com/api/v1/` |
| State Management | Provider (ChangeNotifier) |
| Architecture | Feature-first with services layer |

### Brand Identity
- **Primary Color**: #1A1A1A (Black)
- **Accent Color**: #C8A962 (Gold)
- **Background**: #F8F8F8 (Light Grey)
- **Heading Font**: Playfair Display (via Google Fonts)
- **Body Font**: Inter (via Google Fonts)

---

## 2. Project Structure

```
D:\indistylex_app\
├── android/                    # Android platform config
│   ├── app/
│   │   ├── build.gradle        # App-level Gradle config
│   │   ├── proguard-rules.pro  # R8/ProGuard rules
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       ├── kotlin/com/indistylex/app/MainActivity.kt
│   │       └── res/            # Launch icons, splash, styles
│   ├── build.gradle            # Project-level Gradle
│   ├── gradle.properties       # Gradle JVM args
│   └── gradle/wrapper/
│       └── gradle-wrapper.properties  # Gradle 8.11.1
├── ios/                        # iOS platform config
│   ├── Runner/
│   │   ├── AppDelegate.swift
│   │   ├── Info.plist
│   │   └── Assets.xcassets/    # App icons, launch images
│   ├── Runner.xcodeproj/
│   └── Runner.xcworkspace/
├── lib/                        # Main Dart source code
│   ├── main.dart               # Entry point
│   └── app/
│       ├── app.dart            # MaterialApp + routes
│       ├── constants/
│       │   ├── api_constants.dart   # All API endpoint URLs
│       │   └── app_constants.dart   # App config (keys, contact)
│       ├── models/
│       │   ├── cart.dart
│       │   ├── category.dart
│       │   ├── order.dart
│       │   ├── product.dart    # Product + ProductVariant
│       │   └── user.dart
│       ├── providers/
│       │   ├── auth_provider.dart
│       │   ├── cart_provider.dart
│       │   ├── order_provider.dart
│       │   ├── product_provider.dart
│       │   └── wishlist_provider.dart
│       ├── screens/
│       │   ├── splash_screen.dart
│       │   ├── auth/           # login, register
│       │   ├── home/           # home with banners + categories
│       │   ├── shop/           # product grid with filters
│       │   ├── product/        # product detail
│       │   ├── cart/           # shopping cart
│       │   ├── checkout/       # checkout + address
│       │   ├── order/          # orders list + detail
│       │   ├── profile/        # user profile
│       │   ├── wishlist/       # saved items
│       │   └── search/         # product search
│       ├── services/
│       │   └── api_service.dart  # HTTP client singleton
│       ├── theme/
│       │   └── app_theme.dart    # Colors, typography, themes
│       ├── utils/
│       │   └── helpers.dart      # Utility functions
│       └── widgets/
│           ├── bottom_nav.dart
│           ├── category_card.dart
│           ├── product_card.dart
│           └── section_header.dart
├── assets/
│   ├── images/                 # Logo, banners, placeholders
│   └── icons/                  # Custom SVG icons
├── test/
│   └── widget_test.dart
├── pubspec.yaml                # Dependencies & config
├── analysis_options.yaml       # Lint rules
└── build/                      # Build outputs
    └── app/outputs/flutter-apk/
        └── app-release.apk     # ← BUILT APK (23.8 MB)
```

---

## 3. Prerequisites & Environment Setup

### For Android (Windows/Linux/Mac)

| Requirement | Version | Download |
|-------------|---------|----------|
| Flutter SDK | 3.24.x | https://docs.flutter.dev/get-started/install |
| JDK | 17 (NOT higher) | https://jdk.java.net/17/ |
| Android SDK | 35 | Via Android Studio or cmdline-tools |
| Gradle | 8.11.1 | Auto-downloaded by wrapper |

### For iOS (Mac ONLY)

| Requirement | Version | Download |
|-------------|---------|----------|
| macOS | 13+ (Ventura) | - |
| Xcode | 15+ | Mac App Store |
| CocoaPods | Latest | `sudo gem install cocoapods` |
| Flutter SDK | 3.24.x | https://docs.flutter.dev/get-started/install |

### Windows Setup (Already Done)

```powershell
# Flutter location
D:\flutter\bin\flutter.exe

# JDK 17 location
D:\jdk17\jdk-17.0.2\

# Set PATH for every terminal session
$env:PATH = "D:\flutter\bin;D:\jdk17\jdk-17.0.2\bin;$env:PATH"
$env:JAVA_HOME = "D:\jdk17\jdk-17.0.2"

# Verify
flutter --version
java -version   # Must show 17.x.x
```

### Mac Setup (Fresh Install)

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Flutter
brew install flutter

# Install Xcode from App Store, then:
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
sudo xcodebuild -runFirstLaunch

# Install CocoaPods
sudo gem install cocoapods

# Verify everything
flutter doctor
```

---

## 4. Android Build Guide

### Step 1: Clone/Copy Project
```powershell
# If from Git
git clone https://github.com/indistylex-jpg/indistylex_app.git
cd indistylex_app

# Or copy the D:\indistylex_app folder
```

### Step 2: Set Environment
```powershell
# Windows
$env:PATH = "D:\flutter\bin;D:\jdk17\jdk-17.0.2\bin;$env:PATH"
$env:JAVA_HOME = "D:\jdk17\jdk-17.0.2"

# Linux/Mac
export PATH="$HOME/flutter/bin:$PATH"
export JAVA_HOME="/path/to/jdk-17"
```

### Step 3: Get Dependencies
```bash
flutter pub get
```

### Step 4: Build Debug APK (for testing)
```bash
flutter build apk --debug
# Output: build/app/outputs/flutter-apk/app-debug.apk
```

### Step 5: Build Release APK (for distribution)
```bash
flutter build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk
```

### Step 6: Build App Bundle (for Play Store)
```bash
flutter build appbundle --release
# Output: build/app/outputs/bundle/release/app-release.aab
```

### Step 7: Install on Connected Device
```bash
flutter install
# Or directly:
adb install build/app/outputs/flutter-apk/app-release.apk
```

### Current Build Output
```
Location: D:\indistylex_app\build\app\outputs\flutter-apk\app-release.apk
Size:     23.8 MB
Built:    June 2, 2026
Signed:   Debug key (replace for Play Store)
```

---

## 5. iOS Build Guide (Mac)

### Step 1: Transfer Project to Mac
```bash
# Option A: Git
git clone https://github.com/indistylex-jpg/indistylex_app.git
cd indistylex_app

# Option B: USB/Network copy from Windows
# Copy entire D:\indistylex_app\ folder to Mac
```

### Step 2: Install iOS Dependencies
```bash
flutter pub get
cd ios
pod install
cd ..
```

### Step 3: Open in Xcode (first time setup)
```bash
open ios/Runner.xcworkspace
```
In Xcode:
1. Select **Runner** in the left navigator
2. Under **Signing & Capabilities** tab:
   - Select your Team (Apple Developer account)
   - Set Bundle Identifier to: `com.indistylex.app`
   - Check "Automatically manage signing"
3. Close Xcode

### Step 4: Build for Testing (no signing required)
```bash
flutter build ios --debug --no-codesign
```

### Step 5: Build Release (requires Apple Developer Account - $99/year)
```bash
# Build unsigned (for manual signing)
flutter build ios --release --no-codesign

# Build IPA for App Store
flutter build ipa --release
# Output: build/ios/ipa/indistylex.ipa
```

### Step 6: Run on Simulator
```bash
# List available simulators
flutter devices

# Run on iPhone simulator
flutter run -d "iPhone 15 Pro"
```

### Step 7: Run on Physical iPhone
1. Connect iPhone via USB
2. Trust the computer on the phone
3. ```bash
   flutter run -d <device-id>
   ```

### iOS-Specific Configuration Files
| File | Purpose |
|------|---------|
| `ios/Runner/Info.plist` | App permissions, URL schemes |
| `ios/Runner/AppDelegate.swift` | App lifecycle, Firebase init |
| `ios/Podfile` | CocoaPods dependencies |
| `ios/Runner.xcodeproj/project.pbxproj` | Xcode project settings |

### iOS Permissions (already configured in Info.plist)
```xml
<key>NSCameraUsageDescription</key>
<string>Camera access for profile photo</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>Photo library access for profile photo</string>
```

---

## 6. App Architecture

### State Management: Provider Pattern

```
main.dart
  └── MultiProvider
        ├── AuthProvider      → Login, Register, Token management
        ├── ProductProvider   → Products, Categories, Search, Home data
        ├── CartProvider      → Cart CRUD, Coupon validation
        ├── WishlistProvider  → Toggle wishlist items
        └── OrderProvider     → Create order, Order history, Payment verify
```

### Data Flow
```
Screen (UI) 
  → Provider (Business Logic)
    → ApiService (HTTP Layer)
      → Flask Backend (https://indistylex.com/api/v1/)
        → Response JSON
      ← Parsed Model
    ← Notify Listeners
  ← Rebuild UI
```

### Network Layer
- **ApiService** (Singleton): Handles all HTTP requests
- **Auth**: JWT Bearer token stored in `flutter_secure_storage`
- **Auto-headers**: Content-Type, Accept, Authorization
- **Error handling**: Returns `{success: bool, data/message}`

---

## 7. API Integration

### Backend Details
| Property | Value |
|----------|-------|
| Server | Ubuntu 24.04 @ 138.201.50.228 |
| Domain | https://indistylex.com |
| API Base | https://indistylex.com/api/v1 |
| Auth | JWT Bearer Token |
| Framework | Flask + Gunicorn + Nginx |

### Endpoints Used

#### Authentication
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/auth/login` | Email/password login |
| POST | `/api/v1/auth/register` | New account (firstName, lastName, email, password) |
| POST | `/api/v1/auth/google` | Google OAuth login |
| GET | `/api/v1/auth/me` | Fetch current user profile |
| POST | `/api/v1/auth/forgot-password` | Password reset email |

#### Products
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/home` | Home page data (banners, featured, categories) |
| GET | `/api/v1/products` | All products (paginated) |
| GET | `/api/v1/products?q=query` | Search products |
| GET | `/api/v1/products?featured=1` | Featured products |
| GET | `/api/v1/products/<slug>` | Product detail |
| GET | `/api/v1/categories` | All categories |

#### Cart
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/cart` | Get user's cart |
| POST | `/api/v1/cart/add` | Add item (product_id, quantity, size, color) |
| PUT | `/api/v1/cart/update` | Update quantity |
| DELETE | `/api/v1/cart/remove` | Remove item |

#### Wishlist
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/wishlist` | Get wishlist items |
| POST | `/api/v1/wishlist/toggle` | Add/remove from wishlist |

#### Orders
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/orders` | Order history |
| POST | `/api/v1/orders/create` | Place new order |
| GET | `/api/v1/orders/<number>` | Order detail |
| POST | `/api/v1/orders/verify-payment` | Verify Razorpay payment |

#### Other
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/v1/coupons/validate` | Validate coupon code |
| GET | `/api/v1/addresses` | User addresses |

---

## 8. Features & Screens

### Screen Map

| Screen | Route | Features |
|--------|-------|----------|
| Splash | `/` (initial) | Logo animation → auto-login check |
| Home | `/home` | Banner carousel, categories, featured, new arrivals |
| Login | `/login` | Email/password + Google Sign-In |
| Register | `/register` | First name, last name, email, password |
| Shop | `/shop` | Product grid, category filter, sort |
| Product Detail | `/product` (args: id) | Images, variants (size/color), add to cart, wishlist |
| Cart | `/cart` | Items list, quantity, coupon, total |
| Checkout | `/checkout` | Address form, payment method |
| Orders | `/orders` | Order history list |
| Order Detail | `/order-detail` (args: id) | Full order info, status tracking |
| Profile | `/profile` | User info, edit profile, logout |
| Wishlist | `/wishlist` | Saved products grid |
| Search | `/search` | Real-time product search |

### Feature List
- ✅ JWT Authentication (login/register/logout)
- ✅ Google Sign-In
- ✅ Product browsing with categories
- ✅ Product search
- ✅ Product variants (size + color selection)
- ✅ Shopping cart with quantity management
- ✅ Coupon/discount code validation
- ✅ Wishlist (toggle add/remove)
- ✅ Razorpay payment integration
- ✅ Order placement and history
- ✅ User profile management
- ✅ Image caching (CachedNetworkImage)
- ✅ Loading shimmer effects
- ✅ Pull-to-refresh
- ✅ Dark theme support (configured, light default)
- ✅ Responsive design
- ✅ ProGuard/R8 minification (release builds)

---

## 9. Configuration

### Files to Update Before Production

#### 1. Razorpay Key
**File:** `lib/app/constants/app_constants.dart`
```dart
static const String razorpayKey = 'rzp_live_YOUR_ACTUAL_KEY';
```

#### 2. Google Sign-In
**Android:** Add `google-services.json` to `android/app/`
**iOS:** Add `GoogleService-Info.plist` to `ios/Runner/`

Get these from:
- Firebase Console → Project Settings → Your apps
- Google Cloud Console → OAuth 2.0 Client IDs

#### 3. Firebase Push Notifications
**Android:** Same `google-services.json` as above
**iOS:** 
- Enable Push Notifications in Xcode Capabilities
- Upload APNs key to Firebase Console

#### 4. Facebook Login
**Android:** `android/app/src/main/res/values/strings.xml`:
```xml
<string name="facebook_app_id">YOUR_FB_APP_ID</string>
<string name="fb_login_protocol_scheme">fbYOUR_FB_APP_ID</string>
<string name="facebook_client_token">YOUR_CLIENT_TOKEN</string>
```

#### 5. Release Signing Key (for Play Store)
```bash
# Generate keystore
keytool -genkey -v -keystore ~/indistylex-release.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias indistylex

# Create android/key.properties
storePassword=YOUR_PASSWORD
keyPassword=YOUR_PASSWORD
keyAlias=indistylex
storeFile=/path/to/indistylex-release.jks
```

Then update `android/app/build.gradle`:
```gradle
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}

android {
    ...
    signingConfigs {
        release {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile keystoreProperties['storeFile'] ? file(keystoreProperties['storeFile']) : null
            storePassword keystoreProperties['storePassword']
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

#### 6. App Icon
Place your logo at `assets/images/logo.png` (1024x1024, square), then:
```bash
flutter pub run flutter_launcher_icons
```

---

## 10. Third-Party Services Setup

### Razorpay (Payments)
1. Sign up at https://dashboard.razorpay.com
2. Get API Key ID from Settings → API Keys
3. Update `app_constants.dart` with `rzp_live_XXXXX`
4. Configure webhook at Razorpay Dashboard → Webhooks:
   - URL: `https://indistylex.com/api/v1/webhooks/razorpay`
   - Events: `payment.captured`, `payment.failed`

### Firebase (Push Notifications)
1. Go to https://console.firebase.google.com
2. Create project "Indistylex"
3. Add Android app: package `com.indistylex.app`
4. Download `google-services.json` → place in `android/app/`
5. Add iOS app: bundle ID `com.indistylex.app`
6. Download `GoogleService-Info.plist` → place in `ios/Runner/`

### Google Sign-In
1. Go to https://console.cloud.google.com
2. APIs & Services → Credentials
3. Create OAuth 2.0 Client ID:
   - Android: Package `com.indistylex.app` + SHA-1 fingerprint
   - iOS: Bundle ID `com.indistylex.app`
4. The `google-services.json` from Firebase handles Android config
5. For iOS, add reversed client ID to Info.plist URL schemes

### Get SHA-1 Fingerprint (for Google Sign-In)
```bash
# Debug
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android

# Release
keytool -list -v -keystore /path/to/indistylex-release.jks -alias indistylex
```

---

## 11. Customization

### Change API Base URL
**File:** `lib/app/constants/api_constants.dart`
```dart
static const String baseUrl = 'https://your-domain.com';
```

### Change App Colors
**File:** `lib/app/theme/app_theme.dart`
```dart
class AppColors {
  static const Color primary = Color(0xFF1A1A1A);  // Main color
  static const Color accent = Color(0xFFC8A962);   // Accent/gold
  static const Color background = Color(0xFFF8F8F8);
  // ... modify as needed
}
```

### Change App Name
1. **pubspec.yaml**: `name: indistylex`
2. **Android**: `android/app/src/main/AndroidManifest.xml` → `android:label="Indistylex"`
3. **iOS**: `ios/Runner/Info.plist` → `CFBundleDisplayName` → `Indistylex`

### Add New Screen
1. Create `lib/app/screens/your_screen/your_screen.dart`
2. Add route in `lib/app/app.dart`:
   ```dart
   '/your-route': (context) => const YourScreen(),
   ```
3. Navigate: `Navigator.pushNamed(context, '/your-route')`

### Add New API Endpoint
1. Add URL in `lib/app/constants/api_constants.dart`
2. Create/update provider in `lib/app/providers/`
3. Call from screen via `context.read<YourProvider>().yourMethod()`

---

## 12. Play Store Submission

### Prerequisites
- Google Play Developer Account ($25 one-time)
- Release keystore (see Section 9.5)
- App icon (512x512 for store listing)
- Feature graphic (1024x500)
- Screenshots (phone + tablet)
- Privacy policy URL

### Steps
1. **Build signed AAB:**
   ```bash
   flutter build appbundle --release
   ```
   Output: `build/app/outputs/bundle/release/app-release.aab`

2. **Go to** https://play.google.com/console

3. **Create app** → fill in:
   - App name: Indistylex
   - Default language: English
   - App category: Shopping
   - Free/Paid: Free

4. **Store listing:**
   - Short description: "Premium Kids Fashion - Shop the latest trends"
   - Full description: Feature list
   - Screenshots: At least 2 phone screenshots
   - Feature graphic: 1024x500 banner

5. **Upload AAB** in Production → Create new release

6. **Content rating:** Fill questionnaire (Shopping, no violence)

7. **Pricing & distribution:** Select countries

8. **Review & publish** (takes 1-7 days for first review)

### Version Updates
```bash
# Update version in pubspec.yaml
version: 1.0.1+2   # versionName+versionCode

# Rebuild
flutter build appbundle --release

# Upload new AAB to Play Console
```

---

## 13. App Store Submission

### Prerequisites
- Apple Developer Account ($99/year)
- Mac with Xcode 15+
- App icon (1024x1024, no alpha)
- Screenshots for all device sizes
- Privacy policy URL

### Steps
1. **Build IPA:**
   ```bash
   flutter build ipa --release
   ```
   Output: `build/ios/ipa/indistylex.ipa`

2. **Open Xcode Organizer:**
   ```bash
   open build/ios/archive/Runner.xcarchive
   ```

3. **Upload to App Store Connect:**
   - Use Xcode → Distribute App → App Store Connect
   - Or use `xcrun altool` CLI

4. **Go to** https://appstoreconnect.apple.com

5. **Create app:**
   - Name: Indistylex
   - Bundle ID: com.indistylex.app
   - SKU: indistylex-001

6. **App Information:**
   - Category: Shopping
   - Age Rating: 4+
   - Privacy Policy URL

7. **Screenshots:** Upload for iPhone 6.7", 6.5", 5.5" and iPad

8. **Submit for Review** (takes 1-3 days)

### Using Transporter (Alternative Upload)
```bash
# Install Transporter from Mac App Store
# Or use CLI:
xcrun altool --upload-app -f build/ios/ipa/indistylex.ipa \
  -t ios -u "your@apple.id" -p "app-specific-password"
```

---

## 14. Troubleshooting

### Common Build Issues

#### "Unsupported class file major version 70"
**Cause:** Java 26+ is too new for Gradle
**Fix:** Use JDK 17:
```bash
flutter config --jdk-dir="D:\jdk17\jdk-17.0.2"
# Or set JAVA_HOME
export JAVA_HOME=/path/to/jdk-17
```

#### "CarouselController imported from both..."
**Cause:** carousel_slider 4.x conflicts with Flutter 3.24
**Fix:** Already fixed - using carousel_slider ^5.0.0

#### "Missing classes: com.google.android.play.core"
**Cause:** R8 minification references Play Core
**Fix:** Already fixed in `proguard-rules.pro`:
```
-dontwarn com.google.android.play.core.**
```

#### "Kotlin incremental compilation: different roots"
**Cause:** Pub cache on C: drive, project on D: drive
**Fix:** Already fixed in `gradle.properties`:
```
kotlin.incremental=false
```

#### "flutter pub get" fails
```bash
flutter clean
flutter pub cache repair
flutter pub get
```

#### iOS "No signing certificate"
```bash
# In Xcode, go to Runner → Signing & Capabilities
# Select your team and enable "Automatically manage signing"
```

#### iOS CocoaPods issues
```bash
cd ios
rm -rf Pods Podfile.lock
pod install --repo-update
cd ..
flutter clean
flutter pub get
```

### Useful Commands
```bash
# Check environment
flutter doctor -v

# Clean all build artifacts
flutter clean

# Analyze code for errors
flutter analyze

# Run tests
flutter test

# List connected devices
flutter devices

# Run on specific device
flutter run -d <device-id>

# Build with verbose logging
flutter build apk --release --verbose

# Check outdated packages
flutter pub outdated
```

---

## Quick Reference Card

### Build Commands
| Command | Output |
|---------|--------|
| `flutter build apk --debug` | Debug APK for testing |
| `flutter build apk --release` | Release APK (23.8 MB) |
| `flutter build appbundle --release` | AAB for Play Store |
| `flutter build ios --release --no-codesign` | iOS build (no signing) |
| `flutter build ipa --release` | IPA for App Store |

### Key Files to Configure
| File | What to Change |
|------|---------------|
| `lib/app/constants/app_constants.dart` | Razorpay key, contact info |
| `lib/app/constants/api_constants.dart` | API base URL |
| `android/app/google-services.json` | Firebase (Android) |
| `ios/Runner/GoogleService-Info.plist` | Firebase (iOS) |
| `android/key.properties` | Release signing key |
| `assets/images/logo.png` | App icon source |

### Environment (Windows - Current Setup)
```powershell
$env:PATH = "D:\flutter\bin;D:\jdk17\jdk-17.0.2\bin;$env:PATH"
$env:JAVA_HOME = "D:\jdk17\jdk-17.0.2"
cd D:\indistylex_app
flutter build apk --release
```

---

*Documentation generated: June 2, 2026*
*App Version: 1.0.0+1*
*Flutter: 3.24.5 | Dart: 3.5.4 | Gradle: 8.11.1 | JDK: 17*
