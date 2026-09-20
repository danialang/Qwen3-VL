import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../core/api_client.dart';
import '../../core/session.dart';
import '../../models/user.dart';
import '../../services/auth_service.dart';

class AdminUsersScreen extends StatefulWidget {
  const AdminUsersScreen({super.key});

  @override
  State<AdminUsersScreen> createState() => _AdminUsersScreenState();
}

class _AdminUsersScreenState extends State<AdminUsersScreen> {
  late final AuthService _service;
  List<AppUser> _users = [];
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _service = AuthService(context.read<SessionProvider>().api);
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final users = await _service.listUsers();
      setState(() => _users = users);
    } on ApiException catch (e) {
      setState(() => _error = e.message);
    } catch (_) {
      setState(() => _error = 'Impossible de charger les comptes.');
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _roleLabel(UserRole role) {
    switch (role) {
      case UserRole.dev:
        return 'Développeur';
      case UserRole.admin:
        return 'Admin Collège';
      case UserRole.client:
        return 'Client';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Comptes inscrits')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? ListView(children: [Padding(padding: const EdgeInsets.all(24), child: Text(_error!))])
                : ListView.builder(
                    itemCount: _users.length,
                    itemBuilder: (context, index) {
                      final u = _users[index];
                      return ListTile(
                        leading: CircleAvatar(child: Text(u.fullName.isNotEmpty ? u.fullName[0].toUpperCase() : '?')),
                        title: Text(u.fullName),
                        subtitle: Text('${u.email}${u.phone != null && u.phone!.isNotEmpty ? ' • ${u.phone}' : ''}'),
                        trailing: Chip(label: Text(_roleLabel(u.role))),
                      );
                    },
                  ),
      ),
    );
  }
}
