/**
 * VimFu Simulator – Tmux (Terminal Multiplexer)
 *
 * A faithful simulation of tmux running inside the VimFu terminal.
 * Supports:
 *   - Sessions, windows, and panes (full hierarchy)
 *   - Vertical (%) and horizontal (") pane splitting
 *   - Pane navigation (arrows, o), resizing (Ctrl-arrows), zoom (z)
 *   - Window management: create (c), switch (n/p/0-9), rename (,), last (l)
 *   - Pane close with confirmation (x), break pane to window (!)
 *   - Swap panes ({ / })
 *   - Status bar with window list + clock
 *   - Copy mode ([) with vi keybindings
 *   - Command prompt (:) with tmux commands
 *   - Display pane numbers (q)
 *   - Clock mode (t)
 *   - Cycle layouts (Space)
 *   - Detach (d)
 *   - Help (?)
 *
 * Architecture:
 *   Tmux
 *     └── TmuxSession[]
 *           └── TmuxWindow[]
 *                 └── LayoutNode (binary tree)
 *                       └── TmuxPane (leaf nodes)
 *                             └── SessionManager (per-pane shell+vim)
 *
 * Each pane runs an independent SessionManager with its own shell and
 * optional vim instance. The Tmux class composites their frames together,
 * drawing borders and the status bar.
 */

// No direct import of SessionManager — a factory function is injected
// at construction time to avoid circular dependencies.

// ── Constants ──

const PREFIX_KEY = 'Ctrl-B';

/** Border drawing characters */
const BORDER = {
  H: '\u2500',   // ─  horizontal
  V: '\u2502',   // │  vertical
  TL: '\u250c',  // ┌  top-left
  TR: '\u2510',  // ┐  top-right
  BL: '\u2514',  // └  bottom-left
  BR: '\u2518',  // ┘  bottom-right
  T: '\u252c',   // ┬  top tee
  B: '\u2534',   // ┴  bottom tee
  L: '\u251c',   // ├  left tee
  R: '\u2524',   // ┤  right tee
  X: '\u253c',   // ┼  cross
};

/** Tmux interaction modes */
const TmuxMode = {
  NORMAL: 'normal',           // forwarding keys to active pane
  PREFIX: 'prefix',           // waiting for command after Ctrl-b
  COMMAND: 'command',         // : command prompt
  CONFIRM: 'confirm',         // y/n confirmation (close pane)
  RENAME: 'rename',           // renaming a window
  COPY: 'copy',               // copy mode (scrollback)
  WINDOW_LIST: 'window_list', // interactive window chooser (w)
  PANE_NUMBERS: 'pane_numbers', // showing pane numbers (q)
  CLOCK: 'clock',             // clock display (t)
  HELP: 'help',               // help overlay (?)
};

/** Layout split direction */
const SplitDir = {
  HSPLIT: 'hsplit', // top/bottom (horizontal divider line)
  VSPLIT: 'vsplit', // left/right (vertical divider line)
};

// ── Layout Tree ──

/**
 * Binary tree node for pane layout within a window.
 * Leaf nodes contain a pane; internal nodes split the space.
 */
class LayoutNode {
  /**
   * @param {'leaf'|'hsplit'|'vsplit'} type
   * @param {TmuxPane} [pane] – only for leaf nodes
   */
  constructor(type, pane = null) {
    this.type = type;
    this.pane = pane;
    /** @type {LayoutNode|null} */
    this.first = null;   // top or left child
    /** @type {LayoutNode|null} */
    this.second = null;  // bottom or right child
    this.ratio = 0.5;    // how much space goes to first child

    // Bounding box (set by computeLayout)
    this.top = 0;
    this.left = 0;
    this.width = 0;
    this.height = 0;
  }

  /** Check if this is a leaf node */
  isLeaf() { return this.type === 'leaf'; }

  /** Get all leaf panes under this node */
  getPanes() {
    if (this.isLeaf()) return [this.pane];
    return [...this.first.getPanes(), ...this.second.getPanes()];
  }

  /** Find the leaf node containing a specific pane */
  findLeaf(pane) {
    if (this.isLeaf()) return this.pane === pane ? this : null;
    return this.first.findLeaf(pane) || this.second.findLeaf(pane);
  }

  /** Find the parent of a given node */
  findParent(target) {
    if (this.isLeaf()) return null;
    if (this.first === target || this.second === target) return this;
    return this.first.findParent(target) || this.second.findParent(target);
  }

  /**
   * Compute bounding boxes for all nodes in the tree.
   * @param {number} top
   * @param {number} left
   * @param {number} width
   * @param {number} height
   */
  computeLayout(top, left, width, height) {
    this.top = top;
    this.left = left;
    this.width = width;
    this.height = height;

    if (this.isLeaf()) {
      // Update the pane's dimensions
      if (this.pane) {
        this.pane.top = top;
        this.pane.left = left;
        this.pane.width = width;
        this.pane.height = height;
        this.pane._resize(width, height);
      }
      return;
    }

    if (this.type === SplitDir.HSPLIT) {
      // Horizontal split: top/bottom with a 1-row border between
      // Use floor(height * ratio) to match real tmux: first pane gets ≥ half
      const firstH = Math.max(1, Math.floor(height * this.ratio));
      const secondH = height - 1 - firstH;
      this.first.computeLayout(top, left, width, firstH);
      // border row is at top + firstH
      this.second.computeLayout(top + firstH + 1, left, width, Math.max(1, secondH));
    } else {
      // Vertical split: left/right with a 1-col border between
      // Use floor(width * ratio) to match real tmux: first pane gets ≥ half
      const firstW = Math.max(1, Math.floor(width * this.ratio));
      const secondW = width - 1 - firstW;
      this.first.computeLayout(top, left, firstW, height);
      // border col is at left + firstW
      this.second.computeLayout(top, left + firstW + 1, Math.max(1, secondW), height);
    }
  }
}

// ── Pane ──

let _paneIdCounter = 0;

class TmuxPane {
  /**
   * @param {number} width
   * @param {number} height
   * @param {object} session – a pre-built SessionManager (from factory)
   */
  constructor(width, height, session) {
    this.id = _paneIdCounter++;
    this.width = width;
    this.height = height;
    this.top = 0;
    this.left = 0;

    // Each pane has its own independent SessionManager (injected)
    this.session = session;

    // Copy mode scrollback
    this._copyModeScroll = 0;
    this._copyModeCursor = { row: 0, col: 0 };
  }

  /**
   * Resize the pane's internal SessionManager to match new dimensions.
   */
  _resize(newWidth, newHeight) {
    // Compare against the session's actual dimensions, not the pane layout
    // dimensions (which are already updated by computeLayout before this call)
    if (newWidth === this.session.cols && newHeight === this.session.rows) return;
    this.width = newWidth;
    this.height = newHeight;

    // Update SessionManager dimensions
    this.session.rows = newHeight;
    this.session.cols = newWidth;

    // Update shell dimensions
    this.session.shell.rows = newHeight;
    this.session.shell.cols = newWidth;
    this.session.shell._textRows = newHeight - 1;

    // Update screen renderer dimensions
    this.session.screen.rows = newHeight;
    this.session.screen.cols = newWidth;

    // Update vim engine if active
    if (this.session.engine) {
      this.session.engine.rows = newHeight;
      this.session.engine.cols = newWidth;
      this.session.engine._textRows = newHeight - 2;
    }
  }

  /** Feed a key to this pane's SessionManager */
  feedKey(key) {
    this.session.feedKey(key);
  }

  /** Render this pane's current frame */
  renderFrame() {
    return this.session.renderFrame();
  }

  /** Get display title (current command or shell prompt) */
  getTitle() {
    if (this.session.mode === 'vim') {
      return this.session._vimFilename || '[No Name]';
    }
    return this.session.shell._inputLine
      ? this.session.shell._inputLine.split(/\s/)[0]
      : 'zsh';
  }
}

// ── Window ──

let _windowIdCounter = 0;

class TmuxWindow {
  /**
   * @param {string} name
   * @param {number} rows – available rows for panes (total - status bar)
   * @param {number} cols
   * @param {function} createPaneSession – (cols, rows) => SessionManager
   */
  constructor(name, rows, cols, createPaneSession) {
    this.id = _windowIdCounter++;
    this.name = name;
    this.rows = rows;
    this.cols = cols;
    this._createPaneSession = createPaneSession;

    // Create initial pane
    const pane = new TmuxPane(cols, rows, createPaneSession(cols, rows));
    this.layout = new LayoutNode('leaf', pane);
    this.activePane = pane;
    this.lastActivePane = null;
    this._zoomed = false;
    this._zoomSavedLayout = null;
  }

  /** Get all panes in this window */
  getPanes() {
    return this.layout.getPanes();
  }

  /** Get the index of the active pane among all panes */
  getActivePaneIndex() {
    const panes = this.getPanes();
    return panes.indexOf(this.activePane);
  }

  /**
   * Split the active pane.
   * @param {'h'|'v'} direction – 'h' = horizontal (top/bottom), 'v' = vertical (left/right)
   * @returns {TmuxPane|null} the new pane, or null if too small
   */
  splitPane(direction) {
    const pane = this.activePane;
    const leaf = this.layout.findLeaf(pane);
    if (!leaf) return null;

    // Check minimum size
    if (direction === 'h' && pane.height < 4) return null; // need at least 2+1+1
    if (direction === 'v' && pane.width < 4) return null;  // need at least 2+1+1

    // Create new pane (dimensions will be set by computeLayout)
    const newPane = new TmuxPane(1, 1, this._createPaneSession(1, 1));

    // Transform the leaf into a split node
    const splitType = direction === 'h' ? SplitDir.HSPLIT : SplitDir.VSPLIT;
    leaf.type = splitType;
    leaf.first = new LayoutNode('leaf', pane);
    leaf.second = new LayoutNode('leaf', newPane);
    leaf.pane = null;
    leaf.ratio = 0.5;

    // Recompute layout
    this.layout.computeLayout(0, 0, this.cols, this.rows);

    // Make the new pane active
    this.activePane = newPane;

    return newPane;
  }

  /**
   * Close a pane and adjust the layout.
   * @param {TmuxPane} pane
   * @returns {boolean} true if closed successfully
   */
  closePane(pane) {
    const panes = this.getPanes();
    if (panes.length <= 1) return false; // can't close the last pane

    const leaf = this.layout.findLeaf(pane);
    if (!leaf) return false;

    // Find the parent split that contains this leaf
    const parent = this.layout.findParent(leaf);
    if (!parent) {
      // This leaf IS the root — shouldn't happen if >1 pane
      return false;
    }

    // Replace parent with the sibling
    const sibling = (parent.first === leaf) ? parent.second : parent.first;
    parent.type = sibling.type;
    parent.pane = sibling.pane;
    parent.first = sibling.first;
    parent.second = sibling.second;
    parent.ratio = sibling.ratio;

    // If active pane was closed, switch to another
    if (this.activePane === pane) {
      const remaining = this.getPanes();
      this.activePane = remaining[0];
    }

    // Recompute layout
    this.layout.computeLayout(0, 0, this.cols, this.rows);

    return true;
  }

  /**
   * Navigate to an adjacent pane in the given direction.
   * @param {'Up'|'Down'|'Left'|'Right'} direction
   */
  navigatePane(direction) {
    const panes = this.getPanes();
    if (panes.length <= 1) return;

    const cur = this.activePane;
    const cx = cur.left + cur.width / 2;
    const cy = cur.top + cur.height / 2;

    let best = null;
    let bestDist = Infinity;

    for (const p of panes) {
      if (p === cur) continue;
      const px = p.left + p.width / 2;
      const py = p.top + p.height / 2;

      let valid = false;
      switch (direction) {
        case 'Up':    valid = py < cy; break;
        case 'Down':  valid = py > cy; break;
        case 'Left':  valid = px < cx; break;
        case 'Right': valid = px > cx; break;
      }
      if (!valid) continue;

      const dist = Math.abs(px - cx) + Math.abs(py - cy);
      if (dist < bestDist) {
        bestDist = dist;
        best = p;
      }
    }

    if (best) {
      this.lastActivePane = this.activePane;
      this.activePane = best;
    }
  }

  /** Cycle to next pane */
  nextPane() {
    const panes = this.getPanes();
    const idx = panes.indexOf(this.activePane);
    this.lastActivePane = this.activePane;
    this.activePane = panes[(idx + 1) % panes.length];
  }

  /** Cycle to previous pane */
  prevPane() {
    const panes = this.getPanes();
    const idx = panes.indexOf(this.activePane);
    this.lastActivePane = this.activePane;
    this.activePane = panes[(idx - 1 + panes.length) % panes.length];
  }

  /**
   * Resize the active pane in a direction.
   * @param {'Up'|'Down'|'Left'|'Right'} direction
   * @param {number} [amount=1]
   */
  resizePane(direction, amount = 1) {
    // Walk up the layout tree from the active pane's leaf to find
    // the appropriate split to adjust
    const leaf = this.layout.findLeaf(this.activePane);
    if (!leaf) return;

    const _adjust = (node, dir) => {
      const parent = this.layout.findParent(node);
      if (!parent) return;

      if (dir === 'Up' || dir === 'Down') {
        if (parent.type === SplitDir.HSPLIT) {
          // Real tmux resizes by exactly 1 cell per keystroke
          const currentCells = Math.floor(parent.height * parent.ratio);
          const newCells = dir === 'Up'
            ? currentCells - amount
            : currentCells + amount;
          parent.ratio = Math.max(0.1, Math.min(0.9, newCells / parent.height));
          this.layout.computeLayout(0, 0, this.cols, this.rows);
          return;
        }
        // Wrong split direction, go up
        _adjust(parent, dir);
      } else {
        if (parent.type === SplitDir.VSPLIT) {
          // Real tmux resizes by exactly 1 cell per keystroke
          const currentCells = Math.floor(parent.width * parent.ratio);
          const newCells = dir === 'Left'
            ? currentCells - amount
            : currentCells + amount;
          parent.ratio = Math.max(0.1, Math.min(0.9, newCells / parent.width));
          this.layout.computeLayout(0, 0, this.cols, this.rows);
          return;
        }
        _adjust(parent, dir);
      }
    };

    _adjust(leaf, direction);
  }

  /** Toggle zoom on the active pane */
  toggleZoom() {
    if (this._zoomed) {
      // Unzoom — restore the original layout
      this._zoomed = false;
      this.layout.computeLayout(0, 0, this.cols, this.rows);
    } else {
      // Zoom — active pane takes the full window area
      this._zoomed = true;
      // We don't actually modify the layout tree; we just render
      // only the active pane at full size during compositing
      this.activePane._resize(this.cols, this.rows);
      this.activePane.top = 0;
      this.activePane.left = 0;
    }
  }

  /** Swap the active pane with the next pane */
  swapPaneNext() {
    const panes = this.getPanes();
    const idx = panes.indexOf(this.activePane);
    if (panes.length <= 1) return;
    const nextIdx = (idx + 1) % panes.length;
    this._swapPaneContents(panes[idx], panes[nextIdx]);
  }

  /** Swap the active pane with the previous pane */
  swapPanePrev() {
    const panes = this.getPanes();
    const idx = panes.indexOf(this.activePane);
    if (panes.length <= 1) return;
    const prevIdx = (idx - 1 + panes.length) % panes.length;
    this._swapPaneContents(panes[idx], panes[prevIdx]);
  }

  /** Swap the session contents of two panes */
  _swapPaneContents(a, b) {
    const tmpSession = a.session;
    a.session = b.session;
    b.session = tmpSession;
    // Resize sessions to match their new pane dimensions
    a._resize(a.width, a.height);
    b._resize(b.width, b.height);
  }

  /**
   * Break the active pane out into a new window.
   * @returns {TmuxPane|null} the pane that was broken out
   */
  breakPane() {
    const panes = this.getPanes();
    if (panes.length <= 1) return null; // can't break the only pane

    const pane = this.activePane;
    // Close it from this window's layout
    this.closePane(pane);
    return pane;
  }

  /** Cycle through preset layouts */
  cycleLayout() {
    const panes = this.getPanes();
    if (panes.length <= 1) return;

    // Determine current layout type and cycle to next
    // Supported layouts: even-horizontal, even-vertical, main-horizontal, main-vertical, tiled
    if (!this._layoutCycle) this._layoutCycle = 0;
    this._layoutCycle = (this._layoutCycle + 1) % 4;

    this._applyLayout(panes, this._layoutCycle);
  }

  /** Apply a preset layout to the panes */
  _applyLayout(panes, layoutIdx) {
    if (panes.length <= 1) return;

    switch (layoutIdx) {
      case 0: // even-horizontal: all panes side by side
        this.layout = this._buildEvenSplits(panes, SplitDir.VSPLIT);
        break;
      case 1: // even-vertical: all panes stacked
        this.layout = this._buildEvenSplits(panes, SplitDir.HSPLIT);
        break;
      case 2: // main-horizontal: one big pane on top, rest below
        this.layout = this._buildMainSplit(panes, SplitDir.HSPLIT);
        break;
      case 3: // main-vertical: one big pane on left, rest right
        this.layout = this._buildMainSplit(panes, SplitDir.VSPLIT);
        break;
    }

    this.layout.computeLayout(0, 0, this.cols, this.rows);
  }

  /** Build a balanced tree of even splits */
  _buildEvenSplits(panes, dir) {
    if (panes.length === 1) return new LayoutNode('leaf', panes[0]);
    const mid = Math.ceil(panes.length / 2);
    const node = new LayoutNode(dir);
    node.first = this._buildEvenSplits(panes.slice(0, mid), dir);
    node.second = this._buildEvenSplits(panes.slice(mid), dir);
    node.ratio = mid / panes.length;
    return node;
  }

  /** Build a main + secondary split */
  _buildMainSplit(panes, dir) {
    if (panes.length === 1) return new LayoutNode('leaf', panes[0]);
    const node = new LayoutNode(dir);
    node.first = new LayoutNode('leaf', panes[0]);
    node.second = this._buildEvenSplits(panes.slice(1),
      dir === SplitDir.HSPLIT ? SplitDir.VSPLIT : SplitDir.HSPLIT);
    node.ratio = 0.6;
    return node;
  }
}

// ── Session ──

let _sessionIdCounter = 0;

class TmuxSession {
  /**
   * @param {string} name
   * @param {number} rows – window pane area rows
   * @param {number} cols
   * @param {function} createPaneSession – (cols, rows) => SessionManager
   */
  constructor(name, rows, cols, createPaneSession) {
    this.id = _sessionIdCounter++;
    this.name = name;
    this.rows = rows;
    this.cols = cols;
    this._createPaneSession = createPaneSession;

    // Create initial window
    this.windows = [new TmuxWindow('zsh', rows, cols, createPaneSession)];
    this.activeWindowIndex = 0;
    this.lastWindowIndex = -1;
  }

  /** Get the active window */
  get activeWindow() { return this.windows[this.activeWindowIndex]; }

  /** Create a new window */
  createWindow(name = 'zsh') {
    const win = new TmuxWindow(name, this.rows, this.cols, this._createPaneSession);
    this.windows.push(win);
    this.lastWindowIndex = this.activeWindowIndex;
    this.activeWindowIndex = this.windows.length - 1;
    return win;
  }

  /** Switch to window by index */
  switchWindow(index) {
    if (index >= 0 && index < this.windows.length) {
      this.lastWindowIndex = this.activeWindowIndex;
      this.activeWindowIndex = index;
    }
  }

  /** Switch to next window */
  nextWindow() {
    this.lastWindowIndex = this.activeWindowIndex;
    this.activeWindowIndex = (this.activeWindowIndex + 1) % this.windows.length;
  }

  /** Switch to previous window */
  prevWindow() {
    this.lastWindowIndex = this.activeWindowIndex;
    this.activeWindowIndex = (this.activeWindowIndex - 1 + this.windows.length) % this.windows.length;
  }

  /** Switch to last active window */
  lastWindow() {
    if (this.lastWindowIndex >= 0 && this.lastWindowIndex < this.windows.length) {
      const tmp = this.activeWindowIndex;
      this.activeWindowIndex = this.lastWindowIndex;
      this.lastWindowIndex = tmp;
    }
  }

  /** Close a window by index */
  closeWindow(index) {
    if (this.windows.length <= 1) return false;
    this.windows.splice(index, 1);
    if (this.activeWindowIndex >= this.windows.length) {
      this.activeWindowIndex = this.windows.length - 1;
    }
    if (this.lastWindowIndex >= this.windows.length) {
      this.lastWindowIndex = -1;
    }
    return true;
  }
}

// ── Tmux (main class) ──

export class Tmux {
  /**
   * @param {object} opts
   * @param {number} [opts.rows=20] – total screen rows
   * @param {number} [opts.cols=80] – screen width
   * @param {function} opts.createPaneSession – (cols, rows) => SessionManager
   */
  constructor({ rows = 20, cols = 80, createPaneSession } = {}) {
    this.rows = rows;
    this.cols = cols;
    this._createPaneSession = createPaneSession;

    /** Pane area = total rows minus 1 (status bar at bottom) */
    this._paneRows = rows - 1;

    /** Current interaction mode */
    this._mode = TmuxMode.NORMAL;

    /** All sessions */
    this.sessions = [];
    this._activeSessionIndex = 0;

    /** Command prompt input */
    this._commandInput = '';

    /** Rename input */
    this._renameInput = '';

    /** Confirmation target */
    this._confirmTarget = null;

    /** Transient message */
    this._message = '';
    this._messageTimer = 0;

    /** Copy mode state */
    this._copyPane = null;
    this._copyScroll = 0;
    this._copyCursor = { row: 0, col: 0 };
    this._copySelecting = false;
    this._copyAnchor = null;

    /** Pane numbers display timer */
    this._paneNumberTimer = 0;

    /** Clock mode pane */
    this._clockPane = null;

    /** Window list selection cursor */
    this._windowListCursor = 0;

    /** Help scroll position */
    this._helpScroll = 0;

    /** Whether we are detached (signals to SessionManager to exit tmux) */
    this.detached = false;

    // Create first session
    this._createSession('0');
  }

  // ── Public API ──

  /** Get the active session */
  get activeSession() { return this.sessions[this._activeSessionIndex]; }

  /** Get the active window */
  get activeWindow() { return this.activeSession?.activeWindow; }

  /** Get the active pane */
  get activePane() { return this.activeWindow?.activePane; }

  /**
   * Feed a key event to tmux.
   * @param {string} key
   */
  feedKey(key) {
    // Clear transient message on any key
    if (this._message) this._message = '';

    switch (this._mode) {
      case TmuxMode.NORMAL:
        this._handleNormal(key);
        break;
      case TmuxMode.PREFIX:
        this._handlePrefix(key);
        break;
      case TmuxMode.COMMAND:
        this._handleCommand(key);
        break;
      case TmuxMode.CONFIRM:
        this._handleConfirm(key);
        break;
      case TmuxMode.RENAME:
        this._handleRename(key);
        break;
      case TmuxMode.COPY:
        this._handleCopy(key);
        break;
      case TmuxMode.WINDOW_LIST:
        this._handleWindowList(key);
        break;
      case TmuxMode.PANE_NUMBERS:
        this._handlePaneNumbers(key);
        break;
      case TmuxMode.CLOCK:
        this._handleClock(key);
        break;
      case TmuxMode.HELP:
        this._handleHelp(key);
        break;
    }
  }

  /**
   * Render the composite frame.
   * @returns {object} Frame dict
   */
  renderFrame() {
    // Theme colors
    const t = this._getThemeColors();

    // Initialize the full frame grid
    const frameLines = [];
    for (let r = 0; r < this.rows; r++) {
      frameLines.push({
        text: ' '.repeat(this.cols),
        runs: [{ n: this.cols, fg: t.fg, bg: t.bg }],
      });
    }

    const win = this.activeWindow;
    if (!win) {
      return this._buildFrame(frameLines, { row: 0, col: 0, visible: false });
    }

    // ── Render panes ──
    let cursorRow = 0, cursorCol = 0, cursorVisible = true;
    let cursorShape = 'block';

    if (win._zoomed) {
      // Zoomed: render only the active pane at full size
      const pane = win.activePane;
      const paneFrame = pane.renderFrame();
      this._blitFrame(frameLines, paneFrame, 0, 0, this.cols, this._paneRows);
      cursorRow = paneFrame.cursor.row;
      cursorCol = paneFrame.cursor.col;
      cursorVisible = paneFrame.cursor.visible;
      cursorShape = paneFrame.cursor.shape || 'block';
    } else {
      // Normal: render all panes with borders
      const panes = win.getPanes();

      for (const pane of panes) {
        const paneFrame = pane.renderFrame();
        this._blitFrame(frameLines, paneFrame, pane.top, pane.left, pane.width, pane.height);

        // Track cursor for active pane
        if (pane === win.activePane) {
          cursorRow = pane.top + paneFrame.cursor.row;
          cursorCol = pane.left + paneFrame.cursor.col;
          cursorVisible = paneFrame.cursor.visible;
          cursorShape = paneFrame.cursor.shape || 'block';
        }
      }

      // Draw borders between panes
      this._drawBorders(frameLines, win.layout, t, win.activePane);
    }

    // ── Status bar (last row) ──
    this._renderStatusBar(frameLines, t);

    // ── Overlays ──
    if (this._mode === TmuxMode.COPY) {
      // Copy mode indicator in status bar
      this._renderCopyOverlay(frameLines, t);
      // Cursor is in the copy mode viewport
      cursorRow = this._copyCursor.row;
      cursorCol = this._copyCursor.col;
      cursorShape = 'block';
    } else if (this._mode === TmuxMode.WINDOW_LIST) {
      this._renderWindowList(frameLines, t);
    } else if (this._mode === TmuxMode.PANE_NUMBERS) {
      this._renderPaneNumbers(frameLines, t);
    } else if (this._mode === TmuxMode.CLOCK) {
      this._renderClock(frameLines, t);
    } else if (this._mode === TmuxMode.HELP) {
      this._renderHelpOverlay(frameLines, t);
    }

    // ── Command prompt / messages on status bar ──
    if (this._mode === TmuxMode.COMMAND) {
      const cmdLine = ':' + this._commandInput;
      this._setStatusText(frameLines, cmdLine, t.cmdFg, t.cmdBg);
      cursorRow = this.rows - 1;
      cursorCol = Math.min(cmdLine.length, this.cols - 1);
    } else if (this._mode === TmuxMode.RENAME) {
      const renLine = '(rename-window) ' + this._renameInput;
      this._setStatusText(frameLines, renLine, t.cmdFg, t.cmdBg);
      cursorRow = this.rows - 1;
      cursorCol = Math.min(renLine.length, this.cols - 1);
    } else if (this._mode === TmuxMode.CONFIRM) {
      let confLine;
      if (this._confirmTarget === 'window') {
        const win = this.activeWindow;
        confLine = 'kill-window ' + (win?.name || '') + '? (y/n)';
      } else {
        confLine = 'kill-pane ' + (this._confirmTarget?.id ?? '') + '? (y/n)';
      }
      this._setStatusText(frameLines, confLine, t.cmdFg, t.cmdBg);
      cursorRow = this.rows - 1;
      cursorCol = Math.min(confLine.length, this.cols - 1);
    } else if (this._message) {
      this._setStatusText(frameLines, this._message, t.cmdFg, t.cmdBg);
    }

    // Clamp cursor
    cursorRow = Math.max(0, Math.min(cursorRow, this.rows - 1));
    cursorCol = Math.max(0, Math.min(cursorCol, this.cols - 1));

    return this._buildFrame(frameLines, {
      row: cursorRow, col: cursorCol, visible: cursorVisible, shape: cursorShape,
    });
  }

  // ── Key Handlers ──

  /** Normal mode: forward keys to active pane, watch for prefix */
  _handleNormal(key) {
    if (key === PREFIX_KEY) {
      this._mode = TmuxMode.PREFIX;
      return;
    }
    // Forward to active pane
    if (this.activePane) {
      this.activePane.feedKey(key);
      // Check if the pane's shell exited (like real tmux)
      this._checkPaneExited(this.activePane);
    }
  }

  /**
   * Check if a pane's shell has exited and close it.
   * In real tmux, when a pane's process exits, the pane closes automatically.
   * If it was the last pane in a window, the window closes.
   * If it was the last window, tmux detaches/exits.
   * @private
   */
  _checkPaneExited(pane) {
    if (!pane || !pane.session) return;
    const shell = pane.session.shell;
    if (!shell || !shell._exited) return;

    const win = this.activeWindow;
    if (!win) return;

    const panes = win.getPanes();
    if (panes.length > 1) {
      // Close the pane, remaining panes fill the space
      win.closePane(pane);
    } else {
      // Last pane in window — close the window
      const sess = this.activeSession;
      if (sess.windows.length > 1) {
        sess.closeWindow(sess.activeWindowIndex);
      } else {
        // Last window in session — detach (exit tmux)
        this.detached = true;
      }
    }
  }

  /** Prefix mode: handle tmux commands after Ctrl-b */
  _handlePrefix(key) {
    this._mode = TmuxMode.NORMAL; // most commands return to normal

    const win = this.activeWindow;
    const sess = this.activeSession;
    if (!win || !sess) return;

    switch (key) {
      // ── Pane splitting ──
      case '"':  // horizontal split (top/bottom)
        if (win._zoomed) win.toggleZoom();
        if (!win.splitPane('h')) {
          this._message = 'pane too small';
        }
        break;
      case '%':  // vertical split (left/right)
        if (win._zoomed) win.toggleZoom();
        if (!win.splitPane('v')) {
          this._message = 'pane too small';
        }
        break;

      // ── Pane navigation ──
      case 'ArrowUp':    case 'k': if (win._zoomed) win.toggleZoom(); win.navigatePane('Up');    break;
      case 'ArrowDown':  case 'j': if (win._zoomed) win.toggleZoom(); win.navigatePane('Down');  break;
      case 'ArrowLeft':  case 'h': if (win._zoomed) win.toggleZoom(); win.navigatePane('Left');  break;
      case 'ArrowRight': case 'l': if (win._zoomed) win.toggleZoom(); win.navigatePane('Right'); break;
      case 'o':  if (win._zoomed) win.toggleZoom(); win.nextPane();  break;
      case ';':  // last pane
        if (win.lastActivePane && win.getPanes().includes(win.lastActivePane)) {
          if (win._zoomed) win.toggleZoom();
          const tmp = win.activePane;
          win.activePane = win.lastActivePane;
          win.lastActivePane = tmp;
        }
        break;

      // ── Pane resize (Ctrl + arrow) ──
      case 'Ctrl-Up':    win.resizePane('Up', 1);    break;
      case 'Ctrl-Down':  win.resizePane('Down', 1);  break;
      case 'Ctrl-Left':  win.resizePane('Left', 1);  break;
      case 'Ctrl-Right': win.resizePane('Right', 1); break;

      // ── Pane zoom ──
      case 'z':
        win.toggleZoom();
        break;

      // ── Close pane ──
      case 'x':
        this._confirmTarget = win.activePane;
        this._mode = TmuxMode.CONFIRM;
        break;

      // ── Swap panes ──
      case '{': if (win._zoomed) win.toggleZoom(); win.swapPanePrev(); break;
      case '}': if (win._zoomed) win.toggleZoom(); win.swapPaneNext(); break;

      // ── Break pane to new window ──
      case '!': {
        if (win._zoomed) win.toggleZoom();
        const pane = win.breakPane();
        if (pane) {
          const newWin = new TmuxWindow('zsh', win.rows, win.cols, this.activeSession._createPaneSession);
          // Replace new window's default pane with the broken-out pane
          newWin.layout = new LayoutNode('leaf', pane);
          newWin.activePane = pane;
          newWin.layout.computeLayout(0, 0, newWin.cols, newWin.rows);
          sess.windows.push(newWin);
          sess.lastWindowIndex = sess.activeWindowIndex;
          sess.activeWindowIndex = sess.windows.length - 1;
        } else {
          this._message = "can't break with only one pane";
        }
        break;
      }

      // ── Display pane numbers ──
      case 'q':
        this._mode = TmuxMode.PANE_NUMBERS;
        this._paneNumberTimer = Date.now();
        break;

      // ── Window management ──
      case 'c':  // create window
        sess.createWindow('zsh');
        break;
      case 'n':  // next window
        sess.nextWindow();
        break;
      case 'p':  // previous window
        sess.prevWindow();
        break;
      case ',':  // rename window
        this._renameInput = win.name;
        this._mode = TmuxMode.RENAME;
        break;
      case '&':  // close window (with confirmation)
        this._confirmTarget = 'window';
        this._mode = TmuxMode.CONFIRM;
        break;
      case 'w':  // window list
        this._windowListCursor = sess.activeWindowIndex;
        this._mode = TmuxMode.WINDOW_LIST;
        break;

      // ── Window by number ──
      case '0': case '1': case '2': case '3': case '4':
      case '5': case '6': case '7': case '8': case '9':
        sess.switchWindow(parseInt(key, 10));
        break;

      // ── Last window ──
      case 'L':
        sess.lastWindow();
        break;

      // ── Detach ──
      case 'd':
        this.detached = true;
        break;

      // ── Copy mode ──
      case '[':
      case 'PageUp':   // PageUp also enters copy mode (common shortcut)
        this._enterCopyMode();
        break;

      // ── Command prompt ──
      case ':':
        this._commandInput = '';
        this._mode = TmuxMode.COMMAND;
        break;

      // ── Clock ──
      case 't':
        this._mode = TmuxMode.CLOCK;
        break;

      // ── Cycle layout ──
      case ' ':
        win.cycleLayout();
        break;

      // ── Help ──
      case '?':
        this._helpScroll = 0;
        this._mode = TmuxMode.HELP;
        break;

      // ── Send prefix key to pane (Ctrl-b Ctrl-b) ──
      case PREFIX_KEY:
        if (this.activePane) {
          this.activePane.feedKey(PREFIX_KEY);
        }
        break;

      default:
        // Unknown prefix command — ignore
        break;
    }
  }

  /** Command prompt handler */
  _handleCommand(key) {
    if (key === 'Escape') {
      this._mode = TmuxMode.NORMAL;
      this._commandInput = '';
      return;
    }
    if (key === 'Enter') {
      this._executeCommand(this._commandInput.trim());
      this._mode = TmuxMode.NORMAL;
      this._commandInput = '';
      return;
    }
    if (key === 'Backspace') {
      if (this._commandInput.length > 0) {
        this._commandInput = this._commandInput.slice(0, -1);
      }
      // Stay in command mode even when input is empty (matches real tmux)
      return;
    }
    if (key.length === 1) {
      this._commandInput += key;
    }
  }

  /** Confirm (y/n) handler for pane/window close */
  _handleConfirm(key) {
    if (key === 'y' || key === 'Y') {
      if (this._confirmTarget === 'window') {
        // Window close confirmation (from &)
        const sess = this.activeSession;
        if (sess && sess.windows.length > 1) {
          sess.closeWindow(sess.activeWindowIndex);
        } else if (sess) {
          // Last window — detach
          this.detached = true;
        }
      } else {
        // Pane close confirmation (from x)
        const win = this.activeWindow;
        if (win && this._confirmTarget) {
          const panes = win.getPanes();
          if (panes.length <= 1) {
            // Last pane in window — close the window
            const sess = this.activeSession;
            if (sess.windows.length > 1) {
              sess.closeWindow(sess.activeWindowIndex);
            } else {
              // Last window in session — detach
              this.detached = true;
            }
          } else {
            win.closePane(this._confirmTarget);
          }
        }
      }
    }
    this._confirmTarget = null;
    this._mode = TmuxMode.NORMAL;
  }

  /** Rename window handler */
  _handleRename(key) {
    if (key === 'Escape') {
      this._mode = TmuxMode.NORMAL;
      this._renameInput = '';
      return;
    }
    if (key === 'Enter') {
      if (this.activeWindow && this._renameInput) {
        this.activeWindow.name = this._renameInput;
      }
      this._mode = TmuxMode.NORMAL;
      this._renameInput = '';
      return;
    }
    if (key === 'Backspace') {
      this._renameInput = this._renameInput.slice(0, -1);
      return;
    }
    if (key === 'Ctrl-U') {
      this._renameInput = '';
      return;
    }
    if (key.length === 1) {
      this._renameInput += key;
    }
  }

  /** Copy mode handler (vi keybindings) */
  _handleCopy(key) {
    switch (key) {
      case 'q':
      case 'Escape':
        this._mode = TmuxMode.NORMAL;
        break;
      case 'j':
      case 'ArrowDown':
        this._copyCursor.row = Math.min(this._copyCursor.row + 1, this._paneRows - 1);
        break;
      case 'k':
      case 'ArrowUp':
        if (this._copyCursor.row > 0) {
          this._copyCursor.row--;
        } else if (this._copyScroll > 0) {
          this._copyScroll--;
        }
        break;
      case 'h':
      case 'ArrowLeft':
        this._copyCursor.col = Math.max(0, this._copyCursor.col - 1);
        break;
      case 'l':
      case 'ArrowRight':
        this._copyCursor.col = Math.min(this._copyCursor.col + 1, this.cols - 1);
        break;
      case 'g':
        this._copyCursor.row = 0;
        this._copyScroll = 0;
        break;
      case 'G':
        this._copyCursor.row = this._paneRows - 1;
        break;
      case '0':
        this._copyCursor.col = 0;
        break;
      case '$':
        this._copyCursor.col = this.cols - 1;
        break;
      case 'w': {
        // Simple word forward in copy mode
        this._copyCursor.col = Math.min(this._copyCursor.col + 5, this.cols - 1);
        break;
      }
      case 'b': {
        this._copyCursor.col = Math.max(0, this._copyCursor.col - 5);
        break;
      }
      case 'Ctrl-F':
        this._copyCursor.row = Math.min(this._copyCursor.row + this._paneRows, this._paneRows - 1);
        break;
      case 'Ctrl-B':
        if (this._copyCursor.row > 0) {
          this._copyCursor.row = Math.max(0, this._copyCursor.row - this._paneRows);
        } else {
          this._copyScroll = Math.max(0, this._copyScroll - this._paneRows);
        }
        break;
      case 'Ctrl-D':
        this._copyCursor.row = Math.min(this._copyCursor.row + Math.floor(this._paneRows / 2), this._paneRows - 1);
        break;
      case 'Ctrl-U':
        if (this._copyCursor.row > 0) {
          this._copyCursor.row = Math.max(0, this._copyCursor.row - Math.floor(this._paneRows / 2));
        } else {
          this._copyScroll = Math.max(0, this._copyScroll - Math.floor(this._paneRows / 2));
        }
        break;
      case 'v':
        // Toggle selection
        this._copySelecting = !this._copySelecting;
        if (this._copySelecting) {
          this._copyAnchor = { ...this._copyCursor };
        }
        break;
    }
  }

  /** Window list handler */
  _handleWindowList(key) {
    const sess = this.activeSession;
    if (!sess) { this._mode = TmuxMode.NORMAL; return; }

    switch (key) {
      case 'j':
      case 'ArrowDown':
        this._windowListCursor = Math.min(this._windowListCursor + 1, sess.windows.length - 1);
        break;
      case 'k':
      case 'ArrowUp':
        this._windowListCursor = Math.max(0, this._windowListCursor - 1);
        break;
      case 'Enter':
        sess.switchWindow(this._windowListCursor);
        this._mode = TmuxMode.NORMAL;
        break;
      case 'Escape':
      case 'q':
        this._mode = TmuxMode.NORMAL;
        break;
    }
  }

  /** Pane numbers handler */
  _handlePaneNumbers(key) {
    // If user presses a digit, switch to that pane
    if (key >= '0' && key <= '9') {
      const panes = this.activeWindow?.getPanes();
      const idx = parseInt(key, 10);
      if (panes && idx < panes.length) {
        this.activeWindow.lastActivePane = this.activeWindow.activePane;
        this.activeWindow.activePane = panes[idx];
      }
    }
    this._mode = TmuxMode.NORMAL;
  }

  /** Clock mode handler */
  _handleClock(key) {
    // Any key exits clock mode
    this._mode = TmuxMode.NORMAL;
  }

  /** Help handler */
  _handleHelp(key) {
    if (key === 'q' || key === 'Escape') {
      this._mode = TmuxMode.NORMAL;
      return;
    }
    if (key === 'j' || key === 'ArrowDown') {
      this._helpScroll++;
    } else if (key === 'k' || key === 'ArrowUp') {
      this._helpScroll = Math.max(0, this._helpScroll - 1);
    }
  }

  // ── Command Prompt Execution ──

  _executeCommand(cmd) {
    if (!cmd) return;

    const parts = cmd.split(/\s+/);
    const command = parts[0];
    const args = parts.slice(1);

    switch (command) {
      case 'split-window':
      case 'splitw': {
        const horiz = args.includes('-h');
        const dir = horiz ? 'v' : 'h'; // -h means vertical divider (side by side)
        this.activeWindow?.splitPane(dir);
        break;
      }
      case 'new-window':
      case 'neww': {
        const nameIdx = args.indexOf('-n');
        const name = nameIdx >= 0 && args[nameIdx + 1] ? args[nameIdx + 1] : 'zsh';
        this.activeSession?.createWindow(name);
        break;
      }
      case 'rename-window':
      case 'renamew': {
        if (args[0] && this.activeWindow) {
          this.activeWindow.name = args.join(' ');
        }
        break;
      }
      case 'select-window':
      case 'selectw': {
        const tIdx = args.indexOf('-t');
        if (tIdx >= 0 && args[tIdx + 1]) {
          this.activeSession?.switchWindow(parseInt(args[tIdx + 1], 10));
        }
        break;
      }
      case 'select-pane':
      case 'selectp': {
        const tIdx = args.indexOf('-t');
        if (tIdx >= 0 && args[tIdx + 1]) {
          const panes = this.activeWindow?.getPanes();
          const idx = parseInt(args[tIdx + 1], 10);
          if (panes && idx >= 0 && idx < panes.length) {
            this.activeWindow.activePane = panes[idx];
          }
        }
        break;
      }
      case 'resize-pane':
      case 'resizep': {
        let dir = 'Down', amt = 1;
        for (let i = 0; i < args.length; i++) {
          if (args[i] === '-U') dir = 'Up';
          else if (args[i] === '-D') dir = 'Down';
          else if (args[i] === '-L') dir = 'Left';
          else if (args[i] === '-R') dir = 'Right';
          else if (/^\d+$/.test(args[i])) amt = parseInt(args[i], 10);
        }
        this.activeWindow?.resizePane(dir, amt);
        break;
      }
      case 'kill-pane':
      case 'killp': {
        const win = this.activeWindow;
        if (win) {
          const panes = win.getPanes();
          if (panes.length > 1) {
            win.closePane(win.activePane);
          } else {
            // Last pane — close the window
            const sess = this.activeSession;
            if (sess.windows.length > 1) {
              sess.closeWindow(sess.activeWindowIndex);
            } else {
              // Last window — detach
              this.detached = true;
            }
          }
        }
        break;
      }
      case 'kill-window':
      case 'killw': {
        const sess = this.activeSession;
        if (sess && sess.windows.length > 1) {
          sess.closeWindow(sess.activeWindowIndex);
        }
        break;
      }
      case 'swap-pane':
      case 'swapp': {
        if (args.includes('-U') || args.includes('-D')) {
          if (args.includes('-U')) this.activeWindow?.swapPanePrev();
          else this.activeWindow?.swapPaneNext();
        }
        break;
      }
      case 'new-session':
      case 'new': {
        const sIdx = args.indexOf('-s');
        const name = sIdx >= 0 && args[sIdx + 1] ? args[sIdx + 1] : String(this.sessions.length);
        this._createSession(name);
        break;
      }
      case 'switch-client':
      case 'switchc': {
        const tIdx = args.indexOf('-t');
        if (tIdx >= 0 && args[tIdx + 1]) {
          const target = args[tIdx + 1];
          const idx = this.sessions.findIndex(s => s.name === target);
          if (idx >= 0) {
            this._activeSessionIndex = idx;
          } else {
            this._message = `session not found: ${target}`;
          }
        }
        break;
      }
      case 'list-sessions':
      case 'ls': {
        const lines = this.sessions.map((s, i) =>
          `${s.name}: ${s.windows.length} windows${i === this._activeSessionIndex ? ' (attached)' : ''}`
        );
        this._message = lines.join(' | ');
        break;
      }
      case 'detach-client':
      case 'detach':
        this.detached = true;
        break;
      case 'next-layout':
      case 'nextl':
        this.activeWindow?.cycleLayout();
        break;
      case 'display-panes':
      case 'displayp':
        this._mode = TmuxMode.PANE_NUMBERS;
        break;
      case 'clock-mode':
        this._mode = TmuxMode.CLOCK;
        break;
      case 'list-keys':
      case 'lsk':
        this._helpScroll = 0;
        this._mode = TmuxMode.HELP;
        break;
      default:
        this._message = `unknown command: ${command}`;
        break;
    }
  }

  // ── Session management ──

  _createSession(name) {
    const sess = new TmuxSession(name, this._paneRows, this.cols, this._createPaneSession);
    this.sessions.push(sess);
    this._activeSessionIndex = this.sessions.length - 1;
    return sess;
  }

  // ── Copy mode ──

  _enterCopyMode() {
    this._mode = TmuxMode.COPY;
    this._copyCursor = { row: 0, col: 0 };
    this._copyScroll = 0;
    this._copySelecting = false;
    this._copyAnchor = null;
    this._copyPane = this.activePane;
  }

  // ── Rendering helpers ──

  /** Get theme colors for tmux UI elements */
  _getThemeColors() {
    // Monokai tmux theme — captured from real tmux via ShellPilot.
    // See test/capture_tmux_colors.py and test/tmux_real_colors.json.
    return {
      fg: 'f8f8f2',              // Monokai foreground
      bg: '000000',              // terminal background
      borderFg: '49483e',        // inactive pane border (Monokai selection)
      borderActiveFg: 'a6e22e',  // active pane border (Monokai green)
      statusBg: '272822',        // status bar background (Monokai bg)
      statusFg: 'f8f8f2',        // status bar default text
      statusSepFg: '75715e',     // pipe separators and date (Monokai comment)
      statusActiveFg: 'a6e22e',  // active window + session name (green, bold)
      statusActiveBg: '49483e',  // active window highlight bg
      statusInactiveFg: '75715e', // inactive window text (comment gray)
      statusClockFg: '66d9ef',   // clock digits (Monokai cyan)
      cmdBg: '49483e',           // command/copy prompt bg
      cmdFg: 'f8f8f2',           // command/copy prompt fg
      paneNumFg: 'a6e22e',
      paneNumBg: '000000',
    };
  }

  /** Blit a pane's frame into the composite frame at (top, left) */
  _blitFrame(frameLines, paneFrame, top, left, width, height) {
    for (let r = 0; r < height && r < paneFrame.lines.length; r++) {
      const destRow = top + r;
      if (destRow >= this._paneRows) break;

      const srcLine = paneFrame.lines[r];
      const destLine = frameLines[destRow];

      // Copy text
      const srcText = srcLine.text || '';
      const destText = destLine.text.split('');
      for (let c = 0; c < width && c < srcText.length; c++) {
        const dc = left + c;
        if (dc < this.cols) destText[dc] = srcText[c];
      }
      destLine.text = destText.join('');

      // Build color runs — we need to splice the source runs into the dest
      destLine.runs = this._spliceRuns(destLine.runs, srcLine.runs, left, width, this.cols);
    }
  }

  /**
   * Splice source color runs into dest runs at a specific column offset.
   * @returns {Array} new runs array
   */
  _spliceRuns(destRuns, srcRuns, startCol, width, totalCols) {
    // Expand both run arrays into per-cell color info, splice, re-compact
    const cells = [];

    // Expand dest
    for (const run of destRuns) {
      for (let i = 0; i < run.n; i++) {
        cells.push({ fg: run.fg, bg: run.bg, b: run.b });
      }
    }
    // Pad to totalCols
    while (cells.length < totalCols) {
      cells.push({ fg: 'e0e2ea', bg: '14161b' });
    }

    // Expand src and overwrite
    let srcIdx = 0;
    for (const run of srcRuns) {
      for (let i = 0; i < run.n; i++) {
        const dc = startCol + srcIdx;
        if (dc < totalCols && srcIdx < width) {
          cells[dc] = { fg: run.fg, bg: run.bg, b: run.b };
        }
        srcIdx++;
      }
    }

    // Re-compact into runs
    return this._compactRuns(cells);
  }

  /** Compact per-cell array back into runs */
  _compactRuns(cells) {
    if (cells.length === 0) return [{ n: 0, fg: 'f8f8f2', bg: '000000' }];
    const runs = [];
    let cur = { n: 1, fg: cells[0].fg, bg: cells[0].bg };
    if (cells[0].b) cur.b = true;
    for (let i = 1; i < cells.length; i++) {
      const c = cells[i];
      if (c.fg === cur.fg && c.bg === cur.bg && (c.b || false) === (cur.b || false)) {
        cur.n++;
      } else {
        runs.push(cur);
        cur = { n: 1, fg: c.fg, bg: c.bg };
        if (c.b) cur.b = true;
      }
    }
    runs.push(cur);
    return runs;
  }

  /** Draw borders between panes by traversing the layout tree */
  _drawBorders(frameLines, node, t, activePane) {
    if (node.isLeaf()) return;

    // In real tmux, the border belongs to the first (left/top) child.
    // It uses active color only when the first child contains the active pane.
    const firstHasActive = node.first.getPanes().includes(activePane);
    const borderFg = firstHasActive ? t.borderActiveFg : t.borderFg;

    if (node.type === SplitDir.HSPLIT) {
      // Horizontal border at the split line
      const borderRow = node.first.top + node.first.height;
      if (borderRow < this._paneRows) {
        const line = frameLines[borderRow];
        const chars = line.text.split('');
        for (let c = node.left; c < node.left + node.width && c < this.cols; c++) {
          chars[c] = BORDER.H;
        }
        line.text = chars.join('');
        // Set the run colors for the border
        this._setBorderRuns(line, node.left, node.width, borderFg, t.bg);
      }
    } else {
      // Vertical border at the split column
      const borderCol = node.first.left + node.first.width;
      if (borderCol < this.cols) {
        for (let r = node.top; r < node.top + node.height && r < this._paneRows; r++) {
          const line = frameLines[r];
          const chars = line.text.split('');
          chars[borderCol] = BORDER.V;
          line.text = chars.join('');
          this._setBorderRuns(line, borderCol, 1, borderFg, t.bg);
        }
      }
    }

    // Handle intersections between borders
    this._drawIntersections(frameLines, node, t);

    // Recurse into children
    this._drawBorders(frameLines, node.first, t, activePane);
    this._drawBorders(frameLines, node.second, t, activePane);
  }

  /** Draw intersection characters where borders cross */
  _drawIntersections(frameLines, node, t) {
    // At a split node, check if the children also have splits
    // that create intersections
    if (node.type === SplitDir.HSPLIT) {
      const borderRow = node.first.top + node.first.height;
      if (borderRow >= this._paneRows) return;
      // Check if children have vertical splits at this row
      this._addVIntersections(frameLines, node.first, borderRow, t);
      this._addVIntersections(frameLines, node.second, borderRow, t);
    } else {
      const borderCol = node.first.left + node.first.width;
      // Check if children have horizontal splits at this column
      this._addHIntersections(frameLines, node.first, borderCol, t);
      this._addHIntersections(frameLines, node.second, borderCol, t);
    }
  }

  _addVIntersections(frameLines, node, borderRow, t) {
    if (node.isLeaf()) return;
    if (node.type === SplitDir.VSPLIT) {
      const col = node.first.left + node.first.width;
      if (col < this.cols && borderRow < this._paneRows) {
        const chars = frameLines[borderRow].text.split('');
        chars[col] = BORDER.X;
        frameLines[borderRow].text = chars.join('');
      }
    }
    this._addVIntersections(frameLines, node.first, borderRow, t);
    this._addVIntersections(frameLines, node.second, borderRow, t);
  }

  _addHIntersections(frameLines, node, borderCol, t) {
    if (node.isLeaf()) return;
    if (node.type === SplitDir.HSPLIT) {
      const row = node.first.top + node.first.height;
      if (row < this._paneRows && borderCol < this.cols) {
        const chars = frameLines[row].text.split('');
        chars[borderCol] = BORDER.X;
        frameLines[row].text = chars.join('');
      }
    }
    this._addHIntersections(frameLines, node.first, borderCol, t);
    this._addHIntersections(frameLines, node.second, borderCol, t);
  }

  /** Set border colors for specific cells in a line's run array */
  _setBorderRuns(line, col, width, fg, bg) {
    // Expand, set, re-compact
    const cells = [];
    for (const run of line.runs) {
      for (let i = 0; i < run.n; i++) {
        cells.push({ fg: run.fg, bg: run.bg, b: run.b });
      }
    }
    while (cells.length < this.cols) {
      cells.push({ fg: 'e0e2ea', bg: '14161b' });
    }
    for (let c = col; c < col + width && c < this.cols; c++) {
      cells[c] = { fg, bg };
    }
    line.runs = this._compactRuns(cells);
  }

  /** Render the tmux status bar on the last row */
  _renderStatusBar(frameLines, t) {
    const sess = this.activeSession;
    if (!sess) return;

    // Build status segments matching real tmux Monokai theme:
    //   "sess | 0:zsh* 1:zsh-  | HH:MM | DD-Mon-YY"
    // Each segment has its own color.
    const statusRow = this.rows - 1;
    const totalWidth = this.cols;

    // Segments: session name, separator, windows, separator, clock, separator, date
    const sessName = sess.name + ' ';
    const sep = '| ';

    const windowParts = [];
    for (let i = 0; i < sess.windows.length; i++) {
      const w = sess.windows[i];
      const marker = i === sess.activeWindowIndex ? '*' : '-';
      const zoomFlag = (i === sess.activeWindowIndex && w._zoomed) ? 'Z' : '';
      windowParts.push({ text: `${i}:${w.name}${marker}${zoomFlag}`, active: i === sess.activeWindowIndex });
    }
    const windowStr = windowParts.map(p => p.text).join(' ');

    const now = new Date();
    const timeStr = now.toTimeString().slice(0, 5) + ' ';
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    const dateStr = '| ' + `${now.getDate()}-${months[now.getMonth()]}-${String(now.getFullYear()).slice(-2)}`;

    // Compose left side:  "sess | win0* win1-"
    const leftText = sessName + sep + windowStr;
    // Right side:  "| HH:MM | DD-Mon-YY"
    const rightText = sep + timeStr + dateStr;

    // Build full status string
    const gap = totalWidth - leftText.length - rightText.length;
    let statusText;
    if (gap > 0) {
      statusText = leftText + ' '.repeat(gap) + rightText;
    } else {
      statusText = (leftText + rightText).slice(0, totalWidth);
    }
    statusText = this._padStr(statusText, totalWidth);
    frameLines[statusRow].text = statusText;

    // Build per-cell color array
    const cells = [];
    let pos = 0;

    // Session name (green, bold on statusBg)
    const pushCells = (len, fg, bg, bold) => {
      for (let i = 0; i < len && pos < totalWidth; i++, pos++) {
        const c = { fg, bg };
        if (bold) c.b = true;
        cells.push(c);
      }
    };

    pushCells(sessName.length, t.statusActiveFg, t.statusBg, true); // session name
    pushCells(sep.length, t.statusSepFg, t.statusBg, true);        // "| "

    // Window list — each window colored individually
    for (let wi = 0; wi < windowParts.length; wi++) {
      const wp = windowParts[wi];
      if (wp.active) {
        pushCells(wp.text.length, t.statusActiveFg, t.statusActiveBg, true);
      } else {
        pushCells(wp.text.length, t.statusInactiveFg, t.statusBg, false);
      }
      // Space between windows
      if (wi < windowParts.length - 1) {
        pushCells(1, t.statusFg, t.statusBg, false);
      }
    }

    // Fill gap with default status colors
    const rightStart = leftText.length + Math.max(0, gap);
    while (pos < rightStart && pos < totalWidth) {
      cells.push({ fg: t.statusFg, bg: t.statusBg });
      pos++;
    }

    // Right side: "| " separator
    pushCells(sep.length, t.statusSepFg, t.statusBg, false);
    // Clock
    pushCells(timeStr.length, t.statusClockFg, t.statusBg, false);
    // "| " + date
    pushCells(dateStr.length, t.statusSepFg, t.statusBg, false);

    // Pad remaining
    while (pos < totalWidth) {
      cells.push({ fg: t.statusFg, bg: t.statusBg });
      pos++;
    }

    frameLines[statusRow].runs = this._compactRuns(cells);
  }

  /** Set status bar text (for messages/prompts) */
  _setStatusText(frameLines, text, fg, bg) {
    const statusRow = this.rows - 1;
    frameLines[statusRow].text = this._padStr(text, this.cols);
    frameLines[statusRow].runs = [{ n: this.cols, fg, bg }];
  }

  /** Render copy mode overlay */
  _renderCopyOverlay(frameLines, t) {
    // Real tmux shows the normal status bar but changes the window name
    // to "[tmux]" while in copy mode.  We achieve this by temporarily
    // renaming the active window, rendering the status bar normally,
    // and then restoring the original name.
    const win = this.activeWindow;
    if (!win) return;
    const savedName = win.name;
    win.name = '[tmux]';
    this._renderStatusBar(frameLines, t);
    win.name = savedName;
  }

  /** Render window list overlay */
  _renderWindowList(frameLines, t) {
    const sess = this.activeSession;
    if (!sess) return;

    // Draw a centered box with the window list
    const items = sess.windows.map((w, i) =>
      `${i === this._windowListCursor ? '>' : ' '} ${i}: ${w.name} [${w.getPanes().length} panes]${i === sess.activeWindowIndex ? ' (active)' : ''}`
    );

    const title = '── Choose Window ──';
    const maxWidth = Math.min(this.cols - 4, Math.max(title.length, ...items.map(s => s.length)) + 4);
    const boxLeft = Math.floor((this.cols - maxWidth) / 2);
    const boxTop = Math.max(0, Math.floor((this._paneRows - items.length - 2) / 2));

    // Title bar
    if (boxTop < this._paneRows) {
      const titleLine = (' ' + title + ' ').padEnd(maxWidth);
      this._overlayText(frameLines, boxTop, boxLeft, titleLine, t.statusFg, t.statusBg, maxWidth);
    }

    // Items
    for (let i = 0; i < items.length; i++) {
      const r = boxTop + 1 + i;
      if (r >= this._paneRows) break;
      const line = items[i].padEnd(maxWidth);
      const isSelected = (i === this._windowListCursor);
      this._overlayText(frameLines, r, boxLeft, line,
        isSelected ? t.statusActiveFg : t.statusFg,
        isSelected ? t.statusActiveBg : t.statusBg,
        maxWidth);
    }
  }

  /** Render pane numbers overlay */
  _renderPaneNumbers(frameLines, t) {
    const win = this.activeWindow;
    if (!win) return;

    const panes = win.getPanes();
    for (let i = 0; i < panes.length; i++) {
      const pane = panes[i];
      // Center the number in the pane
      const numStr = String(i);
      const cr = pane.top + Math.floor(pane.height / 2);
      const cc = pane.left + Math.floor(pane.width / 2) - Math.floor(numStr.length / 2);
      if (cr < this._paneRows) {
        const isActive = (pane === win.activePane);
        this._overlayText(frameLines, cr, cc, numStr,
          isActive ? '00ff00' : 'ff0000',
          t.bg, numStr.length);
      }
    }
  }

  /** Render clock mode overlay */
  _renderClock(frameLines, t) {
    const now = new Date();
    const timeStr = now.toTimeString().slice(0, 8); // HH:MM:SS

    // Big ASCII clock centered on screen
    const digits = {
      '0': ['┌─┐','│ │','│ │','│ │','└─┘'],
      '1': ['  │','  │','  │','  │','  │'],
      '2': ['┌─┐','  │','┌─┘','│  ','└─┘'],
      '3': ['┌─┐','  │','├─┤','  │','└─┘'],
      '4': ['│ │','│ │','└─┤','  │','  │'],
      '5': ['┌─┐','│  ','└─┐','  │','└─┘'],
      '6': ['┌─┐','│  ','├─┐','│ │','└─┘'],
      '7': ['┌─┐','  │','  │','  │','  │'],
      '8': ['┌─┐','│ │','├─┤','│ │','└─┘'],
      '9': ['┌─┐','│ │','└─┤','  │','└─┘'],
      ':': [' ',' ','·',' ','·'],
    };

    // Build lines from the time string
    const clockLines = ['', '', '', '', ''];
    for (const ch of timeStr) {
      const d = digits[ch] || digits['0'];
      for (let r = 0; r < 5; r++) {
        clockLines[r] += d[r] + ' ';
      }
    }

    const clockWidth = clockLines[0].length;
    const startRow = Math.floor((this._paneRows - 5) / 2);
    const startCol = Math.floor((this.cols - clockWidth) / 2);

    for (let r = 0; r < 5; r++) {
      const row = startRow + r;
      if (row >= 0 && row < this._paneRows) {
        this._overlayText(frameLines, row, startCol, clockLines[r],
          t.clockFg, t.bg, clockWidth);
      }
    }
  }

  /** Render help overlay */
  _renderHelpOverlay(frameLines, t) {
    const helpLines = [
      'tmux key bindings (prefix: Ctrl-b)',
      '───────────────────────────────────',
      '  %     Split pane vertically',
      '  "     Split pane horizontally',
      '  h/j/k/l Navigate panes (←↓↑→)',
      '  ←↑↓→  Navigate panes',
      '  o     Next pane',
      '  ;     Last pane',
      '  z     Zoom/unzoom pane',
      '  x     Close pane (confirm)',
      '  {     Swap pane up',
      '  }     Swap pane down',
      '  !     Break pane to new window',
      '  q     Display pane numbers',
      '  c     Create new window',
      '  n     Next window',
      '  p     Previous window',
      '  0-9   Switch to window N',
      '  ,     Rename window',
      '  &     Close window',
      '  w     Window list (chooser)',
      '  Space Cycle layout',
      '  d     Detach',
      '  [     Copy mode',
      '  t     Clock',
      '  :     Command prompt',
      '  ?     This help',
      '',
      '  Press q to exit help',
    ];

    const maxWidth = Math.min(this.cols - 2, 40);
    const boxLeft = Math.floor((this.cols - maxWidth) / 2);
    const visibleRows = Math.min(this._paneRows, helpLines.length - this._helpScroll);

    for (let r = 0; r < visibleRows; r++) {
      const row = r;
      const lineIdx = this._helpScroll + r;
      if (lineIdx >= helpLines.length) break;
      if (row >= this._paneRows) break;

      const text = helpLines[lineIdx].padEnd(maxWidth).slice(0, maxWidth);
      this._overlayText(frameLines, row, boxLeft, text, t.fg, '1e1e2e', maxWidth);
    }
  }

  /** Helper: overlay text at a specific position */
  _overlayText(frameLines, row, col, text, fg, bg, width) {
    if (row < 0 || row >= frameLines.length) return;

    const line = frameLines[row];
    const chars = line.text.split('');
    for (let c = 0; c < width && c < text.length; c++) {
      const dc = col + c;
      if (dc >= 0 && dc < this.cols) {
        chars[dc] = text[c];
      }
    }
    line.text = chars.join('');
    this._setBorderRuns(line, col, width, fg, bg);
  }

  /** Pad a string to exact width */
  _padStr(s, width) {
    if (s.length >= width) return s.slice(0, width);
    return s + ' '.repeat(width - s.length);
  }

  /** Build the final frame dict */
  _buildFrame(lines, cursor) {
    return {
      rows: this.rows,
      cols: this.cols,
      cursor,
      defaultFg: 'e0e2ea',
      defaultBg: '14161b',
      lines,
    };
  }
}

// Export internal classes for testing
export { TmuxSession, TmuxWindow, TmuxPane, LayoutNode, TmuxMode, SplitDir };
