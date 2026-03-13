" Null clipboard provider for VimFu ground-truth generation
let g:null_clip_detect_called = 0
let g:null_clip_call_called = 0
function! provider#clipboard#Detect() abort
  let g:null_clip_detect_called += 1
  return 'null'
endfunction
function! provider#clipboard#Call(method, args) abort
  let g:null_clip_call_called += 1
  if a:method ==# 'get'
    return [[], '']
  endif
  return 0
endfunction
