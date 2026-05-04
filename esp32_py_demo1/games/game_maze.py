# ===== MAZE =====
import random

# Game modes: 0=select, 1=playing, 2=win
mz_mode = 0
mz_difficulty = 0  # 0=easy, 1=medium, 2=hard

# Maze sizes per difficulty
MZ_SIZES = [(9, 9), (13, 13), (15, 15)]
MZ_CELL_SIZES = [18, 12, 11]
MZ_OFFSETS_X = [13, 22, 13]
MZ_GRID_Y = 50

# Maze grid (flat list, 1=wall 0=path)
mz_grid = []
mz_rows = 0
mz_cols = 0
mz_grid_w = 0
mz_grid_h = 0

# Player position (logical maze coords)
mz_player_r = 0
mz_player_c = 0
mz_end_r = 0
mz_end_c = 0

# Timer and moves
mz_timer_start = 0
mz_first_move = True
mz_moves = 0
mz_last_timer_text = ""

# Stats
mz_easy_best = 0
mz_easy_wins = 0
mz_med_best = 0
mz_med_wins = 0
mz_hard_best = 0
mz_hard_wins = 0

# Colors
MZ_WALL_COLOR = DARK_GREY
MZ_PLAYER_COLOR = GREEN
MZ_END_COLOR = make_color(0, 60, 0)

# ===== GENERATION =====

def mz_generate(rows, cols):
    """Generate maze using iterative DFS. Flat grid, 1=wall 0=path."""
    global mz_grid, mz_rows, mz_cols, mz_grid_w, mz_grid_h
    mz_rows = rows
    mz_cols = cols
    mz_grid_w = 2 * cols + 1
    mz_grid_h = 2 * rows + 1
    mz_grid = [1] * (mz_grid_w * mz_grid_h)
    visited = [0] * (rows * cols)
    # Start from (0,0)
    stack = [(0, 0)]
    visited[0] = 1
    mz_grid[1 * mz_grid_w + 1] = 0  # Carve start cell
    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]
    while stack:
        r, c = stack[-1]
        neighbors = []
        for d in range(4):
            nr = r + dr[d]
            nc = c + dc[d]
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr * cols + nc]:
                neighbors.append((nr, nc, d))
        if neighbors:
            idx = random.randint(0, len(neighbors) - 1)
            nr, nc, d = neighbors[idx]
            # Remove wall between current and neighbor
            wall_gr = 2 * r + 1 + dr[d]
            wall_gc = 2 * c + 1 + dc[d]
            mz_grid[wall_gr * mz_grid_w + wall_gc] = 0
            # Carve neighbor cell
            mz_grid[(2 * nr + 1) * mz_grid_w + (2 * nc + 1)] = 0
            visited[nr * cols + nc] = 1
            stack.append((nr, nc))
        else:
            stack.pop()

# ===== DRAWING =====

def mz_draw_full():
    """Draw entire maze screen."""
    global mz_last_timer_text
    display.fill(BLACK)
    draw_text(display, "MAZE", 148, 5, GREY, 3, CODE_FONT)
    draw_text(display, "MOVES: 0", 15, 28, GREY, 2, CODE_FONT)
    mz_last_timer_text = "00:00"
    draw_text(display, "00:00", 270, 28, GREEN, 2, CODE_FONT)
    cell = MZ_CELL_SIZES[mz_difficulty]
    ox = MZ_OFFSETS_X[mz_difficulty]
    oy = MZ_GRID_Y
    # Draw walls
    for gr in range(mz_grid_h):
        for gc in range(mz_grid_w):
            if mz_grid[gr * mz_grid_w + gc] == 1:
                display.fill_rect(ox + gc * cell, oy + gr * cell, cell, cell, MZ_WALL_COLOR)
    # Draw end marker
    display.fill_rect(ox + (2 * mz_end_c + 1) * cell, oy + (2 * mz_end_r + 1) * cell, cell, cell, MZ_END_COLOR)
    # Draw player
    display.fill_rect(ox + (2 * mz_player_c + 1) * cell, oy + (2 * mz_player_r + 1) * cell, cell, cell, MZ_PLAYER_COLOR)

def mz_draw_player(old_r, old_c):
    """Dirty-region player redraw."""
    cell = MZ_CELL_SIZES[mz_difficulty]
    ox = MZ_OFFSETS_X[mz_difficulty]
    oy = MZ_GRID_Y
    # Erase old
    if old_r == mz_end_r and old_c == mz_end_c:
        display.fill_rect(ox + (2 * old_c + 1) * cell, oy + (2 * old_r + 1) * cell, cell, cell, MZ_END_COLOR)
    else:
        display.fill_rect(ox + (2 * old_c + 1) * cell, oy + (2 * old_r + 1) * cell, cell, cell, BLACK)
    # Draw new
    display.fill_rect(ox + (2 * mz_player_c + 1) * cell, oy + (2 * mz_player_r + 1) * cell, cell, cell, MZ_PLAYER_COLOR)

def mz_draw_header():
    """Update moves counter."""
    display.fill_rect(15, 28, 160, 16, BLACK)
    draw_text(display, f"MOVES: {mz_moves}", 15, 28, GREY, 2, CODE_FONT)

def mz_draw_timer():
    """Update timer display (called from main loop)."""
    global mz_last_timer_text
    if mz_first_move:
        return
    elapsed = time.ticks_diff(time.ticks_ms(), mz_timer_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    t = f"{mins:02d}:{secs:02d}"
    if t != mz_last_timer_text:
        display.fill_rect(270, 28, 90, 16, BLACK)
        draw_text(display, t, 270, 28, GREEN, 2, CODE_FONT)
        mz_last_timer_text = t

# ===== GAME LOGIC =====

def mz_move(direction):
    """Move player to next intersection/turn. Returns 0=blocked, 1=moved, 2=won."""
    global mz_player_r, mz_player_c, mz_moves, mz_first_move, mz_timer_start
    dr = [-1, 0, 1, 0]
    dc = [0, 1, 0, -1]
    # Check if first step is even possible
    nr = mz_player_r + dr[direction]
    nc = mz_player_c + dc[direction]
    if nr < 0 or nr >= mz_rows or nc < 0 or nc >= mz_cols:
        return 0
    wall_gr = 2 * mz_player_r + 1 + dr[direction]
    wall_gc = 2 * mz_player_c + 1 + dc[direction]
    if mz_grid[wall_gr * mz_grid_w + wall_gc] == 1:
        return 0
    if mz_first_move:
        mz_timer_start = time.ticks_ms()
        mz_first_move = False
    old_r, old_c = mz_player_r, mz_player_c
    # Slide until intersection, dead end, or goal
    while True:
        nr = mz_player_r + dr[direction]
        nc = mz_player_c + dc[direction]
        if nr < 0 or nr >= mz_rows or nc < 0 or nc >= mz_cols:
            break
        wgr = 2 * mz_player_r + 1 + dr[direction]
        wgc = 2 * mz_player_c + 1 + dc[direction]
        if mz_grid[wgr * mz_grid_w + wgc] == 1:
            break
        mz_player_r = nr
        mz_player_c = nc
        mz_moves += 1
        if mz_player_r == mz_end_r and mz_player_c == mz_end_c:
            break
        # Check for perpendicular branches (intersection)
        has_branch = False
        for d in range(4):
            if d == direction or d == (direction + 2) % 4:
                continue
            br = mz_player_r + dr[d]
            bc = mz_player_c + dc[d]
            if 0 <= br < mz_rows and 0 <= bc < mz_cols:
                bwgr = 2 * mz_player_r + 1 + dr[d]
                bwgc = 2 * mz_player_c + 1 + dc[d]
                if mz_grid[bwgr * mz_grid_w + bwgc] == 0:
                    has_branch = True
                    break
        if has_branch:
            break
    mz_draw_player(old_r, old_c)
    mz_draw_header()
    if mz_player_r == mz_end_r and mz_player_c == mz_end_c:
        return 2
    return 1

# ===== SCREENS =====

def mz_draw_select():
    """Difficulty selection screen."""
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    etw = len("EASY") * 6 * 3
    draw_text(display, "EASY", (368 - etw) // 2, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    mtw = len("MEDIUM") * 6 * 3
    draw_text(display, "MEDIUM", (368 - mtw) // 2, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    htw = len("HARD") * 6 * 3
    draw_text(display, "HARD", (368 - htw) // 2, 338, WHITE, 3, CODE_FONT)

def mz_reset():
    """Reset game state and generate new maze."""
    global mz_mode, mz_player_r, mz_player_c, mz_end_r, mz_end_c
    global mz_moves, mz_first_move, mz_timer_start, mz_last_timer_text
    rows, cols = MZ_SIZES[mz_difficulty]
    mz_generate(rows, cols)
    mz_player_r = 0
    mz_player_c = 0
    mz_end_r = rows - 1
    mz_end_c = cols - 1
    mz_moves = 0
    mz_first_move = True
    mz_timer_start = 0
    mz_last_timer_text = ""
    mz_mode = 1

def mz_draw_win(elapsed_s):
    """Win/complete screen."""
    display.fill(BLACK)
    tw = len("COMPLETE!") * 6 * 5
    draw_text(display, "COMPLETE!", (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    mins = elapsed_s // 60
    secs = elapsed_s % 60
    time_text = f"TIME: {mins:02d}:{secs:02d}"
    ttw = len(time_text) * 18
    draw_text(display, time_text, (368 - ttw) // 2, 150, GREY, 3, CODE_FONT)
    moves_text = f"MOVES: {mz_moves}"
    mtw = len(moves_text) * 18
    draw_text(display, moves_text, (368 - mtw) // 2, 190, GREY, 3, CODE_FONT)
    # Check for new best
    if mz_difficulty == 0:
        best = mz_easy_best
    elif mz_difficulty == 1:
        best = mz_med_best
    else:
        best = mz_hard_best
    if best == elapsed_s:
        nbt = "NEW BEST!"
        nbw = len(nbt) * 18
        draw_text(display, nbt, (368 - nbw) // 2, 220, GREEN, 3, CODE_FONT)
    # Standard buttons
    display.fill_rect(25, 280, 150, 70, GAMEOVER_BTN)
    btw = len("MENU") * 6 * 2
    draw_text(display, "MENU", 25 + (150 - btw) // 2, 303, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 280, 150, 70, GAMEOVER_BTN)
    atw = len("RETRY") * 6 * 2
    draw_text(display, "RETRY", 193 + (150 - atw) // 2, 303, WHITE, 2, CODE_FONT)

# ===== ENTRY POINTS =====

def launch_maze():
    global mz_mode
    mz_mode = 0
    mz_draw_select()

def handle_maze_touch(tx, ty):
    global mz_mode, mz_difficulty, current_screen, current_app, last_time_text
    global mz_easy_wins, mz_easy_best, mz_med_wins, mz_med_best
    global mz_hard_wins, mz_hard_best

    if mz_mode == 0:  # Difficulty select
        if 34 <= tx <= 334:
            if 160 <= ty <= 220:
                mz_difficulty = 0
                mz_reset()
                mz_draw_full()
            elif 240 <= ty <= 300:
                mz_difficulty = 1
                mz_reset()
                mz_draw_full()
            elif 320 <= ty <= 380:
                mz_difficulty = 2
                mz_reset()
                mz_draw_full()

    elif mz_mode == 1:  # Playing
        direction = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
        if direction >= 0:
            result = mz_move(direction)
            if result == 2:
                elapsed = time.ticks_diff(time.ticks_ms(), mz_timer_start) // 1000
                if mz_difficulty == 0:
                    mz_easy_wins += 1
                    if mz_easy_best == 0 or elapsed < mz_easy_best:
                        mz_easy_best = elapsed
                elif mz_difficulty == 1:
                    mz_med_wins += 1
                    if mz_med_best == 0 or elapsed < mz_med_best:
                        mz_med_best = elapsed
                else:
                    mz_hard_wins += 1
                    if mz_hard_best == 0 or elapsed < mz_hard_best:
                        mz_hard_best = elapsed
                save_maze_stats()
                mz_mode = 2
                time.sleep_ms(500)
                mz_draw_win(elapsed)

    elif mz_mode == 2:  # Win screen
        if 280 <= ty <= 350:
            if 25 <= tx <= 175:  # MENU
                track_app_exit("MAZE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:  # AGAIN
                mz_reset()
                mz_draw_full()

# ===== STATS =====

def draw_maze_stats():
    display.fill(BLACK)
    draw_text(display, "MAZE", 148, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    for label, best, wins in [("EASY", mz_easy_best, mz_easy_wins),
                                ("MEDIUM", mz_med_best, mz_med_wins),
                                ("HARD", mz_hard_best, mz_hard_wins)]:
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, label, 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"SOLVED: {wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        if best > 0:
            bm = best // 60
            bs = best % 60
            draw_text(display, f"BEST: {bm:02d}:{bs:02d}", 30, y + 8, GREY, 2, CODE_FONT)
        else:
            draw_text(display, "BEST: --:--", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)

def save_maze_stats():
    save_all_stats()
