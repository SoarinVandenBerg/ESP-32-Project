# ===== BRICK BREAKER GAME =====
# Block types: 0=empty, 1=normal, 2=ball (spawns extra ball), 3=TNT (explodes), 4=wide (widens paddle)
BRICK_COLS = 6
BRICK_ROWS = 3
BRICK_W = 56  # Block width
BRICK_H = 25  # Block height
BRICK_GAP = 4
BRICK_TOP = 60  # Y offset for top of bricks
BRICK_LEFT = (368 - (BRICK_COLS * (BRICK_W + BRICK_GAP) - BRICK_GAP)) // 2

# Green color palette for normal bricks (from 2048)
BRICK_GREENS = [
    make_color(0, 130, 0),   # Light green
    make_color(0, 107, 0),
    make_color(0, 83, 0),
    make_color(0, 60, 0),
    make_color(0, 37, 0),    # Dark green
]
BRICK_COLOR_BALL = make_color(50, 200, 50)   # Bright lime green for ball block
BRICK_COLOR_TNT = make_color(80, 160, 0)    # Yellow-green for TNT
BRICK_COLOR_WIDE = make_color(0, 50, 0)     # Dark green for wide paddle

# Paddle settings
BRICK_PADDLE_W = 70
BRICK_PADDLE_H = 12
BRICK_PADDLE_Y = 420
BRICK_PADDLE_SPEED = 8

# Ball settings
BRICK_BALL_SIZE = 10
BRICK_BALL_SPEED = 7

# Game state
brick_bricks = []  # 2D array of block types
brick_paddle_x = 184 - BRICK_PADDLE_W // 2
brick_paddle_w = BRICK_PADDLE_W  # Current paddle width (can change with power-up)
brick_old_paddle_x = brick_paddle_x  # For dirty-region updates
brick_old_paddle_w = brick_paddle_w
brick_wide_timer = 0  # Ticks until paddle returns to normal width
brick_balls = []  # List of [x, y, dx, dy] for each ball (use lists for mutability)
brick_old_balls = []  # Previous ball positions for dirty-region updates
brick_score = 0
brick_last_score = -1  # For dirty-region score updates
brick_level = 1
brick_mode = 0  # 0=menu, 1=playing, 2=game over, 3=level complete
brick_speed_mult = 1.0  # Ball speed multiplier (slowly increases)
brick_destroyed = []  # List of (row, col) bricks destroyed this frame
brick_serving = False  # Ball on paddle waiting for tap to launch

def brick_generate_level():
    """Generate a new level of bricks"""
    global brick_bricks
    brick_bricks = []
    for row in range(BRICK_ROWS):
        brick_row = []
        for col in range(BRICK_COLS):
            # 70% normal, 10% ball, 10% TNT, 10% wide
            r = random.randint(1, 100)
            if r <= 70:
                brick_row.append(1)  # Normal
            elif r <= 80:
                brick_row.append(2)  # Ball
            elif r <= 90:
                brick_row.append(3)  # TNT
            else:
                brick_row.append(4)  # Wide
        brick_bricks.append(brick_row)

def init_brick_game():
    """Initialize a new game"""
    global brick_paddle_x, brick_paddle_w, brick_balls, brick_score, brick_level
    global brick_mode, brick_tnt_list, brick_wide_timer, brick_last_score
    global brick_old_paddle_x, brick_old_paddle_w, brick_old_balls, brick_destroyed
    global brick_speed_mult, brick_serving
    brick_paddle_x = 184 - BRICK_PADDLE_W // 2
    brick_paddle_w = BRICK_PADDLE_W
    brick_old_paddle_x = brick_paddle_x
    brick_old_paddle_w = brick_paddle_w
    brick_wide_timer = 0
    brick_speed_mult = 1.0
    brick_balls = [[184.0, float(BRICK_PADDLE_Y - BRICK_BALL_SIZE - 2), 0.0, 0.0]]
    brick_old_balls = []
    brick_score = 0
    brick_last_score = -1
    brick_level = 1
    brick_mode = 1
    brick_tnt_list = []
    brick_destroyed = []
    brick_serving = True
    brick_generate_level()

def draw_brick_menu():
    """Draw the brick breaker menu screen"""
    display.fill(BLACK)
    # "BRICK" = 5 chars * 6 * 5 = 150px
    draw_text(display, "BRICK", (368 - 150) // 2, 50, GREEN, 5, CODE_FONT)
    # "BREAKER" = 7 chars * 6 * 5 = 210px
    draw_text(display, "BREAKER", (368 - 210) // 2, 110, GREEN, 5, CODE_FONT)
    # High score - centered
    hs_text = f"HIGH SCORE: {brick_high_score}"
    draw_text(display, hs_text, (368 - len(hs_text) * 12) // 2, 210, GREY, 2, CODE_FONT)
    # Start button
    display.fill_rect(84, 320, 200, 60, GREEN)
    # "START" = 5 chars * 6 * 3 = 90px
    draw_text(display, "START", 84 + (200 - 90) // 2, 338, WHITE, 3, CODE_FONT)

def get_brick_color(block_type, row):
    """Get the color for a brick based on type and row"""
    if block_type == 1:  # Normal - use green gradient by row
        return BRICK_GREENS[row % len(BRICK_GREENS)]
    elif block_type == 2:  # Ball
        return BRICK_COLOR_BALL
    elif block_type == 3:  # TNT
        return BRICK_COLOR_TNT
    elif block_type == 4:  # Wide
        return BRICK_COLOR_WIDE
    return BLACK

def draw_single_brick(row, col):
    """Draw a single brick"""
    if brick_bricks[row][col] != 0:
        x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
        y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
        color = get_brick_color(brick_bricks[row][col], row)
        display.fill_rect(x, y, BRICK_W, BRICK_H, color)
        # Draw type indicator
        if brick_bricks[row][col] == 2:  # Ball - draw circle
            display.fill_circle(x + BRICK_W // 2, y + BRICK_H // 2, 6, BLACK)
        elif brick_bricks[row][col] == 3:  # TNT - draw X
            cx, cy = x + BRICK_W // 2, y + BRICK_H // 2
            for i in range(-4, 5):
                display.fill_rect(cx + i, cy + i, 2, 2, BLACK)
                display.fill_rect(cx + i, cy - i, 2, 2, BLACK)
        elif brick_bricks[row][col] == 4:  # Wide - draw arrows
            cx, cy = x + BRICK_W // 2, y + BRICK_H // 2
            display.fill_rect(cx - 10, cy - 1, 20, 3, BLACK)

def erase_brick(row, col):
    """Erase a brick (draw black)"""
    x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
    y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
    display.fill_rect(x, y, BRICK_W, BRICK_H, BLACK)

def draw_brick_game():
    """Draw the full game screen (initial draw only)"""
    global brick_last_score, brick_old_paddle_x, brick_old_paddle_w, brick_old_balls
    display.fill(BLACK)
    # Draw header (safe from rounded corners)
    draw_text(display, f"SCORE:{brick_score}", 20, 10, GREY, 2, CODE_FONT)
    draw_text(display, f"LVL:{brick_level}", 280, 10, GREY, 2, CODE_FONT)
    brick_last_score = brick_score
    # Draw bricks
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            draw_single_brick(row, col)
    # Draw paddle
    display.fill_rect(brick_paddle_x, BRICK_PADDLE_Y, brick_paddle_w, BRICK_PADDLE_H, GREEN)
    brick_old_paddle_x = brick_paddle_x
    brick_old_paddle_w = brick_paddle_w
    # Draw balls
    brick_old_balls = []
    for ball in brick_balls:
        bx, by = int(ball[0]), int(ball[1])
        display.fill_rect(bx, by, BRICK_BALL_SIZE, BRICK_BALL_SIZE, GREEN)
        brick_old_balls.append([bx, by])

def update_brick_score():
    """Update score display only if changed"""
    global brick_last_score
    if brick_score != brick_last_score:
        # Erase old score area
        display.fill_rect(15, 10, 160, 20, BLACK)
        draw_text(display, f"SCORE:{brick_score}", 20, 10, GREY, 2, CODE_FONT)
        brick_last_score = brick_score

def update_brick_paddle():
    """Update paddle display using dirty-region"""
    global brick_old_paddle_x, brick_old_paddle_w
    if brick_paddle_x != brick_old_paddle_x or brick_paddle_w != brick_old_paddle_w:
        # Erase old paddle
        display.fill_rect(brick_old_paddle_x, BRICK_PADDLE_Y, brick_old_paddle_w, BRICK_PADDLE_H, BLACK)
        # Draw new paddle
        display.fill_rect(brick_paddle_x, BRICK_PADDLE_Y, brick_paddle_w, BRICK_PADDLE_H, GREEN)
        brick_old_paddle_x = brick_paddle_x
        brick_old_paddle_w = brick_paddle_w

def update_brick_balls():
    """Update ball displays using dirty-region"""
    global brick_old_balls
    # Erase old ball positions
    for old_pos in brick_old_balls:
        display.fill_rect(old_pos[0], old_pos[1], BRICK_BALL_SIZE, BRICK_BALL_SIZE, BLACK)
    # Draw new ball positions
    brick_old_balls = []
    for ball in brick_balls:
        bx, by = int(ball[0]), int(ball[1])
        display.fill_rect(bx, by, BRICK_BALL_SIZE, BRICK_BALL_SIZE, GREEN)
        brick_old_balls.append([bx, by])

def update_brick_destroyed():
    """Erase destroyed bricks"""
    global brick_destroyed
    for row, col in brick_destroyed:
        erase_brick(row, col)
    brick_destroyed = []

def draw_brick_gameover():
    """Draw game over screen"""
    display.fill(BLACK)
    title = "GAME OVER"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    score_text = f"SCORE: {brick_score}"
    score_w = len(score_text) * 6 * 3
    draw_text(display, score_text, (368 - score_w) // 2, 160, GREY, 3, CODE_FONT)
    if brick_score >= brick_high_score and brick_score > 0:
        best_text = "NEW BEST!"
        best_w = len(best_text) * 6 * 2
        draw_text(display, best_text, (368 - best_w) // 2, 200, GREEN, 2, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "RETRY"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def draw_brick_levelup():
    """Draw level complete screen"""
    display.fill(BLACK)
    title = "CLEARED!"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    level_text = f"LEVEL {brick_level}"
    level_w = len(level_text) * 6 * 3
    draw_text(display, level_text, (368 - level_w) // 2, 160, GREY, 3, CODE_FONT)
    score_text = f"SCORE: {brick_score}"
    score_w = len(score_text) * 6 * 2
    draw_text(display, score_text, (368 - score_w) // 2, 200, GREY, 2, CODE_FONT)
    display.fill_rect(109, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "CONTINUE"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 109 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def brick_check_collision(ball):
    """Check ball collision with bricks, update ball velocity, return if hit"""
    global brick_score, brick_balls, brick_tnt_list, brick_paddle_w, brick_wide_timer, brick_destroyed
    bx, by, bdx, bdy = ball[0], ball[1], ball[2], ball[3]
    # Check each brick
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            if brick_bricks[row][col] != 0:
                brick_x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
                brick_y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
                # Check if ball overlaps brick
                if (bx + BRICK_BALL_SIZE > brick_x and bx < brick_x + BRICK_W and
                    by + BRICK_BALL_SIZE > brick_y and by < brick_y + BRICK_H):
                    block_type = brick_bricks[row][col]
                    brick_bricks[row][col] = 0  # Remove brick
                    brick_destroyed.append((row, col))  # Mark for erase
                    brick_score += 10
                    # Handle special blocks
                    if block_type == 2:  # Ball - spawn extra ball
                        brick_balls.append([bx, by, -bdx, bdy])
                    elif block_type == 3:  # TNT - start flash timer
                        brick_tnt_list.append((col, row, time.ticks_ms()))
                    elif block_type == 4:  # Wide - widen paddle
                        brick_paddle_w = BRICK_PADDLE_W + 40
                        brick_wide_timer = time.ticks_ms()
                    # Determine bounce direction
                    ball_cx = bx + BRICK_BALL_SIZE // 2
                    ball_cy = by + BRICK_BALL_SIZE // 2
                    brick_cx = brick_x + BRICK_W // 2
                    brick_cy = brick_y + BRICK_H // 2
                    # Bounce based on which side was hit
                    if abs(ball_cx - brick_cx) * BRICK_H > abs(ball_cy - brick_cy) * BRICK_W:
                        ball[2] = -bdx  # Side hit
                    else:
                        ball[3] = -bdy  # Top/bottom hit
                    return True
    return False

def brick_process_tnt():
    """Process TNT explosions - flash for 2s then explode"""
    global brick_tnt_list, brick_score, brick_destroyed
    now = time.ticks_ms()
    remaining = []
    for col, row, start_time in brick_tnt_list:
        elapsed = time.ticks_diff(now, start_time)
        if elapsed >= 2000:
            # Explode! Destroy up to 4 random bricks around it
            targets = []
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < BRICK_ROWS and 0 <= nc < BRICK_COLS:
                        if brick_bricks[nr][nc] != 0:
                            targets.append((nr, nc))
            # Always chain TNT neighbors first, then randomly pick up to 4 others
            tnt_targets = []
            other_targets = []
            for t in targets:
                if brick_bricks[t[0]][t[1]] == 3:
                    tnt_targets.append(t)
                else:
                    other_targets.append(t)
            # Chain all neighboring TNTs
            for r, c in tnt_targets:
                brick_tnt_list.append((c, r, now))
                brick_bricks[r][c] = 0
                brick_destroyed.append((r, c))
                brick_score += 5
            # Destroy up to 4 random non-TNT bricks
            destroyed = 0
            while other_targets and destroyed < 4:
                idx = random.randint(0, len(other_targets) - 1)
                r, c = other_targets.pop(idx)
                brick_bricks[r][c] = 0
                brick_destroyed.append((r, c))
                brick_score += 5
                destroyed += 1
            # Remove the TNT brick itself and clear it
            brick_bricks[row][col] = 0
            brick_destroyed.append((row, col))
            # Clear the white flash immediately
            x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
            y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
            display.fill_rect(x, y, BRICK_W, BRICK_H, BLACK)
        else:
            # Flash white while counting down
            flash_period = 300  # Flash every 300ms
            if (elapsed // flash_period) % 2 == 0:
                # Draw white flash
                x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
                y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
                display.fill_rect(x, y, BRICK_W, BRICK_H, WHITE)
            else:
                # Draw normal TNT color
                x = BRICK_LEFT + col * (BRICK_W + BRICK_GAP)
                y = BRICK_TOP + row * (BRICK_H + BRICK_GAP)
                display.fill_rect(x, y, BRICK_W, BRICK_H, BRICK_COLOR_TNT)
                # Draw X indicator
                cx, cy = x + BRICK_W // 2, y + BRICK_H // 2
                for i in range(-4, 5):
                    display.fill_rect(cx + i, cy + i, 2, 2, BLACK)
                    display.fill_rect(cx + i, cy - i, 2, 2, BLACK)
            remaining.append((col, row, start_time))
    brick_tnt_list = remaining

def brick_check_level_complete():
    """Check if all bricks are destroyed"""
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            if brick_bricks[row][col] != 0:
                return False
    return True

def brick_update():
    """Update game state - move balls, check collisions"""
    global brick_balls, brick_mode, brick_paddle_w, brick_wide_timer
    global brick_high_score, brick_levels_cleared, brick_speed_mult
    # Check wide paddle timeout (15 seconds)
    if brick_wide_timer > 0 and time.ticks_diff(time.ticks_ms(), brick_wide_timer) > 15000:
        brick_paddle_w = BRICK_PADDLE_W
        brick_wide_timer = 0
    # Process TNT
    brick_process_tnt()
    # Update each ball
    new_balls = []
    for ball in brick_balls:
        # Move ball (apply speed multiplier)
        ball[0] += ball[2] * brick_speed_mult
        ball[1] += ball[3] * brick_speed_mult
        bx, by = ball[0], ball[1]
        # Wall collisions
        if bx <= 0:
            ball[0] = 0
            ball[2] = abs(ball[2])
        elif bx >= 368 - BRICK_BALL_SIZE:
            ball[0] = 368 - BRICK_BALL_SIZE
            ball[2] = -abs(ball[2])
        if by <= 40:  # Top wall (below header)
            ball[1] = 40
            ball[3] = abs(ball[3])
        # Paddle collision
        if (by + BRICK_BALL_SIZE >= BRICK_PADDLE_Y and by < BRICK_PADDLE_Y + BRICK_PADDLE_H and
            bx + BRICK_BALL_SIZE >= brick_paddle_x and bx <= brick_paddle_x + brick_paddle_w):
            ball[1] = BRICK_PADDLE_Y - BRICK_BALL_SIZE
            ball[3] = -abs(ball[3])
            # Angle based on where ball hit paddle
            hit_pos = (bx + BRICK_BALL_SIZE // 2) - (brick_paddle_x + brick_paddle_w // 2)
            ball[2] = hit_pos * 0.15 + (ball[2] * 0.5)
            # Clamp speed
            if abs(ball[2]) < 2:
                ball[2] = 2 if ball[2] >= 0 else -2
            if abs(ball[2]) > 7:
                ball[2] = 7 if ball[2] > 0 else -7
            # Very slowly speed up (0.5% faster each paddle hit, max 2x speed)
            if brick_speed_mult < 2.0:
                brick_speed_mult += 0.005
        # Brick collision
        brick_check_collision(ball)
        # Check if ball fell off bottom
        if ball[1] > 448:
            continue  # Don't add to new_balls (ball lost)
        new_balls.append(ball)
    brick_balls = new_balls
    # Check game over (no balls left)
    if len(brick_balls) == 0:
        brick_mode = 2  # Game over
        if brick_score > brick_high_score:
            brick_high_score = brick_score
            save_brick_stats()
        return
    # Check level complete
    if brick_check_level_complete() and len(brick_tnt_list) == 0:
        brick_mode = 3  # Level complete

def brick_next_level():
    """Start next level"""
    global brick_level, brick_mode, brick_balls, brick_paddle_w, brick_wide_timer
    global brick_levels_cleared, brick_serving, brick_destroyed
    brick_level += 1
    if brick_level > brick_levels_cleared:
        brick_levels_cleared = brick_level
    save_brick_stats()
    brick_paddle_w = BRICK_PADDLE_W
    brick_wide_timer = 0
    brick_destroyed = []  # Clear destroyed list from previous level
    brick_paddle_cx = brick_paddle_x + brick_paddle_w // 2
    brick_balls = [[float(brick_paddle_cx), float(BRICK_PADDLE_Y - BRICK_BALL_SIZE - 2), 0.0, 0.0]]
    brick_generate_level()
    brick_serving = True
    brick_mode = 1

def launch_brick():
    global brick_mode
    brick_mode = 0
    draw_brick_menu()

def handle_brick_touch(tx, ty):
    global brick_mode, current_screen, current_app, last_time_text
    if brick_mode == 0:  # Menu - tap start button
        if 320 <= ty <= 380 and 84 <= tx <= 284:
            init_brick_game()
            draw_brick_game()
    elif brick_mode == 2:  # Game over - check buttons
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # RETRY button
                init_brick_game()
                draw_brick_game()
            elif 193 <= tx <= 343:  # EXIT button
                track_app_exit("BRICK BREAKER")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
    elif brick_mode == 3:  # Level complete - continue button
        if 245 <= ty <= 315 and 109 <= tx <= 259:
            brick_next_level()
            draw_brick_game()

def loop_brick():
    global brick_paddle_x, brick_paddle_w, brick_tapped, hold_start_time, brick_serving, brick_balls, brick_mode, current_screen, current_app, last_time_text
    # Handle touch for paddle movement (continuous)
    touch = read_touch()
    brick_tapped = False
    if touch is not None:
        tx, ty = touch
        target_x = tx - brick_paddle_w // 2
        target_x = max(0, min(368 - brick_paddle_w, target_x))
        if target_x < brick_paddle_x:
            brick_paddle_x = max(target_x, brick_paddle_x - BRICK_PADDLE_SPEED)
        elif target_x > brick_paddle_x:
            brick_paddle_x = min(target_x, brick_paddle_x + BRICK_PADDLE_SPEED)
        if hold_start_time is None:
            hold_start_time = time.ticks_ms()
            brick_tapped = True
        elif time.ticks_diff(time.ticks_ms(), hold_start_time) > 10000:
            track_app_exit("BRICK BREAKER")
            current_screen = SCREEN_MENU
            current_app = -1
            hold_start_time = None
            draw_menu_screen()
            last_time_text = ""
    else:
        hold_start_time = None
    # Serve: ball follows paddle until tapped
    if brick_serving:
        paddle_cx = brick_paddle_x + brick_paddle_w // 2
        if brick_balls:
            brick_balls[0][0] = float(paddle_cx)
            brick_balls[0][1] = float(BRICK_PADDLE_Y - BRICK_BALL_SIZE - 2)
        if brick_tapped:
            if brick_balls:
                brick_balls[0][2] = float(BRICK_BALL_SPEED)
                brick_balls[0][3] = float(-BRICK_BALL_SPEED)
            brick_serving = False
    # Update game state (skip ball physics while serving)
    if not brick_serving:
        brick_update()
    # Dirty-region updates (only redraw what changed)
    if brick_mode == 1:
        update_brick_destroyed()  # Erase destroyed bricks
        update_brick_paddle()     # Update paddle if moved
        update_brick_balls()      # Update ball positions
        update_brick_score()      # Update score if changed
    elif brick_mode == 2:
        draw_brick_gameover()
    elif brick_mode == 3:
        draw_brick_levelup()
    time.sleep_ms(16)  # ~60fps game speed

def draw_brick_stats():
    display.fill(BLACK)
    draw_text(display, "BREAKER STATS", 70, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    hs_text = f"HIGH SCORE: {brick_high_score}"
    draw_text(display, hs_text, 30, y_start + 15, GREY, 3, CODE_FONT)
    y2 = y_start + row_height
    display.fill_rect(20, y2, 328, 3, DARK_GREY)
    lc_text = f"LEVELS: {brick_levels_cleared}"
    draw_text(display, lc_text, 30, y2 + 15, GREY, 3, CODE_FONT)
    y_final = y2 + row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
