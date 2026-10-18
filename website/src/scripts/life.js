// Conway's B3/S23 rules on a wrapping grid. Kept independent of the canvas.
export function stepLife(cells, columns, rows) {
  const next = new Uint8Array(cells.length);
  for (let y = 0; y < rows; y++) {
    for (let x = 0; x < columns; x++) {
      let neighbors = 0;
      for (let dy = -1; dy <= 1; dy++) {
        for (let dx = -1; dx <= 1; dx++) {
          if (dx === 0 && dy === 0) continue;
          neighbors += cells[((y + dy + rows) % rows) * columns + (x + dx + columns) % columns];
        }
      }
      const index = y * columns + x;
      next[index] = neighbors === 3 || (cells[index] === 1 && neighbors === 2) ? 1 : 0;
    }
  }
  return next;
}

export function seedLife(columns, rows) {
  let seed = 42;
  const cells = new Uint8Array(columns * rows);
  // A reproducible field makes the first composition consistent across visits.
  for (let i = 0; i < cells.length; i++) {
    seed = (seed * 1664525 + 1013904223) >>> 0;
    cells[i] = seed / 4294967296 < 0.27 ? 1 : 0;
  }
  return cells;
}
