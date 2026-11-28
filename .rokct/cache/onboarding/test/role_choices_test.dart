// Copyright (c) 2026 ROKCT INTELLIGENCE (PTY) LTD
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published
// by the Free Software Foundation, version 3.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:onboarding_sdk/onboarding_sdk.dart';

/// Host-supplied role cards (IntroDeps.roleChoices): absent by default, so
/// every app that passes none keeps the shipped two-card role step; a host
/// that opts in (Supacharge's kids path) gets its card, its own slides and
/// its fixed palette for the rest of the run.
void main() {
  const cream = Color(0xFFFFF8E7);
  const palette = OnboardingPalette(
    background: cream,
    card: Colors.white,
    ink: Color(0xFF1F2A44),
    secondaryInk: Color(0xFF5B6478),
    accent: Color(0xFFFFE08A),
    onAccent: Color(0xFF1F2A44),
  );
  const kidsChoice = OnboardingRoleChoice(
    role: OnboardingRole.youngChild,
    label: 'My child (Grades R-3)',
    subtitle: 'A grown-up sets it up',
    emoji: '🧒',
    railLabel: 'My child',
    doneCaption: 'Next, pick who is learning.',
    palette: palette,
  );

  Widget slide(String id) => Builder(
    builder: (context) => Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text('slide $id'),
        TextButton(
          key: Key('host.$id.next'),
          onPressed: OnboardingSlideScope.of(context).next,
          child: const Text('next'),
        ),
      ],
    ),
  );

  List<OnboardingSlide> slides() => [
    OnboardingSlide(
      content: slide('grade'),
      data: const {'id': 'grade'},
      roles: const {OnboardingRole.student},
    ),
    OnboardingSlide(
      content: slide('kid'),
      data: const {'id': 'kid'},
      title: 'Add your child',
      roles: const {OnboardingRole.youngChild},
    ),
  ];

  Future<void> pump(WidgetTester tester, IntroDeps deps) async {
    tester.view.physicalSize = const Size(390, 844);
    tester.view.devicePixelRatio = 1;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);
    await tester.pumpWidget(
      ProviderScope(
        child: ScreenUtilInit(
          designSize: const Size(390, 844),
          builder: (_, __) => MaterialApp(
            theme: ThemeData(brightness: Brightness.dark),
            home: IntroPage(deps: deps),
          ),
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.text('Get started'));
    await tester.pumpAndSettle();
  }

  Color scaffoldColor(WidgetTester tester) =>
      tester.widget<Scaffold>(find.byType(Scaffold).first).backgroundColor!;

  testWidgets('no host choices: the role step is the shipped two cards', (
    tester,
  ) async {
    await pump(
      tester,
      IntroDeps(slides: slides(), store: InMemoryOnboardingProgressStore()),
    );
    expect(find.text("I'm the student"), findsOneWidget);
    expect(find.text("I'm a parent/guardian"), findsOneWidget);
    expect(find.byKey(const Key('onboarding.role.youngChild')), findsNothing);
    expect(find.text('My child (Grades R-3)'), findsNothing);
  });

  testWidgets('an opted-in choice shows after the built-in cards', (
    tester,
  ) async {
    await pump(
      tester,
      IntroDeps(
        slides: slides(),
        roleChoices: const [kidsChoice],
        store: InMemoryOnboardingProgressStore(),
      ),
    );
    final card = find.byKey(const Key('onboarding.role.youngChild'));
    expect(card, findsOneWidget);
    expect(find.text('My child (Grades R-3)'), findsOneWidget);
    expect(find.text('🧒'), findsOneWidget);
    // Below the parent card.
    expect(
      tester.getTopLeft(card).dy,
      greaterThan(tester.getTopLeft(find.text("I'm a parent/guardian")).dy),
    );
  });

  testWidgets(
    'choosing it runs only its own slides, in its palette, to its caption',
    (tester) async {
      final deps = IntroDeps(
        slides: slides(),
        roleChoices: const [kidsChoice],
        store: InMemoryOnboardingProgressStore(),
      );
      await pump(tester, deps);
      final before = scaffoldColor(tester);
      expect(before, isNot(cream));

      await tester.tap(find.byKey(const Key('onboarding.role.youngChild')));
      await tester.pumpAndSettle();

      expect(find.text('slide kid'), findsOneWidget);
      expect(find.text('slide grade'), findsNothing);
      expect(scaffoldColor(tester), cream);
      // The rail names the host's label and counts welcome, role, the one
      // kids slide and done.
      expect(find.text('STEP 3 OF 4'), findsOneWidget);

      await tester.tap(find.byKey(const Key('host.kid.next')));
      await tester.pumpAndSettle();
      expect(find.text("You're all set!"), findsOneWidget);
      expect(find.text('Next, pick who is learning.'), findsOneWidget);
      expect(scaffoldColor(tester), cream);
    },
  );

  testWidgets('a student run keeps the app colours with a choice listed', (
    tester,
  ) async {
    await pump(
      tester,
      IntroDeps(
        slides: slides(),
        roleChoices: const [kidsChoice],
        store: InMemoryOnboardingProgressStore(),
      ),
    );
    await tester.tap(find.text("I'm the student"));
    await tester.pumpAndSettle();
    expect(find.text('slide grade'), findsOneWidget);
    expect(find.text('slide kid'), findsNothing);
    expect(scaffoldColor(tester), isNot(cream));
  });

  test('rail outcome uses the host railLabel; built-ins unchanged', () {
    final n = IntroNotifier(slides: slides(), roleChoices: const [kidsChoice]);
    n.showRoleStep();
    n.chooseRole(OnboardingRole.youngChild);
    expect(n.runSteps[1].outcome, 'My child');
    expect(n.visibleSlides, hasLength(1));
    n.dispose();

    final plain = IntroNotifier(slides: slides());
    plain.showRoleStep();
    plain.chooseRole(OnboardingRole.parent);
    expect(plain.runSteps[1].outcome, 'Parent/guardian');
    expect(plain.visibleSlides, isEmpty);
    plain.dispose();
  });

  test('IntroDeps.choiceFor finds only listed roles', () {
    const deps = IntroDeps(roleChoices: [kidsChoice]);
    expect(deps.choiceFor(OnboardingRole.youngChild), same(kidsChoice));
    expect(deps.choiceFor(OnboardingRole.parent), isNull);
    expect(deps.choiceFor(null), isNull);
    expect(const IntroDeps().roleChoices, isEmpty);
  });

  test('a run record with the new role round-trips', () {
    final r = OnboardingRunRecord(
      stepIndex: 1,
      done: const {'kid'},
      lastTouched: DateTime.utc(2026, 10, 16),
      role: OnboardingRole.youngChild,
      roleStepVisible: true,
    );
    expect(
      OnboardingRunRecord.fromJson(r.toJson())?.role,
      OnboardingRole.youngChild,
    );
  });
}
