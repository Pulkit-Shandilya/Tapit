import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/transaction.dart';
import 'profile_service.dart';

class PaymentHistoryService {
  PaymentHistoryService._();

  static Uri _historyUri([Map<String, String>? queryParameters]) {
    return Uri.parse('${ProfileService.baseUrl}/api/payments/history')
        .replace(queryParameters: queryParameters);
  }

  static Future<List<Transaction>> fetchHistory({String? status}) async {
    final queryParameters = <String, String>{'user_id': ProfileService.userId};
    if (status != null && status.isNotEmpty) {
      queryParameters['status'] = status;
    }

    final response = await http.get(_historyUri(queryParameters));
    if (response.statusCode != 200) {
      throw Exception('Failed to load payment history (${response.statusCode})');
    }

    final decoded = jsonDecode(response.body) as Map<String, dynamic>;
    final transactions = (decoded['transactions'] as List<dynamic>? ?? [])
        .cast<Map<String, dynamic>>()
        .map(_toTransaction)
        .toList();

    return transactions;
  }

  static Transaction _toTransaction(Map<String, dynamic> json) {
    final flowType = (json['flow_type'] as String? ?? 'payment').toLowerCase();
    final fromUserId = json['from_user_id'] as String?;
    final toUserId = json['to_user_id'] as String?;
    final merchantId = json['merchant_id'] as String?;
    final amount = (json['amount'] as num?)?.toDouble() ?? 0;
    final createdAt = DateTime.tryParse(json['created_at'] as String? ?? '') ??
        DateTime.now();

    final isReceived = flowType == 'peer_transfer' && toUserId == ProfileService.userId;

    final name = flowType == 'peer_transfer'
        ? (isReceived ? (fromUserId ?? 'Unknown sender') : (toUserId ?? 'Unknown receiver'))
        : (merchantId ?? 'Merchant');

    final note = flowType == 'peer_transfer'
        ? (isReceived ? 'Received via NFC transfer' : 'Sent via NFC transfer')
        : (json['note'] as String? ?? 'Merchant payment');

    return Transaction(
      id: json['transaction_id'] as String? ?? '',
      name: name,
      amount: amount,
      type: isReceived ? TransactionType.received : TransactionType.sent,
      date: createdAt,
      note: note,
    );
  }
}