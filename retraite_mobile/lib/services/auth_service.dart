import '../core/api_client.dart';
import '../models/user.dart';

class AuthService {
  final ApiClient api;
  AuthService(this.api);

  Future<AppUser> register({
    required String email,
    required String password,
    required String fullName,
    String? phone,
  }) async {
    final json = await api.post('/auth/register', body: {
      'email': email,
      'password': password,
      'full_name': fullName,
      if (phone != null && phone.isNotEmpty) 'phone': phone,
    });
    return AppUser.fromJson(json as Map<String, dynamic>);
  }

  Future<String> login({required String email, required String password}) async {
    final json = await api.post('/auth/login', body: {'email': email, 'password': password});
    return json['access_token'] as String;
  }

  Future<AppUser> me() async {
    final json = await api.get('/auth/me');
    return AppUser.fromJson(json as Map<String, dynamic>);
  }

  Future<List<AppUser>> listUsers() async {
    final json = await api.get('/auth/users') as List;
    return json.map((e) => AppUser.fromJson(e as Map<String, dynamic>)).toList();
  }
}
