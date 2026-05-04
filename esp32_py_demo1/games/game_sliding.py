# ===== SLIDING PUZZLE =====

# Game state
sl_mode = 0        # 0=menu, 1=playing, 2=won
sl_difficulty = 0  # 0=3x3, 1=4x4, 2=5x5
sl_board = []      # flat list, 0 = empty space
sl_size = 3        # current N
sl_empty = 0       # index of empty space in board
sl_moves = 0
sl_timer_start = 0
sl_last_timer_text = ""
sl_last_moves_text = ""

# Layout per difficulty: (N, cell_size, board_px)
SL_SIZES = [3, 4, 5]
SL_CELLS = [100, 80, 65]

# Stats per difficulty
sl_3_best_moves = 0
sl_3_best_time = 0
sl_3_wins = 0
sl_4_best_moves = 0
sl_4_best_time = 0
sl_4_wins = 0
sl_5_best_moves = 0
sl_5_best_time = 0
sl_5_wins = 0

# Tile color
SL_TILE_COLOR = DARK_GREY
SL_TILE_BORDER = make_color(55, 55, 55)

def sl_board_origin():
    """Return (ox, oy) for top-left of board."""
    n = sl_size
    cell = SL_CELLS[sl_difficulty]
    board_px = n * cell
    ox = (368 - board_px) // 2
    oy = 45 + (390 - 45 - board_px) // 2  # center between status bar and bottom
    return ox, oy

def sl_reset():
    """Create solved board then shuffle."""
    global sl_board, sl_empty, sl_moves, sl_timer_start
    global sl_last_timer_text, sl_last_moves_text, sl_size, sl_mode
    sl_size = SL_SIZES[sl_difficulty]
    n = sl_size
    total = n * n
    # Solved state: 1..N*N-1, 0 (empty) at end
    sl_board = list(range(1, total)) + [0]
    sl_empty = total - 1
    sl_moves = 0
    sl_timer_start = time.ticks_ms()
    sl_last_timer_text = ""
    sl_last_moves_text = ""
    sl_mode = 1
    # Shuffle by making random valid moves
    moves = 300 if n >= 4 else 200
    last_dir = -1
    for _ in range(moves):
        er = sl_empty // n
        ec = sl_empty % n
        neighbors = []
        # up
        if er > 0 and last_dir != 2:
            neighbors.append(0)
        # down
        if er < n - 1 and last_dir != 0:
            neighbors.append(2)
        # left
        if ec > 0 and last_dir != 3:
            neighbors.append(1)
        # right
        if ec < n - 1 and last_dir != 1:
            neighbors.append(3)
        d = neighbors[random.randint(0, len(neighbors) - 1)]
        dr = [-1, 0, 1, 0]
        dc = [0, -1, 0, 1]
        nr = er + dr[d]
        nc = ec + dc[d]
        ni = nr * n + nc
        sl_board[sl_empty] = sl_board[ni]
        sl_board[ni] = 0
        sl_empty = ni
        last_dir = d
    sl_timer_start = time.ticks_ms()

def sl_check_win():
    """Check if board is in solved state."""
    n = sl_size
    total = n * n
    for i in range(total - 1):
        if sl_board[i] != i + 1:
            return False
    return sl_board[total - 1] == 0

def sl_draw_tile(idx):
    """Draw a single tile at board index."""
    n = sl_size
    cell = SL_CELLS[sl_difficulty]
    ox, oy = sl_board_origin()
    r = idx // n
    c = idx % n
    x = ox + c * cell
    y = oy + r * cell
    val = sl_board[idx]
    if val == 0:
        # Empty space
        display.fill_rect(x, y, cell, cell, BLACK)
    else:
        # Tile with border effect
        display.fill_rect(x + 1, y + 1, cell - 2, cell - 2, SL_TILE_COLOR)
        display.fill_rect(x + 1, y + 1, cell - 2, 2, SL_TILE_BORDER)
        display.fill_rect(x + 1, y + 1, 2, cell - 2, SL_TILE_BORDER)
        # Number centered in tile
        txt = str(val)
        if n <= 3:
            sz = 4
        elif n == 4:
            sz = 3
        else:
            sz = 2
        char_w = 6 * sz
        tw = len(txt) * char_w
        th = 8 * sz
        tx = x + (cell - tw) // 2
        ty = y + (cell - th) // 2
        draw_text(display, txt, tx, ty, WHITE, sz, CODE_FONT)

def sl_draw_board():
    """Draw entire board."""
    n = sl_size
    ox, oy = sl_board_origin()
    cell = SL_CELLS[sl_difficulty]
    board_px = n * cell
    # Clear board area
    display.fill_rect(ox, oy, board_px, board_px, BLACK)
    # Draw grid lines
    for i in range(n + 1):
        px = ox + i * cell
        py = oy + i * cell
        display.fill_rect(px, oy, 1, board_px, BLACK)
        display.fill_rect(ox, py, board_px, 1, BLACK)
    # Draw all tiles
    for i in range(n * n):
        sl_draw_tile(i)

def sl_draw_status():
    """Draw moves and timer at top."""
    global sl_last_moves_text, sl_last_timer_text
    moves_text = f"MOVES: {sl_moves}"
    if moves_text != sl_last_moves_text:
        display.fill_rect(15, 10, 180, 25, BLACK)
        draw_text(display, moves_text, 15, 12, GREY, 2, CODE_FONT)
        sl_last_moves_text = moves_text
    elapsed = time.ticks_diff(time.ticks_ms(), sl_timer_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    t = f"{mins}:{secs:02d}"
    if t != sl_last_timer_text:
        display.fill_rect(270, 10, 90, 25, BLACK)
        draw_text(display, t, 275, 12, GREEN, 2, CODE_FONT)
        sl_last_timer_text = t

def sl_draw_game():
    """Draw full game screen."""
    global sl_last_timer_text, sl_last_moves_text
    display.fill(BLACK)
    sl_last_timer_text = ""
    sl_last_moves_text = ""
    sl_draw_status()
    sl_draw_board()

def sl_draw_menu():
    """Draw difficulty selection menu."""
    display.fill(BLACK)
    # Title
    title = "SLIDING"
    tw = len(title) * 6 * 4
    draw_text(display, title, (368 - tw) // 2, 20, GREY, 4, CODE_FONT)
    title2 = "PUZZLE"
    tw2 = len(title2) * 6 * 4
    draw_text(display, title2, (368 - tw2) // 2, 65, GREY, 4, CODE_FONT)
    # Difficulty buttons
    display.fill_rect(34, 160, 300, 60, GREEN)
    t = "3 X 3"
    tw = len(t) * 6 * 3
    draw_text(display, t, (368 - tw) // 2, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    t = "4 X 4"
    tw = len(t) * 6 * 3
    draw_text(display, t, (368 - tw) // 2, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    t = "5 X 5"
    tw = len(t) * 6 * 3
    draw_text(display, t, (368 - tw) // 2, 338, WHITE, 3, CODE_FONT)

def sl_draw_win():
    """Draw win/solved screen."""
    display.fill(BLACK)
    title = "SOLVED!"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    elapsed = time.ticks_diff(time.ticks_ms(), sl_timer_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    info = f"{sl_moves} MOVES  {mins}:{secs:02d}"
    iw = len(info) * 6 * 2
    draw_text(display, info, (368 - iw) // 2, 160, GREY, 2, CODE_FONT)
    # Check for new best
    if sl_difficulty == 0:
        bm = sl_3_best_moves
        bt = sl_3_best_time
    elif sl_difficulty == 1:
        bm = sl_4_best_moves
        bt = sl_4_best_time
    else:
        bm = sl_5_best_moves
        bt = sl_5_best_time
    if bm == sl_moves or bt == elapsed:
        nbt = "NEW BEST!"
        nbw = len(nbt) * 6 * 3
        draw_text(display, nbt, (368 - nbw) // 2, 200, GREEN, 3, CODE_FONT)
    # Buttons
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    t = "PLAY"
    tw = len(t) * 6 * 3
    draw_text(display, t, 25 + (150 - tw) // 2, 253, WHITE, 3, CODE_FONT)
    t2 = "AGAIN"
    tw2 = len(t2) * 6 * 3
    draw_text(display, t2, 25 + (150 - tw2) // 2, 278, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    t = "EXIT"
    tw = len(t) * 6 * 3
    draw_text(display, t, 193 + (150 - tw) // 2, 265, WHITE, 3, CODE_FONT)

def sl_update_stats(elapsed):
    """Update stats for current difficulty after a win."""
    global sl_3_best_moves, sl_3_best_time, sl_3_wins
    global sl_4_best_moves, sl_4_best_time, sl_4_wins
    global sl_5_best_moves, sl_5_best_time, sl_5_wins
    if sl_difficulty == 0:
        sl_3_wins += 1
        if sl_3_best_moves == 0 or sl_moves < sl_3_best_moves:
            sl_3_best_moves = sl_moves
        if sl_3_best_time == 0 or elapsed < sl_3_best_time:
            sl_3_best_time = elapsed
    elif sl_difficulty == 1:
        sl_4_wins += 1
        if sl_4_best_moves == 0 or sl_moves < sl_4_best_moves:
            sl_4_best_moves = sl_moves
        if sl_4_best_time == 0 or elapsed < sl_4_best_time:
            sl_4_best_time = elapsed
    else:
        sl_5_wins += 1
        if sl_5_best_moves == 0 or sl_moves < sl_5_best_moves:
            sl_5_best_moves = sl_moves
        if sl_5_best_time == 0 or elapsed < sl_5_best_time:
            sl_5_best_time = elapsed
    save_sl_stats()

def save_sl_stats():
    save_all_stats()

# ===== ENTRY POINTS =====

def launch_sliding():
    global sl_mode, sl_difficulty
    sl_difficulty = 0
    sl_reset()
    sl_draw_game()

def handle_sliding_touch(tx, ty):
    global sl_mode, sl_difficulty, sl_board, sl_empty, sl_moves
    global current_screen, current_app, last_time_text

    if sl_mode == 1:  # Playing
        n = sl_size
        er = sl_empty // n
        ec = sl_empty % n
        # Swipe to slide: direction = which way tiles move into the empty space
        d = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
        # d: 0=up, 1=right, 2=down, 3=left
        # Swipe up -> tile below empty slides up
        # Swipe down -> tile above empty slides down
        # Swipe left -> tile right of empty slides left
        # Swipe right -> tile left of empty slides right
        tr, tc = -1, -1
        if d == 0 and er < n - 1:  # swipe up, tile below moves up
            tr, tc = er + 1, ec
        elif d == 2 and er > 0:  # swipe down, tile above moves down
            tr, tc = er - 1, ec
        elif d == 3 and ec < n - 1:  # swipe left, tile right moves left
            tr, tc = er, ec + 1
        elif d == 1 and ec > 0:  # swipe right, tile left moves right
            tr, tc = er, ec - 1
        if tr >= 0:
            tap_idx = tr * n + tc
            old_empty = sl_empty
            sl_board[sl_empty] = sl_board[tap_idx]
            sl_board[tap_idx] = 0
            sl_empty = tap_idx
            sl_moves += 1
            sl_draw_tile(old_empty)
            sl_draw_tile(tap_idx)
            sl_draw_status()
            if sl_check_win():
                elapsed = time.ticks_diff(time.ticks_ms(), sl_timer_start) // 1000
                sl_mode = 2
                sl_update_stats(elapsed)
                time.sleep_ms(400)
                sl_draw_win()

    elif sl_mode == 2:  # Win screen
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # PLAY AGAIN
                sl_reset()
                sl_draw_game()
            elif 193 <= tx <= 343:  # EXIT
                track_app_exit("SLIDING PUZZLE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""

# ===== STATS =====

def draw_sl_stats():
    display.fill(BLACK)
    draw_text(display, "SLIDING STATS", 70, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    draw_text(display, f"SOLVED: {sl_3_wins}", 30, y_start + 15, GREY, 3, CODE_FONT)
    y2 = y_start + row_height
    display.fill_rect(20, y2, 328, 3, DARK_GREY)
    if sl_3_best_moves > 0:
        draw_text(display, f"BEST MOVES: {sl_3_best_moves}", 30, y2 + 15, GREY, 3, CODE_FONT)
    else:
        draw_text(display, "BEST MOVES: ---", 30, y2 + 15, GREY, 3, CODE_FONT)
    y3 = y2 + row_height
    display.fill_rect(20, y3, 328, 3, DARK_GREY)
    if sl_3_best_time > 0:
        tm = sl_3_best_time // 60
        ts = sl_3_best_time % 60
        draw_text(display, f"BEST TIME: {tm}:{ts:02d}", 30, y3 + 15, GREY, 3, CODE_FONT)
    else:
        draw_text(display, "BEST TIME: --:--", 30, y3 + 15, GREY, 3, CODE_FONT)
    y_final = y3 + row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
