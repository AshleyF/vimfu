const gt = require('./test/ground_truth_ex_commands.json');
const caseName = process.argv[2] || 'marks_no_marks';
let c = gt[caseName];
if (!c) { console.log('Case not found'); process.exit(1); }
console.log('keys:', JSON.stringify(c.keys));
console.log('initialContent:', JSON.stringify(c.initialContent));
const lines = c.frame.lines;
for (let i = 0; i < lines.length; i++) {
  console.log(`row ${i}: text=${JSON.stringify(lines[i].text)}`);
}
console.log('cursor:', JSON.stringify(c.frame.cursor));
