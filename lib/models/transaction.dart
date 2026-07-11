enum TransactionType { sent, received }

class Transaction {
  final String id;
  final String name;
  final double amount;
  final TransactionType type;
  final DateTime date;
  final String? note;

  const Transaction({
    required this.id,
    required this.name,
    required this.amount,
    required this.type,
    required this.date,
    this.note,
  });
}

final List<Transaction> mockTransactions = [
  Transaction(
    id: '1',
    name: 'Priya Sharma',
    amount: 2500.00,
    type: TransactionType.received,
    date: DateTime.now().subtract(const Duration(hours: 5)),
    note: 'NFC Payment',
  ),
  Transaction(
    id: '2',
    name: 'Rahul Verma',
    amount: 1200.00,
    type: TransactionType.sent,
    date: DateTime.now().subtract(const Duration(days: 1)),
    note: 'NFC Payment',
  ),
];
