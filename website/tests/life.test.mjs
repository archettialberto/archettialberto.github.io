import test from 'node:test';
import assert from 'node:assert/strict';
import { seedLife, stepLife } from '../src/scripts/life.js';

const grid = (columns, rows, points) => {
  const cells = new Uint8Array(columns * rows);
  for (const [x, y] of points) cells[y * columns + x] = 1;
  return cells;
};

test('a block remains still and the input grid is unchanged', () => {
  const cells = grid(6, 6, [[2, 2], [2, 3], [3, 2], [3, 3]]);
  const before = cells.slice();
  assert.deepEqual(stepLife(cells, 6, 6), cells);
  assert.deepEqual(cells, before);
});

test('a blinker oscillates every two generations', () => {
  const horizontal = grid(7, 7, [[2, 3], [3, 3], [4, 3]]);
  const vertical = grid(7, 7, [[3, 2], [3, 3], [3, 4]]);
  assert.deepEqual(stepLife(horizontal, 7, 7), vertical);
  assert.deepEqual(stepLife(vertical, 7, 7), horizontal);
});

test('a glider moves diagonally after four generations', () => {
  const points = [[3, 2], [4, 3], [2, 4], [3, 4], [4, 4]];
  let cells = grid(10, 10, points);
  for (let i = 0; i < 4; i++) cells = stepLife(cells, 10, 10);
  assert.deepEqual(cells, grid(10, 10, points.map(([x, y]) => [x + 1, y + 1])));
});

test('the grid wraps at its edges', () => {
  const cells = grid(5, 5, [[0, 0], [4, 0], [0, 4], [4, 4]]);
  assert.deepEqual(stepLife(cells, 5, 5), cells);
});

test('an isolated cell dies and an empty board stays empty', () => {
  const empty = new Uint8Array(25);
  assert.deepEqual(stepLife(grid(5, 5, [[2, 2]]), 5, 5), empty);
  assert.deepEqual(stepLife(empty, 5, 5), empty);
});

test('the initial field is reproducible and contains only living or dead cells', () => {
  const cells = seedLife(100, 50);
  assert.deepEqual(seedLife(100, 50), cells);
  assert.equal(cells.length, 5000);
  assert.ok(cells.some(value => value === 1));
  assert.ok(cells.some(value => value === 0));
  assert.ok(cells.every(value => value === 0 || value === 1));
});
