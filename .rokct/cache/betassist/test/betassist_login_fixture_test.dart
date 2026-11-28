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

import 'package:betassist_sdk/src/common/presentation/pages/login/betassist_login_page.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('a feed row becomes a board row', () {
    final f = BetassistLoginFixture.fromFeed({
      'teamA': 'Home FC',
      'teamB': 'Away United',
      'kickoff_time': '2026-11-28 15:00:00',
      'analysis': {'confidence_score': 64.4, 'prediction': 'Home'},
    })!;
    expect(f.home, 'Home FC');
    expect(f.confidence.round(), 64);
    expect(f.pick, 'Home');
  });
  test('a row with no kickoff is dropped', () {
    expect(BetassistLoginFixture.fromFeed({'teamA': 'x'}), isNull);
  });
}
