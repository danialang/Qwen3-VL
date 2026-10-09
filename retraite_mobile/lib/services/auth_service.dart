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

  Future<void> changePassword({required String currentPassword, required String newPassword}) async {
    await api.post('/auth/change-password', body: {
      'current_password': currentPassword,
      'new_password': newPassword,
    });
  }

  Future<void> forgotPassword({required String email}) async {
    await api.post('/auth/forgot-password', body: {'email': email});
  }

  Future<void> resetPassword({required String email, required String code, required String newPassword}) async {
    await api.post('/auth/reset-password', body: {
      'email': email,
      'code': code,
      'new_password': newPassword,
    });
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
