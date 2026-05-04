# ===== BATTLESHIP GAME =====
BSHIP_SIZE = 8  # 8x8 grid
BSHIP_CELL = 28  # Cell size in pixels
BSHIP_X = (368 - BSHIP_SIZE * BSHIP_CELL) // 2  # Center grid
BSHIP_Y = 80

# Ships: (name, length)
BSHIP_SHIPS = [("BATTLESHIP", 4), ("CRUISER", 3), ("DESTROYER", 2)]

# Colors for battleship
WATER_COLOR = GREY
SHIP_COLOR = GREEN
HIT_COLOR = GREEN  # Hits are green
DARK_HIT_COLOR = make_color(0, 60, 0)  # Darker green for AI hits on player
MISS_COLOR = DARK_GREY

# Game state
bship_mode = 0  # 0=menu, 1=placing, 2=battle, 3=game_over, 4=pass_screen, 5=ai_turn, 6=difficulty_select
bship_vs_ai = False
bship_difficulty = 1  # 0=easy, 1=medium, 2=hard
bship_current_player = 0  # 0 or 1
bship_placing_ship = 0  # Index into BSHIP_SHIPS
bship_horizontal = True  # Ship orientation
bship_winner = -1
bship_last_result = ""  # "HIT!", "MISS!", "SUNK!"
bship_show_own = False  # Toggle to show own board during battle
bship_player_fired = False  # Has player fired this turn?
bship_sunk_name = ""  # Name of ship that was sunk

# Boards: 0=empty, 1=ship, 2=miss, 3=hit
bship_boards = [[[0]*BSHIP_SIZE for _ in range(BSHIP_SIZE)] for _ in range(2)]
# Ship positions for each player: list of (row, col, length, horizontal)
bship_ship_pos = [[], []]

def bship_reset():
    global bship_boards, bship_ship_pos, bship_current_player, bship_placing_ship
    global bship_horizontal, bship_mode, bship_winner, bship_last_result, bship_show_own
    global bship_player_fired, bship_sunk_name
    bship_boards = [[[0]*BSHIP_SIZE for _ in range(BSHIP_SIZE)] for _ in range(2)]
    bship_ship_pos = [[], []]
    bship_current_player = 0
    bship_placing_ship = 0
    bship_horizontal = True
    bship_mode = 1  # Start placing
    bship_winner = -1
    bship_last_result = ""
    bship_show_own = False
    bship_player_fired = False
    bship_sunk_name = ""

def bship_can_place(player, row, col, length, horizontal):
    """Check if ship can be placed at position"""
    for i in range(length):
        r = row if horizontal else row + i
        c = col + i if horizontal else col
        if r < 0 or c < 0 or r >= BSHIP_SIZE or c >= BSHIP_SIZE:
            return False
        if bship_boards[player][r][c] != 0:
            return False
    return True

def bship_place_ship(player, row, col, length, horizontal):
    """Place a ship on the board"""
    for i in range(length):
        r = row if horizontal else row + i
        c = col + i if horizontal else col
        bship_boards[player][r][c] = 1
    bship_ship_pos[player].append((row, col, length, horizontal))

def bship_remove_last_ship(player):
    """Remove the last placed ship from the board"""
    if not bship_ship_pos[player]:
        return None
    row, col, length, horizontal = bship_ship_pos[player].pop()
    for i in range(length):
        r = row if horizontal else row + i
        c = col + i if horizontal else col
        bship_boards[player][r][c] = 0
    return (row, col, length, horizontal)

def bship_rotate_last_ship(player):
    """Rotate the last placed ship from its center"""
    if not bship_ship_pos[player]:
        return False
    # Remove the last ship
    row, col, length, horizontal = bship_remove_last_ship(player)
    new_horizontal = not horizontal

    # Calculate center of ship and new top-left corner after rotation
    if horizontal:
        # Horizontal: center is at (row, col + length//2)
        # After rotation: vertical at (row - length//2, col + length//2)
        new_row = row - length // 2
        new_col = col + length // 2
    else:
        # Vertical: center is at (row + length//2, col)
        # After rotation: horizontal at (row + length//2, col - length//2)
        new_row = row + length // 2
        new_col = col - length // 2

    # Try to place with new orientation at new position
    if bship_can_place(player, new_row, new_col, length, new_horizontal):
        bship_place_ship(player, new_row, new_col, length, new_horizontal)
        return True
    # Can't rotate - put it back as it was
    bship_place_ship(player, row, col, length, horizontal)
    return False

def bship_ai_place_ships():
    """AI places its ships randomly"""
    for name, length in BSHIP_SHIPS:
        placed = False
        attempts = 0
        while not placed and attempts < 100:
            row = random.randint(0, BSHIP_SIZE - 1)
            col = random.randint(0, BSHIP_SIZE - 1)
            horizontal = random.choice([True, False])
            if bship_can_place(1, row, col, length, horizontal):
                bship_place_ship(1, row, col, length, horizontal)
                placed = True
            attempts += 1

def bship_check_sunk(player, ship_idx):
    """Check if a specific ship is sunk"""
    row, col, length, horizontal = bship_ship_pos[player][ship_idx]
    for i in range(length):
        r = row if horizontal else row + i
        c = col + i if horizontal else col
        if bship_boards[player][r][c] != 3:
            return False
    return True

def bship_all_sunk(player):
    """Check if all ships are sunk"""
    for i in range(len(bship_ship_pos[player])):
        if not bship_check_sunk(player, i):
            return False
    return True

def bship_fire(attacker, row, col):
    """Fire at a cell. Returns: (0=miss, 1=hit, 2=sunk, -1=already fired), ship_name if sunk"""
    global bship_sunk_name
    target = 1 - attacker
    cell = bship_boards[target][row][col]
    if cell == 2 or cell == 3:
        return -1, ""  # Already fired
    if cell == 1:  # Hit!
        bship_boards[target][row][col] = 3
        # Check if any ship was sunk
        for i in range(len(bship_ship_pos[target])):
            ship_row, ship_col, length, horiz = bship_ship_pos[target][i]
            # Check if this hit is part of this ship
            for j in range(length):
                sr = ship_row if horiz else ship_row + j
                sc = ship_col + j if horiz else ship_col
                if sr == row and sc == col:
                    if bship_check_sunk(target, i):
                        ship_name = BSHIP_SHIPS[i][0]
                        return 2, ship_name  # Sunk!
                    return 1, ""  # Hit but not sunk
    else:
        bship_boards[target][row][col] = 2
        return 0, ""  # Miss

def bship_ai_fire():
    """AI fires based on difficulty level"""
    # EASY: Pure random with basic adjacent targeting (50% chance to miss adjacents)
    if bship_difficulty == 0:
        # Check for hits, but only 50% chance to target adjacent
        if random.randint(0, 1) == 1:
            for r in range(BSHIP_SIZE):
                for c in range(BSHIP_SIZE):
                    if bship_boards[0][r][c] == 3:  # Hit
                        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < BSHIP_SIZE and 0 <= nc < BSHIP_SIZE:
                                if bship_boards[0][nr][nc] in [0, 1]:
                                    return nr, nc
        # Random shot (no parity)
        valid = [(r, c) for r in range(BSHIP_SIZE) for c in range(BSHIP_SIZE) if bship_boards[0][r][c] in [0, 1]]
        if valid:
            return random.choice(valid)
        return 0, 0

    # MEDIUM & HARD: Smart targeting with hunt/target
    unsunk_hits = []
    for r in range(BSHIP_SIZE):
        for c in range(BSHIP_SIZE):
            if bship_boards[0][r][c] == 3:
                for i, (sr, sc, length, horiz) in enumerate(bship_ship_pos[0]):
                    if not bship_check_sunk(0, i):
                        for j in range(length):
                            hr = sr if horiz else sr + j
                            hc = sc + j if horiz else sc
                            if hr == r and hc == c:
                                unsunk_hits.append((r, c))
                                break

    if unsunk_hits:
        # Line following
        for r, c in unsunk_hits:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if (nr, nc) in unsunk_hits:
                    er, ec = r - dr, c - dc
                    if 0 <= er < BSHIP_SIZE and 0 <= ec < BSHIP_SIZE:
                        if bship_boards[0][er][ec] in [0, 1]:
                            return er, ec
                    er, ec = nr + dr, nc + dc
                    if 0 <= er < BSHIP_SIZE and 0 <= ec < BSHIP_SIZE:
                        if bship_boards[0][er][ec] in [0, 1]:
                            return er, ec

        # Adjacent targeting
        adjacent_cells = []
        for r, c in unsunk_hits:
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < BSHIP_SIZE and 0 <= nc < BSHIP_SIZE:
                    if bship_boards[0][nr][nc] in [0, 1]:
                        adjacent_cells.append((nr, nc))
        if adjacent_cells:
            return random.choice(adjacent_cells)

    # MEDIUM: Parity only
    if bship_difficulty == 1:
        parity_targets = []
        other_targets = []
        for r in range(BSHIP_SIZE):
            for c in range(BSHIP_SIZE):
                if bship_boards[0][r][c] in [0, 1]:
                    if (r + c) % 2 == 0:
                        parity_targets.append((r, c))
                    else:
                        other_targets.append((r, c))
        if parity_targets:
            return random.choice(parity_targets)
        if other_targets:
            return random.choice(other_targets)
        return 0, 0

    # HARD: Probability scoring with parity
    best_score = -1
    best_targets = []
    for r in range(BSHIP_SIZE):
        for c in range(BSHIP_SIZE):
            if bship_boards[0][r][c] not in [0, 1]:
                continue
            if (r + c) % 2 != 0:
                continue
            # Count open space for probability
            score = 0
            # Horizontal space
            h_space = 1
            for dc in [-1, 1]:
                tc = c + dc
                while 0 <= tc < BSHIP_SIZE and bship_boards[0][r][tc] in [0, 1]:
                    h_space += 1
                    tc += dc
            # Vertical space
            v_space = 1
            for dr in [-1, 1]:
                tr = r + dr
                while 0 <= tr < BSHIP_SIZE and bship_boards[0][tr][c] in [0, 1]:
                    v_space += 1
                    tr += dr
            # Score by ship sizes that could fit
            for ship_len in [2, 3, 4]:
                if h_space >= ship_len:
                    score += 1
                if v_space >= ship_len:
                    score += 1
            if score > best_score:
                best_score = score
                best_targets = [(r, c)]
            elif score == best_score:
                best_targets.append((r, c))
    if best_targets:
        return random.choice(best_targets)
    # Fallback
    for r in range(BSHIP_SIZE):
        for c in range(BSHIP_SIZE):
            if bship_boards[0][r][c] in [0, 1]:
                return r, c
    return 0, 0

def draw_bship_menu():
    """Draw mode selection menu"""
    display.fill(BLACK)
    # Center title: "BATTLESHIP" = 10 chars * 6 * 4 = 240 wide, center = (368-240)/2 = 64
    draw_text(display, "BATTLESHIP", 64, 30, GREY, 4, CODE_FONT)

    # Player vs Player button - green, wider
    display.fill_rect(34, 150, 300, 70, GREEN)
    # "PLAYER VS PLAYER" = 16 chars * 6 * 2 = 192, center in 300 = 34 + (300-192)/2 = 88
    draw_text(display, "PLAYER VS PLAYER", 88, 172, WHITE, 2, CODE_FONT)

    # Player vs AI button - green, wider
    display.fill_rect(34, 250, 300, 70, GREEN)
    # "PLAYER VS AI" = 12 chars * 6 * 2 = 144, center in 300 = 34 + (300-144)/2 = 112
    draw_text(display, "PLAYER VS AI", 112, 272, WHITE, 2, CODE_FONT)

def draw_bship_difficulty():
    """Draw AI difficulty selection screen"""
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)

    # Easy button
    display.fill_rect(34, 140, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 158, WHITE, 3, CODE_FONT)

    # Medium button
    display.fill_rect(34, 220, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 238, WHITE, 3, CODE_FONT)

    # Hard button
    display.fill_rect(34, 300, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 318, WHITE, 3, CODE_FONT)

def draw_bship_grid(player, show_ships, own_board=False):
    """Draw a player's grid. own_board=True uses darker hit color for hits on your ships"""
    for r in range(BSHIP_SIZE):
        for c in range(BSHIP_SIZE):
            x = BSHIP_X + c * BSHIP_CELL
            y = BSHIP_Y + r * BSHIP_CELL
            cell = bship_boards[player][r][c]

            if cell == 0:  # Empty
                display.fill_rect(x, y, BSHIP_CELL - 2, BSHIP_CELL - 2, WATER_COLOR)
            elif cell == 1:  # Ship
                if show_ships:
                    display.fill_rect(x, y, BSHIP_CELL - 2, BSHIP_CELL - 2, SHIP_COLOR)
                else:
                    display.fill_rect(x, y, BSHIP_CELL - 2, BSHIP_CELL - 2, WATER_COLOR)
            elif cell == 2:  # Miss - fill whole square
                display.fill_rect(x, y, BSHIP_CELL - 2, BSHIP_CELL - 2, MISS_COLOR)
            elif cell == 3:  # Hit
                # Use darker green for hits on own board (shows where enemy hit you)
                hit_color = DARK_HIT_COLOR if own_board else HIT_COLOR
                display.fill_rect(x, y, BSHIP_CELL - 2, BSHIP_CELL - 2, hit_color)

def draw_bship_placing():
    """Draw ship placement screen"""
    display.fill(BLACK)

    if bship_vs_ai:
        title = "PLACE SHIPS"
        title_x = (368 - len(title) * 6 * 3) // 2
    else:
        title = f"P{bship_current_player + 1} PLACE"
        title_x = (368 - len(title) * 6 * 3) // 2
    draw_text(display, title, title_x, 10, GREY, 3, CODE_FONT)

    # Show which ship we're placing (centered)
    if bship_placing_ship < len(BSHIP_SHIPS):
        ship_name, ship_len = BSHIP_SHIPS[bship_placing_ship]
        ship_text = f"{ship_name} ({ship_len})"
    else:
        ship_text = "ALL PLACED!"
    ship_x = (368 - len(ship_text) * 6 * 2) // 2
    draw_text(display, ship_text, ship_x, 45, GREEN, 2, CODE_FONT)

    # Draw grid with ships shown
    draw_bship_grid(bship_current_player, True)

    btn_y = BSHIP_Y + BSHIP_SIZE * BSHIP_CELL + 15
    if bship_placing_ship >= len(BSHIP_SHIPS):
        # All ships placed - show DONE button
        display.fill_rect(84, btn_y, 200, 55, GREEN)
        draw_text(display, "DONE", 145, btn_y + 17, WHITE, 3, CODE_FONT)
    else:
        # Still placing - show ROTATE button (rotates last placed ship)
        if len(bship_ship_pos[bship_current_player]) > 0:
            display.fill_rect(84, btn_y, 200, 55, GREEN)
            draw_text(display, "ROTATE", 122, btn_y + 17, WHITE, 3, CODE_FONT)
        else:
            # No ships placed yet - grey out rotate
            display.fill_rect(84, btn_y, 200, 55, DARK_GREY)
            draw_text(display, "ROTATE", 122, btn_y + 17, GREY, 3, CODE_FONT)

def draw_bship_battle():
    """Draw battle screen"""
    display.fill(BLACK)

    if bship_vs_ai:
        if bship_show_own:
            title = "YOUR SHIPS"
        else:
            title = "ENEMY WATERS"
    else:
        if bship_show_own:
            title = f"P{bship_current_player + 1} SHIPS"
        else:
            title = f"P{bship_current_player + 1} ATTACK"
    title_x = (368 - len(title) * 6 * 3) // 2
    draw_text(display, title, title_x, 10, GREY, 3, CODE_FONT)

    # Show last result (centered)
    if bship_last_result:
        result_color = HIT_COLOR if "HIT" in bship_last_result or "SUNK" in bship_last_result else GREY
        result_x = (368 - len(bship_last_result) * 6 * 2) // 2
        draw_text(display, bship_last_result, result_x, 45, result_color, 2, CODE_FONT)

    # Draw appropriate grid
    if bship_show_own:
        # Show own ships with darker hit color where enemy hit
        draw_bship_grid(bship_current_player, True, own_board=True)
    else:
        target = 1 - bship_current_player
        draw_bship_grid(target, False)

    # Both buttons green
    btn_y = BSHIP_Y + BSHIP_SIZE * BSHIP_CELL + 15
    display.fill_rect(30, btn_y, 150, 50, GREEN)
    btn_text = "ENEMY" if bship_show_own else "MY SHIPS"
    btn_x = 30 + (150 - len(btn_text) * 6 * 2) // 2
    draw_text(display, btn_text, btn_x, btn_y + 15, WHITE, 2, CODE_FONT)

    # Fire/Done button when viewing enemy (both 1v1 and VS AI modes)
    if not bship_show_own:
        display.fill_rect(188, btn_y, 150, 50, GREEN)
        if bship_vs_ai:
            draw_text(display, "FIRE!", 227, btn_y + 15, WHITE, 2, CODE_FONT)
        elif bship_player_fired:
            draw_text(display, "DONE", 230, btn_y + 15, WHITE, 2, CODE_FONT)
        else:
            draw_text(display, "FIRE!", 227, btn_y + 15, WHITE, 2, CODE_FONT)

def draw_bship_pass():
    """Draw pass device screen"""
    display.fill(BLACK)
    if bship_mode == 1:  # Placing phase
        text = f"PASS TO P{bship_current_player + 1}"
    else:  # Battle phase
        text = f"P{bship_current_player + 1} TURN"
    text_x = (368 - len(text) * 6 * 4) // 2
    draw_text(display, text, text_x, 180, GREY, 4, CODE_FONT)
    tap_text = "TAP TO START"
    tap_x = (368 - len(tap_text) * 6 * 2) // 2
    draw_text(display, tap_text, tap_x, 250, DARK_GREY, 2, CODE_FONT)

def draw_bship_ai_turn():
    """Draw AI turn screen - shows your ships and AI TURN text"""
    display.fill(BLACK)
    title = "AI TURN"
    title_x = (368 - len(title) * 6 * 4) // 2
    draw_text(display, title, title_x, 10, GREY, 4, CODE_FONT)
    # Show "YOUR SHIPS" subtitle
    sub = "YOUR SHIPS"
    sub_x = (368 - len(sub) * 6 * 2) // 2
    draw_text(display, sub, sub_x, 50, DARK_GREY, 2, CODE_FONT)
    # Draw player's board showing their ships (own_board=True for darker hit color)
    draw_bship_grid(0, True, own_board=True)

def draw_bship_gameover():
    """Draw game over screen"""
    display.fill(BLACK)
    if bship_vs_ai:
        if bship_winner == 0:
            title = "YOU WIN!"
        else:
            title = "AI WINS!"
    else:
        title = f"P{bship_winner + 1} WINS!"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def launch_battleship():
    global bship_mode
    bship_mode = 0
    draw_bship_menu()

def handle_battleship_touch(tx, ty):
    global bship_mode, bship_vs_ai, bship_difficulty, bship_current_player
    global bship_placing_ship, bship_horizontal, bship_show_own, bship_player_fired
    global bship_last_result, bship_winner, bship_sunk_name
    global bship_easy_wins, bship_easy_losses, bship_med_wins, bship_med_losses
    global bship_hard_wins, bship_hard_losses, bship_p1_wins, bship_p2_wins
    global current_screen, current_app, last_time_text

    btn_y = BSHIP_Y + BSHIP_SIZE * BSHIP_CELL + 15  # 80 + 224 + 15 = 319
    if bship_mode == 0:  # Menu
        if 150 <= ty <= 220:  # 1v1 button
            bship_vs_ai = False
            bship_reset()
            draw_bship_placing()
        elif 250 <= ty <= 320:  # VS AI button
            bship_vs_ai = True
            bship_mode = 6  # Go to difficulty select
            draw_bship_difficulty()
    elif bship_mode == 6:  # Difficulty select
        if 140 <= ty <= 200:  # Easy
            bship_difficulty = 0
            bship_reset()
            bship_ai_place_ships()
            draw_bship_placing()
        elif 220 <= ty <= 280:  # Medium
            bship_difficulty = 1
            bship_reset()
            bship_ai_place_ships()
            draw_bship_placing()
        elif 300 <= ty <= 360:  # Hard
            bship_difficulty = 2
            bship_reset()
            bship_ai_place_ships()
            draw_bship_placing()
    elif bship_mode == 4:  # Pass screen
        if bship_placing_ship < len(BSHIP_SHIPS):
            bship_mode = 1
            draw_bship_placing()
        else:
            bship_mode = 2
            bship_show_own = False
            bship_last_result = ""
            bship_player_fired = False
            draw_bship_battle()
    elif bship_mode == 1:  # Placing ships
        # Check button (x=84-284, y=319-374)
        if btn_y <= ty <= btn_y + 55 and 84 <= tx <= 284:
            if bship_placing_ship >= len(BSHIP_SHIPS):
                # DONE button - proceed to next phase
                if bship_vs_ai or bship_current_player == 1:
                    # Start battle
                    bship_current_player = 0
                    bship_mode = 2
                    bship_show_own = False
                    bship_player_fired = False
                    draw_bship_battle()
                else:
                    # Switch to player 2
                    bship_current_player = 1
                    bship_placing_ship = 0
                    bship_mode = 4  # Pass screen
                    draw_bship_pass()
            else:
                # ROTATE button - rotate last placed ship
                if len(bship_ship_pos[bship_current_player]) > 0:
                    bship_rotate_last_ship(bship_current_player)
                    draw_bship_placing()
        # Check grid tap
        elif BSHIP_Y <= ty < BSHIP_Y + BSHIP_SIZE * BSHIP_CELL:
            if bship_placing_ship < len(BSHIP_SHIPS):
                col = (tx - BSHIP_X) // BSHIP_CELL
                row = (ty - BSHIP_Y) // BSHIP_CELL
                if 0 <= col < BSHIP_SIZE and 0 <= row < BSHIP_SIZE:
                    ship_name, ship_len = BSHIP_SHIPS[bship_placing_ship]
                    if bship_can_place(bship_current_player, row, col, ship_len, bship_horizontal):
                        bship_place_ship(bship_current_player, row, col, ship_len, bship_horizontal)
                        bship_placing_ship += 1
                        draw_bship_placing()
    elif bship_mode == 2:  # Battle
        # Check toggle view button (x=30-180, y=btn_y to btn_y+50)
        if btn_y <= ty <= btn_y + 50 and 30 <= tx <= 180:
            bship_show_own = not bship_show_own
            draw_bship_battle()
        # Check done button (1v1 only, must have fired, x=188-338)
        elif not bship_vs_ai and bship_player_fired and btn_y <= ty <= btn_y + 50 and 188 <= tx <= 338:
            # Switch turns
            bship_current_player = 1 - bship_current_player
            bship_show_own = False
            bship_last_result = ""
            bship_player_fired = False
            bship_mode = 4
            draw_bship_pass()
        # Check grid tap (fire!) - only if haven't fired yet
        elif not bship_show_own and not bship_player_fired and BSHIP_Y <= ty < BSHIP_Y + BSHIP_SIZE * BSHIP_CELL:
            col = (tx - BSHIP_X) // BSHIP_CELL
            row = (ty - BSHIP_Y) // BSHIP_CELL
            if 0 <= col < BSHIP_SIZE and 0 <= row < BSHIP_SIZE:
                result, sunk_ship = bship_fire(bship_current_player, row, col)
                if result >= 0:  # Valid shot
                    bship_player_fired = True
                    if result == 0:
                        bship_last_result = "MISS!"
                    elif result == 1:
                        bship_last_result = "HIT!"
                    elif result == 2:
                        bship_last_result = f"SUNK {sunk_ship}!"
                    # Check for win
                    target = 1 - bship_current_player
                    if bship_all_sunk(target):
                        bship_winner = bship_current_player
                        bship_mode = 3
                        # Update stats
                        if bship_vs_ai:
                            if bship_difficulty == 0:
                                bship_easy_wins += 1
                            elif bship_difficulty == 1:
                                bship_med_wins += 1
                            else:
                                bship_hard_wins += 1
                        else:
                            if bship_winner == 0:
                                bship_p1_wins += 1
                            else:
                                bship_p2_wins += 1
                        save_bship_stats()
                        draw_bship_gameover()
                    elif bship_vs_ai:
                        # Show player's result briefly
                        draw_bship_battle()
                        time.sleep_ms(1000)
                        # Show AI turn screen
                        draw_bship_ai_turn()
                        time.sleep_ms(1500)
                        # AI fires
                        ai_row, ai_col = bship_ai_fire()
                        ai_result, ai_sunk = bship_fire(1, ai_row, ai_col)
                        if ai_result == 0:
                            bship_last_result = "AI MISSED!"
                        elif ai_result == 1:
                            bship_last_result = "AI HIT YOU!"
                        elif ai_result == 2:
                            bship_last_result = f"AI SUNK {ai_sunk}!"
                        if bship_all_sunk(0):
                            bship_winner = 1
                            bship_mode = 3
                            # AI wins - track by difficulty
                            if bship_difficulty == 0:
                                bship_easy_losses += 1
                            elif bship_difficulty == 1:
                                bship_med_losses += 1
                            else:
                                bship_hard_losses += 1
                            save_bship_stats()
                            draw_bship_gameover()
                        else:
                            bship_player_fired = False  # Reset for next turn
                            draw_bship_battle()
                    else:
                        draw_bship_battle()
    elif bship_mode == 3:  # Game over
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                bship_mode = 0
                draw_bship_menu()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("BATTLESHIP")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""

def draw_bship_stats():
    display.fill(BLACK)
    draw_text(display, "BATTLESHIP", 90, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32  # Row height

    # EASY section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (EASY)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {bship_easy_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {bship_easy_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # MEDIUM section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (MED)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {bship_med_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {bship_med_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # HARD section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS AI (HARD)", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {bship_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {bship_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh

    # PvP section
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P1 WINS: {bship_p1_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"P2 WINS: {bship_p2_wins}", 30, y + 8, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
