enum TransactionType { sent, received, payment }

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
    name: 'Swiggy',
    amount: 349.00,
    type: TransactionType.payment,
    date: DateTime.now().subtract(const Duration(hours: 2)),
    note: 'Lunch order',
  ),
  Transaction(
    id: '2',
    name: 'Priya Sharma',
    amount: 2500.00,
    type: TransactionType.received,
    date: DateTime.now().subtract(const Duration(hours: 5)),
    note: 'Dinner split',
  ),
  Transaction(
    id: '3',
    name: 'Netflix India',
    amount: 649.00,
    type: TransactionType.payment,
    date: DateTime.now().subtract(const Duration(days: 1)),
  ),
  Transaction(
    id: '4',
    name: 'Rahul Verma',
    amount: 1200.00,
    type: TransactionType.sent,
    date: DateTime.now().subtract(const Duration(days: 1)),
    note: 'Movie tickets',
  ),
  Transaction(
    id: '5',
    name: 'Flipkart',
    amount: 3499.00,
    type: TransactionType.payment,
    date: DateTime.now().subtract(const Duration(days: 2)),
  ),
  Transaction(
    id: '6',
    name: 'Anjali Singh',
    amount: 8000.00,
    type: TransactionType.received,
    date: DateTime.now().subtract(const Duration(days: 3)),
    note: 'Rent share',
  ),
];
