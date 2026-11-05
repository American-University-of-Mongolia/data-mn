import { test } from 'node:test';
import assert from 'node:assert/strict';
import { compareStatRows, latestSeason, playerIdentity } from '../src/scripts/sports-browser.js';

test('null statistics sort last in both directions, with an equal null/null comparison', () => {
  const rows = [{ name: 'a', value: null }, { name: 'b', value: 0 }, { name: 'c', value: 5 }, { name: 'd' }];
  for (const direction of [-1, 1]) {
    const compare = (a, b) => compareStatRows(a, b, 'value', direction);
    assert.equal(compare(rows[0], rows[3]), 0);
    assert.equal(compare(rows[3], rows[0]), 0);
    for (const a of rows) for (const b of rows) assert.equal(compare(a, b) + compare(b, a), 0);
    assert.deepEqual(
      [...rows].sort(compare).map((r) => r.name),
      direction === 1 ? ['b', 'c', 'a', 'd'] : ['c', 'b', 'a', 'd']
    );
  }
});

test('same-name players on different teams or profiles remain distinct', () => {
  assert.notEqual(playerIdentity({ team: 'A', name: 'Same Name' }), playerIdentity({ team: 'B', name: 'Same Name' }));
  assert.notEqual(
    playerIdentity({ team: 'A', name: 'Same Name', identity: 'one' }),
    playerIdentity({ team: 'A', name: 'Same Name', identity: 'two' })
  );
  assert.equal(
    playerIdentity({ team: 'A', name: 'Latin', identity: 'one' }),
    playerIdentity({ team: 'A', name: 'Кирилл', identity: 'one' })
  );
});

test('adding a season changes the default without hardcoded years or source order', () => {
  assert.equal(latestSeason([{ id: '2027-28' }, { id: '2024-25' }, { id: '2025-26' }]).id, '2027-28');
  assert.equal(latestSeason([{ id: '2030-31' }]).id, '2030-31');
});
