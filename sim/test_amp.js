// Correct order: escape $ FIRST, then convert &
let replacement = '[&]';
let jsReplacement = replacement
  .replace(/\\&/g, '\x00AMP')      // protect literal \&
  .replace(/\$/g, '$$$$')           // escape ALL bare $ (vim $ is literal) 
  .replace(/&/g, '$$&')             // vim & → JS $&
  .replace(/\x00AMP/g, '&');        // restore literal &
console.log('case1 jsReplacement:', JSON.stringify(jsReplacement));
console.log('case1 final:', 'Line 01'.replace(/Line/g, jsReplacement));

// Test with literal $ in vim replacement (should stay literal)
let rep2 = '$[&]';
let js2 = rep2
  .replace(/\\&/g, '\x00AMP')
  .replace(/\$/g, '$$$$')
  .replace(/&/g, '$$&')
  .replace(/\x00AMP/g, '&');
console.log('case2 jsReplacement:', JSON.stringify(js2));
console.log('case2 final:', 'Line 01'.replace(/Line/g, js2));

// Test with escaped \& (literal & in output)
let rep3 = '[\\&]';
let js3 = rep3
  .replace(/\\&/g, '\x00AMP')
  .replace(/\$/g, '$$$$')
  .replace(/&/g, '$$&')
  .replace(/\x00AMP/g, '&');
console.log('case3 jsReplacement:', JSON.stringify(js3));
console.log('case3 final:', 'Line 01'.replace(/Line/g, js3));
