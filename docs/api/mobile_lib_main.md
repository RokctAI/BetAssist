# API Reference: main

Source file: `mobile/lib/main.dart`

## Classes

### class `UserProfile`

### class `OnboardingScreen`

## Whitelisted API Endpoints

### `UserProfile(user: user, localFavoriteTeam: localFavoriteTeam ?? this.localFavoriteTeam, intlFavoriteTeam: intlFavoriteTeam ?? this.intlFavoriteTeam, monthlyBudget: monthlyBudget ?? this.monthlyBudget, remainingBudget: remainingBudget ?? this.remainingBudget, budgetLocked: budgetLocked ?? this.budgetLocked, followedTeams: followedTeams ?? this.followedTeams, ); } } class UserProfileNotifier extends StateNotifier<UserProfile> { UserProfileNotifier() : super(UserProfile(user: "User123")); void setLocalFavorite(String team)`
*No documentation provided (generation failed).*

### `Duration(hours: 48)), league: "PSL", status: "Scheduled", score: "0-0", confidenceScore: 78.0, predictedWinner: "Orlando Pirates", whyWin: "Orlando Pirates has a 4-match winning streak at home, while Kaizer Chiefs faces suspensions for their two key central defenders.", whyLose: "Kaizer Chiefs excels at quick counter-attacks. If Pirates overcommit their fullbacks early, they risk conceding on transition.", ), SoccerMatch( id: "m2", teamA: "Mamelodi Sundowns", teamB: "SuperSport United", teamALogo: "🌟", teamBLogo: "🛡️", kickoffTime: DateTime.now().add(const Duration(hours: 24)), league: "PSL", status: "Scheduled", score: "0-0", confidenceScore: 85.0, predictedWinner: "Mamelodi Sundowns", whyWin: "Sundowns have dominated possession statistics (averaging 68% in their last 5 matches) and play with home advantage.", whyLose: "SuperSport United are physical on set pieces. A lack of concentration on corners is Sundowns' primary vulnerability.", ), SoccerMatch( id: "m3", teamA: "Manchester City", teamB: "Arsenal", teamALogo: "🩵", teamBLogo: "🔴", kickoffTime: DateTime.now().add(const Duration(hours: 12)), league: "EPL", status: "Scheduled", score: "0-0", confidenceScore: 62.0, predictedWinner: "Manchester City", whyWin: "City has won the last three home clashes against Arsenal, showcasing superior attacking transition metrics.", whyLose: "Arsenal boasts the best defensive expected goals (xGA) record away from home in the league this season.", ), ]; }); class AppColors { static const Color background = Color(0xFF0A0E12); static const Color surface = Color(0xFF141A22); static const Color accent = Color(0xFF00E676); static const Color alert = Color(0xFFFF3D00); static const Color textPrimary = Colors.white; static const Color textSecondary = Color(0xFF90A4AE); } final themeData = ThemeData( scaffoldBackgroundColor: AppColors.background, primaryColor: AppColors.accent, colorScheme: ColorScheme.dark( surface: AppColors.background, primary: AppColors.accent, secondary: AppColors.accent, ), textTheme: const TextTheme( headlineMedium: TextStyle(color: AppColors.textPrimary, fontSize: 24, fontWeight: FontWeight.bold), bodyMedium: TextStyle(color: AppColors.textSecondary, fontSize: 14), ), ); final routerProvider = Provider<GoRouter>((ref)`
*No documentation provided (generation failed).*

### `build(BuildContext context)`
*No documentation provided (generation failed).*

### `Scaffold(body: SafeArea( child: Padding( padding: const EdgeInsets.all(24.0), child: Column( crossAxisAlignment: CrossAxisAlignment.start, children: [ Row( mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [ Text("BETASSIST", style: TextStyle(color: AppColors.accent, fontWeight: FontWeight.bold, letterSpacing: 1.5)), Text("STEP $_step OF 3", style: const TextStyle(color: AppColors.textSecondary)), ], ), const SizedBox(height: 8), LinearProgressIndicator( value: _step / 3.0, backgroundColor: AppColors.surface, valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accent), ), const SizedBox(height: 48), if (_step == 1) ...[ const Text("Choose Local Favorite Team", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)), const SizedBox(height: 8), const Text("This selection is permanent. You will never be allowed to place bets on matches involving this team to eliminate bias.", style: TextStyle(color: AppColors.textSecondary)), const SizedBox(height: 24), Expanded( child: ListView.builder( itemCount: localTeams.length, itemBuilder: (context, index)`
*No documentation provided (generation failed).*

### `Duration(milliseconds: 350), ()`
*No documentation provided (generation failed).*

### `dispose()`
*No documentation provided (generation failed).*

### `RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16)), ), builder: (context)`
*No documentation provided (generation failed).*

### `Container(padding: const EdgeInsets.only(bottom: 24), height: 420, child: ARCardBack( match: match, isFav: isFav, isFollowing: isFollowing, recommendedStake: maxBet, onPlaceBet: ()`
*No documentation provided (generation failed).*

### `SnackBar(content: Text("Failed to place bet. Budget exhausted or locked."), backgroundColor: AppColors.alert, ), ); } }, ), ); }, ); } @override Widget build(BuildContext context)`
*No documentation provided (generation failed).*

### `Scaffold(bottomNavigationBar: BottomAppBar( color: AppColors.surface, child: Padding( padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 8.0), child: Row( mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [ IconButton(icon: const Icon(Icons.home, color: AppColors.accent), onPressed: ()`
*No documentation provided (generation failed).*

### `ARScanScreen(match: currentMatch, isFav: isFav, isFollowing: isFollowing, recommendedStake: maxBet, onPlaceBet: ()`
*No documentation provided (generation failed).*

### `SnackBar(content: Text("Failed to place bet. Budget exhausted or locked."), backgroundColor: AppColors.alert, ), ); } }, ), ), ); } else { ScaffoldMessenger.of(context).showSnackBar( const SnackBar( content: Text("AR Scan requires a Gyroscope. Tap any match to view analysis instead."), backgroundColor: AppColors.surface, ), ); } }, child: const Icon(Icons.camera_alt, color: Colors.black), ), IconButton(icon: const Icon(Icons.person, color: Colors.white), onPressed: ()`
*No documentation provided (generation failed).*

### `Text("AVAILABLE BANKROLL", style: TextStyle(fontSize: 11, color: AppColors.textSecondary, letterSpacing: 1.0)), Text("R ${profile.remainingBudget.toStringAsFixed(2)}", style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.accent)), ], ), Column( crossAxisAlignment: CrossAxisAlignment.end, children: [ const Text("MONTHLY LIMIT", style: TextStyle(fontSize: 11, color: AppColors.textSecondary, letterSpacing: 1.0)), Text("R ${profile.monthlyBudget.toStringAsFixed(2)}", style: const TextStyle(fontSize: 16, color: Colors.white)), ], ), ], ), const SizedBox(height: 16), LinearProgressIndicator( value: profile.remainingBudget / (profile.monthlyBudget > 0 ? profile.monthlyBudget : 1.0), backgroundColor: AppColors.surface, valueColor: const AlwaysStoppedAnimation<Color>(AppColors.accent), ), const SizedBox(height: 32), Row( mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [ const Text("LIVE TELEMETRY FEED", style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.textSecondary, letterSpacing: 1.2)), Text("${feedMatches.length} Matches Loaded", style: const TextStyle(fontSize: 11, color: AppColors.accent)), ], ), const SizedBox(height: 16), Expanded( child: ListView.builder( itemCount: feedMatches.length, itemBuilder: (context, index)`
*No documentation provided (generation failed).*

### `Card(color: AppColors.surface, margin: const EdgeInsets.only(bottom: 16), child: Padding( padding: const EdgeInsets.all(16.0), child: Column( children: [ Row( mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [ Text(match.league, style: const TextStyle(fontSize: 11, color: AppColors.accent, fontWeight: FontWeight.bold)), Text(match.status, style: const TextStyle(fontSize: 11, color: AppColors.textSecondary)), ], ), const SizedBox(height: 16), Row( mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [ Column( children: [ Text(match.teamALogo, style: const TextStyle(fontSize: 32)), const SizedBox(height: 4), Text(match.teamA, style: TextStyle(fontSize: 13, color: isFavA ? AppColors.accent : Colors.white)), if (isFavA) const Text("FAVORITE (LOCKED)", style: TextStyle(fontSize: 8, color: AppColors.alert, fontWeight: FontWeight.bold)), ], ), const Text("VS", style: TextStyle(color: AppColors.textSecondary, fontWeight: FontWeight.bold)), Column( children: [ Text(match.teamBLogo, style: const TextStyle(fontSize: 32)), const SizedBox(height: 4), Text(match.teamB, style: TextStyle(fontSize: 13, color: isFavB ? AppColors.accent : Colors.white)), if (isFavB) const Text("FAVORITE (LOCKED)", style: TextStyle(fontSize: 8, color: AppColors.alert, fontWeight: FontWeight.bold)), ], ), ], ), const SizedBox(height: 16), Row( mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [ Text("Confidence: ${match.confidenceScore}%", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)), TextButton( onPressed: ()`
*No documentation provided (generation failed).*

### `ARScanScreen(match: match, isFav: isFav, isFollowing: isFollowing, recommendedStake: maxBet, onPlaceBet: ()`
*No documentation provided (generation failed).*
