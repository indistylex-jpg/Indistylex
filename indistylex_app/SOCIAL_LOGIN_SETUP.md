# Google & Facebook Login Setup

## Google Sign-In

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials:
   - **Web client** — use this as `GOOGLE_CLIENT_ID` on your server (.env)
   - **Android client** — package name: `com.indistylex.app`, SHA-1 from your keystore
3. Update `lib/app/constants/app_constants.dart`:
   ```dart
   static const String googleWebClientId = 'YOUR_WEB_CLIENT_ID.apps.googleusercontent.com';
   ```
4. Server `.env` must have the same Web client ID:
   ```
   GOOGLE_CLIENT_ID=your-web-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-secret
   ```

Get SHA-1 for debug:
```bash
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android -keypass android
```

## Facebook Login

1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Create an app → add **Facebook Login** product
3. Add Android platform:
   - Package: `com.indistylex.app`
   - Class: `com.indistylex.app.MainActivity`
   - Key hashes (debug + release SHA-1 converted to base64)
4. Update these files with your App ID:
   - `lib/app/constants/app_constants.dart` → `facebookAppId`
   - `android/app/src/main/res/values/strings.xml` → `facebook_app_id`, `fb_login_protocol_scheme`
   - `android/app/src/main/AndroidManifest.xml` → `ClientToken`
5. Server `.env`:
   ```
   FACEBOOK_APP_ID=your-app-id
   FACEBOOK_APP_SECRET=your-app-secret
   ```
6. Deploy updated backend (includes `/api/v1/auth/facebook` endpoint)

## Test

```bash
flutter run
```

Sign in with email, Google, or Facebook from Profile → Sign In.
