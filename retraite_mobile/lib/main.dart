import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/api_client.dart';
import 'core/constants.dart';
import 'core/session.dart';
import 'core/theme.dart';
import 'core/server_address.dart';
import 'core/theme_provider.dart';
import 'screens/splash_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final apiBaseUrl = await loadServerAddress();
  runApp(RetraiteApp(initialApiBaseUrl: apiBaseUrl));
}

class RetraiteApp extends StatelessWidget {
  final String? initialApiBaseUrl;
  const RetraiteApp({super.key, this.initialApiBaseUrl});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiClient>(create: (_) => ApiClient(baseUrl: initialApiBaseUrl ?? kApiBaseUrl)),
        ChangeNotifierProvider<SessionProvider>(
          create: (context) => SessionProvider(context.read<ApiClient>()),
        ),
        ChangeNotifierProvider<ThemeModeProvider>(create: (_) => ThemeModeProvider()),
      ],
      child: Consumer<ThemeModeProvider>(
        builder: (context, themeProvider, _) => MaterialApp(
          title: kAppName,
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light(),
          darkTheme: AppTheme.dark(),
          themeMode: themeProvider.mode,
          home: const SplashScreen(),
        ),
      ),
    );
  }
}
