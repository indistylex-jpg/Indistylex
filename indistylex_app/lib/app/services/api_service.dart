import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';

import '../constants/app_constants.dart';
import 'security_service.dart';
import 'app_info_service.dart';

typedef UnauthorizedCallback = void Function();

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  static const _requestTimeout = Duration(seconds: 30);

  final _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  UnauthorizedCallback? onUnauthorized;

  Future<String?> get _token async {
    return await _storage.read(key: AppConstants.tokenKey);
  }

  Future<Map<String, String>> get _headers async {
    final token = await _token;
    final info = AppInfoService();
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'X-App-Version': info.version,
      'X-App-Build': info.buildNumber,
      'X-App-Platform': Platform.isAndroid ? 'android' : 'ios',
      'X-Request-ID': const Uuid().v4(),
      if (token != null) 'Authorization': 'Bearer $token',
    };
  }

  Future<Map<String, dynamic>> get(String url,
      {Map<String, String>? queryParams}) async {
    return _request('GET', url, queryParams: queryParams);
  }

  Future<Map<String, dynamic>> post(String url,
      {Map<String, dynamic>? body}) async {
    return _request('POST', url, body: body);
  }

  Future<Map<String, dynamic>> put(String url,
      {Map<String, dynamic>? body}) async {
    return _request('PUT', url, body: body);
  }

  Future<Map<String, dynamic>> delete(String url) async {
    return _request('DELETE', url);
  }

  Future<Map<String, dynamic>> _request(
    String method,
    String url, {
    Map<String, String>? queryParams,
    Map<String, dynamic>? body,
  }) async {
    try {
      if (SecurityService.isApiUrl(url)) {
        SecurityService.assertUrlAllowed(url);
      }

      final uri = Uri.parse(url).replace(queryParameters: queryParams);
      final headers = await _headers;

      final Future<http.Response> request;
      switch (method) {
        case 'GET':
          request = http.get(uri, headers: headers);
        case 'POST':
          request = http.post(uri, headers: headers, body: body != null ? jsonEncode(body) : null);
        case 'PUT':
          request = http.put(uri, headers: headers, body: body != null ? jsonEncode(body) : null);
        case 'DELETE':
          request = http.delete(uri, headers: headers);
        default:
          return {'success': false, 'message': 'Unsupported method'};
      }

      final response = await request.timeout(_requestTimeout);
      return _handleResponse(response);
    } on SecurityException catch (e) {
      if (kDebugMode) debugPrint('Security blocked: $e');
      return {'success': false, 'message': 'Secure connection required'};
    } on TimeoutException {
      return {'success': false, 'message': 'Request timed out. Please try again.'};
    } catch (e) {
      return {'success': false, 'message': 'Connection error. Check your network.'};
    }
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final data = jsonDecode(response.body);
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return {'success': true, 'data': data};
      } else if (response.statusCode == 401) {
        _handleUnauthorized();
        return {
          'success': false,
          'message': 'Session expired. Please login again.',
          'unauthorized': true,
        };
      } else {
        return {
          'success': false,
          'message': data['message'] ?? data['error'] ?? 'Something went wrong',
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Invalid response from server'};
    }
  }

  Future<void> _handleUnauthorized() async {
    await clearToken();
    onUnauthorized?.call();
  }

  Future<void> saveToken(String token) async {
    await _storage.write(key: AppConstants.tokenKey, value: token);
  }

  Future<void> clearToken() async {
    await _storage.delete(key: AppConstants.tokenKey);
  }

  Future<bool> isLoggedIn() async {
    final token = await _token;
    return token != null && token.isNotEmpty;
  }
}
