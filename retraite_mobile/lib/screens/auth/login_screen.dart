import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/server_address.dart';
import '../../core/session.dart';
import '../../services/auth_service.dart';
import '../../widgets/college_logo.dart';
import '../../widgets/password_field.dart';
import '../home/home_screen.dart';
import 'register_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _loading = false;
  String? _error;

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      _loading = true;
      _error = null;
    });
    final session = context.read<SessionProvider>();
    final authService = AuthService(session.api);
    try {
      final token = await authService.login(email: _emailCtrl.text.trim(), password: _passwordCtrl.text);
      session.api.setToken(token);
      final user = await authService.me();
      await session.setSession(token, user);
      if (!mounted) return;
      Navigator.of(context).pushReplacement(MaterialPageRoute(builder: (_) => const HomeScreen()));
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error =
          "Impossible de contacter le serveur. Vérifiez le Wi-Fi et l'adresse du serveur (bouton en bas de l'écran).");
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _editServerAddress() async {
    final api = context.read<SessionProvider>().api;
    final controller = TextEditingController(text: api.baseUrl);
    final entered = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Adresse du serveur'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Adresse de l'ordinateur où tourne le serveur, sur le même Wi-Fi. Exemple : 192.168.1.20:8000",
            ),
            const SizedBox(height: 12),
            TextField(
              controller: controller,
              keyboardType: TextInputType.url,
              autocorrect: false,
              decoration: const InputDecoration(labelText: 'Adresse'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(dialogContext).pop(), child: const Text('Annuler')),
          ElevatedButton(
            onPressed: () => Navigator.of(dialogContext).pop(controller.text),
            child: const Text('Enregistrer'),
          ),
        ],
      ),
    );
    if (entered == null) return;
    final address = normalizeServerAddress(entered);
    api.baseUrl = address;
    await saveServerAddress(address);
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Serveur : $address')));
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const CollegeLogo(),
                  const SizedBox(height: 16),
                  Text(
                    'Collège Catholique Bilingue\nde la Retraite',
                    textAlign: TextAlign.center,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 32),
                  TextFormField(
                    controller: _emailCtrl,
                    keyboardType: TextInputType.emailAddress,
                    decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined)),
                    validator: (v) => (v == null || !v.contains('@')) ? 'Email invalide' : null,
                  ),
                  const SizedBox(height: 16),
                  PasswordField(
                    controller: _passwordCtrl,
                    label: 'Mot de passe',
                    validator: (v) => (v == null || v.isEmpty) ? 'Mot de passe requis' : null,
                  ),
                  if (_error != null) ...[
                    const SizedBox(height: 12),
                    Text(_error!, style: const TextStyle(color: Colors.red)),
                  ],
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading
                          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Text('Se connecter'),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () => Navigator.of(context).push(MaterialPageRoute(builder: (_) => const RegisterScreen())),
                    child: const Text('Pas encore de compte ? Inscrivez-vous'),
                  ),
                  TextButton.icon(
                    onPressed: _editServerAddress,
                    icon: const Icon(Icons.settings_ethernet),
                    label: const Text('Adresse du serveur'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
