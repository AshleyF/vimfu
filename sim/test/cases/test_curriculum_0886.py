"""Tests for video range 0886-0895: recipe series."""

CASES = {
    # ── 0886 :%norm A; — append semicolons to every line ────
    "recipe_append_semicolons": {
        "description": ":%norm A; appends ; to every line",
        "keys": ":%norm A;\r",
        "initial": "let x = 1\nlet y = 2\nlet z = x + y\nconsole.log(x)\n",
    },

    # ── 0888 :%sort u — sort + dedup ─────────────────────
    "recipe_sort_unique": {
        "description": ":%sort u sorts and removes duplicate lines",
        "keys": ":%sort u\r",
        "initial": "banana\napple\ncherry\napple\ndate\nbanana\ncherry\nfig\napple\ndate\n",
    },

    # ── 0889 :g/^/m 0 — reverse file ─────────────────────
    "recipe_reverse_file": {
        "description": ":g/^/m 0 reverses entire file",
        "keys": ":g/^/m 0\r",
        "initial": "1. First\n2. Second\n3. Third\n4. Fourth\n5. Fifth\n",
    },

    # ── 0890 :v/PATTERN/d — keep matching, delete rest ───
    "recipe_extract_matching_v": {
        "description": ":v/TODO/d keeps only lines with TODO",
        "keys": ":v/TODO/d\r",
        "initial": "setup database\nTODO: fix login bug\nwrite tests\nTODO: add validation\ndeploy server\nTODO: update docs\n",
    },

    # ── 0891 :3,7norm I# — comment a range ────────────────
    "recipe_comment_range": {
        "description": ":3,7norm I#<space> comments lines 3-7",
        "keys": ":3,7norm I# \r",
        "initial": "def process():\n    load_data()\n    validate()\n    transform()\n    save()\n    notify()\n    cleanup()\n    report()\n",
    },

    # ── 0892 :2,5> — indent a range ───────────────────────
    "recipe_indent_range": {
        "description": ":set shiftwidth=4 then :2,5> indents lines 2-5",
        "keys": ":set shiftwidth=4\r:2,5>\r",
        "initial": "def greet():\nname = \"World\"\nmsg = \"Hello\"\nprint(msg)\nreturn msg\n",
    },

    # ── 0893 :1,4y a then "ap — yank to named register ────
    "recipe_yank_to_named_register": {
        "description": ":1,4y a then G then \"ap pastes lines 1-4 at bottom",
        "keys": ":1,4y a\rG\"ap",
        "initial": "alpha()\nbravo()\ncharlie()\ndelta()\n\n# paste here:\n",
    },

    # ── 0894 :1,6sort — sort a range ──────────────────────
    "recipe_sort_range": {
        "description": ":1,6sort sorts only first 6 lines",
        "keys": ":1,6sort\r",
        "initial": "import sys\nimport json\nimport os\nimport re\nimport math\nimport csv\n\ndef main():\n    pass\n",
    },

    # ── 0895 :%s/\\s\\+$// — clean trailing whitespace ────
    "recipe_clean_trailing_whitespace": {
        "description": ":%s/\\s\\+$//g removes trailing whitespace from all lines",
        "keys": ":%s/\\s\\+$//g\r",
        "initial": "name = \"Alice\"   \nage = 30         \ncity = \"NYC\"     \nscore = 95       \ngrade = \"A\"      \n",
    },
}
