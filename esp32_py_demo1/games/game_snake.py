# ===== SNAKE GAME =====
SNAKE_CELL = 16  # Size of each cell
SNAKE_COLS = 368 // SNAKE_CELL  # 23 columns
SNAKE_ROWS = (390 - 50) // SNAKE_CELL  # 21 rows (leave room for score)
SNAKE_AREA_TOP = 50
SNAKE_AREA_LEFT = (368 - SNAKE_COLS * SNAKE_CELL) // 2  # Center horizontally

snake_body = []  # List of (col, row) tuples, head is first
snake_dir = (1, 0)  # (dx, dy) - starts moving right
snake_food = None  # (col, row) of food
snake_score = 0
snake_high_score = 0
snake_mode = 0  # 0=ready, 1=playing, 2=game_over
snake_speed = 150  # ms between moves
snake_last_move = 0
snake_dir_changed = False  # Track if direction changed this move cycle

def snake_reset():
    """Reset snake game to initial state"""
    global snake_body, snake_dir, snake_food, snake_score, snake_mode, snake_last_move, snake_dir_changed
    # Start in middle, 3 segments long
    mid_col = SNAKE_COLS // 2
    mid_row = SNAKE_ROWS // 2
    snake_body = [(mid_col, mid_row), (mid_col - 1, mid_row), (mid_col - 2, mid_row)]
    snake_dir = (1, 0)  # Moving right
    snake_score = 0
    snake_mode = 0
    snake_last_move = 0
    snake_dir_changed = False
    snake_spawn_food()

def snake_spawn_food():
    """Spawn food at random empty location"""
    global snake_food
    while True:
        col = random.randint(0, SNAKE_COLS - 1)
        row = random.randint(0, SNAKE_ROWS - 1)
        if (col, row) not in snake_body:
            snake_food = (col, row)
            break

def snake_update():
    """Move snake one step, return True if alive"""
    global snake_body, snake_score, snake_mode, snake_high_score

    # Calculate new head position
    head_col, head_row = snake_body[0]
    new_col = head_col + snake_dir[0]
    new_row = head_row + snake_dir[1]

    # Check wall collision
    if new_col < 0 or new_col >= SNAKE_COLS or new_row < 0 or new_row >= SNAKE_ROWS:
        snake_mode = 2  # Game over
        if snake_score > snake_high_score:
            snake_high_score = snake_score
        return False

    # Check self collision (excluding tail which will move)
    if (new_col, new_row) in snake_body[:-1]:
        snake_mode = 2
        if snake_score > snake_high_score:
            snake_high_score = snake_score
        return False

    # Move snake - add new head
    snake_body.insert(0, (new_col, new_row))

    # Check food collision
    if (new_col, new_row) == snake_food:
        snake_score += 10
        snake_spawn_food()
        # Don't remove tail - snake grows
    else:
        # Remove tail
        snake_body.pop()

    return True

def draw_snake_cell(col, row, color):
    """Draw a single cell"""
    x = SNAKE_AREA_LEFT + col * SNAKE_CELL
    y = SNAKE_AREA_TOP + row * SNAKE_CELL
    # Draw with small gap for grid effect
    display.fill_rect(x + 1, y + 1, SNAKE_CELL - 2, SNAKE_CELL - 2, color)

def draw_snake_grid():
    """Draw the faint grid lines"""
    grid_color = make_color(20, 20, 20)  # Very dark grey
    # Vertical lines
    for c in range(SNAKE_COLS + 1):
        x = SNAKE_AREA_LEFT + c * SNAKE_CELL
        display.fill_rect(x, SNAKE_AREA_TOP, 1, SNAKE_ROWS * SNAKE_CELL, grid_color)
    # Horizontal lines
    for r in range(SNAKE_ROWS + 1):
        y = SNAKE_AREA_TOP + r * SNAKE_CELL
        display.fill_rect(SNAKE_AREA_LEFT, y, SNAKE_COLS * SNAKE_CELL, 1, grid_color)

def draw_snake_game():
    """Draw the full snake game screen"""
    display.fill(BLACK)

    # Draw score (shifted to edges)
    draw_text(display, f"{snake_score}", 15, 15, GREEN, 3, CODE_FONT)
    draw_text(display, f"BEST:{snake_high_score}", 220, 20, GREY, 2, CODE_FONT)

    # Draw border box around playing area
    box_x = SNAKE_AREA_LEFT - 2
    box_y = SNAKE_AREA_TOP - 2
    box_w = SNAKE_COLS * SNAKE_CELL + 4
    box_h = SNAKE_ROWS * SNAKE_CELL + 4
    display.fill_rect(box_x, box_y, box_w, 2, DARK_GREY)  # Top
    display.fill_rect(box_x, box_y + box_h - 2, box_w, 2, DARK_GREY)  # Bottom
    display.fill_rect(box_x, box_y, 2, box_h, DARK_GREY)  # Left
    display.fill_rect(box_x + box_w - 2, box_y, 2, box_h, DARK_GREY)  # Right

    # Draw grid
    draw_snake_grid()

    # Draw snake
    for i, (col, row) in enumerate(snake_body):
        if i == 0:
            draw_snake_cell(col, row, GREEN)  # Head is bright
        else:
            draw_snake_cell(col, row, make_color(0, 150, 0))  # Body darker

    # Draw food (light green)
    if snake_food:
        draw_snake_cell(snake_food[0], snake_food[1], make_color(150, 255, 150))

def draw_snake_gameover():
    """Draw game over screen with buttons"""
    display.fill(BLACK)
    title = "GAME OVER"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    score_text = f"SCORE: {snake_score}"
    score_w = len(score_text) * 6 * 3
    draw_text(display, score_text, (368 - score_w) // 2, 160, GREY, 3, CODE_FONT)
    best_text = f"BEST: {snake_high_score}"
    best_w = len(best_text) * 6 * 2
    draw_text(display, best_text, (368 - best_w) // 2, 200, GREY, 2, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "RETRY"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def snake_move_head():
    """Redraw just the head and erase old tail for smooth updates"""
    # Draw new head
    head_col, head_row = snake_body[0]
    draw_snake_cell(head_col, head_row, GREEN)

    # Make previous head darker (now body)
    if len(snake_body) > 1:
        prev_col, prev_row = snake_body[1]
        draw_snake_cell(prev_col, prev_row, make_color(0, 150, 0))

def snake_erase_tail(old_tail):
    """Erase the old tail position"""
    col, row = old_tail
    x = SNAKE_AREA_LEFT + col * SNAKE_CELL
    y = SNAKE_AREA_TOP + row * SNAKE_CELL
    display.fill_rect(x + 1, y + 1, SNAKE_CELL - 2, SNAKE_CELL - 2, BLACK)
    # Redraw grid lines at this cell
    grid_color = make_color(20, 20, 20)
    display.fill_rect(x, y, 1, SNAKE_CELL, grid_color)  # Left line
    display.fill_rect(x, y, SNAKE_CELL, 1, grid_color)  # Top line

def snake_draw_food():
    """Draw food (light green apple)"""
    if snake_food:
        draw_snake_cell(snake_food[0], snake_food[1], make_color(150, 255, 150))

def launch_snake():
    snake_reset()
    draw_snake_game()

def handle_snake_touch(tx, ty):
    global snake_mode, snake_dir, snake_last_move, current_screen, current_app, last_time_text
    if snake_mode == 0:  # Ready - swipe to start
        direction = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
        if direction >= 0:
            # Set initial direction based on swipe
            if direction == 0:  # Up
                snake_dir = (0, -1)
            elif direction == 1:  # Right
                snake_dir = (1, 0)
            elif direction == 2:  # Down
                snake_dir = (0, 1)
            elif direction == 3:  # Left
                snake_dir = (-1, 0)
            snake_mode = 1  # Start playing
            snake_last_move = time.ticks_ms()
    elif snake_mode == 1:  # Playing - swipe to change direction
        direction = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
        if direction >= 0:
            # Prevent 180-degree turns
            if direction == 0 and snake_dir != (0, 1):  # Up
                snake_dir = (0, -1)
            elif direction == 1 and snake_dir != (-1, 0):  # Right
                snake_dir = (1, 0)
            elif direction == 2 and snake_dir != (0, -1):  # Down
                snake_dir = (0, 1)
            elif direction == 3 and snake_dir != (1, 0):  # Left
                snake_dir = (-1, 0)
    elif snake_mode == 2:  # Game over - buttons
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # RETRY
                snake_reset()
                draw_snake_game()
            elif 193 <= tx <= 343:  # EXIT
                track_app_exit("SNAKE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""

def loop_snake():
    global snake_last_move, snake_score, snake_high_score, snake_dir, snake_mode, snake_dir_changed

    # Check for swipes continuously (while playing)
    if snake_mode == 1 and not snake_dir_changed:
        touch = read_touch()
        if touch and swipe_start_x >= 0:
            tx, ty = touch
            direction = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
            if direction >= 0:
                # Prevent 180-degree turns, only change once per move
                if direction == 0 and snake_dir != (0, 1):  # Up
                    snake_dir = (0, -1)
                    snake_dir_changed = True
                elif direction == 1 and snake_dir != (-1, 0):  # Right
                    snake_dir = (1, 0)
                    snake_dir_changed = True
                elif direction == 2 and snake_dir != (0, -1):  # Down
                    snake_dir = (0, 1)
                    snake_dir_changed = True
                elif direction == 3 and snake_dir != (1, 0):  # Left
                    snake_dir = (-1, 0)
                    snake_dir_changed = True

    now = time.ticks_ms()
    if time.ticks_diff(now, snake_last_move) >= snake_speed:
        snake_last_move = now
        snake_dir_changed = False  # Allow direction change for next move
        # Store old tail before update
        old_tail = snake_body[-1] if snake_body else None
        old_food = snake_food

        if snake_update():
            # Still alive - draw updates
            snake_move_head()
            # Erase old tail if it was removed (didn't eat food)
            if old_tail and old_tail not in snake_body:
                snake_erase_tail(old_tail)
            # If food changed (eaten), draw new food
            if snake_food != old_food:
                snake_draw_food()
            # Update score display
            display.fill_rect(10, 10, 180, 35, BLACK)
            draw_text(display, f"{snake_score}", 15, 15, GREEN, 3, CODE_FONT)
        else:
            # Game over - save high score and show game over screen
            if snake_score >= snake_high_score and snake_score > 0:
                save_snake_stats()
            draw_snake_gameover()

def draw_snake_stats():
    display.fill(BLACK)
    draw_text(display, "SNAKE STATS", 90, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    hs_text = f"HIGH SCORE: {snake_high_score}"
    draw_text(display, hs_text, 30, y_start + 15, GREY, 3, CODE_FONT)
    y_final = y_start + row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
