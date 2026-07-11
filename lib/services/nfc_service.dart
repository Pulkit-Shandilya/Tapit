import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class NFCService {
  static final NFCService _instance = NFCService._internal();
  static const MethodChannel _channel = MethodChannel('tapit/nfc');

  factory NFCService() {
    return _instance;
  }

  NFCService._internal();

  final StreamController<NFCMessage> _messageController =
      StreamController<NFCMessage>.broadcast();

  Stream<NFCMessage> get messageStream => _messageController.stream;
  bool _isSessionActive = false;

  Future<bool> isNFCAvailable() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      return false;
    }

    try {
      return await _channel.invokeMethod<bool>('isAvailable') ?? false;
    } catch (_) {
      return false;
    }
  }

  Future<void> preparePeerReceive(NFCMessage message) async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      throw Exception('Peer NFC is only available on Android');
    }

    try {
      final payload = jsonEncode(message.toJson());
      await _channel.invokeMethod('setPeerPayload', {'payload': payload});
      _messageController.add(message);
    } catch (e) {
      throw Exception('Failed to prepare peer NFC payload: ${e.toString()}');
    }
  }

  Future<NFCMessage> readPeerMessage() async {
    if (defaultTargetPlatform != TargetPlatform.android) {
      throw Exception('Peer NFC is only available on Android');
    }

    try {
      if (_isSessionActive) {
        throw Exception('NFC session already active');
      }

      _isSessionActive = true;
      final String? payload = await _channel.invokeMethod<String>('startPeerRead');
      if (payload == null || payload.isEmpty) {
        throw Exception('No NFC payload received');
      }

      final decoded = jsonDecode(payload) as Map<String, dynamic>;
      final message = NFCMessage.fromJson(decoded);
      _messageController.add(message);
      return message;
    } catch (e) {
      throw Exception('Failed to read peer NFC message: ${e.toString()}');
    } finally {
      _isSessionActive = false;
    }
  }

  Future<void> stopSession() async {
    try {
      if (defaultTargetPlatform == TargetPlatform.android) {
        await _channel.invokeMethod('stopPeerRead');
      }
    } catch (_) {
      // Ignore cleanup errors.
    } finally {
      _isSessionActive = false;
    }
  }

  void dispose() {
    if (!_messageController.isClosed) {
      _messageController.close();
    }
  }
}

class NFCMessage {
  final String userId;
  final String action;
  final double? amount;
  final String timestamp;

  NFCMessage({
    required this.userId,
    required this.action,
    this.amount,
    required this.timestamp,
  });

  factory NFCMessage.fromJson(Map<String, dynamic> json) {
    return NFCMessage(
      userId: json['userId'] as String? ?? 'unknown',
      action: json['action'] as String? ?? 'unknown',
      amount:
          json['amount'] != null ? (json['amount'] as num).toDouble() : null,
      timestamp:
          json['timestamp'] as String? ?? DateTime.now().toIso8601String(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userId': userId,
      'action': action,
      'amount': amount,
      'timestamp': timestamp,
    };
  }
}