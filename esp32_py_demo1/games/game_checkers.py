# ===== CHECKERS GAME =====
CHK_SZ = 40  # Cell size
CHK_X = 24   # Board left offset (368 - 320) / 2
CHK_Y = 70   # Board top offset
CHK_LIGHT = DARK_GREY
CHK_DARK = make_color(20, 20, 20)
CHK_SEL_G = make_color(100, 200, 50)  # Selected GREEN piece border
CHK_SEL_R = make_color(120, 120, 120)  # Selected GREY piece border
CHK_DOT_G = make_color(0, 180, 0)     # Valid move dot for GREEN
CHK_DOT_R = make_color(80, 80, 80)    # Valid move dot for GREY

# Board encoding: 0=empty, 1=P1 man, 2=P1 king, -1=P2 man, -2=P2 king
# Only dark squares used (where (r+c)%2==1)

chk_mode = 0  # 0=menu, 1=difficulty, 2=playing, 3=game over
chk_vs_ai = False
chk_difficulty = 0
chk_turn = 1  # 1=P1(bottom/GREEN), -1=P2(top/GREY)
chk_board = None
chk_sel = None  # (r, c) selected piece
chk_valid = []  # Valid destination squares [(r,c), ...]
chk_must_jump = False  # True if current selection is mid-multi-jump
chk_winner = 0  # 1=P1, -1=P2
chk_moves = 0  # Move counter

# Stats (defined here but also need to be in main.py globals)
chk_easy_wins = 0
chk_easy_losses = 0
chk_med_wins = 0
chk_med_losses = 0
chk_hard_wins = 0
chk_hard_losses = 0
chk_p1_wins = 0
chk_p2_wins = 0

def chk_init():
    global chk_board, chk_sel, chk_valid, chk_turn, chk_must_jump, chk_moves
    # 8x8 board, only dark squares (r+c odd) have pieces
    chk_board = []
    for r in range(8):
        row = []
        for c in range(8):
            if (r + c) % 2 == 1:
                if r < 3:
                    row.append(-1)  # P2 pieces (top)
                elif r > 4:
                    row.append(1)   # P1 pieces (bottom)
                else:
                    row.append(0)
            else:
                row.append(0)
        chk_board.append(row)
    chk_sel = None
    chk_valid = []
    chk_turn = 1
    chk_must_jump = False
    chk_moves = 0

def chk_get_jumps(r, c):
    """Get jump moves for piece at (r,c). Returns list of (dr, dc, mr, mc) = dest + captured."""
    b = chk_board
    p = b[r][c]
    if p == 0:
        return []
    side = 1 if p > 0 else -1
    is_king = abs(p) == 2
    jumps = []
    # Directions: P1 moves up (-1), P2 moves down (+1), kings both
    dirs = []
    if side == 1 or is_king:
        dirs.extend([(-1, -1), (-1, 1)])
    if side == -1 or is_king:
        dirs.extend([(1, -1), (1, 1)])
    for dr, dc in dirs:
        mr, mc = r + dr, c + dc  # Middle (captured) square
        nr, nc = r + 2*dr, c + 2*dc  # Destination
        if 0 <= nr < 8 and 0 <= nc < 8:
            mid = b[mr][mc]
            if mid != 0 and (1 if mid > 0 else -1) != side and b[nr][nc] == 0:
                jumps.append((nr, nc, mr, mc))
    return jumps

def chk_get_moves(r, c):
    """Get simple (non-jump) moves for piece at (r,c). Returns list of (dr, dc)."""
    b = chk_board
    p = b[r][c]
    if p == 0:
        return []
    side = 1 if p > 0 else -1
    is_king = abs(p) == 2
    moves = []
    dirs = []
    if side == 1 or is_king:
        dirs.extend([(-1, -1), (-1, 1)])
    if side == -1 or is_king:
        dirs.extend([(1, -1), (1, 1)])
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and b[nr][nc] == 0:
            moves.append((nr, nc))
    return moves

def chk_any_jumps(side):
    """Check if any piece of given side has a jump available."""
    for r in range(8):
        for c in range(8):
            p = chk_board[r][c]
            if p != 0 and (1 if p > 0 else -1) == side:
                if chk_get_jumps(r, c):
                    return True
    return False

def chk_all_moves(side):
    """Get all valid moves for a side. Returns list of (fr, fc, tr, tc, is_jump, cap_r, cap_c)."""
    has_jumps = chk_any_jumps(side)
    moves = []
    for r in range(8):
        for c in range(8):
            p = chk_board[r][c]
            if p != 0 and (1 if p > 0 else -1) == side:
                if has_jumps:
                    for nr, nc, mr, mc in chk_get_jumps(r, c):
                        moves.append((r, c, nr, nc, True, mr, mc))
                else:
                    for nr, nc in chk_get_moves(r, c):
                        moves.append((r, c, nr, nc, False, -1, -1))
    return moves

def chk_do_move(r, c, nr, nc, cap_r, cap_c):
    """Execute a move. Returns True if piece was promoted to king."""
    global chk_board
    p = chk_board[r][c]
    chk_board[r][c] = 0
    if cap_r >= 0:
        chk_board[cap_r][cap_c] = 0
    # King promotion
    promoted = False
    side = 1 if p > 0 else -1
    if abs(p) == 1:
        if (side == 1 and nr == 0) or (side == -1 and nr == 7):
            p = side * 2
            promoted = True
    chk_board[nr][nc] = p
    return promoted

def chk_count(side):
    """Count pieces for a side."""
    n = 0
    for r in range(8):
        for c in range(8):
            p = chk_board[r][c]
            if p != 0 and (1 if p > 0 else -1) == side:
                n += 1
    return n

def chk_check_winner():
    """Check if game is over. Returns winner side or 0."""
    if chk_count(1) == 0 or not chk_all_moves(1):
        return -1
    if chk_count(-1) == 0 or not chk_all_moves(-1):
        return 1
    return 0

# ===== DRAWING =====
def draw_chk_board():
    """Draw the full board and pieces."""
    display.fill(BLACK)
    # Status bar - centered turn indicator only
    if chk_vs_ai:
        if chk_turn == 1:
            txt = "YOUR TURN"
        else:
            txt = "AI THINKING"
    else:
        txt = "P1 TURN" if chk_turn == 1 else "P2 TURN"
    tc = GREEN if chk_turn == 1 else GREY
    tw = len(txt) * 6 * 2
    draw_text(display, txt, (368 - tw) // 2, 5, tc, 2, CODE_FONT)
    # Board squares
    for r in range(8):
        for c in range(8):
            x = CHK_X + c * CHK_SZ
            y = CHK_Y + r * CHK_SZ
            color = CHK_LIGHT if (r + c) % 2 == 0 else CHK_DARK
            display.fill_rect(x, y, CHK_SZ, CHK_SZ, color)
    # Valid move dots - color matches current turn
    dot_c = CHK_DOT_G if chk_turn == 1 else CHK_DOT_R
    for vr, vc in chk_valid:
        cx = CHK_X + vc * CHK_SZ + CHK_SZ // 2
        cy = CHK_Y + vr * CHK_SZ + CHK_SZ // 2
        display.fill_circle(cx, cy, 6, dot_c)
    # Pieces
    sel_c = CHK_SEL_G if chk_turn == 1 else CHK_SEL_R
    for r in range(8):
        for c in range(8):
            p = chk_board[r][c]
            if p != 0:
                cx = CHK_X + c * CHK_SZ + CHK_SZ // 2
                cy = CHK_Y + r * CHK_SZ + CHK_SZ // 2
                # Selection highlight - color matches piece
                if chk_sel and chk_sel[0] == r and chk_sel[1] == c:
                    display.fill_circle(cx, cy, 18, sel_c)
                # Piece color
                pc = GREEN if p > 0 else GREY
                display.fill_circle(cx, cy, 15, pc)
                # King marker - inner circle
                if abs(p) == 2:
                    display.fill_circle(cx, cy, 7, BLACK)
                    display.fill_circle(cx, cy, 5, pc)

def draw_chk_menu():
    """Draw mode selection menu."""
    display.fill(BLACK)
    # Title: "CHECKERS" = 8 chars * 6 * 4 = 192, center = (368-192)/2 = 88
    draw_text(display, "CHECKERS", 88, 30, GREY, 4, CODE_FONT)
    # PvP button
    display.fill_rect(34, 150, 300, 70, GREEN)
    txt = "PLAYER VS PLAYER"
    tw = len(txt) * 6 * 2
    draw_text(display, txt, 34 + (300 - tw) // 2, 172, WHITE, 2, CODE_FONT)
    # AI button
    display.fill_rect(34, 250, 300, 70, GREEN)
    txt = "PLAYER VS AI"
    tw = len(txt) * 6 * 2
    draw_text(display, txt, 34 + (300 - tw) // 2, 272, WHITE, 2, CODE_FONT)

def draw_chk_difficulty():
    """Draw difficulty selection screen."""
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 140, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 158, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 220, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 238, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 300, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 318, WHITE, 3, CODE_FONT)

def draw_chk_gameover():
    """Draw game over screen."""
    display.fill(BLACK)
    if chk_vs_ai:
        title = "YOU WIN!" if chk_winner == 1 else "AI WINS!"
    else:
        title = f"P{1 if chk_winner == 1 else 2} WINS!"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    # Info line
    info = f"P1:{chk_count(1)} P2:{chk_count(-1)} MOVES:{chk_moves}"
    iw = len(info) * 6 * 2
    draw_text(display, info, (368 - iw) // 2, 160, GREY, 2, CODE_FONT)
    # Buttons
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    txt = "PLAY AGAIN"
    tw = len(txt) * 6 * 2
    draw_text(display, txt, 25 + (150 - tw) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    txt = "EXIT"
    tw = len(txt) * 6 * 2
    draw_text(display, txt, 193 + (150 - tw) // 2, 273, WHITE, 2, CODE_FONT)

# ===== AI =====
def chk_eval(board, side):
    """Evaluate board position for the given side. Better heuristics."""
    score = 0
    my_count = 0
    opp_count = 0
    for r in range(8):
        for c in range(8):
            p = board[r][c]
            if p == 0:
                continue
            ps = 1 if p > 0 else -1
            is_king = abs(p) == 2
            # Base value: men=100, kings=150 (1.5x)
            val = 150 if is_king else 100
            # Center control (2x2 center = best, 4x4 inner = good)
            if 3 <= c <= 4 and 3 <= r <= 4:
                val += 15
            elif 2 <= c <= 5 and 2 <= r <= 5:
                val += 8
            # Back row defense (important to prevent opponent kings)
            if not is_king:
                if (ps == 1 and r == 7) or (ps == -1 and r == 0):
                    val += 12
                # Advancement bonus for men (closer to promotion)
                if ps == 1:
                    val += (7 - r) * 3
                else:
                    val += r * 3
            # Edge safety bonus (can't be jumped from one side)
            if c == 0 or c == 7:
                val += 5
            if ps == side:
                score += val
                if is_king: my_count += 2
                else: my_count += 1
            else:
                score -= val
                if is_king: opp_count += 2
                else: opp_count += 1
    # Trading bonus when ahead - encourage trades
    if my_count > opp_count + 2:
        score += (my_count - opp_count) * 20
    return score

def chk_do_multi_jump_ai(r, c):
    """Complete multi-jump chain for AI piece at (r,c)."""
    while True:
        jumps = chk_get_jumps(r, c)
        if not jumps:
            break
        best_j = None
        best_v = -99999
        for nr, nc, mr, mc in jumps:
            saved = chk_save_state()
            promoted = chk_do_move(r, c, nr, nc, mr, mc)
            v = chk_eval(chk_board, -1)
            chk_restore_state(saved)
            if v > best_v:
                best_v = v
                best_j = (nr, nc, mr, mc)
        if best_j:
            nr, nc, mr, mc = best_j
            promoted = chk_do_move(r, c, nr, nc, mr, mc)
            r, c = nr, nc
            if promoted:
                break

def chk_save_state():
    """Save board state for undo."""
    return [row[:] for row in chk_board]

def chk_restore_state(saved):
    """Restore board state."""
    global chk_board
    for r in range(8):
        for c in range(8):
            chk_board[r][c] = saved[r][c]

def chk_apply_move_full(m):
    """Apply a move including multi-jumps. Returns (tr, tc) final position."""
    fr, fc, tr, tc, is_jump, cr, cc = m
    promoted = chk_do_move(fr, fc, tr, tc, cr, cc)
    if is_jump and not promoted:
        while True:
            jj = chk_get_jumps(tr, tc)
            if not jj:
                break
            # Pick first jump (for minimax consistency)
            nr, nc, mr, mc = jj[0]
            promoted = chk_do_move(tr, tc, nr, nc, mr, mc)
            tr, tc = nr, nc
            if promoted:
                break
    return tr, tc

def chk_check_danger(side):
    """Check if opponent can jump any of our pieces next turn."""
    opp = -side
    return chk_any_jumps(opp)

def chk_ai_move():
    """Execute AI move based on difficulty."""
    global chk_turn, chk_moves, chk_must_jump, chk_sel, chk_valid
    if chk_difficulty == 0:
        chk_ai_easy()
    elif chk_difficulty == 1:
        chk_ai_medium()
    else:
        chk_ai_hard()

def chk_ai_easy():
    """80% blunder rate - usually picks random, sometimes picks a decent move."""
    global chk_turn, chk_moves, chk_must_jump
    moves = chk_all_moves(-1)
    if not moves:
        return
    # Must take jumps (game rules)
    jump_moves = [m for m in moves if m[4]]
    pick = jump_moves if jump_moves else moves
    # 20% chance to play smart (avoid danger), 80% pure random
    if random.randint(1, 10) <= 2 and not jump_moves:
        safe = []
        for m in pick:
            saved = chk_save_state()
            chk_apply_move_full(m)
            danger = chk_any_jumps(1)
            chk_restore_state(saved)
            if not danger:
                safe.append(m)
        if safe:
            pick = safe
    m = pick[random.randint(0, len(pick) - 1)]
    fr, fc, tr, tc, is_jump, cr, cc = m
    promoted = chk_do_move(fr, fc, tr, tc, cr, cc)
    chk_moves += 1
    if is_jump and not promoted:
        while True:
            jumps = chk_get_jumps(tr, tc)
            if not jumps:
                break
            idx = random.randint(0, len(jumps) - 1)
            nr, nc, mr, mc = jumps[idx]
            promoted = chk_do_move(tr, tc, nr, nc, mr, mc)
            tr, tc = nr, nc
            if promoted:
                break
    chk_must_jump = False

def chk_ai_medium():
    """Random but picks best captures and avoids obvious danger."""
    global chk_turn, chk_moves, chk_must_jump
    moves = chk_all_moves(-1)
    if not moves:
        return
    # Always take best jump if available (captures)
    jump_moves = [m for m in moves if m[4]]
    if jump_moves:
        best = None
        best_caps = 0
        for m in jump_moves:
            saved = chk_save_state()
            fr, fc, tr, tc = m[0], m[1], m[2], m[3]
            chk_do_move(fr, fc, tr, tc, m[5], m[6])
            caps = 1
            r2, c2 = tr, tc
            while True:
                jj = chk_get_jumps(r2, c2)
                if not jj:
                    break
                nr, nc, mr, mc = jj[0]
                chk_do_move(r2, c2, nr, nc, mr, mc)
                r2, c2 = nr, nc
                caps += 1
            chk_restore_state(saved)
            if caps > best_caps:
                best_caps = caps
                best = m
        if best:
            moves = [best]
    # Among remaining, avoid moves that let opponent jump
    safe_moves = []
    for m in moves:
        saved = chk_save_state()
        chk_apply_move_full(m)
        danger = chk_any_jumps(1)
        chk_restore_state(saved)
        if not danger:
            safe_moves.append(m)
    pick = safe_moves if safe_moves else moves
    m = pick[random.randint(0, len(pick) - 1)]
    fr, fc, tr, tc, is_jump, cr, cc = m
    promoted = chk_do_move(fr, fc, tr, tc, cr, cc)
    chk_moves += 1
    if is_jump and not promoted:
        while True:
            jumps = chk_get_jumps(tr, tc)
            if not jumps:
                break
            idx = random.randint(0, len(jumps) - 1)
            nr, nc, mr, mc = jumps[idx]
            promoted = chk_do_move(tr, tc, nr, nc, mr, mc)
            tr, tc = nr, nc
            if promoted:
                break
    chk_must_jump = False

def chk_minimax(depth, is_max, alpha, beta):
    """Minimax with alpha-beta. is_max=True means AI's turn (-1 side)."""
    w = chk_check_winner()
    if w == -1:
        return 10000 + depth
    if w == 1:
        return -10000 - depth
    if depth == 0:
        return chk_eval(chk_board, -1)
    side = -1 if is_max else 1
    moves = chk_all_moves(side)
    if not moves:
        return -10000 if is_max else 10000
    # Move ordering: jumps first (better pruning)
    moves.sort(key=lambda m: (0 if m[4] else 1))
    if is_max:
        val = -99999
        for m in moves:
            saved = chk_save_state()
            chk_apply_move_full(m)
            v = chk_minimax(depth - 1, False, alpha, beta)
            chk_restore_state(saved)
            if v > val:
                val = v
            if val > alpha:
                alpha = val
            if alpha >= beta:
                break
        return val
    else:
        val = 99999
        for m in moves:
            saved = chk_save_state()
            chk_apply_move_full(m)
            v = chk_minimax(depth - 1, True, alpha, beta)
            chk_restore_state(saved)
            if v < val:
                val = v
            if val < beta:
                beta = val
            if alpha >= beta:
                break
        return val

def chk_ai_hard():
    """Minimax with alpha-beta pruning, depth 4."""
    global chk_turn, chk_moves, chk_must_jump
    moves = chk_all_moves(-1)
    if not moves:
        return
    # Move ordering: jumps first
    moves.sort(key=lambda m: (0 if m[4] else 1))
    best_move = None
    best_val = -99999
    alpha = -99999
    beta = 99999
    for m in moves:
        saved = chk_save_state()
        chk_apply_move_full(m)
        val = chk_minimax(3, False, alpha, beta)
        chk_restore_state(saved)
        if val > best_val:
            best_val = val
            best_move = m
        if val > alpha:
            alpha = val
    if best_move:
        fr, fc, tr, tc, is_jump, cr, cc = best_move
        promoted = chk_do_move(fr, fc, tr, tc, cr, cc)
        chk_moves += 1
        if is_jump and not promoted:
            chk_do_multi_jump_ai(tr, tc)
    chk_must_jump = False

# ===== TOUCH + GAME FLOW =====
def chk_update_selection(r, c):
    """Update selected piece and compute valid moves."""
    global chk_sel, chk_valid
    chk_sel = (r, c)
    chk_valid = []
    has_jumps = chk_any_jumps(chk_turn)
    if has_jumps:
        for nr, nc, mr, mc in chk_get_jumps(r, c):
            chk_valid.append((nr, nc))
    else:
        for nr, nc in chk_get_moves(r, c):
            chk_valid.append((nr, nc))

def chk_end_game(winner):
    """Handle game end."""
    global chk_mode, chk_winner
    global chk_easy_wins, chk_easy_losses, chk_med_wins, chk_med_losses
    global chk_hard_wins, chk_hard_losses, chk_p1_wins, chk_p2_wins
    chk_winner = winner
    chk_mode = 3
    # Update stats
    if chk_vs_ai:
        if winner == 1:
            if chk_difficulty == 0:
                chk_easy_wins += 1
            elif chk_difficulty == 1:
                chk_med_wins += 1
            else:
                chk_hard_wins += 1
        else:
            if chk_difficulty == 0:
                chk_easy_losses += 1
            elif chk_difficulty == 1:
                chk_med_losses += 1
            else:
                chk_hard_losses += 1
    else:
        if winner == 1:
            chk_p1_wins += 1
        else:
            chk_p2_wins += 1
    save_chk_stats()
    draw_chk_gameover()

def launch_checkers():
    global chk_mode
    chk_mode = 0
    draw_chk_menu()

def handle_checkers_touch(tx, ty):
    global chk_mode, chk_vs_ai, chk_difficulty, chk_turn
    global chk_sel, chk_valid, chk_must_jump, chk_moves
    global current_screen, current_app, last_time_text

    if chk_mode == 0:  # Menu
        if 150 <= ty <= 220 and 34 <= tx <= 334:
            chk_vs_ai = False
            chk_init()
            chk_mode = 2
            draw_chk_board()
        elif 250 <= ty <= 320 and 34 <= tx <= 334:
            chk_vs_ai = True
            chk_mode = 1
            draw_chk_difficulty()

    elif chk_mode == 1:  # Difficulty select
        if 34 <= tx <= 334:
            diff = -1
            if 140 <= ty <= 200:
                diff = 0
            elif 220 <= ty <= 280:
                diff = 1
            elif 300 <= ty <= 360:
                diff = 2
            if diff >= 0:
                chk_difficulty = diff
                chk_init()
                chk_mode = 2
                draw_chk_board()

    elif chk_mode == 2:  # Playing
        # Convert touch to board coords
        bc = (tx - CHK_X) // CHK_SZ
        br = (ty - CHK_Y) // CHK_SZ
        if 0 <= br < 8 and 0 <= bc < 8:
            p = chk_board[br][bc]
            side = 0 if p == 0 else (1 if p > 0 else -1)

            # If AI's turn, ignore touch
            if chk_vs_ai and chk_turn == -1:
                return

            # Tapped a valid move destination
            if (br, bc) in chk_valid and chk_sel:
                sr, sc = chk_sel
                # Determine if jump
                is_jump = abs(br - sr) == 2
                cr, cc = -1, -1
                if is_jump:
                    cr = (sr + br) // 2
                    cc = (sc + bc) // 2
                promoted = chk_do_move(sr, sc, br, bc, cr, cc)
                chk_moves += 1

                # Check multi-jump
                if is_jump and not promoted:
                    more_jumps = chk_get_jumps(br, bc)
                    if more_jumps:
                        chk_must_jump = True
                        chk_sel = (br, bc)
                        chk_valid = [(nr, nc) for nr, nc, mr, mc in more_jumps]
                        draw_chk_board()
                        return

                # Turn complete
                chk_must_jump = False
                chk_sel = None
                chk_valid = []

                # Check winner
                w = chk_check_winner()
                if w != 0:
                    chk_end_game(w)
                    return

                # Switch turn
                chk_turn = -chk_turn
                draw_chk_board()

                # AI turn
                if chk_vs_ai and chk_turn == -1:
                    chk_ai_move()
                    w = chk_check_winner()
                    if w != 0:
                        chk_end_game(w)
                        return
                    chk_turn = 1
                    chk_sel = None
                    chk_valid = []
                    draw_chk_board()

            # Tapped own piece (select/reselect)
            elif side == chk_turn and not chk_must_jump:
                chk_update_selection(br, bc)
                draw_chk_board()

            # During multi-jump, can only tap valid squares
            elif chk_must_jump:
                pass  # Ignore invalid taps during multi-jump

    elif chk_mode == 3:  # Game over
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                chk_mode = 0
                draw_chk_menu()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("CHECKERS")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""

def save_chk_stats():
    save_all_stats()

def draw_chk_stats():
    display.fill(BLACK)
    draw_text(display, "CHECKERS", 100, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    # EASY
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (EASY)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {chk_easy_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {chk_easy_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    # MEDIUM
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (MED)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {chk_med_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {chk_med_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    # HARD
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (HARD)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {chk_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {chk_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    # PvP
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P1 WINS: {chk_p1_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P2 WINS: {chk_p2_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
