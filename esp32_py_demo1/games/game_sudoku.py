# ===== SUDOKU GAME =====
import random
# Sudoku state
sdk_mode = 0  # 0=difficulty select, 1=playing, 2=won
sdk_difficulty = 0  # 0=easy, 1=medium, 2=hard
sdk_board = [0] * 81
sdk_fixed = [0] * 81
sdk_solution = [0] * 81
sdk_sel_row = -1
sdk_sel_col = -1
sdk_timer_start = 0
sdk_timer_elapsed = 0
sdk_last_timer_text = ""

# Sudoku stats (per difficulty)
sdk_easy_best = 0
sdk_easy_wins = 0
sdk_easy_losses = 0
sdk_med_best = 0
sdk_med_wins = 0
sdk_med_losses = 0
sdk_hard_best = 0
sdk_hard_wins = 0
sdk_hard_losses = 0
sdk_stats_page = 0

# Layout constants
SDK_GRID_X = 31
SDK_GRID_Y = 45
SDK_CELL = 34
SDK_PAD_Y = 360
SDK_PAD_H = 34
SDK_SEL_COLOR = make_color(25, 25, 40)
SDK_HIGHLIGHT = make_color(20, 20, 30)

def sdk_valid(board, pos, num):
    row = pos // 9
    col = pos % 9
    base = row * 9
    for c in range(9):
        if board[base + c] == num:
            return False
    for r in range(9):
        if board[r * 9 + col] == num:
            return False
    br = (row // 3) * 3
    bc = (col // 3) * 3
    for r in range(br, br + 3):
        for c in range(bc, bc + 3):
            if board[r * 9 + c] == num:
                return False
    return True

def sdk_solve_iter(board, randomize=False, count_only=False, max_count=2):
    empties = []
    for i in range(81):
        if board[i] == 0:
            empties.append(i)
    if not empties:
        return 1 if count_only else True
    candidates = []
    for pos in empties:
        nums = list(range(1, 10))
        if randomize:
            for i in range(8, 0, -1):
                j = random.randint(0, i)
                nums[i], nums[j] = nums[j], nums[i]
        candidates.append(nums)
    solutions = 0
    idx = 0
    ci = [0] * len(empties)
    while idx >= 0:
        pos = empties[idx]
        placed = False
        while ci[idx] < len(candidates[idx]):
            num = candidates[idx][ci[idx]]
            ci[idx] += 1
            if sdk_valid(board, pos, num):
                board[pos] = num
                placed = True
                break
        if placed:
            if idx == len(empties) - 1:
                if count_only:
                    solutions += 1
                    if solutions >= max_count:
                        for i in range(len(empties)):
                            board[empties[i]] = 0
                        return solutions
                    board[pos] = 0
                    placed = False
                else:
                    return True
            if placed:
                idx += 1
                continue
        if not placed:
            board[pos] = 0
            ci[idx] = 0
            idx -= 1
    return solutions if count_only else False

def sdk_generate(difficulty):
    global sdk_board, sdk_fixed, sdk_solution
    sdk_board = [0] * 81
    sdk_solve_iter(sdk_board, randomize=True)
    sdk_solution = sdk_board[:]
    if difficulty == 0:
        remove_count = 38
    elif difficulty == 1:
        remove_count = 47
    else:
        remove_count = 53
    positions = list(range(81))
    for i in range(80, 0, -1):
        j = random.randint(0, i)
        positions[i], positions[j] = positions[j], positions[i]
    removed = 0
    for pos in positions:
        if removed >= remove_count:
            break
        val = sdk_board[pos]
        sdk_board[pos] = 0
        test = sdk_board[:]
        if sdk_solve_iter(test, count_only=True, max_count=2) != 1:
            sdk_board[pos] = val
        else:
            removed += 1
    sdk_fixed = [0] * 81
    for i in range(81):
        if sdk_board[i] != 0:
            sdk_fixed[i] = 1

def sdk_reset():
    global sdk_sel_row, sdk_sel_col, sdk_timer_start, sdk_timer_elapsed, sdk_last_timer_text, sdk_mode
    sdk_sel_row = -1
    sdk_sel_col = -1
    sdk_timer_start = time.ticks_ms()
    sdk_timer_elapsed = 0
    sdk_last_timer_text = ""
    sdk_mode = 1

def sdk_check_win():
    for i in range(81):
        if sdk_board[i] != sdk_solution[i]:
            return False
    return True

def draw_sdk_difficulty():
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 338, WHITE, 3, CODE_FONT)

def draw_sdk_cell(row, col):
    x = SDK_GRID_X + col * SDK_CELL
    y = SDK_GRID_Y + row * SDK_CELL
    # Background
    if row == sdk_sel_row and col == sdk_sel_col:
        display.fill_rect(x + 1, y + 1, SDK_CELL - 2, SDK_CELL - 2, SDK_SEL_COLOR)
    elif row == sdk_sel_row or col == sdk_sel_col:
        display.fill_rect(x + 1, y + 1, SDK_CELL - 2, SDK_CELL - 2, SDK_HIGHLIGHT)
    else:
        display.fill_rect(x + 1, y + 1, SDK_CELL - 2, SDK_CELL - 2, BLACK)
    # Number
    pos = row * 9 + col
    if sdk_board[pos] != 0:
        ch = str(sdk_board[pos])
        color = WHITE if sdk_fixed[pos] else GREEN
        draw_text(display, ch, x + 8, y + 7, color, 3, CODE_FONT)

def draw_sdk_game():
    global sdk_last_timer_text
    display.fill(BLACK)
    # Title
    draw_text(display, "SUDOKU", 10, 10, GREY, 3, CODE_FONT)
    # Timer
    sdk_last_timer_text = "00:00"
    draw_text(display, "00:00", 268, 10, GREEN, 3, CODE_FONT)
    # Draw grid lines
    gx = SDK_GRID_X
    gy = SDK_GRID_Y
    gs = SDK_CELL * 9
    # Thin cell lines
    for i in range(10):
        px = gx + i * SDK_CELL
        py = gy + i * SDK_CELL
        display.fill_rect(px, gy, 1, gs, DARK_GREY)
        display.fill_rect(gx, py, gs, 1, DARK_GREY)
    # Thick 3x3 box lines
    for i in range(4):
        px = gx + i * SDK_CELL * 3
        py = gy + i * SDK_CELL * 3
        display.fill_rect(px - 1, gy, 2, gs, GREY)
        display.fill_rect(gx, py - 1, gs, 2, GREY)
    # Draw all cells
    for r in range(9):
        for c in range(9):
            pos = r * 9 + c
            if sdk_board[pos] != 0:
                x = gx + c * SDK_CELL
                y = gy + r * SDK_CELL
                color = WHITE if sdk_fixed[pos] else GREEN
                draw_text(display, str(sdk_board[pos]), x + 8, y + 7, color, 3, CODE_FONT)
    # Number pad
    for i in range(9):
        bx = SDK_GRID_X + i * SDK_CELL
        display.fill_rect(bx, SDK_PAD_Y, SDK_CELL - 2, SDK_PAD_H, GREEN)
        draw_text(display, str(i + 1), bx + 10, SDK_PAD_Y + 7, WHITE, 2, CODE_FONT)
    # Erase button
    erase_x = (368 - 100) // 2
    display.fill_rect(erase_x, 400, 100, SDK_PAD_H, GREEN)
    txt = "ERASE"
    tw = len(txt) * 12
    draw_text(display, txt, erase_x + (100 - tw) // 2, 407, WHITE, 2, CODE_FONT)

def draw_sdk_timer():
    global sdk_last_timer_text, sdk_timer_elapsed
    sdk_timer_elapsed = time.ticks_diff(time.ticks_ms(), sdk_timer_start) // 1000
    mins = sdk_timer_elapsed // 60
    secs = sdk_timer_elapsed % 60
    t = f"{mins:02d}:{secs:02d}"
    if t != sdk_last_timer_text:
        display.fill_rect(268, 10, 90, 25, BLACK)
        draw_text(display, t, 268, 10, GREEN, 3, CODE_FONT)
        sdk_last_timer_text = t

def draw_sdk_gameover(elapsed_s):
    display.fill(BLACK)
    title = "SOLVED!"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    mins = elapsed_s // 60
    secs = elapsed_s % 60
    time_text = f"TIME: {mins:02d}:{secs:02d}"
    tw2 = len(time_text) * 18
    draw_text(display, time_text, (368 - tw2) // 2, 160, GREY, 3, CODE_FONT)
    # Show if new best
    if sdk_difficulty == 0:
        best = sdk_easy_best
    elif sdk_difficulty == 1:
        best = sdk_med_best
    else:
        best = sdk_hard_best
    if best == elapsed_s:
        draw_text(display, "NEW BEST!", (368 - 9 * 18) // 2, 200, GREEN, 3, CODE_FONT)
    # Standard buttons
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "MENU", 61, 268, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "RETRY", 223, 268, WHITE, 3, CODE_FONT)

def save_sdk_stats():
    save_all_stats()

def draw_sudoku_stats():
    display.fill(BLACK)
    draw_text(display, "SUDOKU STATS", 80, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    if sdk_stats_page == 0:
        for label, best, wins, losses in [("EASY", sdk_easy_best, sdk_easy_wins, sdk_easy_losses),
                                           ("MEDIUM", sdk_med_best, sdk_med_wins, sdk_med_losses)]:
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
        draw_text(display, f"WINS: {sdk_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {sdk_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        if sdk_hard_best > 0:
            bm = sdk_hard_best // 60
            bs = sdk_hard_best % 60
            draw_text(display, f"BEST: {bm:02d}:{bs:02d}", 30, y + 8, GREY, 2, CODE_FONT)
        else:
            draw_text(display, "BEST: --:--", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + i, i * 2 + 1, 2, GREY)

def launch_sudoku():
    global sdk_mode
    sdk_mode = 0
    draw_sdk_difficulty()

def handle_sudoku_touch(tx, ty):
    global sdk_mode, sdk_difficulty, sdk_sel_row, sdk_sel_col
    global sdk_board, sdk_fixed, sdk_timer_start
    global sdk_easy_wins, sdk_easy_best
    global sdk_med_wins, sdk_med_best
    global sdk_hard_wins, sdk_hard_best
    global current_screen, current_app, last_time_text
    if sdk_mode == 0:  # Difficulty select
        if 160 <= ty <= 220 and 34 <= tx <= 334:
            sdk_difficulty = 0
            display.fill(BLACK)
            draw_text(display, "GENERATING...", 56, 200, GREY, 3, CODE_FONT)
            sdk_generate(0)
            sdk_reset()
            draw_sdk_game()
        elif 240 <= ty <= 300 and 34 <= tx <= 334:
            sdk_difficulty = 1
            display.fill(BLACK)
            draw_text(display, "GENERATING...", 56, 200, GREY, 3, CODE_FONT)
            sdk_generate(1)
            sdk_reset()
            draw_sdk_game()
        elif 320 <= ty <= 380 and 34 <= tx <= 334:
            sdk_difficulty = 2
            display.fill(BLACK)
            draw_text(display, "GENERATING...", 56, 200, GREY, 3, CODE_FONT)
            sdk_generate(2)
            sdk_reset()
            draw_sdk_game()
    elif sdk_mode == 1:  # Playing
        if SDK_GRID_Y <= ty < SDK_GRID_Y + 9 * SDK_CELL and SDK_GRID_X <= tx < SDK_GRID_X + 9 * SDK_CELL:
            # Grid tap - select cell
            row = (ty - SDK_GRID_Y) // SDK_CELL
            col = (tx - SDK_GRID_X) // SDK_CELL
            old_row, old_col = sdk_sel_row, sdk_sel_col
            sdk_sel_row = row
            sdk_sel_col = col
            # Redraw affected cells (old selection row/col + new)
            cells_to_redraw = set()
            if old_row >= 0:
                for c in range(9):
                    cells_to_redraw.add((old_row, c))
                for r in range(9):
                    cells_to_redraw.add((r, old_col))
            for c in range(9):
                cells_to_redraw.add((row, c))
            for r in range(9):
                cells_to_redraw.add((r, col))
            for cr, cc in cells_to_redraw:
                draw_sdk_cell(cr, cc)
        elif SDK_PAD_Y <= ty <= SDK_PAD_Y + SDK_PAD_H and SDK_GRID_X <= tx < SDK_GRID_X + 9 * SDK_CELL:
            # Number pad tap
            num = (tx - SDK_GRID_X) // SDK_CELL + 1
            if 1 <= num <= 9 and sdk_sel_row >= 0:
                pos = sdk_sel_row * 9 + sdk_sel_col
                if sdk_fixed[pos] == 0:
                    sdk_board[pos] = num
                    draw_sdk_cell(sdk_sel_row, sdk_sel_col)
                    if sdk_check_win():
                        elapsed_s = time.ticks_diff(time.ticks_ms(), sdk_timer_start) // 1000
                        if sdk_difficulty == 0:
                            sdk_easy_wins += 1
                            if sdk_easy_best == 0 or elapsed_s < sdk_easy_best:
                                sdk_easy_best = elapsed_s
                        elif sdk_difficulty == 1:
                            sdk_med_wins += 1
                            if sdk_med_best == 0 or elapsed_s < sdk_med_best:
                                sdk_med_best = elapsed_s
                        else:
                            sdk_hard_wins += 1
                            if sdk_hard_best == 0 or elapsed_s < sdk_hard_best:
                                sdk_hard_best = elapsed_s
                        save_sdk_stats()
                        sdk_mode = 2
                        draw_sdk_gameover(elapsed_s)
        elif 400 <= ty <= 434 and 134 <= tx <= 234:
            # Erase button
            if sdk_sel_row >= 0:
                pos = sdk_sel_row * 9 + sdk_sel_col
                if sdk_fixed[pos] == 0:
                    sdk_board[pos] = 0
                    draw_sdk_cell(sdk_sel_row, sdk_sel_col)
    elif sdk_mode == 2:  # Won screen
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # MENU
                track_app_exit("SUDOKU")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:  # RETRY
                display.fill(BLACK)
                draw_text(display, "GENERATING...", 56, 200, GREY, 3, CODE_FONT)
                sdk_generate(sdk_difficulty)
                sdk_reset()
                draw_sdk_game()
