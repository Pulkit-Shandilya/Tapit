import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:flutter/foundation.dart';

class ProfileData {
  final String userId;
  final String firstName;
  final String lastName;
  final int? age;
  final String phoneNumber;
  final String email;
  final double balance;
  final bool balanceLocked;

  const ProfileData({
    required this.userId,
    required this.firstName,
    required this.lastName,
    required this.age,
    required this.phoneNumber,
    required this.email,
    required this.balance,
    required this.balanceLocked,
  });

  String get displayName {
    final name = '$firstName $lastName'.trim();
    return name.isEmpty ? 'TapIt User' : name;
  }

  factory ProfileData.fromJson(Map<String, dynamic> json) {
    final profile = json['profile'] as Map<String, dynamic>? ?? json;
    return ProfileData(
      userId: profile['user_id'] as String? ?? ProfileService.userId,
      firstName: profile['first_name'] as String? ?? 'TapIt',
      lastName: profile['last_name'] as String? ?? 'User',
      age: profile['age'] is int
          ? profile['age'] as int
          : int.tryParse('${profile['age'] ?? ''}'),
      phoneNumber: profile['phone_number'] as String? ?? '',
      email: profile['email'] as String? ?? '',
      balance: (json['balance'] as num?)?.toDouble() ??
          (profile['wallet_balance'] as num?)?.toDouble() ??
          0,
      balanceLocked: json['balance_locked'] as bool? ?? true,
    );
  }
}

class ProfileUpdateRequest {
  final String firstName;
  final String lastName;
  final int? age;
  final String phoneNumber;
  final String email;

  const ProfileUpdateRequest({
    required this.firstName,
    required this.lastName,
    required this.age,
    required this.phoneNumber,
    required this.email,
  });

  Map<String, dynamic> toJson() {
    return {
      'first_name': firstName,
      'last_name': lastName,
      'age': age,
      'phone_number': phoneNumber,
      'email': email,
    };
  }
}

class ProfileService {
  ProfileService._();

  static const String baseUrl = String.fromEnvironment(
    'TAPIT_API_BASE_URL',
    defaultValue: 'http://127.0.0.1:5000',
  );

  static const String userId = String.fromEnvironment(
    'TAPIT_USER_ID',
    defaultValue: 'user_primary',
  );
  static final ValueNotifier<double> balanceNotifier = ValueNotifier<double>(0);
  static bool _balanceLoaded = false;

  static Uri _profileUri([String? suffix]) {
    final path = '/api/users/profile/$userId${suffix ?? ''}';
    return Uri.parse('$baseUrl$path');
  }

  static Future<ProfileData> fetchProfile() async {
    final response = await http.get(_profileUri());
    if (response.statusCode != 200) {
      throw Exception('Failed to load profile (${response.statusCode})');
    }

    final profile = ProfileData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
    if (!_balanceLoaded) {
      balanceNotifier.value = profile.balance;
      _balanceLoaded = true;
    }
    return profile;
  }

  static Future<ProfileData> updateProfile(ProfileUpdateRequest request) async {
    final response = await http.put(
      _profileUri(),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode(request.toJson()),
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to update profile (${response.statusCode})');
    }

    return ProfileData.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  static Future<double> fetchBalance() async {
    final response = await http.get(_profileUri('/balance'));
    if (response.statusCode != 200) {
      throw Exception('Failed to load balance (${response.statusCode})');
    }

    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    final balance = (decoded['balance'] as num?)?.toDouble() ?? 0;
    balanceNotifier.value = balance;
    _balanceLoaded = true;
    return balance;
  }

  static Future<double> refreshBalance() async {
    return fetchBalance();
  }
}