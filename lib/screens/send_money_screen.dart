import 'package:flutter/material.dart';

class SendMoneyScreen extends StatefulWidget {
  const SendMoneyScreen({super.key});

  @override
  State<SendMoneyScreen> createState() => _SendMoneyScreenState();
}

class _SendMoneyScreenState extends State<SendMoneyScreen> {
  String _amount = '0';
  final _noteController = TextEditingController();
  String? _selectedContact;

  final List<Map<String, String>> _contacts = [
    {'name': 'Priya Sharma', 'tag': 'priya@tapit'},
    {'name': 'Rahul Verma', 'tag': 'rahul@tapit'},
    {'name': 'Anjali Singh', 'tag': 'anjali@tapit'},
    {'name': 'Arjun Mehta', 'tag': 'arjun@tapit'},
  ];

  void _onKey(String key) {
    setState(() {
      if (key == '⌫') {
        if (_amount.length > 1) {
          _amount = _amount.substring(0, _amount.length - 1);
        } else {
          _amount = '0';
        }
      } else if (key == '.') {
        if (!_amount.contains('.')) _amount += '.';
      } else {
        if (_amount == '0') {
          _amount = key;
        } else {
          if (_amount.contains('.')) {
            final parts = _amount.split('.');
            if (parts[1].length < 2) _amount += key;
          } else {
            _amount += key;
          }
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F5F7),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Send Money',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Column(
                children: [
                  const SizedBox(height: 16),
                  _buildContactSelector(),
                  const SizedBox(height: 32),
                  _buildAmountDisplay(),
                  const SizedBox(height: 16),
                  _buildNoteField(),
                  const SizedBox(height: 16),
                ],
              ),
            ),
          ),
          _buildNumpad(),
          Padding(
            padding: const EdgeInsets.fromLTRB(20, 12, 20, 28),
            child: SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton(
                onPressed: _selectedContact != null && _amount != '0'
                    ? () => _confirmPayment(context)
                    : null,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6C63FF),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  elevation: 0,
                ),
                child: const Text(
                  'Send Now',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContactSelector() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Send To',
          style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
        ),
        const SizedBox(height: 10),
        SizedBox(
          height: 80,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: _contacts.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (context, i) {
              final contact = _contacts[i];
              final selected = _selectedContact == contact['name'];
              return GestureDetector(
                onTap: () =>
                    setState(() => _selectedContact = contact['name']),
                child: Column(
                  children: [
                    Container(
                      width: 52,
                      height: 52,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: selected
                            ? const Color(0xFF6C63FF)
                            : const Color(0xFF6C63FF).withOpacity(0.12),
                        border: selected
                            ? Border.all(
                                color: const Color(0xFF6C63FF), width: 2)
                            : null,
                      ),
                      child: Center(
                        child: Text(
                          contact['name']![0],
                          style: TextStyle(
                            color: selected
                                ? Colors.white
                                : const Color(0xFF6C63FF),
                            fontWeight: FontWeight.bold,
                            fontSize: 18,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      contact['name']!.split(' ')[0],
                      style: const TextStyle(fontSize: 11),
                    ),
                  ],
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildAmountDisplay() {
    return Column(
      children: [
        Text(
          _selectedContact != null
              ? 'To ${_selectedContact!.split(' ')[0]}'
              : 'Select a recipient',
          style: TextStyle(color: Colors.grey[500], fontSize: 14),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Padding(
              padding: EdgeInsets.only(top: 12),
              child: Text(
                '₹',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF6C63FF),
                ),
              ),
            ),
            Text(
              _amount,
              style: const TextStyle(
                fontSize: 64,
                fontWeight: FontWeight.bold,
                letterSpacing: -2,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildNoteField() {
    return TextField(
      controller: _noteController,
      decoration: InputDecoration(
        hintText: 'Add a note (optional)',
        hintStyle: TextStyle(color: Colors.grey[400]),
        filled: true,
        fillColor: Colors.white,
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(14),
          borderSide: BorderSide.none,
        ),
        prefixIcon: const Icon(Icons.note_alt_outlined, color: Colors.grey),
      ),
    );
  }

  Widget _buildNumpad() {
    final keys = [
      ['1', '2', '3'],
      ['4', '5', '6'],
      ['7', '8', '9'],
      ['.', '0', '⌫'],
    ];

    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      child: Column(
        children: keys.map((row) {
          return Row(
            children: row.map((key) {
              return Expanded(
                child: TextButton(
                  onPressed: () => _onKey(key),
                  child: Text(
                    key,
                    style: TextStyle(
                      fontSize: key == '⌫' ? 22 : 24,
                      fontWeight: FontWeight.w500,
                      color: Colors.black87,
                    ),
                  ),
                ),
              );
            }).toList(),
          );
        }).toList(),
      ),
    );
  }

  void _confirmPayment(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.all(28),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const SizedBox(height: 24),
            const Text(
              'Confirm Payment',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),
            _confirmRow('To', _selectedContact!),
            const Divider(height: 24),
            _confirmRow('Amount', '₹$_amount'),
            if (_noteController.text.isNotEmpty) ...[
              const Divider(height: 24),
              _confirmRow('Note', _noteController.text),
            ],
            const SizedBox(height: 28),
            SizedBox(
              width: double.infinity,
              height: 52,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content:
                          Text('Sent ₹$_amount to $_selectedContact!'),
                      backgroundColor: const Color(0xFF00BFA5),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF6C63FF),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                ),
                child: const Text(
                  'Confirm & Send',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  Widget _confirmRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: TextStyle(color: Colors.grey[500])),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w600)),
      ],
    );
  }

  @override
  void dispose() {
    _noteController.dispose();
    super.dispose();
  }
}
