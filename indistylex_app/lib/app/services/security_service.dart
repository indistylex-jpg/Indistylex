import 'package:flutter/foundation.dart';
import 'package:safe_device/safe_device.dart';

import '../constants/api_constants.dart';

/// Device and runtime security checks.
class SecurityService {
  static final SecurityService _instance = SecurityService._internal();
  factory SecurityService() => _instance;
  SecurityService._internal();

  SecurityReport? _cachedReport;

  /// Allowed API hosts — blocks traffic to unknown/malicious endpoints.
  static const allowedHosts = {'indistylex.com', 'www.indistylex.com'};

  Future<SecurityReport> runChecks({bool forceRefresh = false}) async {
    if (_cachedReport != null && !forceRefresh) return _cachedReport!;

    final threats = <String>[];

    if (kDebugMode) {
      _cachedReport = SecurityReport(isSecure: true, threats: const ['debug_mode']);
      return _cachedReport!;
    }

    try {
      final isJailBroken = await SafeDevice.isJailBroken;
      final isRealDevice = await SafeDevice.isRealDevice;
      final isMockLocation = await SafeDevice.isMockLocation;
      final isDevelopmentMode = await SafeDevice.isDevelopmentModeEnable;

      if (isJailBroken) threats.add('rooted_or_jailbroken');
      if (!isRealDevice) threats.add('emulator_detected');
      if (isMockLocation) threats.add('mock_location');
      if (isDevelopmentMode) threats.add('developer_mode');
    } catch (_) {
      // If check fails, allow app to run but log internally.
    }

    _cachedReport = SecurityReport(
      isSecure: threats.isEmpty,
      threats: threats,
    );
    return _cachedReport!;
  }

  /// Reject non-HTTPS or untrusted API hosts (MITM / proxy attacks).
  static bool isUrlAllowed(String url) {
    final uri = Uri.tryParse(url);
    if (uri == null) return false;
    if (uri.scheme != 'https') return false;
    return allowedHosts.contains(uri.host.toLowerCase());
  }

  static void assertUrlAllowed(String url) {
    if (!isUrlAllowed(url)) {
      throw SecurityException('Blocked request to untrusted host: $url');
    }
  }

  static bool isApiUrl(String url) {
    return url.startsWith(ApiConstants.apiUrl) || url.startsWith(ApiConstants.baseUrl);
  }

  String threatMessage(List<String> threats) {
    if (threats.contains('rooted_or_jailbroken')) {
      return 'This device appears to be rooted or jailbroken. For your safety, Indistylex cannot run on modified devices.';
    }
    if (threats.contains('emulator_detected')) {
      return 'Indistylex cannot run on emulators in production mode.';
    }
    if (threats.contains('mock_location')) {
      return 'Mock location detected. Please disable fake GPS apps to continue.';
    }
    if (threats.contains('developer_mode')) {
      return 'Developer options are enabled. Disable USB debugging for secure shopping.';
    }
    return 'Security check failed. Please use a secure device.';
  }
}

class SecurityReport {
  final bool isSecure;
  final List<String> threats;

  const SecurityReport({required this.isSecure, required this.threats});
}

class SecurityException implements Exception {
  final String message;
  SecurityException(this.message);

  @override
  String toString() => message;
}
