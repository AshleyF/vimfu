const gt = require('./test/ground_truth_ex_commands.json');
const cases = Object.values(gt).flat ? Object.values(gt).flat() : gt;
let c;
if (Array.isArray(gt)) {
  c = gt.find(x => x.name === 'normal_dd_on_range');
} else {
  // It's an object keyed by name
  c = gt['normal_dd_on_range'];
}
if (!c) {
  // Try iterating
  for (const [k, v] of Object.entries(gt)) {
    if (k === 'normal_dd_on_range' || (v && v.name === 'normal_dd_on_range')) {
      c = v;
      break;
    }
  }
}
console.log('keys:', JSON.stringify(c.keys));
console.log('initialContent:', JSON.stringify(c.initialContent));
console.log('textLines:', JSON.stringify(c.textLines));
console.log('cursor:', JSON.stringify(c.cursor || c.frame.cursor));
const lines = c.frame.lines;
for (let i = 0; i < Math.min(6, lines.length); i++) {
  console.log(`row ${i}: ${JSON.stringify(lines[i].text)}`);
}
