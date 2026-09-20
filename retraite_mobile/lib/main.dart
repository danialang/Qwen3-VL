import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'core/api_client.dart';
import 'core/constants.dart';
import 'core/session.dart';
import 'core/theme.dart';
import 'core/theme_provider.dart';
import 'screens/splash_screen.dart';

void main() {
  runApp(const RetraiteApp());
}

class RetraiteApp extends StatelessWidget {
  const RetraiteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        Provider<ApiClient>(create: (_) => ApiClient()),
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
