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
