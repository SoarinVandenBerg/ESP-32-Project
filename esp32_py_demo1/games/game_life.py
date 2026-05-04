# ===== GAME OF LIFE =====
LIFE_COLS = 30
LIFE_ROWS = 28
LIFE_CELL = 12  # Cell size in pixels
LIFE_X = (368 - LIFE_COLS * LIFE_CELL) // 2  # Center grid
LIFE_Y = 50

life_grid = [[0] * LIFE_COLS for _ in range(LIFE_ROWS)]
life_running = False
life_generation = 0
life_prev_touch = None  # For drag drawing

def life_clear():
    global life_grid, life_generation, life_prev_touch
    life_grid = [[0] * LIFE_COLS for _ in range(LIFE_ROWS)]
    life_generation = 0
    life_prev_touch = None

def life_randomize():
    global life_grid, life_generation
    import random
    for r in range(LIFE_ROWS):
        for c in range(LIFE_COLS):
            life_grid[r][c] = 1 if random.random() < 0.3 else 0
    life_generation = 0

def life_toggle_cell(x, y):
    """Toggle cell at screen coordinates"""
    # Convert screen coords to grid coords
    col = (x - LIFE_X) // LIFE_CELL
    row = (y - LIFE_Y) // LIFE_CELL
    if 0 <= col < LIFE_COLS and 0 <= row < LIFE_ROWS:
        life_grid[row][col] = 1 - life_grid[row][col]
        return True
    return False

def life_set_cell(x, y):
    """Set cell to alive at screen coordinates (for drag drawing)"""
    col = (x - LIFE_X) // LIFE_CELL
    row = (y - LIFE_Y) // LIFE_CELL
    if 0 <= col < LIFE_COLS and 0 <= row < LIFE_ROWS:
        if life_grid[row][col] == 0:
            life_grid[row][col] = 1
            cell_x = LIFE_X + col * LIFE_CELL
            cell_y = LIFE_Y + row * LIFE_CELL
            display.fill_rect(cell_x, cell_y, LIFE_CELL - 1, LIFE_CELL - 1, GREEN)
            return True
    return False

def life_add_point(tx, ty):
    """Add cells in a small brush area around the point"""
    if ty < LIFE_Y or ty > LIFE_Y + LIFE_ROWS * LIFE_CELL:
        return
    # Set the cell at this point
    life_set_cell(tx, ty)

def life_add(tx, ty):
    """Add cells from previous touch to current touch (line interpolation)"""
    global life_prev_touch
    if life_prev_touch is not None:
        px, py = life_prev_touch
        # Bresenham line to fill cells between touches
        dx = abs(tx - px)
        dy = abs(ty - py)
        sx = 1 if px < tx else -1
        sy = 1 if py < ty else -1
        err = dx - dy
        x, y = px, py
        while True:
            life_set_cell(x, y)
            if x == tx and y == ty:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
    else:
        life_add_point(tx, ty)
    life_prev_touch = (tx, ty)

def life_count_neighbors(row, col):
    """Count live neighbors with wrapping"""
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            r = (row + dr) % LIFE_ROWS
            c = (col + dc) % LIFE_COLS
            count += life_grid[r][c]
    return count

def life_has_cells():
    """Check if any cells are alive"""
    for r in range(LIFE_ROWS):
        for c in range(LIFE_COLS):
            if life_grid[r][c]:
                return True
    return False

def life_step():
    """Advance one generation"""
    global life_grid, life_generation, life_running
    new_grid = [[0] * LIFE_COLS for _ in range(LIFE_ROWS)]
    for r in range(LIFE_ROWS):
        for c in range(LIFE_COLS):
            neighbors = life_count_neighbors(r, c)
            if life_grid[r][c]:
                # Live cell survives with 2 or 3 neighbors
                new_grid[r][c] = 1 if neighbors in [2, 3] else 0
            else:
                # Dead cell becomes alive with exactly 3 neighbors
                new_grid[r][c] = 1 if neighbors == 3 else 0
    life_grid = new_grid
    life_generation += 1
    # Auto-pause if no cells are alive
    if not life_has_cells():
        life_running = False

def draw_life_app():
    display.fill(BLACK)
    draw_text(display, "LIFE", 155, 15, GREY, 3, CODE_FONT)
    # Show generation count on right side
    gen_text = f"GEN:{life_generation}"
    draw_text(display, gen_text, 255, 12, DARK_GREY, 2, CODE_FONT)

    # Draw grid
    for r in range(LIFE_ROWS):
        for c in range(LIFE_COLS):
            x = LIFE_X + c * LIFE_CELL
            y = LIFE_Y + r * LIFE_CELL
            if life_grid[r][c]:
                display.fill_rect(x, y, LIFE_CELL - 1, LIFE_CELL - 1, GREEN)
            else:
                display.fill_rect(x, y, LIFE_CELL - 1, LIFE_CELL - 1, DARK_GREY)

    # Draw controls at bottom
    btn_y = 395
    if life_running:
        display.fill_rect(20, btn_y, 100, 45, DARK_GREY)
        draw_text(display, "PAUSE", 35, btn_y + 12, GREY, 2, CODE_FONT)
    else:
        display.fill_rect(20, btn_y, 100, 45, GREEN)
        draw_text(display, "PLAY", 45, btn_y + 12, WHITE, 2, CODE_FONT)

    display.fill_rect(134, btn_y, 100, 45, GREEN)
    draw_text(display, "CLEAR", 149, btn_y + 12, WHITE, 2, CODE_FONT)

    display.fill_rect(248, btn_y, 100, 45, GREEN)
    draw_text(display, "RANDOM", 255, btn_y + 12, WHITE, 2, CODE_FONT)

def update_life_grid():
    """Update only the grid cells that changed - reduces flicker"""
    # For now, just redraw the whole grid area (still faster than full redraw)
    for r in range(LIFE_ROWS):
        for c in range(LIFE_COLS):
            x = LIFE_X + c * LIFE_CELL
            y = LIFE_Y + r * LIFE_CELL
            if life_grid[r][c]:
                display.fill_rect(x, y, LIFE_CELL - 1, LIFE_CELL - 1, GREEN)
            else:
                display.fill_rect(x, y, LIFE_CELL - 1, LIFE_CELL - 1, DARK_GREY)

    # Update generation count
    display.fill_rect(255, 10, 110, 20, BLACK)
    gen_text = f"GEN:{life_generation}"
    draw_text(display, gen_text, 255, 12, DARK_GREY, 2, CODE_FONT)

def launch_life():
    global life_running
    life_clear()
    life_running = False
    draw_life_app()

def handle_life_touch(tx, ty):
    global life_running, life_prev_touch, current_screen, current_app, last_time_text

    # Game of Life touch handling
    btn_y = 395
    # Check buttons first
    if btn_y <= ty <= btn_y + 45:
        if 20 <= tx <= 120:
            # Play/Pause
            life_running = not life_running
            draw_life_app()
        elif 134 <= tx <= 234:
            # Clear
            life_clear()
            life_running = False
            draw_life_app()
        elif 248 <= tx <= 348:
            # Random
            life_randomize()
            draw_life_app()
        # Wait for touch release
        while read_touch() is not None:
            time.sleep_ms(30)
    elif LIFE_Y <= ty <= LIFE_Y + LIFE_ROWS * LIFE_CELL:
        # Grid touch - continuous drag-to-fill
        life_prev_touch = None
        life_touch_start = time.ticks_ms()
        while True:
            t = read_touch()
            if t is None:
                break
            tx, ty = t
            if LIFE_Y <= ty <= LIFE_Y + LIFE_ROWS * LIFE_CELL:
                life_add(tx, ty)
            time.sleep_ms(5)
        life_prev_touch = None

def loop_life():
    global life_running

    life_step()
    update_life_grid()
    # If auto-paused (no cells alive), update the button
    if not life_running:
        btn_y = 395
        display.fill_rect(20, btn_y, 100, 45, GREEN)
        draw_text(display, "PLAY", 45, btn_y + 12, WHITE, 2, CODE_FONT)
    time.sleep_ms(100)  # Slow down simulation a bit

def loop_life_paused():
    global life_running, life_prev_touch, current_screen, current_app, last_time_text

    # Read touch FRESH - don't use stale touch variable
    t = read_touch()
    if t is not None:
        tx, ty = t
        btn_y = 395
        # Check buttons
        if btn_y <= ty <= btn_y + 45:
            if 20 <= tx <= 120:
                # Play
                life_running = True
                draw_life_app()
            elif 134 <= tx <= 234:
                # Clear
                life_clear()
                draw_life_app()
            elif 248 <= tx <= 348:
                # Random
                life_randomize()
                draw_life_app()
            # Wait for touch release
            while read_touch() is not None:
                time.sleep_ms(30)
        elif LIFE_Y <= ty <= LIFE_Y + LIFE_ROWS * LIFE_CELL:
            # Continuous drawing loop on grid
            life_prev_touch = None
            life_touch_start = time.ticks_ms()
            while True:
                t = read_touch()
                if t is None:
                    break
                tx, ty = t
                if LIFE_Y <= ty <= LIFE_Y + LIFE_ROWS * LIFE_CELL:
                    life_add(tx, ty)
                time.sleep_ms(5)  # Fast sampling for smooth drawing
            life_prev_touch = None
    time.sleep_ms(20)
