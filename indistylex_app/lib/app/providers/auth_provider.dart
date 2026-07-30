import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:flutter_facebook_auth/flutter_facebook_auth.dart';

import '../models/user.dart';
import '../services/api_service.dart';
import '../constants/api_constants.dart';
import '../constants/app_constants.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  final _storage = const FlutterSecureStorage();

  User? _user;
  bool _isLoading = false;
  String? _error;
  bool _isLoggedIn = false;

  User? get user => _user;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _isLoggedIn;

  Future<void> init() async {
    final token = await _storage.read(key: AppConstants.tokenKey);
    if (token != null) {
      _isLoggedIn = true;
      await fetchProfile();
    }
    notifyListeners();
  }

  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final response = await _api.post(ApiConstants.login, body: {
      'email': email,
      'password': password,
    });

    _isLoading = false;
    return await _handleAuthResponse(response);
  }

  Future<bool> register(
      String firstName, String lastName, String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    final response = await _api.post(ApiConstants.register, body: {
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'password': password,
    });

    _isLoading = false;
    return await _handleAuthResponse(response);
  }

  Future<bool> signInWithGoogle() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final googleSignIn = GoogleSignIn(
        serverClientId: AppConstants.googleWebClientId.contains('YOUR_')
            ? null
            : AppConstants.googleWebClientId,
        scopes: ['email', 'profile'],
      );

      final account = await googleSignIn.signIn();
      if (account == null) {
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final auth = await account.authentication;
      final idToken = auth.idToken;
      if (idToken == null) {
        _error = 'Could not get Google ID token. Check your Google Client ID setup.';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final response = await _api.post(ApiConstants.googleAuth, body: {
        'id_token': idToken,
      });

      _isLoading = false;
      return await _handleAuthResponse(response);
    } catch (e) {
      _error = 'Google sign-in failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> signInWithFacebook() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final result = await FacebookAuth.instance.login(
        permissions: ['email', 'public_profile'],
      );

      if (result.status != LoginStatus.success) {
        _error = result.message ?? 'Facebook login cancelled';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final accessToken = result.accessToken?.token;
      if (accessToken == null) {
        _error = 'Could not get Facebook access token';
        _isLoading = false;
        notifyListeners();
        return false;
      }

      final response = await _api.post(ApiConstants.facebookAuth, body: {
        'access_token': accessToken,
      });

      _isLoading = false;

      if (!response['success'] &&
          (response['message']?.contains('404') == true ||
              response['message']?.toLowerCase().contains('not found') == true)) {
        _error =
            'Facebook login requires server setup. Add /api/v1/auth/facebook endpoint on your backend.';
        notifyListeners();
        return false;
      }

      return await _handleAuthResponse(response);
    } catch (e) {
      _error = 'Facebook sign-in failed: $e';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  Future<bool> _handleAuthResponse(Map<String, dynamic> response) async {
    if (response['success']) {
      final data = response['data'];
      await _api.saveToken(data['token']);
      _user = User.fromJson(data['user']);
      _isLoggedIn = true;
      await _storage.write(key: AppConstants.userKey, value: jsonEncode(data['user']));
      notifyListeners();
      return true;
    } else {
      _error = response['message'];
      notifyListeners();
      return false;
    }
  }

  Future<void> fetchProfile() async {
    final response = await _api.get(ApiConstants.profile);
    if (response['success']) {
      final userData = response['data']['user'] ?? response['data'];
      _user = User.fromJson(userData);
      notifyListeners();
    }
  }

  Future<bool> updateProfile(Map<String, dynamic> data) async {
    _isLoading = true;
    notifyListeners();

    final response = await _api.put(ApiConstants.profile, body: data);
    _isLoading = false;

    if (response['success']) {
      final userData = response['data']['user'] ?? response['data'];
      _user = User.fromJson(userData);
      notifyListeners();
      return true;
    }
    _error = response['message'];
    notifyListeners();
    return false;
  }

  Future<bool> forgotPassword(String email) async {
    final response = await _api.post(ApiConstants.forgotPassword, body: {
      'email': email,
    });
    return response['success'];
  }

  Future<void> logout() async {
    await _api.clearToken();
    await _storage.delete(key: AppConstants.userKey);
    try {
      await GoogleSignIn().signOut();
      await FacebookAuth.instance.logOut();
    } catch (_) {}
    _user = null;
    _isLoggedIn = false;
    notifyListeners();
  }
}
