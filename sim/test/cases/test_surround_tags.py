"""Surround tag operations: dst, cst, ys{motion}t, visual S t.

In nvim-surround:
  - dst: deletes nearest surrounding HTML tag (no prompt)
  - cst: finds nearest tag, then prompts "Enter the HTML tag:" for replacement
         (user types tag name + Enter)
  - ys{motion}t: prompts "Enter the HTML tag:", user types tag name + Enter
  - visual S then t: prompts for tag name + Enter
"""

# Use nvim with user's config (has nvim-surround installed via lazy.nvim)
NVIM_CMD = 'nvim'

CASES = {
    # ==========================================================
    # dst — DELETE SURROUNDING TAG
    # ==========================================================

    "dst_simple": {
        "description": "dst removes simple div tags",
        "keys": "dst",
        "initial": "<div>hello</div>\n",
    },
    "dst_cursor_in_content": {
        "description": "dst with cursor inside content",
        "keys": "fhdst",
        "initial": "<div>hello</div>\n",
    },
    "dst_with_attrs": {
        "description": "dst removes tag with attributes",
        "keys": "dst",
        "initial": '<div class="foo">hello</div>\n',
    },
    "dst_nested_inner": {
        "description": "dst on inner tag when cursor is inside it",
        "keys": "fhdst",
        "initial": "<p><b>hello</b></p>\n",
    },
    "dst_multiline": {
        "description": "dst on multiline tag",
        "keys": "jdst",
        "initial": "<div>\n  content\n</div>\n",
    },
    "dst_empty_tag": {
        "description": "dst on tag with empty content",
        "keys": "dst",
        "initial": "<span></span>\n",
    },

    # ==========================================================
    # cst — CHANGE SURROUNDING TAG (prompts for new tag name)
    # ==========================================================

    "cst_to_span": {
        "description": "cst + span + Enter changes div to span",
        "keys": "cstspan\r",
        "initial": "<div>hello</div>\n",
    },
    "cst_to_h2": {
        "description": "cst + h2 + Enter changes div to h2",
        "keys": "csth2\r",
        "initial": "<div>hello</div>\n",
    },
    "cst_with_attrs": {
        "description": "cst on tag with attributes",
        "keys": "cstp\r",
        "initial": '<div class="foo">hello</div>\n',
    },
    "cst_nested_inner": {
        "description": "cst changes inner tag",
        "keys": "fhcstem\r",
        "initial": "<p><b>hello</b></p>\n",
    },
    "cst_multiline": {
        "description": "cst on multiline tag",
        "keys": "jcstspan\r",
        "initial": "<div>\n  content\n</div>\n",
    },

    # ==========================================================
    # ys{motion}t — ADD TAG SURROUND (prompts for tag name)
    # ==========================================================

    "ysiw_tag_div": {
        "description": "ysiwt + div + Enter wraps word in div tag",
        "keys": "ysiwtdiv\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
    "ysiw_tag_p": {
        "description": "ysiwt + p + Enter wraps word in p tag",
        "keys": "ysiwtp\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
    "ysiw_tag_span": {
        "description": "ysiwt + span + Enter wraps word in span tag",
        "keys": "ysiwtspan\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
    "ysaw_tag_b": {
        "description": "ysawt + b + Enter wraps a-word in b tag",
        "keys": "ysawtb\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
    "yss_tag_div": {
        "description": "ysst + div + Enter wraps whole line in div",
        "keys": "ysstdiv\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },

    # ==========================================================
    # VISUAL S + t — TAG SURROUND IN VISUAL MODE
    # ==========================================================

    "visual_S_tag_div": {
        "description": "viwSt + div + Enter wraps visual in div",
        "keys": "viwStdiv\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
    "visual_line_S_tag_div": {
        "description": "VSt + div + Enter wraps visual line in div",
        "keys": "VStdiv\r",
        "initial": "hello world\n",
        "settle": 0.5,
    },
}
