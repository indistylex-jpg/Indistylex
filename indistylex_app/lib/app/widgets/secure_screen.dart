import 'package:flutter/material.dart';
import 'package:screen_protector/screen_protector.dart';

/// Prevents screenshots and screen recording on sensitive screens (login, checkout).
class SecureScreen extends StatefulWidget {
  final Widget child;

  const SecureScreen({super.key, required this.child});

  @override
  State<SecureScreen> createState() => _SecureScreenState();
}

class _SecureScreenState extends State<SecureScreen> {
  @override
  void initState() {
    super.initState();
    _enableProtection();
  }

  Future<void> _enableProtection() async {
    try {
      await ScreenProtector.protectDataLeakageOn();
    } catch (_) {}
  }

  @override
  void dispose() {
    ScreenProtector.protectDataLeakageOff();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
