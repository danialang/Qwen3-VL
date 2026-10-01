import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../services/auth_service.dart';
import '../../widgets/password_field.dart';

/// Mot de passe oublié : 1) on saisit l'email, 2) on tape le code reçu par email et on choisit un nouveau mot de passe.
class ForgotPasswordScreen extends StatefulWidget {
  final String initialEmail;

  const ForgotPasswordScreen({super.key, this.initialEmail = ''});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  static final _strongPasswordRegex = RegExp(r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[^A-Za-z0-9]).{8,}$');

  final _emailFormKey = GlobalKey<FormState>();
  final _resetFormKey = GlobalKey<FormState>();
  late final TextEditingController _emailCtrl;
  final _codeCtrl = TextEditingController();
  final _newCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  bool _codeSent = false;
  bool _loading = false;
  String? _error;
  String? _info;

  @override
  void initState() {
    super.initState();
    _emailCtrl = TextEditingController(text: widget.initialEmail);
  }

  @override
  void dispose() {
    _emailCtrl.dispose();
    _codeCtrl.dispose();
    _newCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  AuthService get _auth => AuthService(context.read<SessionProvider>().api);

  Future<void> _run(Future<void> Function() action) async {
    setState(() {
      _loading = true;
      _error = null;
      _info = null;
    });
    try {
      await action();
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Impossible de contacter le serveur. Vérifiez le Wi-Fi.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _sendCode() async {
    if (!_emailFormKey.currentState!.validate()) return;
    await _run(() async {
      await _auth.forgotPassword(email: _emailCtrl.text.trim());
      if (!mounted) return;
      setState(() {
        _codeSent = true;
        _info = 'Si un compte existe avec cet email, un code à 6 chiffres vient d\'être envoyé. '
            'Il est valable 15 minutes. Pensez à regarder les courriers indésirables (spam).';
      });
    });
  }

  Future<void> _resetPassword() async {
    if (!_resetFormKey.currentState!.validate()) return;
    await _run(() async {
      await _auth.resetPassword(
        email: _emailCtrl.text.trim(),
        code: _codeCtrl.text.trim(),
        newPassword: _newCtrl.text,
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Mot de passe modifié. Vous pouvez vous connecter.')));
      Navigator.of(context).pop();
    });
  }

  Widget _loader() =>
      const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white));

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mot de passe oublié')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Form(
                key: _emailFormKey,
                child: TextFormField(
                  controller: _emailCtrl,
                  enabled: !_codeSent,
                  keyboardType: TextInputType.emailAddress,
                  decoration: const InputDecoration(labelText: 'Email du compte', prefixIcon: Icon(Icons.email_outlined)),
                  validator: (v) => (v == null || !v.contains('@')) ? 'Email invalide' : null,
                ),
              ),
              if (_info != null) ...[
                const SizedBox(height: 12),
                Text(_info!, style: TextStyle(color: Theme.of(context).colorScheme.primary)),
              ],
              if (_error != null) ...[
                const SizedBox(height: 12),
                Text(_error!, style: const TextStyle(color: Colors.red)),
              ],
              const SizedBox(height: 16),
              if (!_codeSent)
                ElevatedButton(
                  onPressed: _loading ? null : _sendCode,
                  child: _loading ? _loader() : const Text('Envoyer le code'),
                )
              else ...[
                Form(
                  key: _resetFormKey,
                  child: Column(
                    children: [
                      TextFormField(
                        controller: _codeCtrl,
                        keyboardType: TextInputType.number,
                        maxLength: 6,
                        decoration: const InputDecoration(labelText: 'Code reçu par email', prefixIcon: Icon(Icons.pin_outlined)),
                        validator: (v) => (v == null || v.trim().length != 6) ? 'Le code a 6 chiffres' : null,
                      ),
                      const SizedBox(height: 8),
                      PasswordField(
                        controller: _newCtrl,
                        label: 'Nouveau mot de passe',
                        helperText: '8 caractères min., une majuscule, un chiffre, un caractère spécial',
                        textInputAction: TextInputAction.next,
                        validator: (v) => (v == null || !_strongPasswordRegex.hasMatch(v)) ? 'Mot de passe trop faible' : null,
                      ),
                      const SizedBox(height: 16),
                      PasswordField(
                        controller: _confirmCtrl,
                        label: 'Confirmer le nouveau mot de passe',
                        validator: (v) => v != _newCtrl.text ? 'Les deux mots de passe sont différents' : null,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _loading ? null : _resetPassword,
                  child: _loading ? _loader() : const Text('Changer le mot de passe'),
                ),
                TextButton(
                  onPressed: _loading ? null : _sendCode,
                  child: const Text('Renvoyer un code'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
