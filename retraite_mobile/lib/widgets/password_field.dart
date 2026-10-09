import 'package:flutter/material.dart';

/// Champ mot de passe avec un œil pour afficher / masquer ce qui est saisi.
class PasswordField extends StatefulWidget {
  final TextEditingController controller;
  final String label;
  final String? helperText;
  final String? Function(String?)? validator;
  final TextInputAction? textInputAction;

  const PasswordField({
    super.key,
    required this.controller,
    required this.label,
    this.helperText,
    this.validator,
    this.textInputAction,
  });

  @override
  State<PasswordField> createState() => _PasswordFieldState();
}

class _PasswordFieldState extends State<PasswordField> {
  bool _hidden = true;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      controller: widget.controller,
      obscureText: _hidden,
      autocorrect: false,
      enableSuggestions: false,
      textInputAction: widget.textInputAction,
      decoration: InputDecoration(
        labelText: widget.label,
        helperText: widget.helperText,
        helperMaxLines: 2,
        prefixIcon: const Icon(Icons.lock_outline),
        suffixIcon: IconButton(
          tooltip: _hidden ? 'Afficher le mot de passe' : 'Masquer le mot de passe',
          icon: Icon(_hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined),
          onPressed: () => setState(() => _hidden = !_hidden),
        ),
      ),
      validator: widget.validator,
    );
  }
}
