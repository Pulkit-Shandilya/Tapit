import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import '../services/nfc_service.dart';
import '../services/profile_service.dart';

class TapPayScreen extends StatefulWidget {
  final String mode; // 'pay' or 'receive'

  const TapPayScreen({super.key, required this.mode});

  @override
  State<TapPayScreen> createState() => _TapPayScreenState();
}

class _TapPayScreenState extends State<TapPayScreen>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<double> _pulseAnimation;
  final NFCService _nfcService = NFCService();
  final TextEditingController _amountController = TextEditingController();

  bool _isSearching = false;
  String _statusMessage = '';
  Timer? _searchTimer;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 1),
    )..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.9, end: 1.1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
    _checkNFCAvailability();
  }

  Future<void> _checkNFCAvailability() async {
    final available = await _nfcService.isNFCAvailable();
    if (!available && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('NFC is not available on this device'),
          duration: Duration(seconds: 3),
        ),
      );
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    _searchTimer?.cancel();
    _amountController.dispose();
    _nfcService.stopSession();
    _nfcService.dispose();
    super.dispose();
  }

  void _startPayMode() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Enter Amount'),
          content: TextField(
            controller: _amountController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(
              hintText: 'Enter amount in ₹',
              prefixText: '₹ ',
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                final amount = double.tryParse(_amountController.text);
                if (amount != null && amount > 0) {
                  Navigator.pop(context);
                  _performPayment(amount);
                } else {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Invalid amount')),
                  );
                }
              },
              child: const Text('Continue'),
            ),
          ],
        );
      },
    );
  }

  void _performPayment(double amount) {
    setState(() {
      _isSearching = true;
      _statusMessage = 'Waiting for the receiver device to be tapped...';
    });

    _startNFCRead(amount);

    _searchTimer = Timer(const Duration(minutes: 2), () {
      if (mounted && _isSearching) {
        _cancelSearch();
      }
    });
  }

  void _cancelSearch() {
    _searchTimer?.cancel();
    if (mounted) {
      setState(() {
        _isSearching = false;
        _statusMessage = 'Search cancelled or timeout';
      });
    }
    _nfcService.stopSession();
  }

  Future<void> _startNFCRead(double amount) async {
    try {
      final receiverMessage = await _nfcService.readPeerMessage();

      final transferResponse = await http.post(
        Uri.parse('${ProfileService.baseUrl}/api/payments/transfer'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'from_user_id': ProfileService.userId,
          'to_user_id': receiverMessage.userId,
          'amount': amount,
        }),
      );

      if (transferResponse.statusCode != 200) {
        throw Exception('Transfer failed (${transferResponse.statusCode})');
      }

      await ProfileService.refreshBalance();

      if (!mounted) return;
      setState(() {
        _isSearching = false;
        _statusMessage = 'Payment completed';
      });

      _showTransferSuccessDialog(amount, receiverMessage.userId);
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _isSearching = false;
        _statusMessage = 'Error: $e';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('NFC Error: $e'),
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  void _showTransferSuccessDialog(double amount, String receiverId) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) {
        return AlertDialog(
          title: const Text('Payment Sent'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.check_circle, color: Color(0xFF00BFA5), size: 60),
              const SizedBox(height: 16),
              const Text('The payment was transferred to the nearby device.'),
              const SizedBox(height: 8),
              Text('Receiver: $receiverId'),
              const SizedBox(height: 8),
              Text(
                '₹${amount.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFFF6B6B),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
              },
              child: const Text('Done'),
            ),
          ],
        );
      },
    );
  }

  void _startReceiveMode() {
    setState(() {
      _isSearching = true;
      _statusMessage = 'Broadcasting receiver identity for NFC detection...';
    });

    final message = NFCMessage(
      userId: 'demo_receiver',
      action: 'receive',
      amount: null,
      timestamp: DateTime.now().toIso8601String(),
    );

    _nfcService.preparePeerReceive(message);

    if (mounted) {
      setState(() {
        _statusMessage = 'Ready to receive. Keep this device unlocked and near the payer.';
      });
    }
  }

  void _toggleListening() {
    if (_isSearching) {
      _cancelSearch();
    } else if (widget.mode == 'pay') {
      _startPayMode();
    } else {
      _startReceiveMode();
    }
  }

  @override
  Widget build(BuildContext context) {
    final isPayMode = widget.mode == 'pay';
    final color = isPayMode ? const Color(0xFFFF6B6B) : const Color(0xFF00BFA5);
    final title = isPayMode ? 'Send Payment' : 'Receive Payment';
    final instruction = isPayMode
        ? 'Tap to detect the receiver device via NFC'
        : 'Keep this device ready so the payer can detect it';

    return PopScope(
      canPop: true,
      onPopInvokedWithResult: (didPop, _) {
        if (didPop) return;
        if (_isSearching) {
          _cancelSearch();
        }
      },
      child: Scaffold(
        backgroundColor: color,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.white),
            onPressed: () {
              if (_isSearching) {
                _cancelSearch();
              }
              _nfcService.stopSession();
              Navigator.pop(context);
            },
          ),
          title: Text(
            title,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
        ),
        body: Center(
          child: _buildNFCState(instruction),
        ),
      ),
    );
  }

  Widget _buildNFCState(String instruction) {
    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              instruction,
              style: const TextStyle(color: Colors.white70, fontSize: 16),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            if (_isSearching)
              ScaleTransition(
                scale: _pulseAnimation,
                child: Container(
                  width: 180,
                  height: 180,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withValues(alpha: 0.15),
                    border: Border.all(color: Colors.white30, width: 2),
                  ),
                  child: const Icon(
                    Icons.nfc_rounded,
                    size: 90,
                    color: Colors.white,
                  ),
                ),
              )
            else
              GestureDetector(
                onTap: _toggleListening,
                child: Container(
                  width: 180,
                  height: 180,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.white.withValues(alpha: 0.15),
                    border: Border.all(color: Colors.white30, width: 2),
                  ),
                  child: const Icon(
                    Icons.nfc_rounded,
                    size: 90,
                    color: Colors.white,
                  ),
                ),
              ),
            const SizedBox(height: 48),
            if (_isSearching)
              Column(
                children: [
                  const CircularProgressIndicator(color: Colors.white),
                  const SizedBox(height: 20),
                  Text(
                    _statusMessage,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _toggleListening,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.white.withValues(alpha: 0.2),
                    ),
                    child: const Text(
                      'Cancel',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              )
            else
              Text(
                'Tap the circle to ${widget.mode == 'pay' ? 'send' : 'receive'}',
                style: const TextStyle(color: Colors.white54, fontSize: 13),
              ),
          ],
        ),
      ),
    );
  }
}