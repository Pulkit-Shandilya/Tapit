import 'package:flutter/material.dart';

class TapPayScreen extends StatefulWidget {
  const TapPayScreen({super.key});

  @override
  State<TapPayScreen> createState() => _TapPayScreenState();
}

class _TapPayScreenState extends State<TapPayScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _pulseAnimation;
  bool _paid = false;

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

  void _simulateTap() {
    setState(() => _paid = true);
    _controller.stop();
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) Navigator.pop(context);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF6C63FF),
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded,
              color: Colors.white),
          onPressed: () => Navigator.pop(context),
        ),
        title: const Text(
          'Tap to Pay',
          style:
              TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: Center(
        child: _paid ? _buildSuccessState() : _buildTapState(),
      ),
    );
  }

  Widget _buildTapState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        const Text(
          'Hold near NFC reader',
          style: TextStyle(color: Colors.white70, fontSize: 16),
        ),
        const SizedBox(height: 48),
        ScaleTransition(
          scale: _pulseAnimation,
          child: GestureDetector(
            onTap: _simulateTap,
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
        ),
        const SizedBox(height: 48),
        const Text(
          'Tap the circle to simulate payment',
          style: TextStyle(color: Colors.white54, fontSize: 13),
        ),
        const SizedBox(height: 48),
        Container(
          margin: const EdgeInsets.symmetric(horizontal: 32),
          padding:
              const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.1),
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Amount',
                  style: TextStyle(color: Colors.white70)),
              Text(
                '₹0.00',
                style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18),
              ),
            ],
          ),
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
        const Text(
          'Redirecting back...',
          style: TextStyle(color: Colors.white60),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}
