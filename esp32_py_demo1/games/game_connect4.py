# ===== CONNECT FOUR GAME =====
# Board: 7 columns x 6 rows, cell size 46px
C4_COLS = 7
C4_ROWS = 6
C4_CELL = 46
C4_BOARD_W = C4_COLS * C4_CELL  # 322
C4_BOARD_X = (368 - C4_BOARD_W) // 2  # 23
C4_BOARD_Y = 110
C4_RADIUS = 19

# Colors
C4_P1_COLOR = GREEN
C4_P2_COLOR = GREY
C4_WIN_COLOR = make_color(0, 60, 0)  # Dark green highlight for winning pieces

# Game state
c4_mode = 0  # 0=menu, 1=difficulty, 2=playing, 3=game over
c4_vs_ai = False
c4_difficulty = 0  # 0=easy, 1=medium, 2=hard
c4_turn = 1  # 1=P1 (green), 2=P2/AI (grey)
c4_winner = 0  # 0=none/draw, 1=P1, 2=P2
c4_board = bytearray(C4_ROWS * C4_COLS)  # 0=empty, 1=P1, 2=P2
c4_win_cells = []  # List of (row, col) for winning 4
c4_ai_thinking = False

def c4_reset():
    global c4_board, c4_turn, c4_winner, c4_win_cells, c4_ai_thinking
    c4_board = bytearray(C4_ROWS * C4_COLS)
    c4_turn = 1
    c4_winner = 0
    c4_win_cells = []
    c4_ai_thinking = False

def c4_get(r, c):
    return c4_board[r * C4_COLS + c]

def c4_set(r, c, val):
    c4_board[r * C4_COLS + c] = val

def c4_drop(col, player):
    """Drop piece in column. Returns row placed or -1 if full."""
    for r in range(C4_ROWS - 1, -1, -1):
        if c4_get(r, col) == 0:
            c4_set(r, col, player)
            return r
    return -1

def c4_undrop(col):
    """Remove top piece from column (for minimax)."""
    for r in range(C4_ROWS):
        if c4_get(r, col) != 0:
            c4_set(r, col, 0)
            return

def c4_valid_cols():
    """Return list of columns that aren't full."""
    return [c for c in range(C4_COLS) if c4_get(0, c) == 0]

def c4_check_win(player):
    """Check if player has 4 in a row. Returns winning cells or None."""
    # Horizontal
    for r in range(C4_ROWS):
        for c in range(C4_COLS - 3):
            if all(c4_get(r, c + i) == player for i in range(4)):
                return [(r, c + i) for i in range(4)]
    # Vertical
    for r in range(C4_ROWS - 3):
        for c in range(C4_COLS):
            if all(c4_get(r + i, c) == player for i in range(4)):
                return [(r + i, c) for i in range(4)]
    # Diagonal down-right
    for r in range(C4_ROWS - 3):
        for c in range(C4_COLS - 3):
            if all(c4_get(r + i, c + i) == player for i in range(4)):
                return [(r + i, c + i) for i in range(4)]
    # Diagonal down-left
    for r in range(C4_ROWS - 3):
        for c in range(3, C4_COLS):
            if all(c4_get(r + i, c - i) == player for i in range(4)):
                return [(r + i, c - i) for i in range(4)]
    return None

def c4_is_full():
    return len(c4_valid_cols()) == 0

# ===== AI =====
# Center-out column ordering for better alpha-beta pruning
C4_COL_ORDER = [3, 2, 4, 1, 5, 0, 6]

def c4_playable_row(col):
    """Return the row a piece would land in, or -1 if full."""
    for r in range(C4_ROWS - 1, -1, -1):
        if c4_get(r, col) == 0:
            return r
    return -1

def c4_win_or_block(me, opp):
    """Check if me can win, or if opp has a threat to block. Returns col or -1."""
    cols = c4_valid_cols()
    # Win immediately
    for c in cols:
        c4_drop(c, me)
        if c4_check_win(me):
            c4_undrop(c)
            return c
        c4_undrop(c)
    # Block opponent win
    for c in cols:
        c4_drop(c, opp)
        if c4_check_win(opp):
            c4_undrop(c)
            return c
        c4_undrop(c)
    return -1

def c4_safe_cols(me, opp):
    """Return cols that don't give opponent an immediate win above."""
    cols = c4_valid_cols()
    safe = []
    for c in cols:
        r = c4_playable_row(c)
        if r < 0:
            continue
        # Simulate our move, then check if opponent wins by playing on top
        c4_set(r, c, me)
        r2 = c4_playable_row(c)
        gives_win = False
        if r2 >= 0:
            c4_set(r2, c, opp)
            if c4_check_win(opp):
                gives_win = True
            c4_set(r2, c, 0)
        c4_set(r, c, 0)
        if not gives_win:
            safe.append(c)
    return safe if safe else cols  # If all moves lose, return all

def c4_ai_easy():
    """Random but always blocks immediate wins."""
    c = c4_win_or_block(2, 1)
    if c >= 0:
        return c
    cols = c4_valid_cols()
    return cols[random.randint(0, len(cols) - 1)]

def c4_ai_medium():
    """Minimax AI, depth 2 - thinks ahead but not as deep as hard."""
    c = c4_win_or_block(2, 1)
    if c >= 0:
        return c
    safe = c4_safe_cols(2, 1)
    if len(safe) == 1:
        return safe[0]
    best_col = safe[0] if safe else C4_COL_ORDER[0]
    best_score = -999999
    ordered = [c for c in C4_COL_ORDER if c in safe]
    for c in ordered:
        c4_drop(c, 2)
        _, score = c4_minimax(1, -999999, 999999, False)
        c4_undrop(c)
        if score > best_score:
            best_score = score
            best_col = c
    return best_col

def c4_eval_window(me, opp, emp):
    """Score a window of 4 cells."""
    if me == 4:
        return 1000
    if opp == 4:
        return -1000
    if me == 3 and emp == 1:
        return 50
    if opp == 3 and emp == 1:
        return -70  # Slightly higher weight on defense
    if me == 2 and emp == 2:
        return 10
    if opp == 2 and emp == 2:
        return -12
    return 0

def c4_evaluate():
    """Evaluate board for player 2 (AI)."""
    score = 0
    # Center column preference (columns closer to center worth more)
    for r in range(C4_ROWS):
        for c in range(C4_COLS):
            v = c4_get(r, c)
            if v == 0:
                continue
            # Center bonus: col 3 = +3, cols 2,4 = +2, cols 1,5 = +1
            cb = max(0, 3 - abs(c - 3))
            if v == 2:
                score += cb
            else:
                score -= cb
    # Score all windows of 4 (horizontal, vertical, both diagonals)
    for r in range(C4_ROWS):
        for c in range(C4_COLS - 3):
            me = opp = emp = 0
            for i in range(4):
                v = c4_get(r, c + i)
                if v == 2: me += 1
                elif v == 1: opp += 1
                else: emp += 1
            score += c4_eval_window(me, opp, emp)
    for r in range(C4_ROWS - 3):
        for c in range(C4_COLS):
            me = opp = emp = 0
            for i in range(4):
                v = c4_get(r + i, c)
                if v == 2: me += 1
                elif v == 1: opp += 1
                else: emp += 1
            score += c4_eval_window(me, opp, emp)
    for r in range(C4_ROWS - 3):
        for c in range(C4_COLS - 3):
            me = opp = emp = 0
            for i in range(4):
                v = c4_get(r + i, c + i)
                if v == 2: me += 1
                elif v == 1: opp += 1
                else: emp += 1
            score += c4_eval_window(me, opp, emp)
    for r in range(C4_ROWS - 3):
        for c in range(3, C4_COLS):
            me = opp = emp = 0
            for i in range(4):
                v = c4_get(r + i, c - i)
                if v == 2: me += 1
                elif v == 1: opp += 1
                else: emp += 1
            score += c4_eval_window(me, opp, emp)
    return score

def c4_minimax(depth, alpha, beta, maximizing):
    """Minimax with alpha-beta pruning. AI is player 2 (maximizing)."""
    # Check terminal states
    w2 = c4_check_win(2)
    if w2:
        return None, 50000 + depth
    w1 = c4_check_win(1)
    if w1:
        return None, -50000 - depth
    cols = c4_valid_cols()
    if not cols or depth == 0:
        return None, c4_evaluate()
    # Center-out ordering for better pruning
    ordered = [c for c in C4_COL_ORDER if c in cols]
    if maximizing:
        best_score = -999999
        best_col = ordered[0]
        for c in ordered:
            c4_drop(c, 2)
            _, score = c4_minimax(depth - 1, alpha, beta, False)
            c4_undrop(c)
            if score > best_score:
                best_score = score
                best_col = c
            if score > alpha:
                alpha = score
            if alpha >= beta:
                break
        return best_col, best_score
    else:
        best_score = 999999
        best_col = ordered[0]
        for c in ordered:
            c4_drop(c, 1)
            _, score = c4_minimax(depth - 1, alpha, beta, True)
            c4_undrop(c)
            if score < best_score:
                best_score = score
                best_col = c
            if score < beta:
                beta = score
            if alpha >= beta:
                break
        return best_col, best_score

def c4_ai_hard():
    """Minimax AI, depth 4 with safety checks."""
    # Immediate win/block
    c = c4_win_or_block(2, 1)
    if c >= 0:
        return c
    # Filter out moves that give opponent a win on top
    safe = c4_safe_cols(2, 1)
    if len(safe) == 1:
        return safe[0]
    # Only search safe columns to save time
    best_col = safe[0] if safe else C4_COL_ORDER[0]
    best_score = -999999
    ordered = [c for c in C4_COL_ORDER if c in safe]
    for c in ordered:
        c4_drop(c, 2)
        _, score = c4_minimax(3, -999999, 999999, False)
        c4_undrop(c)
        if score > best_score:
            best_score = score
            best_col = c
    return best_col

# ===== DRAWING =====
def draw_c4_menu():
    display.fill(BLACK)
    draw_text(display, "CONNECT FOUR", 40, 30, GREY, 4, CODE_FONT)
    # PvP button
    display.fill_rect(34, 150, 300, 70, GREEN)
    draw_text(display, "PLAYER VS PLAYER", 88, 172, WHITE, 2, CODE_FONT)
    # vs AI button
    display.fill_rect(34, 250, 300, 70, GREEN)
    draw_text(display, "PLAYER VS AI", 112, 272, WHITE, 2, CODE_FONT)

def draw_c4_difficulty():
    display.fill(BLACK)
    draw_text(display, "CONNECT FOUR", 40, 30, GREY, 4, CODE_FONT)
    # Easy
    display.fill_rect(34, 140, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 158, WHITE, 3, CODE_FONT)
    # Medium
    display.fill_rect(34, 220, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 238, WHITE, 3, CODE_FONT)
    # Hard
    display.fill_rect(34, 300, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 318, WHITE, 3, CODE_FONT)

def c4_draw_piece(r, c, player, highlight=False):
    """Draw a single piece at board position (r,c)."""
    cx = C4_BOARD_X + c * C4_CELL + C4_CELL // 2
    cy = C4_BOARD_Y + r * C4_CELL + C4_CELL // 2
    if highlight:
        color = C4_WIN_COLOR
    elif player == 1:
        color = C4_P1_COLOR
    elif player == 2:
        color = C4_P2_COLOR
    else:
        color = BLACK
    display.fill_circle(cx, cy, C4_RADIUS, color)

def draw_c4_board():
    """Draw the full game board."""
    display.fill(BLACK)
    # Status text at top
    c4_draw_status()
    # Board background
    display.fill_rect(C4_BOARD_X, C4_BOARD_Y, C4_BOARD_W, C4_ROWS * C4_CELL, DARK_GREY)
    # Draw all cells
    for r in range(C4_ROWS):
        for c in range(C4_COLS):
            val = c4_get(r, c)
            is_win = (r, c) in c4_win_cells if c4_win_cells else False
            c4_draw_piece(r, c, val, is_win)

def c4_draw_status():
    """Draw turn/status text at top of screen."""
    # Clear status area
    display.fill_rect(0, 0, 368, C4_BOARD_Y - 5, BLACK)
    if c4_mode == 3:
        return
    if c4_ai_thinking:
        txt = "AI THINKING..."
    elif c4_vs_ai:
        txt = "YOUR TURN" if c4_turn == 1 else "AI TURN"
    else:
        txt = f"P{c4_turn} TURN"
    tc = C4_P1_COLOR if c4_turn == 1 else C4_P2_COLOR
    tw = len(txt) * 6 * 3
    draw_text(display, txt, (368 - tw) // 2, 30, tc, 3, CODE_FONT)

def c4_draw_col_indicators():
    """Draw small arrows/markers above each column for current turn."""
    if c4_mode != 2:
        return
    y = C4_BOARD_Y - 12
    color = C4_P1_COLOR if c4_turn == 1 else C4_P2_COLOR
    for c in range(C4_COLS):
        if c4_get(0, c) == 0:  # Column not full
            cx = C4_BOARD_X + c * C4_CELL + C4_CELL // 2
            # Small down-pointing triangle
            for i in range(6):
                display.fill_rect(cx - i, y - i, i * 2 + 1, 1, color)

def draw_c4_gameover():
    """Draw game over screen."""
    display.fill(BLACK)
    if c4_winner == 0:
        title = "DRAW!"
    elif c4_vs_ai:
        title = "YOU WIN!" if c4_winner == 1 else "AI WINS!"
    else:
        title = f"P{c4_winner} WINS!"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    # Play Again button
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    # Exit button
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def c4_do_move(col):
    """Execute a move: drop piece, check win/draw, switch turn or end game."""
    global c4_turn, c4_winner, c4_win_cells, c4_mode
    player = c4_turn
    row = c4_drop(col, player)
    if row < 0:
        return  # Column full
    # Draw the placed piece
    c4_draw_piece(row, col, player)
    # Check win
    win = c4_check_win(player)
    if win:
        c4_winner = player
        c4_win_cells = win
        c4_mode = 3
        # Highlight winning pieces
        for wr, wc in win:
            c4_draw_piece(wr, wc, player, True)
        # Update stats
        c4_update_stats()
        time.sleep_ms(1500)
        draw_c4_gameover()
        return
    # Check draw
    if c4_is_full():
        c4_winner = 0
        c4_mode = 3
        c4_update_stats()
        time.sleep_ms(800)
        draw_c4_gameover()
        return
    # Switch turn
    c4_turn = 2 if c4_turn == 1 else 1
    c4_draw_status()

def c4_update_stats():
    """Update stats based on game result."""
    global c4_easy_wins, c4_easy_losses, c4_med_wins, c4_med_losses
    global c4_hard_wins, c4_hard_losses, c4_p1_wins, c4_p2_wins, c4_draws
    if c4_winner == 0:
        c4_draws += 1
    elif c4_vs_ai:
        if c4_winner == 1:  # Player wins
            if c4_difficulty == 0:
                c4_easy_wins += 1
            elif c4_difficulty == 1:
                c4_med_wins += 1
            else:
                c4_hard_wins += 1
        else:  # AI wins
            if c4_difficulty == 0:
                c4_easy_losses += 1
            elif c4_difficulty == 1:
                c4_med_losses += 1
            else:
                c4_hard_losses += 1
    else:
        if c4_winner == 1:
            c4_p1_wins += 1
        else:
            c4_p2_wins += 1
    save_c4_stats()

def c4_ai_move():
    """Execute AI move."""
    global c4_ai_thinking
    c4_ai_thinking = True
    c4_draw_status()
    if c4_difficulty == 0:
        col = c4_ai_easy()
    elif c4_difficulty == 1:
        col = c4_ai_medium()
    else:
        col = c4_ai_hard()
    c4_ai_thinking = False
    c4_do_move(col)

# ===== MAIN INTERFACE =====
def launch_connect4():
    global c4_mode
    c4_mode = 0
    draw_c4_menu()

def handle_connect4_touch(tx, ty):
    global c4_mode, c4_vs_ai, c4_difficulty
    global current_screen, current_app, last_time_text

    if c4_mode == 0:  # Menu
        if 150 <= ty <= 220:  # PvP
            c4_vs_ai = False
            c4_reset()
            c4_mode = 2
            draw_c4_board()
        elif 250 <= ty <= 320:  # vs AI
            c4_vs_ai = True
            c4_mode = 1
            draw_c4_difficulty()

    elif c4_mode == 1:  # Difficulty select
        if 140 <= ty <= 200:
            c4_difficulty = 0
        elif 220 <= ty <= 280:
            c4_difficulty = 1
        elif 300 <= ty <= 360:
            c4_difficulty = 2
        else:
            return
        c4_reset()
        c4_mode = 2
        draw_c4_board()

    elif c4_mode == 2:  # Playing
        # Only allow human moves
        if c4_vs_ai and c4_turn == 2:
            return
        # Determine which column was tapped
        if C4_BOARD_X <= tx <= C4_BOARD_X + C4_BOARD_W:
            col = (tx - C4_BOARD_X) // C4_CELL
            if col < 0:
                col = 0
            if col >= C4_COLS:
                col = C4_COLS - 1
            if c4_get(0, col) != 0:
                return  # Column full
            c4_do_move(col)
            # If vs AI and game not over, do AI move
            if c4_vs_ai and c4_mode == 2:
                c4_ai_move()

    elif c4_mode == 3:  # Game over
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                c4_mode = 0
                draw_c4_menu()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("CONNECT FOUR")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""

def draw_c4_stats():
    display.fill(BLACK)
    draw_text(display, "CONNECT FOUR", 18, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32

    # EASY section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (EASY)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {c4_easy_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {c4_easy_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # MEDIUM section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (MED)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {c4_med_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {c4_med_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # HARD section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (HARD)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {c4_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {c4_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # PvP section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P1 WINS: {c4_p1_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P2 WINS: {c4_p2_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"DRAWS: {c4_draws}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
