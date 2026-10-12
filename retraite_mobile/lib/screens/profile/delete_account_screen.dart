import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../services/auth_service.dart';
import '../../widgets/password_field.dart';

/// Suppression du compte par le client lui-même (exigence du Play Store et de l'App Store).
class DeleteAccountScreen extends StatefulWidget {
  const DeleteAccountScreen({super.key});

  @override
  State<DeleteAccountScreen> createState() => _DeleteAccountScreenState();
}

class _DeleteAccountScreenState extends State<DeleteAccountScreen> {
  final _formKey = GlobalKey<FormState>();
  final _passwordCtrl = TextEditingController();
  bool _confirmed = false;
  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    final session = context.read<SessionProvider>();
    final navigator = Navigator.of(context);
    final messenger = ScaffoldMessenger.of(context);
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      await AuthService(session.api).deleteAccount(password: _passwordCtrl.text);
      await session.logout();
      navigator.popUntil((route) => route.isFirst);
      messenger.showSnackBar(const SnackBar(content: Text('Votre compte a été supprimé.')));
    } on ApiException catch (e) {
      if (mounted) setState(() => _error = e.message);
    } catch (_) {
      if (mounted) setState(() => _error = 'Impossible de contacter le serveur. Vérifiez la connexion.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Supprimer mon compte')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Cette action est définitive.',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.red),
                ),
                const SizedBox(height: 12),
                const Text(
                  'Votre nom, votre email, votre téléphone et votre mot de passe seront effacés tout de suite. '
                  'Vos réservations en attente à venir seront annulées. Les réservations passées et les reçus restent '
                  'enregistrés, sans aucun nom, car ce sont des pièces comptables du Collège.\n\n'
                  "Si une réservation validée est à venir, annulez-la ou contactez l'administration d'abord.",
                  style: TextStyle(height: 1.4),
                ),
                const SizedBox(height: 20),
                PasswordField(
                  controller: _passwordCtrl,
                  label: 'Votre mot de passe',
                  validator: (v) => (v == null || v.isEmpty) ? 'Entrez votre mot de passe.' : null,
                ),
                const SizedBox(height: 8),
                CheckboxListTile(
                  contentPadding: EdgeInsets.zero,
                  controlAffinity: ListTileControlAffinity.leading,
                  value: _confirmed,
                  onChanged: (v) => setState(() => _confirmed = v ?? false),
                  title: const Text('Je comprends que la suppression est définitive.'),
                ),
                if (_error != null) ...[
                  const SizedBox(height: 8),
                  Text(_error!, style: const TextStyle(color: Colors.red)),
                ],
                const SizedBox(height: 16),
                ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
                  onPressed: (_loading || !_confirmed) ? null : _submit,
                  child: _loading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Text('Supprimer définitivement mon compte'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
