import '../core/api_client.dart';

class AssistantMessage {
  final String role;
  final String content;

  AssistantMessage({required this.role, required this.content});

  Map<String, dynamic> toJson() => {'role': role, 'content': content};

  factory AssistantMessage.fromJson(Map<String, dynamic> json) =>
      AssistantMessage(role: json['role'] as String, content: json['content'] as String);
}

class AssistantReply {
  final String reply;
  final List<AssistantMessage> history;
  AssistantReply({required this.reply, required this.history});
}

/// Client pour les endpoints d'assistant IA (`/assistant/client` ou `/assistant/admin`).
/// L'historique est renvoyé par le backend à chaque appel (API sans état côté client).
class AssistantService {
  final ApiClient api;
  final String path;

  AssistantService(this.api, {required this.path});

  Future<AssistantReply> send(String message, List<AssistantMessage> history) async {
    final json = await api.post(path, body: {
      'message': message,
      'history': history.map((m) => m.toJson()).toList(),
    }) as Map<String, dynamic>;

    final newHistory = (json['history'] as List)
        .map((e) => AssistantMessage.fromJson(e as Map<String, dynamic>))
        .toList();
    return AssistantReply(reply: json['reply'] as String, history: newHistory);
  }
}
