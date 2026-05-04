# ===== MINESWEEPER GAME =====
import random

# Minesweeper state
ms_board = [0] * 81       # -1=mine, 0-8=adjacent count
ms_revealed = [0] * 81    # 0=hidden, 1=revealed
ms_flagged = [0] * 81     # 0=no flag, 1=flagged
ms_mode = 0               # 0=difficulty, 1=playing, 2=won, 3=lost
ms_difficulty = 0          # 0=easy, 1=med, 2=hard
ms_dig_mode = True         # True=DIG, False=FLAG
ms_first_tap = True
ms_timer_start = 0
ms_last_timer_text = ""
ms_mines_count = 10
ms_hit_pos = -1            # which mine was hit (for red highlight)

# Minesweeper stats
ms_easy_best = 0
ms_easy_wins = 0
ms_easy_losses = 0
ms_med_best = 0
ms_med_wins = 0
ms_med_losses = 0
ms_hard_best = 0
ms_hard_wins = 0
ms_hard_losses = 0
ms_stats_page = 0

# Layout
MS_GRID_X = 13
MS_GRID_Y = 42
MS_CELL = 38
MS_HIDDEN_COLOR = make_color(45, 45, 55)
MS_HIDDEN_LIGHT = make_color(60, 60, 70)
MS_REVEALED_COLOR = make_color(20, 20, 25)
MS_FLAG_COLOR = make_color(220, 50, 50)    # Red flag
MS_MINE_COLOR = make_color(150, 30, 30)    # Red for revealed mines
MS_EXPLODE_COLOR = make_color(150, 30, 30) # Red for mine you hit

# Number colors: Classic Minesweeper, softened for AMOLED
MS_NUM_COLORS = [
    0,                           # 0 not drawn
    make_color(70, 100, 255),    # 1 - Blue
    make_color(50, 180, 50),     # 2 - Green
    make_color(230, 50, 50),     # 3 - Red
    make_color(50, 50, 180),     # 4 - Dark Blue
    make_color(180, 70, 30),     # 5 - Brown/Maroon
    make_color(50, 180, 180),    # 6 - Cyan/Teal
    make_color(100, 100, 100),   # 7 - Dark Grey (not black on black bg)
    make_color(160, 160, 160),   # 8 - Light Grey
]

def ms_place_mines(safe_pos):
    global ms_board
    ms_board = [0] * 81
    safe_r = safe_pos // 9
    safe_c = safe_pos % 9
    # Build list of valid positions (exclude safe cell + neighbors)
    valid = []
    for i in range(81):
        r = i // 9
        c = i % 9
        if abs(r - safe_r) <= 1 and abs(c - safe_c) <= 1:
            continue
        valid.append(i)
    # Shuffle and pick mines
    for i in range(len(valid) - 1, 0, -1):
        j = random.randint(0, i)
        valid[i], valid[j] = valid[j], valid[i]
    for i in range(min(ms_mines_count, len(valid))):
        ms_board[valid[i]] = -1
    # Calculate adjacent counts
    for i in range(81):
        if ms_board[i] == -1:
            continue
        r = i // 9
        c = i % 9
        count = 0
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = r + dr, c + dc
                if 0 <= nr < 9 and 0 <= nc < 9:
                    if ms_board[nr * 9 + nc] == -1:
                        count += 1
        ms_board[i] = count

def ms_flood_fill(pos):
    stack = [pos]
    while stack:
        p = stack.pop()
        if ms_revealed[p]:
            continue
        ms_revealed[p] = 1
        if ms_board[p] == 0:
            r = p // 9
            c = p % 9
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 9 and 0 <= nc < 9:
                        np = nr * 9 + nc
                        if not ms_revealed[np] and not ms_flagged[np]:
                            stack.append(np)

def ms_check_win():
    for i in range(81):
        if ms_board[i] != -1 and not ms_revealed[i]:
            return False
    return True

def ms_reset():
    global ms_board, ms_revealed, ms_flagged, ms_mode, ms_dig_mode, ms_first_tap
    global ms_timer_start, ms_last_timer_text, ms_hit_pos
    ms_board = [0] * 81
    ms_revealed = [0] * 81
    ms_flagged = [0] * 81
    ms_mode = 1
    ms_dig_mode = True
    ms_first_tap = True
    ms_timer_start = time.ticks_ms()
    ms_last_timer_text = ""
    ms_hit_pos = -1

def draw_ms_difficulty():
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 338, WHITE, 3, CODE_FONT)

def draw_ms_cell(row, col):
    x = MS_GRID_X + col * MS_CELL
    y = MS_GRID_Y + row * MS_CELL
    pos = row * 9 + col
    if ms_revealed[pos]:
        # Revealed cell
        if ms_board[pos] == -1:
            # Mine
            bg = MS_EXPLODE_COLOR if pos == ms_hit_pos else MS_MINE_COLOR
            display.fill_rect(x + 1, y + 1, MS_CELL - 2, MS_CELL - 2, bg)
            # Draw mine circle
            cx = x + MS_CELL // 2
            cy = y + MS_CELL // 2
            display.fill_circle(cx, cy, 7, BLACK)
            display.fill_circle(cx, cy, 3, WHITE)
        else:
            display.fill_rect(x + 1, y + 1, MS_CELL - 2, MS_CELL - 2, MS_REVEALED_COLOR)
            if ms_board[pos] > 0:
                ch = str(ms_board[pos])
                draw_text(display, ch, x + 10, y + 9, MS_NUM_COLORS[ms_board[pos]], 3, CODE_FONT)
    elif ms_flagged[pos]:
        # Flagged cell
        display.fill_rect(x + 1, y + 1, MS_CELL - 2, MS_CELL - 2, MS_HIDDEN_COLOR)
        # Draw flag (small red rectangle + pole)
        fx = x + MS_CELL // 2
        fy = y + 8
        display.fill_rect(fx - 1, fy, 2, 20, WHITE)
        display.fill_rect(fx + 1, fy, 10, 7, MS_FLAG_COLOR)
    else:
        # Hidden cell - raised look
        display.fill_rect(x + 1, y + 1, MS_CELL - 2, MS_CELL - 2, MS_HIDDEN_COLOR)
        display.fill_rect(x + 1, y + 1, MS_CELL - 2, 2, MS_HIDDEN_LIGHT)
        display.fill_rect(x + 1, y + 1, 2, MS_CELL - 2, MS_HIDDEN_LIGHT)

def draw_ms_toggle():
    bw = 160
    bx = (368 - bw) // 2
    by = 395
    bh = 35
    if ms_dig_mode:
        display.fill_rect(bx, by, bw, bh, GREEN)
        txt = "DIG"
    else:
        display.fill_rect(bx, by, bw, bh, MS_FLAG_COLOR)
        txt = "FLAG"
    tw = len(txt) * 18
    draw_text(display, txt, bx + (bw - tw) // 2, by + 7, WHITE, 3, CODE_FONT)

def draw_ms_mine_counter():
    flags = 0
    for i in range(81):
        if ms_flagged[i]:
            flags += 1
    remaining = ms_mines_count - flags
    display.fill_rect(20, 12, 110, 25, BLACK)
    txt = f"MINES: {remaining}"
    draw_text(display, txt, 20, 12, GREY, 2, CODE_FONT)

def draw_ms_timer():
    global ms_last_timer_text
    elapsed = time.ticks_diff(time.ticks_ms(), ms_timer_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    t = f"{mins:02d}:{secs:02d}"
    if t != ms_last_timer_text:
        display.fill_rect(255, 12, 95, 25, BLACK)
        draw_text(display, t, 258, 12, GREEN, 3, CODE_FONT)
        ms_last_timer_text = t

def draw_ms_game():
    global ms_last_timer_text
    display.fill(BLACK)
    # Mine counter
    draw_ms_mine_counter()
    # Timer
    ms_last_timer_text = "00:00"
    draw_text(display, "00:00", 258, 12, GREEN, 3, CODE_FONT)
    # Grid lines
    gx = MS_GRID_X
    gy = MS_GRID_Y
    gs = MS_CELL * 9
    for i in range(10):
        px = gx + i * MS_CELL
        py = gy + i * MS_CELL
        display.fill_rect(px, gy, 1, gs, DARK_GREY)
        display.fill_rect(gx, py, gs, 1, DARK_GREY)
    # Draw all cells
    for r in range(9):
        for c in range(9):
            draw_ms_cell(r, c)
    # Toggle button
    draw_ms_toggle()

def draw_ms_gameover(elapsed_s=-1):
    display.fill(BLACK)
    if ms_mode == 2:
        title = "YOU WIN!"
        mins = elapsed_s // 60
        secs = elapsed_s % 60
        info = f"TIME: {mins:02d}:{secs:02d}"
    else:
        title = "GAME OVER"
        info = "HIT A MINE!"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    iw = len(info) * 18
    draw_text(display, info, (368 - iw) // 2, 160, GREY, 3, CODE_FONT)
    # Show NEW BEST on win
    if ms_mode == 2 and elapsed_s >= 0:
        if ms_difficulty == 0:
            best = ms_easy_best
        elif ms_difficulty == 1:
            best = ms_med_best
        else:
            best = ms_hard_best
        if best == elapsed_s:
            draw_text(display, "NEW BEST!", (368 - 9 * 18) // 2, 200, GREEN, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "MENU", 61, 268, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "RETRY", 223, 268, WHITE, 3, CODE_FONT)

def save_ms_stats():
    save_all_stats()

def draw_ms_stats():
    display.fill(BLACK)
    draw_text(display, "MINESWEEPER", 72, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    if ms_stats_page == 0:
        for label, best, wins, losses in [("EASY", ms_easy_best, ms_easy_wins, ms_easy_losses),
                                           ("MEDIUM", ms_med_best, ms_med_wins, ms_med_losses)]:
            display.fill_rect(20, y, 328, 3, DARK_GREY)
            draw_text(display, label, 30, y + 8, GREEN, 2, CODE_FONT)
            y += rh
            display.fill_rect(20, y, 328, 3, DARK_GREY)
            draw_text(display, f"WINS: {wins}", 30, y + 8, GREY, 2, CODE_FONT)
            y += rh
            display.fill_rect(20, y, 328, 3, DARK_GREY)
            draw_text(display, f"LOSSES: {losses}", 30, y + 8, GREY, 2, CODE_FONT)
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
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + 12 - i, i * 2 + 1, 2, GREY)
    else:
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "HARD", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {ms_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {ms_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        if ms_hard_best > 0:
            bm = ms_hard_best // 60
            bs = ms_hard_best % 60
            draw_text(display, f"BEST: {bm:02d}:{bs:02d}", 30, y + 8, GREY, 2, CODE_FONT)
        else:
            draw_text(display, "BEST: --:--", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + i, i * 2 + 1, 2, GREY)

def launch_minesweeper():
    global ms_mode
    ms_mode = 0
    draw_ms_difficulty()

def handle_minesweeper_touch(tx, ty):
    global ms_mode, ms_difficulty, ms_mines_count, ms_dig_mode, ms_first_tap, ms_timer_start
    global ms_hit_pos, ms_revealed, ms_board
    global ms_easy_wins, ms_easy_losses, ms_easy_best
    global ms_med_wins, ms_med_losses, ms_med_best
    global ms_hard_wins, ms_hard_losses, ms_hard_best
    global current_screen, current_app, last_time_text
    if ms_mode == 0:  # Difficulty select
        if 160 <= ty <= 220 and 34 <= tx <= 334:
            ms_mines_count = 10
            ms_difficulty = 0
            ms_reset()
            draw_ms_game()
        elif 240 <= ty <= 300 and 34 <= tx <= 334:
            ms_mines_count = 15
            ms_difficulty = 1
            ms_reset()
            draw_ms_game()
        elif 320 <= ty <= 380 and 34 <= tx <= 334:
            ms_mines_count = 25
            ms_difficulty = 2
            ms_reset()
            draw_ms_game()
    elif ms_mode == 1:  # Playing
        if MS_GRID_Y <= ty < MS_GRID_Y + 9 * MS_CELL and MS_GRID_X <= tx < MS_GRID_X + 9 * MS_CELL:
            row = (ty - MS_GRID_Y) // MS_CELL
            col = (tx - MS_GRID_X) // MS_CELL
            pos = row * 9 + col
            if not ms_revealed[pos]:
                if ms_dig_mode and not ms_flagged[pos]:
                    # DIG mode
                    if ms_first_tap:
                        ms_place_mines(pos)
                        ms_first_tap = False
                        ms_timer_start = time.ticks_ms()
                    if ms_board[pos] == -1:
                        # Hit a mine!
                        ms_hit_pos = pos
                        ms_revealed[pos] = 1
                        # Reveal all mines
                        for i in range(81):
                            if ms_board[i] == -1:
                                ms_revealed[i] = 1
                        ms_mode = 3
                        if ms_difficulty == 0:
                            ms_easy_losses += 1
                        elif ms_difficulty == 1:
                            ms_med_losses += 1
                        else:
                            ms_hard_losses += 1
                        save_ms_stats()
                        # Redraw grid to show mines
                        for r in range(9):
                            for c in range(9):
                                draw_ms_cell(r, c)
                        time.sleep_ms(1500)
                        draw_ms_gameover()
                    else:
                        # Safe - reveal with flood fill
                        ms_flood_fill(pos)
                        for r in range(9):
                            for c in range(9):
                                draw_ms_cell(r, c)
                        if ms_check_win():
                            elapsed = time.ticks_diff(time.ticks_ms(), ms_timer_start) // 1000
                            if ms_difficulty == 0:
                                ms_easy_wins += 1
                                if ms_easy_best == 0 or elapsed < ms_easy_best:
                                    ms_easy_best = elapsed
                            elif ms_difficulty == 1:
                                ms_med_wins += 1
                                if ms_med_best == 0 or elapsed < ms_med_best:
                                    ms_med_best = elapsed
                            else:
                                ms_hard_wins += 1
                                if ms_hard_best == 0 or elapsed < ms_hard_best:
                                    ms_hard_best = elapsed
                            save_ms_stats()
                            ms_mode = 2
                            time.sleep_ms(500)
                            draw_ms_gameover(elapsed)
                else:
                    # FLAG mode - toggle flag
                    if ms_flagged[pos]:
                        ms_flagged[pos] = 0
                    else:
                        ms_flagged[pos] = 1
                    draw_ms_cell(row, col)
                    draw_ms_mine_counter()
        elif 395 <= ty <= 430:
            # Toggle DIG/FLAG button
            ms_dig_mode = not ms_dig_mode
            draw_ms_toggle()
    elif ms_mode in (2, 3):  # Won or Lost
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # MENU
                track_app_exit("MINESWEEPER")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:  # RETRY
                ms_reset()
                draw_ms_game()
