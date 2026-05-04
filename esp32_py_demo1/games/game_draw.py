# ===== GRAVITY DRAW - Physics Sandbox =====
import math

# Drawing state
draw_mode = 0  # 0=menu, 1=gravity/physics, 2=sand
draw_lines = []  # List of (x1, y1, x2, y2) line segments
draw_balls = []  # List of [x, y, vx, vy, old_x, old_y] balls
draw_first_point = None  # First tap point for line drawing

# Physics constants (mode 1)
DRAW_GRAVITY = 0.5  # Slightly stronger gravity for faster rolling
DRAW_BOUNCE = 0.8  # More bouncy (was 0.65)
DRAW_FRICTION = 0.992  # Less friction for faster rolling
DRAW_BALL_R = 8  # Ball radius

# Sand simulation (mode 2) - OPTIMIZED VERSION with instant physics
SAND_CELL = 4  # Pixel size of each sand cell
SAND_COLS = 368 // SAND_CELL  # 92 columns
SAND_ROWS = (395 - 55) // SAND_CELL  # 85 rows (drawing area)
# Grid values: 0=empty, 1=sand
sand_grid = None  # bytearray grid
sand_prev_touch = None  # Previous touch position for line drawing
sand_touch_start = 0  # For hold-to-exit timing
sand_brush_size = 2  # 1=small (1x1), 2=medium (2x2), 3=large (3x3)
# Optimization: track which rows have sand (skip empty rows)
sand_active_rows = None  # set() of row indices with sand

# Sketch mode (mode 3)
SKETCH_CELL = 2  # Smaller pixels for more detail
SKETCH_COLS = 368 // SKETCH_CELL
SKETCH_ROWS = (390 - 55) // SKETCH_CELL  # Leave room for buttons
sketch_grid = None
sketch_prev_touch = None
sketch_brush_size = 2  # 1=small, 2=medium, 3=large
sketch_eraser = False  # Eraser mode
sketch_touch_start = 0

def draw_reset():
    """Reset the drawing canvas"""
    global draw_lines, draw_balls, draw_first_point
    draw_lines = []
    draw_balls = []
    draw_first_point = None

def draw_add_ball():
    """Add a ball at the top center"""
    # [x, y, vx, vy, old_x, old_y]
    x = 184 + random.randint(-50, 50)
    draw_balls.append([x, 70, 0, 0, x, 70])

def draw_line_collision(bx, by, x1, y1, x2, y2):
    """Check if ball collides with line segment. Returns (collided, nx, ny, dist)"""
    dx = x2 - x1
    dy = y2 - y1
    length_sq = dx*dx + dy*dy
    if length_sq == 0:
        return (False, 0, 0, 999)

    t = max(0, min(1, ((bx - x1)*dx + (by - y1)*dy) / length_sq))
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    dist_x = bx - closest_x
    dist_y = by - closest_y
    dist = math.sqrt(dist_x*dist_x + dist_y*dist_y)

    # Slightly larger collision radius to catch fast balls
    if dist < DRAW_BALL_R + 2 and dist > 0:
        nx = dist_x / dist
        ny = dist_y / dist
        return (True, nx, ny, dist)
    return (False, 0, 0, dist)

def draw_safe_erase(x, y, r):
    """Erase a circle area using clamped fill_rect (avoids edge glitches)"""
    # Calculate rect bounds
    x1 = x - r
    y1 = y - r
    x2 = x + r
    y2 = y + r
    # Clamp to drawing area (0-368 x, 55-395 y)
    x1 = max(0, x1)
    y1 = max(55, y1)
    x2 = min(368, x2)
    y2 = min(395, y2)
    # Draw black rect if valid
    if x2 > x1 and y2 > y1:
        display.fill_rect(x1, y1, x2 - x1, y2 - y1, BLACK)

def draw_update_physics():
    """Update ball physics - no gyro, fixed gravity"""
    balls_to_remove = []

    for i, ball in enumerate(draw_balls):
        # Store old position for incremental redraw
        ball[4] = ball[0]
        ball[5] = ball[1]

        # Apply fixed gravity (down)
        ball[3] += DRAW_GRAVITY  # vy

        # Apply friction
        ball[2] *= DRAW_FRICTION
        ball[3] *= DRAW_FRICTION

        # Sub-step movement to prevent tunneling
        steps = 3
        vx_step = ball[2] / steps
        vy_step = ball[3] / steps

        for _ in range(steps):
            # Move a little
            ball[0] += vx_step
            ball[1] += vy_step

            # Check line collisions after each sub-step
            for line in draw_lines:
                collided, nx, ny, dist = draw_line_collision(ball[0], ball[1], line[0], line[1], line[2], line[3])
                if collided:
                    overlap = DRAW_BALL_R - dist + 1
                    ball[0] += nx * overlap
                    ball[1] += ny * overlap
                    # Only bounce if moving fast enough toward line
                    dot = ball[2]*nx + ball[3]*ny
                    if dot < -0.5:  # Moving into line with some speed
                        ball[2] = (ball[2] - 2*dot*nx) * DRAW_BOUNCE
                        ball[3] = (ball[3] - 2*dot*ny) * DRAW_BOUNCE
                        vx_step = ball[2] / steps
                        vy_step = ball[3] / steps

        # Wall collisions (left, right, top)
        if ball[0] < DRAW_BALL_R + 2:
            ball[0] = DRAW_BALL_R + 2
            ball[2] = -ball[2] * DRAW_BOUNCE
        if ball[0] > 366 - DRAW_BALL_R:
            ball[0] = 366 - DRAW_BALL_R
            ball[2] = -ball[2] * DRAW_BOUNCE
        if ball[1] < 57 + DRAW_BALL_R:
            ball[1] = 57 + DRAW_BALL_R
            ball[3] = -ball[3] * DRAW_BOUNCE

        # Bottom - delete ball
        if ball[1] > 393 - DRAW_BALL_R:
            balls_to_remove.append(i)
            draw_safe_erase(int(ball[4]), int(ball[5]), DRAW_BALL_R + 4)
            draw_safe_erase(int(ball[0]), int(ball[1]), DRAW_BALL_R + 4)
            continue

    # Remove balls that hit the bottom (in reverse order to maintain indices)
    for i in reversed(balls_to_remove):
        draw_balls.pop(i)

def draw_draw_line(x1, y1, x2, y2):
    """Draw a thick green line using Bresenham algorithm"""
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy

    while True:
        # Draw 3x3 block for thickness
        display.fill_rect(x1 - 1, y1 - 1, 3, 3, GREEN)

        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy

def draw_draw_app():
    """Draw the full gravity draw screen"""
    display.fill(BLACK)

    # Header
    draw_text(display, "DRAW", 155, 5, GREY, 2, CODE_FONT)
    if draw_first_point:
        draw_text(display, "TAP END POINT", 95, 30, GREEN, 2, CODE_FONT)

    # Draw all lines
    for line in draw_lines:
        draw_draw_line(line[0], line[1], line[2], line[3])

    # Draw first point marker if set
    if draw_first_point:
        px, py = draw_first_point
        display.fill_circle(int(px), int(py), 5, GREEN)

    # Draw all balls
    for ball in draw_balls:
        display.fill_circle(int(ball[0]), int(ball[1]), DRAW_BALL_R, GREEN)

    # Buttons at bottom
    # DROP button
    display.fill_rect(20, 400, 100, 40, GREEN)
    draw_text(display, "DROP", 40, 410, WHITE, 2, CODE_FONT)

    # CLEAR button
    display.fill_rect(248, 400, 100, 40, GREEN)
    draw_text(display, "CLEAR", 265, 410, WHITE, 2, CODE_FONT)

def draw_update_balls():
    """Incremental update - only redraw balls that moved"""
    for ball in draw_balls:
        old_x, old_y = int(ball[4]), int(ball[5])
        new_x, new_y = int(ball[0]), int(ball[1])

        # Only update if moved
        if old_x != new_x or old_y != new_y:
            # Erase old position with safe clamped rect (bigger to catch artifacts)
            draw_safe_erase(old_x, old_y, DRAW_BALL_R + 4)

            # Redraw any lines that might have been erased
            for line in draw_lines:
                x1, y1, x2, y2 = line
                # Check if line is near the erased area (simple box check)
                if (min(x1, x2) - 20 < old_x < max(x1, x2) + 20 and
                    min(y1, y2) - 20 < old_y < max(y1, y2) + 20):
                    draw_draw_line(x1, y1, x2, y2)

            # Draw new position
            display.fill_circle(new_x, new_y, DRAW_BALL_R, GREEN)

def draw_draw_menu():
    """Draw the mode selection menu"""
    display.fill(BLACK)
    draw_text(display, "DRAW", 140, 30, GREY, 4, CODE_FONT)

    # Mode 1: Gravity/Physics
    display.fill_rect(34, 120, 300, 60, GREEN)
    draw_text(display, "GRAVITY", 115, 137, WHITE, 3, CODE_FONT)

    # Mode 2: Sand
    display.fill_rect(34, 200, 300, 60, GREEN)
    draw_text(display, "SAND", 140, 217, WHITE, 3, CODE_FONT)

    # Mode 3: Sketch
    display.fill_rect(34, 280, 300, 60, GREEN)
    draw_text(display, "SKETCH", 125, 297, WHITE, 3, CODE_FONT)

def sand_reset():
    """Reset the sand grid - uses bytearray for efficiency"""
    global sand_grid, sand_prev_touch, sand_touch_start, sand_brush_size, sand_active_rows
    # bytearray is more memory efficient than list of lists
    sand_grid = [bytearray(SAND_COLS) for _ in range(SAND_ROWS)]
    sand_prev_touch = None
    sand_touch_start = 0
    sand_brush_size = 2  # Reset to medium
    sand_active_rows = set()  # Track which rows have sand

def sand_draw_full():
    """Draw full sand screen"""
    display.fill(BLACK)
    draw_text(display, "SAND", 155, 5, GREY, 2, CODE_FONT)

    # Draw existing sand as rectangles (no gaps)
    for r in range(SAND_ROWS):
        for c in range(SAND_COLS):
            if sand_grid[r][c]:
                x = c * SAND_CELL
                y = 55 + r * SAND_CELL
                display.fill_rect(x, y, SAND_CELL, SAND_CELL, GREEN)

    # Button bar - clear area first
    display.fill_rect(0, 395, 368, 53, BLACK)

    # Size button (left)
    display.fill_rect(24, 400, 100, 35, GREEN)
    size_text = ["SML", "MED", "LRG"][sand_brush_size - 1]
    draw_text(display, size_text, 52, 410, WHITE, 2, CODE_FONT)

    # Clear button (middle)
    display.fill_rect(134, 400, 100, 35, GREEN)
    draw_text(display, "CLEAR", 149, 410, WHITE, 2, CODE_FONT)

    # Preview (right)
    display.fill_rect(244, 400, 100, 35, DARK_GREY)
    preview_r = [2, 4, 6][sand_brush_size - 1]
    display.fill_circle(294, 417, preview_r, GREEN)

def sand_add_point(tx, ty):
    """Add sand in a brush area around the point"""
    if ty < 55 or ty > 395:
        return
    c = tx // SAND_CELL
    r = (ty - 55) // SAND_CELL
    # Add sand with current brush size (1x1, 2x2, or 3x3)
    for dr in range(sand_brush_size):
        for dc in range(sand_brush_size):
            nr, nc = r + dr, c + dc
            if 0 <= nr < SAND_ROWS and 0 <= nc < SAND_COLS:
                if sand_grid[nr][nc] == 0:
                    sand_grid[nr][nc] = 1
                    sand_active_rows.add(nr)  # Mark row as active
                    x = nc * SAND_CELL
                    y = 55 + nr * SAND_CELL
                    display.fill_rect(x, y, SAND_CELL, SAND_CELL, GREEN)

def sand_add(tx, ty):
    """Add sand from previous touch to current touch (line)"""
    global sand_prev_touch
    if sand_prev_touch is not None:
        # Draw line of sand between previous and current touch
        px, py = sand_prev_touch
        dx = tx - px
        dy = ty - py
        dist = max(abs(dx), abs(dy))
        if dist > 0:
            for i in range(dist + 1):
                t = i / dist
                x = int(px + dx * t)
                y = int(py + dy * t)
                sand_add_point(x, y)
    else:
        sand_add_point(tx, ty)
    sand_prev_touch = (tx, ty)

def sand_update():
    """Update sand physics - INSTANT FALL: sand drops all the way down immediately"""
    global sand_active_rows

    if not sand_active_rows:
        return

    new_active_rows = set()

    # Process active rows from bottom to top
    for r in sorted(sand_active_rows, reverse=True):
        if r >= SAND_ROWS - 1:
            new_active_rows.add(r)
            continue

        # Alternate scan direction
        col_range = range(SAND_COLS) if random.getrandbits(1) else range(SAND_COLS - 1, -1, -1)
        row_has_sand = False

        for c in col_range:
            if sand_grid[r][c] == 1:
                # Find how far down this grain can fall (all the way to bottom or until it hits something)
                fall_dist = 0
                for dr in range(1, SAND_ROWS - r):
                    if sand_grid[r + dr][c] == 0:
                        fall_dist = dr
                    else:
                        break

                if fall_dist > 0:
                    # Fall all the way instantly!
                    sand_grid[r + fall_dist][c] = 1
                    sand_grid[r][c] = 0
                    x = c * SAND_CELL
                    display.fill_rect(x, 55 + r * SAND_CELL, SAND_CELL, SAND_CELL, BLACK)
                    display.fill_rect(x, 55 + (r + fall_dist) * SAND_CELL, SAND_CELL, SAND_CELL, GREEN)
                    new_active_rows.add(r + fall_dist)
                else:
                    # Can't fall straight - try diagonal (just 1 step at a time for diagonal)
                    d = 1 if random.getrandbits(1) else -1
                    moved = False
                    for dc in [d, -d]:
                        nc = c + dc
                        if 0 <= nc < SAND_COLS and sand_grid[r + 1][nc] == 0:
                            # Move diagonally down one step
                            sand_grid[r + 1][nc] = 1
                            sand_grid[r][c] = 0
                            display.fill_rect(c * SAND_CELL, 55 + r * SAND_CELL, SAND_CELL, SAND_CELL, BLACK)
                            display.fill_rect(nc * SAND_CELL, 55 + (r + 1) * SAND_CELL, SAND_CELL, SAND_CELL, GREEN)
                            new_active_rows.add(r + 1)
                            moved = True
                            break

                    if not moved:
                        row_has_sand = True

        if row_has_sand:
            new_active_rows.add(r)

    sand_active_rows = new_active_rows

def sketch_reset():
    """Reset the sketch canvas"""
    global sketch_grid, sketch_prev_touch, sketch_brush_size, sketch_eraser, sketch_touch_start
    sketch_grid = [[0 for _ in range(SKETCH_COLS)] for _ in range(SKETCH_ROWS)]
    sketch_prev_touch = None
    sketch_brush_size = 2
    sketch_eraser = False
    sketch_touch_start = 0

def sketch_draw_full():
    """Draw full sketch screen"""
    display.fill(BLACK)
    draw_text(display, "SKETCH", 155, 5, GREY, 2, CODE_FONT)

    # Draw canvas
    for r in range(SKETCH_ROWS):
        for c in range(SKETCH_COLS):
            if sketch_grid[r][c] == 1:
                x = c * SKETCH_CELL
                y = 55 + r * SKETCH_CELL
                display.fill_rect(x, y, SKETCH_CELL, SKETCH_CELL, GREEN)

    # Draw buttons at bottom
    sketch_draw_buttons()

def sketch_draw_buttons():
    """Draw the button bar - safe from rounded corners"""
    # Clear bottom area
    display.fill_rect(0, 390, 368, 58, BLACK)

    # Size button (left) - away from rounded corner
    display.fill_rect(10, 400, 70, 35, GREEN)
    size_text = ["SML", "MED", "LRG"][sketch_brush_size - 1]
    draw_text(display, size_text, 18, 410, WHITE, 2, CODE_FONT)

    # Eraser toggle (middle-left)
    if sketch_eraser:
        display.fill_rect(90, 400, 75, 35, WHITE)
        draw_text(display, "ERASE", 97, 410, BLACK, 2, CODE_FONT)
    else:
        display.fill_rect(90, 400, 75, 35, GREEN)
        draw_text(display, "ERASE", 97, 410, WHITE, 2, CODE_FONT)

    # Clear button (middle-right)
    display.fill_rect(180, 400, 75, 35, GREEN)
    draw_text(display, "CLEAR", 187, 410, WHITE, 2, CODE_FONT)

    # Brush preview (right) - away from rounded corner
    display.fill_rect(270, 400, 78, 35, DARK_GREY)
    # Draw preview circle (centered in button)
    preview_r = [2, 4, 6][sketch_brush_size - 1]
    color = BLACK if sketch_eraser else GREEN
    display.fill_circle(314, 420, preview_r, color)

def sketch_add_point(tx, ty):
    """Add or erase at a point with current brush"""
    if ty < 55 or ty > 390:
        return
    c = tx // SKETCH_CELL
    r = (ty - 55) // SKETCH_CELL

    # Brush radius based on size
    radius = sketch_brush_size
    value = 0 if sketch_eraser else 1
    color = BLACK if sketch_eraser else GREEN

    for dr in range(-radius, radius + 1):
        for dc in range(-radius, radius + 1):
            # Circular brush
            if dr*dr + dc*dc <= radius*radius:
                nr, nc = r + dr, c + dc
                if 0 <= nr < SKETCH_ROWS and 0 <= nc < SKETCH_COLS:
                    if sketch_grid[nr][nc] != value:
                        sketch_grid[nr][nc] = value
                        x = nc * SKETCH_CELL
                        y = 55 + nr * SKETCH_CELL
                        display.fill_rect(x, y, SKETCH_CELL, SKETCH_CELL, color)

def sketch_add(tx, ty):
    """Add/erase from previous touch to current touch (line)"""
    global sketch_prev_touch
    if sketch_prev_touch is not None:
        px, py = sketch_prev_touch
        dx = tx - px
        dy = ty - py
        dist = max(abs(dx), abs(dy))
        if dist > 0:
            for i in range(dist + 1):
                t = i / dist
                x = int(px + dx * t)
                y = int(py + dy * t)
                sketch_add_point(x, y)
    else:
        sketch_add_point(tx, ty)
    sketch_prev_touch = (tx, ty)

def launch_draw():
    global draw_mode
    draw_mode = 0
    draw_draw_menu()

def handle_draw_touch(tx, ty):
    global draw_mode, draw_first_point, draw_lines
    if draw_mode == 0:  # Menu
        if 120 <= ty <= 180:  # Gravity mode
            draw_mode = 1
            draw_reset()
            draw_draw_app()
        elif 200 <= ty <= 260:  # Sand mode
            draw_mode = 2
            sand_reset()
            sand_draw_full()
        elif 280 <= ty <= 340:  # Sketch mode
            draw_mode = 3
            sketch_reset()
            sketch_draw_full()
    elif draw_mode == 1:  # Gravity mode
        if ty >= 400:  # Button area
            if tx < 150:  # DROP button
                draw_add_ball()
                ball = draw_balls[-1]
                display.fill_circle(int(ball[0]), int(ball[1]), DRAW_BALL_R, GREEN)
            elif tx > 220:  # CLEAR button
                draw_reset()
                draw_draw_app()
        elif 55 < ty < 395:  # Drawing area
            if draw_first_point is None:
                draw_first_point = (tx, ty)
                display.fill_circle(int(tx), int(ty), 5, GREEN)
                draw_text(display, "TAP END POINT", 95, 30, GREEN, 2, CODE_FONT)
            else:
                x1, y1 = draw_first_point
                draw_lines.append((x1, y1, tx, ty))
                draw_draw_line(x1, y1, tx, ty)
                display.fill_circle(int(x1), int(y1), 6, BLACK)
                draw_draw_line(x1, y1, tx, ty)
                draw_first_point = None
                display.fill_rect(60, 25, 250, 25, BLACK)

def loop_draw():
    global draw_mode, draw_balls, draw_lines, draw_first_point
    global sand_grid, sand_prev_touch, sand_touch_start, sand_brush_size, sand_active_rows
    global sketch_grid, sketch_prev_touch, sketch_brush_size, sketch_eraser, sketch_touch_start
    global current_screen, current_app, last_time_text

    if draw_mode == 1 and len(draw_balls) > 0:
        draw_update_physics()
        draw_update_balls()
        time.sleep_ms(16)
    elif draw_mode == 2:
        # OPTIMIZED SAND - physics runs continuously, drawing is smooth
        t = read_touch()
        if t is not None:
            tx, ty = t
            if sand_touch_start == 0:
                sand_touch_start = time.ticks_ms()
            # Check for buttons (3-section layout - updated positions)
            if ty >= 395:
                if 24 <= tx <= 124:  # Size button (left)
                    sand_brush_size = (sand_brush_size % 3) + 1
                    sand_draw_full()
                    while read_touch() is not None:
                        time.sleep_ms(30)
                elif 134 <= tx <= 234:  # Clear button (middle)
                    sand_reset()
                    sand_draw_full()
                    sand_touch_start = 0
                    while read_touch() is not None:
                        time.sleep_ms(30)
            # Drawing area - ULTRA-FAST sampling for perfectly smooth curves
            elif 55 < ty < 395:
                # Pure drawing loop - NO physics interruption!
                while True:
                    t = read_touch()
                    if t is None:
                        break
                    tx, ty = t
                    if 55 < ty < 395:
                        sand_add(tx, ty)
                    # NO physics during drawing - just pure smooth sampling!
                    # No sleep at all - maximum smoothness!
                sand_prev_touch = None
        else:
            sand_prev_touch = None
            sand_touch_start = 0

        # Run physics many times per frame for smooth falling (3 cells × 10 updates = 30 cells/frame)
        for _ in range(10):
            sand_update()
        time.sleep_ms(8)
    elif draw_mode == 3:  # Sketch mode
        touch = read_touch()
        if touch is not None:
            tx, ty = touch
            sketch_touch_start = time.ticks_ms()
            if ty >= 390:  # Button area
                if 10 <= tx <= 80:  # Size button
                    sketch_brush_size = (sketch_brush_size % 3) + 1
                    sketch_draw_buttons()
                    while read_touch() is not None:
                        time.sleep_ms(30)
                elif 90 <= tx <= 170:  # Eraser toggle
                    sketch_eraser = not sketch_eraser
                    sketch_draw_buttons()
                    while read_touch() is not None:
                        time.sleep_ms(30)
                elif 180 <= tx <= 260:  # Clear button
                    sketch_reset()
                    sketch_draw_full()
                    while read_touch() is not None:
                        time.sleep_ms(30)
            elif 55 < ty < 390:  # Drawing area
                # Continuous drawing loop
                sketch_touch_start = time.ticks_ms()
                while True:
                    t = read_touch()
                    if t is None:
                        break
                    tx, ty = t
                    if time.ticks_diff(time.ticks_ms(), sketch_touch_start) > 10000:
                        track_app_exit("DRAW")
                        current_screen = SCREEN_MENU
                        current_app = -1
                        draw_menu_screen()
                        last_time_text = ""
                        sketch_prev_touch = None
                        break
                    if 55 < ty < 390:
                        sketch_add(tx, ty)
                    time.sleep_ms(5)
                sketch_prev_touch = None
        time.sleep_ms(20)
