enum UserRole { dev, admin, client }

UserRole userRoleFromString(String value) {
  return UserRole.values.firstWhere(
    (r) => r.name == value,
    orElse: () => UserRole.client,
  );
}

class AppUser {
  final int id;
  final String email;
  final String fullName;
  final String? phone;
  final UserRole role;
  final DateTime createdAt;

  AppUser({
    required this.id,
    required this.email,
    required this.fullName,
    required this.phone,
    required this.role,
    required this.createdAt,
  });

  bool get isAdminOrDev => role == UserRole.admin || role == UserRole.dev;

  factory AppUser.fromJson(Map<String, dynamic> json) => AppUser(
        id: json['id'] as int,
        email: json['email'] as String,
        fullName: json['full_name'] as String,
        phone: json['phone'] as String?,
        role: userRoleFromString(json['role'] as String),
        createdAt: DateTime.parse(json['created_at'] as String),
      );
}
