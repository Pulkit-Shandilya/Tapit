import 'package:flutter/material.dart';

class QuickActions extends StatelessWidget {
  final VoidCallback onSend;
  final VoidCallback onReceive;
  final VoidCallback onPay;
  final VoidCallback onHistory;

  const QuickActions({
    super.key,
    required this.onSend,
    required this.onReceive,
    required this.onPay,
    required this.onHistory,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        _ActionButton(
          icon: Icons.arrow_upward_rounded,
          label: 'Send',
          color: const Color(0xFF6C63FF),
          onTap: onSend,
        ),
        _ActionButton(
          icon: Icons.arrow_downward_rounded,
          label: 'Receive',
          color: const Color(0xFF00BFA5),
          onTap: onReceive,
        ),
        _ActionButton(
          icon: Icons.nfc_rounded,
          label: 'Tap Pay',
          color: const Color(0xFFFF6B6B),
          onTap: onPay,
        ),
        _ActionButton(
          icon: Icons.history_rounded,
          label: 'History',
          color: const Color(0xFFFFB347),
          onTap: onHistory,
        ),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onTap;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
