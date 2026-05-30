import 'package:nfc_manager/nfc_manager.dart';
import 'dart:convert';
import 'dart:async';

class NFCService {
  static final NFCService _instance = NFCService._internal();

  factory NFCService() {
    return _instance;
  }

  NFCService._internal();

  final StreamController<NFCMessage> _messageController =
      StreamController<NFCMessage>.broadcast();

  Stream<NFCMessage> get messageStream => _messageController.stream;

  Future<bool> isNFCAvailable() async {
    return await NfcManager.instance.isAvailable();
  }

  /// Start listening for NFC tags (Receive mode)
  Future<void> startListening({
    required Function(NFCMessage) onMessageReceived,
    required Function(String) onError,
  }) async {
    try {
      NfcManager.instance.startSession(
        onDiscovered: (NfcTag tag) async {
          try {
            // Get NDEF records from the tag
            final Ndef? ndef = Ndef.from(tag);
            if (ndef != null && ndef.cachedMessage != null) {
              final message = ndef.cachedMessage!;
              final payload = _parseNDEFMessage(message);
              onMessageReceived(payload);
            }
          } catch (e) {
            onError('Error reading NFC tag: $e');
          }
        },
      );
    } catch (e) {
      onError('Failed to start NFC session: $e');
    }
  }

  /// Write NFC message to a tag (Pay mode)
  Future<void> writeNFCMessage(NFCMessage message) async {
    try {
      NfcManager.instance.startSession(
        onDiscovered: (NfcTag tag) async {
          try {
            final Ndef? ndef = Ndef.from(tag);
            if (ndef != null && ndef.isWritable) {
              final ndefMessage = _createNDEFMessage(message);
              await ndef.write(ndefMessage);
              await NfcManager.instance.stopSession();
            } else {
              throw Exception('Tag is not writable');
            }
          } catch (e) {
            await NfcManager.instance.stopSession();
            rethrow;
          }
        },
      );
    } catch (e) {
      throw Exception('Failed to write NFC message: $e');
    }
  }

  /// Stop NFC session
  Future<void> stopSession() async {
    try {
      await NfcManager.instance.stopSession();
    } catch (e) {
      // Session might already be stopped
    }
  }

  /// Parse NDEF message to extract data
  NFCMessage _parseNDEFMessage(NdefMessage message) {
    for (var record in message.records) {
      if (record.typeNameFormat == NdefTypeNameFormat.media &&
          record.type == utf8.encode('application/tapit')) {
        final payload = utf8.decode(record.payload);
        return NFCMessage.fromJson(jsonDecode(payload));
      }
    }
    throw Exception('No valid TapIt NDEF record found');
  }

  /// Create NDEF message from NFCMessage
  NdefMessage _createNDEFMessage(NFCMessage message) {
    final record = NdefRecord(
      typeNameFormat: NdefTypeNameFormat.media,
      type: utf8.encode('application/tapit'),
      identifier: utf8.encode('tapit_payment'),
      payload: utf8.encode(jsonEncode(message.toJson())),
    );
    return NdefMessage([record]);
  }
}

class NFCMessage {
  final String userId;
  final String action; // 'pay' or 'receive'
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
      userId: json['userId'] as String,
      action: json['action'] as String,
      amount:
          json['amount'] != null ? (json['amount'] as num).toDouble() : null,
      timestamp: json['timestamp'] as String,
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
