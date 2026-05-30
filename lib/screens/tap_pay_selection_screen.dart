import 'package:flutter/material.dart';
import 'tap_pay_screen.dart';

class TapPaySelectionScreen extends StatelessWidget {
  const TapPaySelectionScreen({super.key});

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
          'Tap to Pay/Receive',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.nfc_rounded, size: 80, color: Color(0xFFFF6B6B)),
            const SizedBox(height: 32),
            const Text(
              'Choose an action',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Select whether you want to send or receive payment',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 48),
            _buildActionCard(
              context,
              title: 'Send Payment',
              subtitle: 'Search for NFC readers and send money',
              icon: Icons.arrow_upward_rounded,
              color: const Color(0xFFFF6B6B),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const TapPayScreen(mode: 'pay'),
                ),
              ),
            ),
            const SizedBox(height: 20),
            _buildActionCard(
              context,
              title: 'Receive Payment',
              subtitle: 'Listen for incoming payments',
              icon: Icons.arrow_downward_rounded,
              color: const Color(0xFF00BFA5),
              onTap: () => Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const TapPayScreen(mode: 'receive'),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context, {
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 5),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              width: 70,
              height: 70,
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: color, size: 36),
            ),
            const SizedBox(width: 20),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 13,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Icon(Icons.arrow_forward_ios_rounded,
                color: color, size: 18),
          ],
        ),
      ),
    );
  }
}
