# ===== ULTIMATE TIC TAC TOE =====

# Layout constants
TTT_CELL = 30
TTT_CELL_GAP = 2
TTT_SB_SIZE = 94  # 30*3 + 2*2
TTT_SB_GAP = 6
TTT_BIG_SIZE = 294  # 94*3 + 6*2
TTT_BIG_X = 37
TTT_BIG_Y = 90

# Colors - all pieces are green
TTT_PIECE = make_color(0, 60, 0)
TTT_PIECE_DIM = make_color(0, 60, 0)
TTT_ACTIVE_BG = make_color(25, 25, 25)
TTT_WON_BG = make_color(10, 30, 10)
TTT_DRAW_BG = make_color(25, 25, 25)
TTT_GRID = make_color(80, 80, 80)
TTT_GRID_BIG = make_color(120, 120, 120)
TTT_GRID_ACTIVE = make_color(110, 110, 110)

# Win lines (indices within a 9-cell board)
TTT_WIN_LINES = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))

# Game state
ttt_boards = bytearray(81)
ttt_board_winners = bytearray(9)
ttt_mode = 0          # 0=menu, 1=difficulty, 2=playing, 3=game over
ttt_vs_ai = True
ttt_difficulty = 0
ttt_active_board = -1
ttt_current_player = 1
ttt_player_piece = 1
ttt_winner = 0

# Stats
ttt_stats_page = 0
ttt_easy_wins = 0
ttt_easy_losses = 0
ttt_med_wins = 0
ttt_med_losses = 0
ttt_hard_wins = 0
ttt_hard_losses = 0
ttt_pvp_x_wins = 0
ttt_pvp_o_wins = 0
ttt_draws = 0

def ttt_cell_xy(br, bc, cr, cc):
    sx = TTT_BIG_X + bc * (TTT_SB_SIZE + TTT_SB_GAP)
    sy = TTT_BIG_Y + br * (TTT_SB_SIZE + TTT_SB_GAP)
    return sx + cc * (TTT_CELL + TTT_CELL_GAP), sy + cr * (TTT_CELL + TTT_CELL_GAP)

def ttt_touch_to_cell(tx, ty):
    if tx < TTT_BIG_X or tx >= TTT_BIG_X + TTT_BIG_SIZE:
        return None
    if ty < TTT_BIG_Y or ty >= TTT_BIG_Y + TTT_BIG_SIZE:
        return None
    rx = tx - TTT_BIG_X
    ry = ty - TTT_BIG_Y
    bc = rx // (TTT_SB_SIZE + TTT_SB_GAP)
    br = ry // (TTT_SB_SIZE + TTT_SB_GAP)
    if bc > 2:
        bc = 2
    if br > 2:
        br = 2
    lx = rx - bc * (TTT_SB_SIZE + TTT_SB_GAP)
    ly = ry - br * (TTT_SB_SIZE + TTT_SB_GAP)
    if lx >= TTT_SB_SIZE or ly >= TTT_SB_SIZE:
        return None
    cc = lx // (TTT_CELL + TTT_CELL_GAP)
    cr = ly // (TTT_CELL + TTT_CELL_GAP)
    if cc > 2:
        cc = 2
    if cr > 2:
        cr = 2
    return br * 3 + bc, cr * 3 + cc

def ttt_draw_x(px, py, sz, color):
    m = sz // 6
    for i in range(sz - 2 * m):
        display.fill_rect(px + m + i, py + m + i, 3, 3, color)
        display.fill_rect(px + sz - m - i - 3, py + m + i, 3, 3, color)

def ttt_draw_o(px, py, sz, color):
    cx = px + sz // 2
    cy = py + sz // 2
    r = sz // 2 - sz // 6
    display.fill_circle(cx, cy, r, color)
    display.fill_circle(cx, cy, r - 4, BLACK)

def ttt_draw_big_x(sx, sy):
    m = 10
    for i in range(TTT_SB_SIZE - 2 * m):
        display.fill_rect(sx + m + i, sy + m + i, 5, 5, TTT_PIECE)
        display.fill_rect(sx + TTT_SB_SIZE - m - i - 5, sy + m + i, 5, 5, TTT_PIECE)

def ttt_draw_big_o(sx, sy):
    cx = sx + TTT_SB_SIZE // 2
    cy = sy + TTT_SB_SIZE // 2
    r = TTT_SB_SIZE // 2 - 10
    display.fill_circle(cx, cy, r, TTT_PIECE)
    display.fill_circle(cx, cy, r - 8, TTT_WON_BG)

def ttt_check_small_win(bi):
    base = bi * 9
    for a, b, c in TTT_WIN_LINES:
        va = ttt_boards[base + a]
        if va != 0 and va == ttt_boards[base + b] and va == ttt_boards[base + c]:
            return va
    for i in range(9):
        if ttt_boards[base + i] == 0:
            return 0
    return 3

def ttt_check_big_win():
    for a, b, c in TTT_WIN_LINES:
        va = ttt_board_winners[a]
        if va in (1, 2) and va == ttt_board_winners[b] and va == ttt_board_winners[c]:
            return va
    for i in range(9):
        if ttt_board_winners[i] == 0:
            return 0
    return 3

def draw_ttt_small_board(bi):
    br = bi // 3
    bc = bi % 3
    sx = TTT_BIG_X + bc * (TTT_SB_SIZE + TTT_SB_GAP)
    sy = TTT_BIG_Y + br * (TTT_SB_SIZE + TTT_SB_GAP)
    w = ttt_board_winners[bi]
    if w != 0:
        display.fill_rect(sx, sy, TTT_SB_SIZE, TTT_SB_SIZE, TTT_WON_BG if w != 3 else TTT_DRAW_BG)
        if w == 1:
            ttt_draw_big_x(sx, sy)
        elif w == 2:
            ttt_draw_big_o(sx, sy)
    else:
        is_active = ttt_active_board == -1 or ttt_active_board == bi
        bg = TTT_ACTIVE_BG if is_active else BLACK
        gc = TTT_GRID_ACTIVE if is_active else TTT_GRID
        display.fill_rect(sx, sy, TTT_SB_SIZE, TTT_SB_SIZE, bg)
        for i in range(1, 3):
            lx = sx + i * (TTT_CELL + TTT_CELL_GAP) - 1
            display.fill_rect(lx, sy + 2, 2, TTT_SB_SIZE - 4, gc)
            ly = sy + i * (TTT_CELL + TTT_CELL_GAP) - 1
            display.fill_rect(sx + 2, ly, TTT_SB_SIZE - 4, 2, gc)
        base = bi * 9
        for r in range(3):
            for c in range(3):
                v = ttt_boards[base + r * 3 + c]
                if v != 0:
                    px, py = ttt_cell_xy(br, bc, r, c)
                    if v == 1:
                        ttt_draw_x(px, py, TTT_CELL, TTT_PIECE)
                    else:
                        ttt_draw_o(px, py, TTT_CELL, TTT_PIECE)

def draw_ttt_status():
    display.fill_rect(0, 28, 368, 30, BLACK)
    if ttt_mode != 2:
        return
    if ttt_current_player == 1:
        txt = "X TURN"
    else:
        txt = "O TURN"
    if ttt_vs_ai and ttt_current_player == 2:
        txt = "AI THINKING..."
    tw = len(txt) * 12
    draw_text(display, txt, (368 - tw) // 2, 33, GREEN, 2, CODE_FONT)

def draw_ttt_board():
    display.fill(BLACK)
    draw_text(display, "TIC-TAC-TOE", 85, 5, GREY, 3, CODE_FONT)
    draw_ttt_status()
    for i in range(1, 3):
        vx = TTT_BIG_X + i * (TTT_SB_SIZE + TTT_SB_GAP) - TTT_SB_GAP // 2
        display.fill_rect(vx, TTT_BIG_Y, 2, TTT_BIG_SIZE, TTT_GRID_BIG)
        hy = TTT_BIG_Y + i * (TTT_SB_SIZE + TTT_SB_GAP) - TTT_SB_GAP // 2
        display.fill_rect(TTT_BIG_X, hy, TTT_BIG_SIZE, 2, TTT_GRID_BIG)
    for b in range(9):
        draw_ttt_small_board(b)

def ttt_place_move(bi, ci):
    global ttt_current_player, ttt_active_board, ttt_winner, ttt_mode
    ttt_boards[bi * 9 + ci] = ttt_current_player
    result = ttt_check_small_win(bi)
    if result != 0 and ttt_board_winners[bi] == 0:
        ttt_board_winners[bi] = result
        draw_ttt_small_board(bi)
        big = ttt_check_big_win()
        if big != 0:
            ttt_winner = big
            ttt_mode = 3
            return False
    else:
        br = bi // 3
        bc = bi % 3
        cr = ci // 3
        cc = ci % 3
        px, py = ttt_cell_xy(br, bc, cr, cc)
        if ttt_current_player == 1:
            ttt_draw_x(px, py, TTT_CELL, TTT_PIECE)
        else:
            ttt_draw_o(px, py, TTT_CELL, TTT_PIECE)
    nb = ci
    if ttt_board_winners[nb] != 0:
        ttt_active_board = -1
    else:
        ttt_active_board = nb
    for b in range(9):
        if ttt_board_winners[b] == 0:
            draw_ttt_small_board(b)
    ttt_current_player = 3 - ttt_current_player
    draw_ttt_status()
    return True

# ===== AI =====
def ttt_get_valid_moves():
    moves = []
    if ttt_active_board >= 0:
        boards = [ttt_active_board]
    else:
        boards = [b for b in range(9) if ttt_board_winners[b] == 0]
    for b in boards:
        base = b * 9
        for c in range(9):
            if ttt_boards[base + c] == 0:
                moves.append((b, c))
    return moves

def ttt_count_line_threats(piece, bi):
    """Count how many lines piece can still win in board bi"""
    base = bi * 9
    other = 3 - piece
    threats = 0
    for a1, a2, a3 in TTT_WIN_LINES:
        v = [ttt_boards[base + a1], ttt_boards[base + a2], ttt_boards[base + a3]]
        if other not in v:
            if v.count(piece) >= 1:
                threats += 1
    return threats

def ttt_big_line_value(piece, bi):
    """How valuable is winning board bi for big-board lines?"""
    other = 3 - piece
    val = 0
    for a1, a2, a3 in TTT_WIN_LINES:
        if bi not in (a1, a2, a3):
            continue
        vals = [ttt_board_winners[a1], ttt_board_winners[a2], ttt_board_winners[a3]]
        # Replace bi's value with piece (simulating winning it)
        idx = [a1, a2, a3].index(bi)
        vals[idx] = piece
        if vals.count(piece) == 3:
            val += 500  # Wins the game
        elif vals.count(piece) == 2 and vals.count(other) == 0 and vals.count(3) == 0:
            val += 80  # Two in a row on big board
        elif vals.count(piece) == 1 and vals.count(other) == 0 and vals.count(3) == 0:
            val += 15
    return val

def ttt_ai_easy():
    moves = ttt_get_valid_moves()
    if not moves:
        return None
    # 25% chance of making a smart move (win/block)
    if random.randint(0, 3) == 0:
        for b, c in moves:
            ttt_boards[b * 9 + c] = 2
            if ttt_check_small_win(b) == 2:
                ttt_boards[b * 9 + c] = 0
                return (b, c)
            ttt_boards[b * 9 + c] = 0
    return moves[random.randint(0, len(moves) - 1)]

def ttt_ai_medium():
    moves = ttt_get_valid_moves()
    if not moves:
        return None
    ai = 2
    hu = 1
    best = None
    best_sc = -999
    for b, c in moves:
        sc = 0
        base = b * 9
        # Win a small board
        ttt_boards[base + c] = ai
        if ttt_check_small_win(b) == ai:
            sc += 200
            # Check if it wins the game
            old_w = ttt_board_winners[b]
            ttt_board_winners[b] = ai
            if ttt_check_big_win() == ai:
                sc += 5000
            ttt_board_winners[b] = old_w
        ttt_boards[base + c] = 0
        # Block opponent winning a board
        ttt_boards[base + c] = hu
        if ttt_check_small_win(b) == hu:
            sc += 150
            old_w = ttt_board_winners[b]
            ttt_board_winners[b] = hu
            if ttt_check_big_win() == hu:
                sc += 3000
            ttt_board_winners[b] = old_w
        ttt_boards[base + c] = 0
        # Position preference
        if c == 4:
            sc += 8
        elif c in (0, 2, 6, 8):
            sc += 4
        # Prefer center board
        if b == 4:
            sc += 6
        # Where we send opponent
        nb = c
        if ttt_board_winners[nb] != 0:
            sc -= 25  # Gives free choice
        else:
            # Check if opponent can win that board
            nb_base = nb * 9
            for nc in range(9):
                if ttt_boards[nb_base + nc] == 0:
                    ttt_boards[nb_base + nc] = hu
                    if ttt_check_small_win(nb) == hu:
                        ttt_boards[nb_base + nc] = 0
                        sc -= 40
                        break
                    ttt_boards[nb_base + nc] = 0
        sc += random.randint(0, 5)
        if sc > best_sc:
            best_sc = sc
            best = (b, c)
    return best

def ttt_ai_hard():
    moves = ttt_get_valid_moves()
    if not moves:
        return None
    ai = 2
    hu = 1
    best_score = -99999
    best_moves = []
    for b, c in moves:
        score = 0
        base = b * 9
        # === WINNING / BLOCKING ===
        # Win small board?
        ttt_boards[base + c] = ai
        wins_board = ttt_check_small_win(b) == ai
        ttt_boards[base + c] = 0
        if wins_board:
            score += 300
            # Does winning this board win the game?
            old_w = ttt_board_winners[b]
            ttt_board_winners[b] = ai
            if ttt_check_big_win() == ai:
                score += 10000
            else:
                # Value of this board for big-board lines
                score += ttt_big_line_value(ai, b)
            ttt_board_winners[b] = old_w
        # Block opponent winning small board?
        ttt_boards[base + c] = hu
        blocks_board = ttt_check_small_win(b) == hu
        ttt_boards[base + c] = 0
        if blocks_board:
            score += 250
            old_w = ttt_board_winners[b]
            ttt_board_winners[b] = hu
            if ttt_check_big_win() == hu:
                score += 8000  # Must block game loss
            else:
                score += ttt_big_line_value(hu, b)
            ttt_board_winners[b] = old_w
        # === SMALL BOARD TACTICS ===
        # Two-in-a-row setup (threatening to win small board)
        ttt_boards[base + c] = ai
        for a1, a2, a3 in TTT_WIN_LINES:
            v = [ttt_boards[base + a1], ttt_boards[base + a2], ttt_boards[base + a3]]
            if v.count(ai) == 2 and v.count(hu) == 0:
                score += 25
        ttt_boards[base + c] = 0
        # Block opponent two-in-a-row
        ttt_boards[base + c] = hu
        for a1, a2, a3 in TTT_WIN_LINES:
            v = [ttt_boards[base + a1], ttt_boards[base + a2], ttt_boards[base + a3]]
            if v.count(hu) == 2 and v.count(ai) == 0:
                score += 15
        ttt_boards[base + c] = 0
        # Cell position preference
        if c == 4:
            score += 8
        elif c in (0, 2, 6, 8):
            score += 4
        else:
            score += 1
        # Board strategic value (center board most valuable)
        if b == 4:
            score += 10
        elif b in (0, 2, 6, 8):
            score += 5
        # === WHERE WE SEND OPPONENT ===
        nb = c
        if ttt_board_winners[nb] != 0:
            score -= 60  # Gives free choice - very bad
        else:
            # Can opponent win that board immediately?
            opp_can_win = False
            nb_base = nb * 9
            for nc in range(9):
                if ttt_boards[nb_base + nc] == 0:
                    ttt_boards[nb_base + nc] = hu
                    if ttt_check_small_win(nb) == hu:
                        opp_can_win = True
                    ttt_boards[nb_base + nc] = 0
                    if opp_can_win:
                        break
            if opp_can_win:
                # How bad is opponent winning that board?
                old_w = ttt_board_winners[nb]
                ttt_board_winners[nb] = hu
                if ttt_check_big_win() == hu:
                    score -= 5000  # Sending to game-losing board
                else:
                    bv = ttt_big_line_value(hu, nb)
                    score -= 80 - min(bv, 200)
                ttt_board_winners[nb] = old_w
            else:
                # Prefer sending to board where opponent is weak
                hu_threats = ttt_count_line_threats(hu, nb)
                ai_threats = ttt_count_line_threats(ai, nb)
                if ai_threats > hu_threats:
                    score += 15  # We're stronger there
                elif hu_threats > ai_threats:
                    score -= 10
            # Can AI win that board? (sending opponent to our strong board is fine)
            ai_can_win = False
            for nc in range(9):
                if ttt_boards[nb_base + nc] == 0:
                    ttt_boards[nb_base + nc] = ai
                    if ttt_check_small_win(nb) == ai:
                        ai_can_win = True
                    ttt_boards[nb_base + nc] = 0
                    if ai_can_win:
                        break
            if ai_can_win:
                score -= 20  # Sending to board we could win ourselves
        # === BIG BOARD STRATEGY ===
        if wins_board:
            # Check if winning creates a fork (2+ ways to win big board)
            old_w = ttt_board_winners[b]
            ttt_board_winners[b] = ai
            win_threats = 0
            for a1, a2, a3 in TTT_WIN_LINES:
                vals = [ttt_board_winners[a1], ttt_board_winners[a2], ttt_board_winners[a3]]
                if vals.count(ai) == 2 and vals.count(hu) == 0 and vals.count(3) == 0:
                    win_threats += 1
            if win_threats >= 2:
                score += 400  # Fork on big board
            ttt_board_winners[b] = old_w
        score += random.randint(0, 3)
        if score > best_score:
            best_score = score
            best_moves = [(b, c)]
        elif score == best_score:
            best_moves.append((b, c))
    return best_moves[random.randint(0, len(best_moves) - 1)]

def ttt_ai_move():
    if ttt_difficulty == 0:
        move = ttt_ai_easy()
    elif ttt_difficulty == 1:
        move = ttt_ai_medium()
    else:
        move = ttt_ai_hard()
    if move:
        ttt_place_move(move[0], move[1])

# ===== MENU / GAME OVER / STATS =====
def draw_ttt_menu():
    display.fill(BLACK)
    draw_text(display, "TIC-TAC-TOE", 52, 30, GREY, 4, CODE_FONT)
    display.fill_rect(34, 150, 300, 70, GREEN)
    draw_text(display, "PLAYER VS PLAYER", 88, 175, WHITE, 2, CODE_FONT)
    display.fill_rect(34, 250, 300, 70, GREEN)
    draw_text(display, "PLAYER VS AI", 112, 275, WHITE, 2, CODE_FONT)

def draw_ttt_difficulty():
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 338, WHITE, 3, CODE_FONT)

def init_ttt_game():
    global ttt_boards, ttt_board_winners, ttt_active_board
    global ttt_current_player, ttt_winner, ttt_mode
    ttt_boards = bytearray(81)
    ttt_board_winners = bytearray(9)
    ttt_active_board = -1
    ttt_current_player = 1
    ttt_winner = 0
    ttt_mode = 2

def draw_ttt_gameover():
    global ttt_mode
    ttt_mode = 3
    display.fill(BLACK)
    if ttt_winner == 3:
        title = "DRAW!"
    elif ttt_vs_ai:
        if ttt_winner == ttt_player_piece:
            title = "YOU WIN!"
        else:
            title = "AI WINS!"
    else:
        title = "X WINS!" if ttt_winner == 1 else "O WINS!"
    tw = len(title) * 30
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    if ttt_vs_ai:
        dn = ["EASY", "MED", "HARD"]
        info = "PLAYER VS AI (" + dn[ttt_difficulty] + ")"
    else:
        info = "PLAYER VS PLAYER"
    iw = len(info) * 18
    draw_text(display, info, (368 - iw) // 2, 160, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    t = "PLAY AGAIN"
    bw = len(t) * 12
    draw_text(display, t, 25 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    t = "EXIT"
    bw = len(t) * 12
    draw_text(display, t, 193 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)

def ttt_update_stats():
    global ttt_easy_wins, ttt_easy_losses, ttt_med_wins, ttt_med_losses
    global ttt_hard_wins, ttt_hard_losses, ttt_pvp_x_wins, ttt_pvp_o_wins, ttt_draws
    if ttt_winner == 3:
        ttt_draws += 1
        return
    if ttt_vs_ai:
        won = ttt_winner == ttt_player_piece
        if ttt_difficulty == 0:
            if won:
                ttt_easy_wins += 1
            else:
                ttt_easy_losses += 1
        elif ttt_difficulty == 1:
            if won:
                ttt_med_wins += 1
            else:
                ttt_med_losses += 1
        else:
            if won:
                ttt_hard_wins += 1
            else:
                ttt_hard_losses += 1
    else:
        if ttt_winner == 1:
            ttt_pvp_x_wins += 1
        else:
            ttt_pvp_o_wins += 1

def draw_ttt_stats():
    display.fill(BLACK)
    draw_text(display, "TIC-TAC-TOE", 85, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    if ttt_stats_page == 0:
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (EASY)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {ttt_easy_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {ttt_easy_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (MED)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {ttt_med_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {ttt_med_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (HARD)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {ttt_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {ttt_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        # Down arrow
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + 12 - i, i * 2 + 1, 2, GREY)
    else:
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"X WINS: {ttt_pvp_x_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"O WINS: {ttt_pvp_o_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"DRAWS: {ttt_draws}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        # Up arrow
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + i, i * 2 + 1, 2, GREY)

def launch_tictactoe():
    global ttt_mode
    ttt_mode = 0
    draw_ttt_menu()

def handle_tictactoe_touch(tx, ty):
    global ttt_mode, ttt_vs_ai, ttt_difficulty
    global current_screen, current_app, last_time_text
    if ttt_mode == 0:
        if 150 <= ty <= 220 and 34 <= tx <= 334:
            ttt_vs_ai = False
            init_ttt_game()
            draw_ttt_board()
        elif 250 <= ty <= 320 and 34 <= tx <= 334:
            ttt_vs_ai = True
            ttt_mode = 1
            draw_ttt_difficulty()
    elif ttt_mode == 1:
        if 34 <= tx <= 334:
            if 160 <= ty <= 220:
                ttt_difficulty = 0
            elif 240 <= ty <= 300:
                ttt_difficulty = 1
            elif 320 <= ty <= 380:
                ttt_difficulty = 2
            else:
                return
            init_ttt_game()
            draw_ttt_board()
    elif ttt_mode == 2:
        if ttt_vs_ai and ttt_current_player == 2:
            return
        result = ttt_touch_to_cell(tx, ty)
        if result is None:
            return
        bi, ci = result
        if ttt_board_winners[bi] != 0:
            return
        if ttt_boards[bi * 9 + ci] != 0:
            return
        if ttt_active_board >= 0 and ttt_active_board != bi:
            return
        cont = ttt_place_move(bi, ci)
        if not cont:
            ttt_update_stats()
            save_all_stats()
            time.sleep_ms(800)
            draw_ttt_gameover()
            return
        if ttt_vs_ai and ttt_current_player == 2:
            time.sleep_ms(300)
            ttt_ai_move()
            if ttt_mode == 3:
                ttt_update_stats()
                save_all_stats()
                time.sleep_ms(800)
                draw_ttt_gameover()
    elif ttt_mode == 3:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:
                ttt_mode = 0
                draw_ttt_menu()
            elif 193 <= tx <= 343:
                track_app_exit("TIC-TAC-TOE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
