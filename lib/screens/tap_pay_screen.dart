import 'package:flutter/material.dart';
import '../services/nfc_service.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:async';

class TapPayScreen extends StatefulWidget {
  final String mode; // 'pay' or 'receive'

  const TapPayScreen({super.key, required this.mode});

  @override
  State<TapPayScreen> createState() => _TapPayScreenState();
}

class _TapPayScreenState extends State<TapPayScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pulseAnimation;
  final NFCService _nfcService = NFCService();
  
  TextEditingController _amountController = TextEditingController();
  bool _isSearching = false;
  bool _paymentConfirmed = false;
  bool _paymentSuccessful = false;
  Timer? _searchTimer;
  NFCMessage? _receivedMessage;
  double? _payAmount;
  String _statusMessage = '';

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
  }

  @override
  void dispose() {
    _controller.dispose();
    _searchTimer?.cancel();
    _amountController.dispose();
    _nfcService.stopSession();
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
            keyboardType:
                const TextInputType.numberWithOptions(decimal: true),
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
      _payAmount = amount;
      _isSearching = true;
      _statusMessage = 'Searching for NFC readers...';
    });

    // Start NFC write session
    _startNFCWrite(amount);

    // Set 2-minute timeout
    _searchTimer = Timer(const Duration(minutes: 2), () {
      if (mounted && _isSearching && !_paymentSuccessful) {
        setState(() {
          _isSearching = false;
          _statusMessage = 'Search timeout - no NFC reader found';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('No NFC reader found. Payment cancelled.')),
        );
      }
    });
  }

  void _startNFCWrite(double amount) async {
    try {
      final message = NFCMessage(
        userId: 'user_123', // Replace with actual user ID
        action: 'pay',
        amount: amount,
        timestamp: DateTime.now().toIso8601String(),
      );

      await _nfcService.writeNFCMessage(message);
      // If write is successful, wait for response
      _waitForPaymentResponse();
    } catch (e) {
      if (mounted) {
        setState(() {
          _isSearching = false;
          _statusMessage = 'Error: ${e.toString()}';
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('NFC Error: $e')),
        );
      }
    }
  }

  void _waitForPaymentResponse() {
    // Listen for confirmation from receiver
    _nfcService.messageStream.listen((message) {
      if (mounted && message.action == 'receive' && _isSearching) {
        setState(() {
          _receivedMessage = message;
          _paymentConfirmed = true;
          _isSearching = false;
        });
        _showConfirmationDialog();
      }
    });
  }

  void _showConfirmationDialog() {
    if (!mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Confirm Payment'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('Receiver found!'),
              const SizedBox(height: 16),
              Text(
                '₹${_payAmount?.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFFFF6B6B),
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Confirm this payment?',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                setState(() {
                  _isSearching = false;
                  _statusMessage = 'Payment cancelled';
                });
              },
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                _processBlockchainPayment();
              },
              child: const Text('Confirm'),
            ),
          ],
        );
      },
    );
  }

  void _processBlockchainPayment() async {
    try {
      // Call backend API to process blockchain transfer
      final response = await http
          .post(
            Uri.parse('http://your-backend-url/api/payments/transfer'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'from_user_id': 'user_123', // Replace with actual sender ID
              'to_user_id': _receivedMessage?.userId,
              'amount': _payAmount,
            }),
          )
          .timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        setState(() {
          _paymentSuccessful = true;
          _statusMessage = 'Payment successful!';
        });
        _showSuccessScreen();
      } else {
        throw Exception('Payment failed: ${response.statusCode}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Payment failed: $e')),
        );
        setState(() {
          _isSearching = false;
          _statusMessage = 'Payment failed';
        });
      }
    }
  }

  void _startReceiveMode() {
    setState(() {
      _isSearching = true;
      _statusMessage = 'Listening for NFC signals...';
    });

    _nfcService.startListening(
      onMessageReceived: (message) {
        if (mounted && message.action == 'pay') {
          setState(() {
            _receivedMessage = message;
            _paymentConfirmed = true;
            _isSearching = false;
          });
          _showReceiveConfirmationDialog();
        }
      },
      onError: (error) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('NFC Error: $error')),
          );
        }
      },
    );
  }

  void _showReceiveConfirmationDialog() {
    if (!mounted) return;

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Incoming Payment'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.check_circle_outline,
                  color: Color(0xFF00BFA5), size: 60),
              const SizedBox(height: 16),
              Text(
                '₹${_receivedMessage?.amount?.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF00BFA5),
                ),
              ),
              const SizedBox(height: 8),
              const Text('Receiving payment...'),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                _processBlockchainReceive();
              },
              child: const Text('Accept'),
            ),
          ],
        );
      },
    );
  }

  void _processBlockchainReceive() async {
    try {
      // Payment is already processed from sender side
      // Just update receiver's blockchain record
      setState(() {
        _paymentSuccessful = true;
        _statusMessage = 'Payment received!';
      });
      _showSuccessScreen();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e')),
        );
      }
    }
  }

  void _showSuccessScreen() {
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) {
        showDialog(
          context: context,
          barrierDismissible: false,
          builder: (BuildContext context) {
            return AlertDialog(
              content: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 100,
                    height: 100,
                    decoration: const BoxDecoration(
                      shape: BoxShape.circle,
                      color: Color(0xFF00BFA5),
                    ),
                    child: const Icon(Icons.check,
                        size: 60, color: Colors.white),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Successful!',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '₹${_payAmount?.toStringAsFixed(2)}',
                    style: const TextStyle(
                      fontSize: 18,
                      color: Color(0xFF00BFA5),
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            );
          },
        );

        Future.delayed(const Duration(seconds: 3), () {
          if (mounted) {
            Navigator.popUntil(context, (route) => route.isFirst);
          }
        });
      }
    });
  }

  void _toggleListening() {
    if (_isSearching) {
      setState(() {
        _isSearching = false;
        _statusMessage = '';
      });
      _nfcService.stopSession();
      if (_searchTimer != null) {
        _searchTimer!.cancel();
      }
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
    final title =
        isPayMode ? 'Send Payment' : 'Receive Payment';
    final instruction = isPayMode
        ? 'Hold near NFC device to send'
        : 'Hold near NFC device to receive';

    return Scaffold(
      backgroundColor: color,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded,
              color: Colors.white),
          onPressed: () {
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
        child: _paymentSuccessful ? _buildSuccessState() : _buildNFCState(color, instruction),
      ),
    );
  }

  Widget _buildNFCState(Color color, String instruction) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          instruction,
          style: const TextStyle(color: Colors.white70, fontSize: 16),
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
                color: Colors.white.withOpacity(0.15),
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
                color: Colors.white.withOpacity(0.15),
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
              const CircularProgressIndicator(color: Colors.white)
              ,
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
                  backgroundColor: Colors.white.withOpacity(0.2),
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
            'Tap the circle to ${widget.mode == 'pay' ? 'send payment' : 'receive payment'}',
            style: const TextStyle(color: Colors.white54, fontSize: 13),
          ),
      ],
    );
  }

  Widget _buildSuccessState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 120,
          height: 120,
          decoration: const BoxDecoration(
            shape: BoxShape.circle,
            color: Colors.white,
          ),
          child: const Icon(
            Icons.check_rounded,
            size: 70,
            color: Color(0xFF00BFA5),
          ),
        ),
        const SizedBox(height: 28),
        const Text(
          'Payment Successful!',
          style: TextStyle(
            color: Colors.white,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          '₹${_payAmount?.toStringAsFixed(2)}',
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 18,
          ),
        ),
      ],
    );
  }
}
