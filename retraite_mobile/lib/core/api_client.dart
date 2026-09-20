import 'dart:convert';

import 'package:http/http.dart' as http;

import 'constants.dart';

class ApiException implements Exception {
  final int statusCode;
  final String message;

  ApiException(this.statusCode, this.message);

  @override
  String toString() => message;
}

/// Client HTTP minimal pour l'API FastAPI : ajoute le token JWT et
/// transforme les réponses d'erreur en [ApiException] avec le message
/// renvoyé par le backend (`detail`).
class ApiClient {
  final String baseUrl;
  String? _token;

  ApiClient({this.baseUrl = kApiBaseUrl});

  void setToken(String? token) => _token = token;

  Map<String, String> _headers({bool json = true}) => {
        if (json) 'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  Uri _uri(String path, [Map<String, dynamic>? query]) {
    Map<String, String>? params;
    if (query != null) {
      params = {};
      query.forEach((key, value) {
        if (value != null) params![key] = value.toString();
      });
    }
    return Uri.parse('$baseUrl$path').replace(queryParameters: params);
  }

  dynamic _decode(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (response.body.isEmpty) return null;
      return jsonDecode(utf8.decode(response.bodyBytes));
    }
    String message = 'Erreur (${response.statusCode})';
    try {
      final body = jsonDecode(utf8.decode(response.bodyBytes));
      if (body is Map && body['detail'] != null) {
        final detail = body['detail'];
        message = detail is String ? detail : detail.toString();
      }
    } catch (_) {
      // réponse non-JSON : on garde le message générique
    }
    throw ApiException(response.statusCode, message);
  }

  Future<dynamic> get(String path, {Map<String, dynamic>? query}) async {
    final response = await http.get(_uri(path, query), headers: _headers());
    return _decode(response);
  }

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    final response = await http.post(
      _uri(path),
      headers: _headers(),
      body: body != null ? jsonEncode(body) : null,
    );
    return _decode(response);
  }

  Future<List<int>> getBytes(String path) async {
    final response = await http.get(_uri(path), headers: _headers(json: false));
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.bodyBytes;
    }
    throw ApiException(response.statusCode, 'Impossible de récupérer le fichier.');
  }
}
