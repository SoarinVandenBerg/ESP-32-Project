# ===== CHESS GAME =====
CHESS_SQ = 46  # Square size (46*8 = 368 = screen width)
CHESS_Y = 40   # Board top offset
CHESS_LIGHT = make_color(140, 180, 100)
CHESS_DARK = make_color(60, 100, 30)
CHESS_SEL = make_color(180, 200, 50)
CHESS_DOT = make_color(200, 200, 50)
CHESS_W_BASE = make_color(230, 220, 190)
CHESS_B_BASE = make_color(50, 50, 50)



chess_mode = 0  # 0=menu, 1=playing, 2=gameover
chess_turn = 1  # 1=white, -1=black
chess_selected = None  # (row, col) of selected piece
chess_valid_moves = []  # List of (row, col) valid destinations
chess_board = None
chess_winner = 0  # 0=draw, 1=white, -1=black
chess_can_castle = [True, True, True, True]  # WK, WQ, BK, BQ
chess_en_passant = None  # (row, col) of en passant target square
chess_vs_ai = False
chess_difficulty = 1  # 0=easy, 1=medium, 2=hard
chess_p1_wins = 0
chess_p2_wins = 0
chess_draws = 0
chess_human_wins = 0
chess_ai_wins = 0
chess_ai_draws = 0
CHESS_PIECE_VAL = {1: 100, 2: 320, 3: 330, 4: 500, 5: 900, 6: 20000}

def chess_init():
    global chess_board, chess_turn, chess_selected, chess_valid_moves
    global chess_mode, chess_winner, chess_can_castle, chess_en_passant
    chess_board = [
        [-4, -2, -3, -5, -6, -3, -2, -4],
        [-1, -1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1],
        [4, 2, 3, 5, 6, 3, 2, 4],
    ]
    chess_turn = 1
    chess_selected = None
    chess_valid_moves = []
    chess_mode = 1
    chess_winner = 0
    chess_can_castle = [True, True, True, True]
    chess_en_passant = None

def chess_get_moves(r, c):
    """Get pseudo-legal moves for piece at (r,c). Does NOT filter for check."""
    b = chess_board
    p = b[r][c]
    if p == 0:
        return []
    color = 1 if p > 0 else -1
    pt = abs(p)
    moves = []

    if pt == 1:  # Pawn
        d = -1 if color == 1 else 1
        start_row = 6 if color == 1 else 1
        # Forward
        if 0 <= r + d < 8 and b[r + d][c] == 0:
            moves.append((r + d, c))
            # Double move
            if r == start_row and b[r + 2 * d][c] == 0:
                moves.append((r + 2 * d, c))
        # Captures
        for dc in [-1, 1]:
            nr, nc = r + d, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                if b[nr][nc] != 0 and (1 if b[nr][nc] > 0 else -1) != color:
                    moves.append((nr, nc))
                elif chess_en_passant and (nr, nc) == chess_en_passant:
                    moves.append((nr, nc))

    elif pt == 2:  # Knight
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                t = b[nr][nc]
                if t == 0 or (1 if t > 0 else -1) != color:
                    moves.append((nr, nc))

    elif pt == 3 or pt == 5:  # Bishop or Queen (diagonals)
        for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                t = b[nr][nc]
                if t == 0:
                    moves.append((nr, nc))
                elif (1 if t > 0 else -1) != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc

    if pt == 4 or pt == 5:  # Rook or Queen (straights)
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                t = b[nr][nc]
                if t == 0:
                    moves.append((nr, nc))
                elif (1 if t > 0 else -1) != color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc

    if pt == 6:  # King
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    t = b[nr][nc]
                    if t == 0 or (1 if t > 0 else -1) != color:
                        moves.append((nr, nc))
        # Castling
        if color == 1:  # White
            if chess_can_castle[0] and b[7][5] == 0 and b[7][6] == 0:  # Kingside
                if not chess_is_attacked(7, 4, -1) and not chess_is_attacked(7, 5, -1):
                    moves.append((7, 6))
            if chess_can_castle[1] and b[7][1] == 0 and b[7][2] == 0 and b[7][3] == 0:  # Queenside
                if not chess_is_attacked(7, 4, -1) and not chess_is_attacked(7, 3, -1):
                    moves.append((7, 2))
        else:  # Black
            if chess_can_castle[2] and b[0][5] == 0 and b[0][6] == 0:
                if not chess_is_attacked(0, 4, 1) and not chess_is_attacked(0, 5, 1):
                    moves.append((0, 6))
            if chess_can_castle[3] and b[0][1] == 0 and b[0][2] == 0 and b[0][3] == 0:
                if not chess_is_attacked(0, 4, 1) and not chess_is_attacked(0, 3, 1):
                    moves.append((0, 2))

    return moves

def chess_is_attacked(r, c, by_color):
    """Check if square (r,c) is attacked by any piece of by_color"""
    b = chess_board
    # Knight attacks
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and b[nr][nc] == 2 * by_color:
            return True
    # Pawn attacks
    d = 1 if by_color == 1 else -1  # Direction pawns attack FROM
    for dc in [-1, 1]:
        nr, nc = r + d, c + dc
        if 0 <= nr < 8 and 0 <= nc < 8 and b[nr][nc] == 1 * by_color:
            return True
    # King attacks
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8 and b[nr][nc] == 6 * by_color:
                return True
    # Sliding pieces: bishop/queen (diagonals)
    for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            t = b[nr][nc]
            if t != 0:
                if t == 3 * by_color or t == 5 * by_color:
                    return True
                break
            nr += dr
            nc += dc
    # Sliding pieces: rook/queen (straights)
    for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
        nr, nc = r + dr, c + dc
        while 0 <= nr < 8 and 0 <= nc < 8:
            t = b[nr][nc]
            if t != 0:
                if t == 4 * by_color or t == 5 * by_color:
                    return True
                break
            nr += dr
            nc += dc
    return False

def chess_find_king(color):
    """Find king position for given color"""
    target = 6 * color
    for r in range(8):
        for c in range(8):
            if chess_board[r][c] == target:
                return r, c
    return 0, 0

def chess_in_check(color):
    """Is the given color's king in check?"""
    kr, kc = chess_find_king(color)
    return chess_is_attacked(kr, kc, -color)

def chess_get_legal_moves(r, c):
    """Get legal moves (filters out moves that leave own king in check)"""
    b = chess_board
    p = b[r][c]
    if p == 0:
        return []
    color = 1 if p > 0 else -1
    pseudo = chess_get_moves(r, c)
    legal = []
    for mr, mc in pseudo:
        # Try the move
        orig_dest = b[mr][mc]
        orig_src = b[r][c]
        b[mr][mc] = orig_src
        b[r][c] = 0
        # Handle en passant capture
        ep_captured = 0
        ep_r = -1
        if abs(orig_src) == 1 and chess_en_passant and (mr, mc) == chess_en_passant:
            ep_r = r  # Captured pawn is on same row as moving pawn
            ep_captured = b[ep_r][mc]
            b[ep_r][mc] = 0
        # Check if own king is in check after move
        if not chess_in_check(color):
            legal.append((mr, mc))
        # Undo
        b[r][c] = orig_src
        b[mr][mc] = orig_dest
        if ep_r >= 0:
            b[ep_r][mc] = ep_captured
    return legal

def chess_has_legal_moves(color):
    """Does the given color have any legal move?"""
    for r in range(8):
        for c in range(8):
            p = chess_board[r][c]
            if p != 0 and (1 if p > 0 else -1) == color:
                if chess_get_legal_moves(r, c):
                    return True
    return False

def chess_make_move(fr, fc, tr, tc):
    """Execute a move and handle special rules"""
    global chess_turn, chess_en_passant, chess_mode, chess_winner
    b = chess_board
    p = b[fr][fc]
    color = 1 if p > 0 else -1
    pt = abs(p)

    # En passant capture
    if pt == 1 and chess_en_passant and (tr, tc) == chess_en_passant:
        b[fr][tc] = 0  # Remove captured pawn

    # Update en passant target
    chess_en_passant = None
    if pt == 1 and abs(tr - fr) == 2:
        chess_en_passant = ((fr + tr) // 2, fc)

    # Castling - move rook
    if pt == 6 and abs(tc - fc) == 2:
        if tc == 6:  # Kingside
            b[fr][5] = b[fr][7]
            b[fr][7] = 0
        elif tc == 2:  # Queenside
            b[fr][3] = b[fr][0]
            b[fr][0] = 0

    # Update castling rights
    if pt == 6:  # King moved
        if color == 1:
            chess_can_castle[0] = False
            chess_can_castle[1] = False
        else:
            chess_can_castle[2] = False
            chess_can_castle[3] = False
    if pt == 4:  # Rook moved
        if fr == 7 and fc == 7:
            chess_can_castle[0] = False
        elif fr == 7 and fc == 0:
            chess_can_castle[1] = False
        elif fr == 0 and fc == 7:
            chess_can_castle[2] = False
        elif fr == 0 and fc == 0:
            chess_can_castle[3] = False
    # Rook captured
    if tr == 7 and tc == 7:
        chess_can_castle[0] = False
    elif tr == 7 and tc == 0:
        chess_can_castle[1] = False
    elif tr == 0 and tc == 7:
        chess_can_castle[2] = False
    elif tr == 0 and tc == 0:
        chess_can_castle[3] = False

    # Make the move
    b[tr][tc] = p
    b[fr][fc] = 0

    # Pawn promotion (auto-queen)
    if pt == 1 and (tr == 0 or tr == 7):
        b[tr][tc] = 5 * color

    # Switch turn
    chess_turn = -color

    # Check for checkmate or stalemate
    if not chess_has_legal_moves(chess_turn):
        chess_mode = 2
        if chess_in_check(chess_turn):
            chess_winner = color  # Checkmate
        else:
            chess_winner = 0  # Stalemate

def chess_evaluate():
    """Evaluate board position. Positive = white advantage."""
    score = 0
    b = chess_board
    for r in range(8):
        for c in range(8):
            p = b[r][c]
            if p != 0:
                pt = abs(p)
                val = CHESS_PIECE_VAL[pt]
                if p > 0:
                    score += val
                    if pt in (2, 3) and 2 <= r <= 5 and 2 <= c <= 5:
                        score += 10
                else:
                    score -= val
                    if pt in (2, 3) and 2 <= r <= 5 and 2 <= c <= 5:
                        score -= 10
    return score

def chess_ai_try_move(fr, fc, tr, tc):
    """Make temporary move for AI search. Returns saved state for undo."""
    global chess_en_passant
    b = chess_board
    saved = ([row[:] for row in b], chess_en_passant, chess_can_castle[:])
    p = b[fr][fc]
    color = 1 if p > 0 else -1
    pt = abs(p)
    # En passant capture
    if pt == 1 and chess_en_passant and (tr, tc) == chess_en_passant:
        b[fr][tc] = 0
    # Update en passant target
    chess_en_passant = None
    if pt == 1 and abs(tr - fr) == 2:
        chess_en_passant = ((fr + tr) // 2, fc)
    # Castling - move rook
    if pt == 6 and abs(tc - fc) == 2:
        if tc == 6:
            b[fr][5] = b[fr][7]
            b[fr][7] = 0
        elif tc == 2:
            b[fr][3] = b[fr][0]
            b[fr][0] = 0
    # Update castling rights
    if pt == 6:
        idx = 0 if color == 1 else 2
        chess_can_castle[idx] = False
        chess_can_castle[idx + 1] = False
    if pt == 4:
        if fr == 7 and fc == 7: chess_can_castle[0] = False
        elif fr == 7 and fc == 0: chess_can_castle[1] = False
        elif fr == 0 and fc == 7: chess_can_castle[2] = False
        elif fr == 0 and fc == 0: chess_can_castle[3] = False
    if tr == 7 and tc == 7: chess_can_castle[0] = False
    elif tr == 7 and tc == 0: chess_can_castle[1] = False
    elif tr == 0 and tc == 7: chess_can_castle[2] = False
    elif tr == 0 and tc == 0: chess_can_castle[3] = False
    # Make the move
    b[tr][tc] = p
    b[fr][fc] = 0
    # Pawn promotion (auto-queen)
    if pt == 1 and (tr == 0 or tr == 7):
        b[tr][tc] = 5 * color
    return saved

def chess_ai_undo(saved):
    """Restore board state from saved."""
    global chess_en_passant
    sb, sep, sc = saved
    for r in range(8):
        for c in range(8):
            chess_board[r][c] = sb[r][c]
    chess_en_passant = sep
    chess_can_castle[:] = sc

def chess_minimax(depth, alpha, beta, maximizing):
    """Minimax with alpha-beta pruning."""
    if depth == 0:
        return chess_evaluate()
    color = 1 if maximizing else -1
    # Generate all legal moves
    moves = []
    b = chess_board
    for r in range(8):
        for c in range(8):
            p = b[r][c]
            if p != 0 and (1 if p > 0 else -1) == color:
                for mr, mc in chess_get_legal_moves(r, c):
                    moves.append((r, c, mr, mc))
    if not moves:
        if chess_in_check(color):
            return -30000 if maximizing else 30000
        return 0
    # Move ordering: captures first for better pruning
    moves.sort(key=lambda m: abs(b[m[2]][m[3]]), reverse=True)
    if maximizing:
        best = -99999
        for fr, fc, tr, tc in moves:
            saved = chess_ai_try_move(fr, fc, tr, tc)
            val = chess_minimax(depth - 1, alpha, beta, False)
            chess_ai_undo(saved)
            if val > best:
                best = val
            if val > alpha:
                alpha = val
            if beta <= alpha:
                break
        return best
    else:
        best = 99999
        for fr, fc, tr, tc in moves:
            saved = chess_ai_try_move(fr, fc, tr, tc)
            val = chess_minimax(depth - 1, alpha, beta, True)
            chess_ai_undo(saved)
            if val < best:
                best = val
            if val < beta:
                beta = val
            if beta <= alpha:
                break
        return best

def chess_ai_move():
    """AI selects and executes a move. Elo-calibrated difficulties."""
    gc.collect()
    color = chess_turn
    moves = []
    b = chess_board
    for r in range(8):
        for c in range(8):
            p = b[r][c]
            if p != 0 and (1 if p > 0 else -1) == color:
                for mr, mc in chess_get_legal_moves(r, c):
                    moves.append((r, c, mr, mc))
    if not moves:
        return
    # Elo-calibrated: (depth, eval_noise, blunder%)
    # 300 Elo: shallow, big noise, frequent blunders
    # 500 Elo: shallow, moderate noise, some blunders
    # 750 Elo: deeper, small noise, rare blunders
    if chess_difficulty == 0:
        depth, noise, blunder = 1, 200, 25
    elif chess_difficulty == 1:
        depth, noise, blunder = 1, 80, 10
    else:
        depth, noise, blunder = 2, 30, 5
    # Blunder: play a random legal move
    if random.randint(0, 99) < blunder:
        m = moves[random.randint(0, len(moves) - 1)]
        chess_make_move(m[0], m[1], m[2], m[3])
        return
    maximizing = (color == 1)
    moves.sort(key=lambda m: abs(b[m[2]][m[3]]), reverse=True)
    best_move = moves[0]
    best_val = -99999 if maximizing else 99999
    for fr, fc, tr, tc in moves:
        saved = chess_ai_try_move(fr, fc, tr, tc)
        val = chess_minimax(depth - 1, -99999, 99999, not maximizing)
        chess_ai_undo(saved)
        val += random.randint(-noise, noise)
        if maximizing:
            if val > best_val:
                best_val = val
                best_move = (fr, fc, tr, tc)
        else:
            if val < best_val:
                best_val = val
                best_move = (fr, fc, tr, tc)
    chess_make_move(best_move[0], best_move[1], best_move[2], best_move[3])

def draw_chess_piece(cx, cy, pt, base_c, out_c):
    """Draw shaped chess piece at center (cx, cy) with outline"""
    if pt == 1:  # Pawn - circle head, stem, base
        display.fill_circle(cx, cy - 5, 9, out_c)
        display.fill_rect(cx - 6, cy + 2, 12, 6, out_c)
        display.fill_rect(cx - 10, cy + 7, 20, 7, out_c)
        display.fill_circle(cx, cy - 5, 7, base_c)
        display.fill_rect(cx - 5, cy + 3, 10, 4, base_c)
        display.fill_rect(cx - 9, cy + 8, 18, 5, base_c)
    elif pt == 2:  # Knight - symmetrical horse head (front view)
        display.fill_rect(cx - 8, cy - 16, 5, 7, out_c)
        display.fill_rect(cx + 3, cy - 16, 5, 7, out_c)
        display.fill_circle(cx, cy - 5, 10, out_c)
        display.fill_rect(cx - 6, cy + 3, 12, 6, out_c)
        display.fill_rect(cx - 10, cy + 7, 20, 7, out_c)
        display.fill_rect(cx - 7, cy - 15, 4, 6, base_c)
        display.fill_rect(cx + 3, cy - 15, 4, 6, base_c)
        display.fill_circle(cx, cy - 5, 8, base_c)
        display.fill_rect(cx - 5, cy + 4, 10, 4, base_c)
        display.fill_rect(cx - 9, cy + 8, 18, 5, base_c)
    elif pt == 3:  # Bishop - pointed cap with body
        display.fill_circle(cx, cy - 13, 5, out_c)
        display.fill_circle(cx, cy - 1, 11, out_c)
        display.fill_rect(cx - 11, cy + 7, 22, 7, out_c)
        display.fill_circle(cx, cy - 13, 3, base_c)
        display.fill_circle(cx, cy - 1, 9, base_c)
        display.fill_rect(cx - 10, cy + 8, 20, 5, base_c)
    elif pt == 4:  # Rook - castle tower with battlements
        display.fill_rect(cx - 13, cy - 15, 7, 9, out_c)
        display.fill_rect(cx - 4, cy - 15, 8, 9, out_c)
        display.fill_rect(cx + 6, cy - 15, 7, 9, out_c)
        display.fill_rect(cx - 11, cy - 8, 22, 20, out_c)
        display.fill_rect(cx - 13, cy + 7, 26, 7, out_c)
        display.fill_rect(cx - 12, cy - 14, 5, 8, base_c)
        display.fill_rect(cx - 3, cy - 14, 6, 8, base_c)
        display.fill_rect(cx + 7, cy - 14, 5, 8, base_c)
        display.fill_rect(cx - 9, cy - 7, 18, 19, base_c)
        display.fill_rect(cx - 12, cy + 8, 24, 5, base_c)
    elif pt == 5:  # Queen - crown with body
        display.fill_circle(cx - 9, cy - 10, 5, out_c)
        display.fill_circle(cx, cy - 14, 5, out_c)
        display.fill_circle(cx + 9, cy - 10, 5, out_c)
        display.fill_circle(cx, cy, 12, out_c)
        display.fill_rect(cx - 13, cy + 7, 26, 7, out_c)
        display.fill_circle(cx - 9, cy - 10, 3, base_c)
        display.fill_circle(cx, cy - 14, 3, base_c)
        display.fill_circle(cx + 9, cy - 10, 3, base_c)
        display.fill_circle(cx, cy, 10, base_c)
        display.fill_rect(cx - 12, cy + 8, 24, 5, base_c)
    elif pt == 6:  # King - cross with body
        display.fill_rect(cx - 3, cy - 17, 6, 14, out_c)
        display.fill_rect(cx - 7, cy - 15, 14, 6, out_c)
        display.fill_circle(cx, cy + 1, 12, out_c)
        display.fill_rect(cx - 13, cy + 7, 26, 7, out_c)
        display.fill_circle(cx, cy + 1, 10, base_c)
        display.fill_rect(cx - 2, cy - 16, 4, 12, base_c)
        display.fill_rect(cx - 6, cy - 14, 12, 4, base_c)
        display.fill_rect(cx - 12, cy + 8, 24, 5, base_c)

def draw_chess_square(r, c, highlight=False):
    """Draw a single board square with piece if present"""
    x = c * CHESS_SQ
    y = CHESS_Y + r * CHESS_SQ
    # Square color
    if highlight:
        sq_color = CHESS_SEL
    elif (r + c) % 2 == 0:
        sq_color = CHESS_LIGHT
    else:
        sq_color = CHESS_DARK
    display.fill_rect(x, y, CHESS_SQ, CHESS_SQ, sq_color)
    # Draw piece
    p = chess_board[r][c]
    if p != 0:
        color = 1 if p > 0 else -1
        pt = abs(p)
        cx = x + CHESS_SQ // 2
        cy = y + CHESS_SQ // 2
        base_color = CHESS_W_BASE if color == 1 else CHESS_B_BASE
        out_color = BLACK if color == 1 else WHITE
        draw_chess_piece(cx, cy, pt, base_color, out_color)

def draw_chess_board():
    """Draw the full chess board"""
    for r in range(8):
        for c in range(8):
            is_sel = chess_selected and (r, c) == chess_selected
            draw_chess_square(r, c, highlight=is_sel)
    # Draw valid move indicators
    for mr, mc in chess_valid_moves:
        x = mc * CHESS_SQ + CHESS_SQ // 2
        y = CHESS_Y + mr * CHESS_SQ + CHESS_SQ // 2
        if chess_board[mr][mc] != 0:
            # Capture: draw corner markers on the square
            sx = mc * CHESS_SQ
            sy = CHESS_Y + mr * CHESS_SQ
            for dx, dy in [(0,0),(CHESS_SQ-8,0),(0,CHESS_SQ-8),(CHESS_SQ-8,CHESS_SQ-8)]:
                display.fill_rect(sx + dx, sy + dy, 8, 8, CHESS_DOT)
        else:
            # Empty: draw small dot
            display.fill_circle(x, y, 6, CHESS_DOT)

def draw_chess_status(thinking=False):
    """Draw turn indicator at top"""
    display.fill_rect(0, 0, 368, 38, BLACK)
    if thinking:
        status = "AI THINKING..."
    elif chess_vs_ai:
        status = "YOUR TURN" if chess_turn == 1 else "AI'S TURN"
    else:
        status = "WHITE'S TURN" if chess_turn == 1 else "BLACK'S TURN"
    if not thinking and chess_in_check(chess_turn):
        status += " CHECK!"
    sw = len(status) * 6 * 2
    draw_text(display, status, (368 - sw) // 2, 10, GREY, 2, CODE_FONT)

def draw_chess_game():
    """Draw full chess screen"""
    display.fill(BLACK)
    draw_chess_board()
    draw_chess_status()

def draw_chess_menu():
    """Draw mode selection menu"""
    display.fill(BLACK)
    title = "CHESS"
    title_w = len(title) * 6 * 4
    draw_text(display, title, (368 - title_w) // 2, 30, GREY, 4, CODE_FONT)
    display.fill_rect(34, 150, 300, 70, GREEN)
    btn_text = "PLAYER VS PLAYER"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 34 + (300 - btn_w) // 2, 172, WHITE, 2, CODE_FONT)
    display.fill_rect(34, 250, 300, 70, GREEN)
    btn_text = "PLAYER VS AI"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 34 + (300 - btn_w) // 2, 272, WHITE, 2, CODE_FONT)

def draw_chess_difficulty():
    """Draw difficulty selection screen"""
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 338, WHITE, 3, CODE_FONT)

def draw_chess_gameover():
    """Draw game over screen"""
    display.fill(BLACK)
    if chess_winner == 0:
        title = "STALEMATE"
    elif chess_vs_ai:
        title = "YOU WIN!" if chess_winner == 1 else "YOU LOSE!"
    else:
        title = "WHITE WINS" if chess_winner == 1 else "BLACK WINS"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    if chess_winner != 0:
        sub = "CHECKMATE!"
    else:
        sub = "DRAW"
    sub_w = len(sub) * 6 * 3
    draw_text(display, sub, (368 - sub_w) // 2, 160, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def save_chess_stats():
    save_all_stats()

def draw_chess_stats():
    display.fill(BLACK)
    draw_text(display, "CHESS STATS", 100, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WHITE WINS: {chess_p1_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"BLACK WINS: {chess_p2_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"DRAWS: {chess_draws}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {chess_human_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {chess_ai_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"DRAWS: {chess_ai_draws}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)

def launch_chess():
    global chess_mode
    chess_mode = 0
    draw_chess_menu()

def handle_chess_touch(tx, ty):
    global chess_mode, chess_vs_ai, chess_difficulty, chess_selected, chess_valid_moves, chess_turn, chess_winner, chess_p1_wins, chess_p2_wins, chess_draws, chess_human_wins, chess_ai_wins, chess_ai_draws, current_screen, current_app, last_time_text
    if chess_mode == 0:  # Mode select
        if 150 <= ty <= 220 and 34 <= tx <= 334:
            chess_vs_ai = False
            chess_init()
            draw_chess_game()
        elif 250 <= ty <= 320 and 34 <= tx <= 334:
            chess_vs_ai = True
            chess_mode = 3
            draw_chess_difficulty()
    elif chess_mode == 3:  # Difficulty select
        if 34 <= tx <= 334:
            if 160 <= ty <= 220:
                chess_difficulty = 0
                chess_init()
                draw_chess_game()
            elif 240 <= ty <= 300:
                chess_difficulty = 1
                chess_init()
                draw_chess_game()
            elif 320 <= ty <= 380:
                chess_difficulty = 2
                chess_init()
                draw_chess_game()
    elif chess_mode == 1:  # Playing
        # Only allow input on human's turn
        if chess_vs_ai and chess_turn == -1:
            pass  # AI's turn, ignore taps
        else:
            br = (ty - CHESS_Y) // CHESS_SQ
            bc = tx // CHESS_SQ
            if 0 <= br < 8 and 0 <= bc < 8:
                p = chess_board[br][bc]
                p_color = 1 if p > 0 else (-1 if p < 0 else 0)
                if chess_selected is None:
                    if p_color == chess_turn:
                        chess_selected = (br, bc)
                        chess_valid_moves = chess_get_legal_moves(br, bc)
                        draw_chess_board()
                        draw_chess_status()
                else:
                    sr, sc = chess_selected
                    if (br, bc) in chess_valid_moves:
                        chess_make_move(sr, sc, br, bc)
                        chess_selected = None
                        chess_valid_moves = []
                        if chess_mode == 2:
                            # Human move ended the game
                            if chess_vs_ai:
                                if chess_winner == 1:
                                    chess_human_wins += 1
                                elif chess_winner == -1:
                                    chess_ai_wins += 1
                                else:
                                    chess_ai_draws += 1
                            else:
                                if chess_winner == 1:
                                    chess_p1_wins += 1
                                elif chess_winner == -1:
                                    chess_p2_wins += 1
                                else:
                                    chess_draws += 1
                            save_chess_stats()
                            draw_chess_gameover()
                        elif chess_vs_ai and chess_turn == -1:
                            # AI's turn
                            draw_chess_board()
                            draw_chess_status(thinking=True)
                            chess_ai_move()
                            chess_selected = None
                            chess_valid_moves = []
                            if chess_mode == 2:
                                if chess_winner == 1:
                                    chess_human_wins += 1
                                elif chess_winner == -1:
                                    chess_ai_wins += 1
                                else:
                                    chess_ai_draws += 1
                                save_chess_stats()
                                draw_chess_gameover()
                            else:
                                draw_chess_board()
                                draw_chess_status()
                        else:
                            draw_chess_board()
                            draw_chess_status()
                    elif p_color == chess_turn:
                        chess_selected = (br, bc)
                        chess_valid_moves = chess_get_legal_moves(br, bc)
                        draw_chess_board()
                        draw_chess_status()
                    else:
                        chess_selected = None
                        chess_valid_moves = []
                        draw_chess_board()
                        draw_chess_status()
    elif chess_mode == 2:  # Game over
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                chess_mode = 0
                draw_chess_menu()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("CHESS")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
