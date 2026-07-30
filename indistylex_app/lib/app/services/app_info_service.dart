import 'package:package_info_plus/package_info_plus.dart';

/// Cached app version/build info from pubspec.
class AppInfoService {
  static final AppInfoService _instance = AppInfoService._internal();
  factory AppInfoService() => _instance;
  AppInfoService._internal();

  PackageInfo? _info;

  Future<void> init() async {
    _info = await PackageInfo.fromPlatform();
  }

  String get version => _info?.version ?? '1.0.0';
  String get buildNumber => _info?.buildNumber ?? '1';
  String get appName => _info?.appName ?? 'Indistylex';
  String get packageName => _info?.packageName ?? 'com.indistylex.app';

  String get fullVersion => 'v$version ($buildNumber)';
  String get displayVersion => 'Version $version';
}
