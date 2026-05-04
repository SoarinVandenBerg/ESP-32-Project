BALL_RADIUS = 18
GYRO_LEVEL_THRESH = 15  # pixels from center to count as "level"
gyro_was_level = False
gyro_mode = 0  # 0=level, 1=gforce
gforce_current = 0.0
gforce_peak = 0.0
gforce_high = 0.0
gforce_last_bar = -1
gforce_last_text = ""
gforce_display_g = 0.0  # What's shown on bar (holds peak briefly)
gforce_peak_time = 0  # ticks_ms when peak was last hit
GFORCE_HOLD_MS = 750  # How long peak color/bar holds
GFORCE_ORANGE = make_color(255, 165, 0)
GFORCE_RED = make_color(255, 0, 0)

def draw_gyro_buttons():
    """Draw LEVEL / G-FORCE mode buttons at bottom"""
    if gyro_mode == 0:
        display.fill_rect(34, 405, 145, 35, GREEN)
        draw_text(display, "LEVEL", 72, 413, WHITE, 2, CODE_FONT)
        display.fill_rect(189, 405, 145, 35, DARK_GREY)
        draw_text(display, "G-FORCE", 217, 413, GREY, 2, CODE_FONT)
    else:
        display.fill_rect(34, 405, 145, 35, DARK_GREY)
        draw_text(display, "LEVEL", 72, 413, GREY, 2, CODE_FONT)
        display.fill_rect(189, 405, 145, 35, GREEN)
        draw_text(display, "G-FORCE", 217, 413, WHITE, 2, CODE_FONT)

def draw_gyro_crosshair():
    """Draw center crosshair target"""
    cx, cy = 184, 220
    display.fill_rect(cx - 25, cy, 51, 1, DARK_GREY)
    display.fill_rect(cx, cy - 25, 1, 51, DARK_GREY)
    display.fill_circle(cx, cy, 20, DARK_GREY)
    display.fill_circle(cx, cy, 18, BLACK)

def draw_gyro_app():
    display.fill(BLACK)
    draw_text(display, "GYRO LEVEL", 100, 15, GREY, 3, CODE_FONT)
    draw_gyro_crosshair()
    cx, cy = 184, 220
    display.fill_circle(cx, cy, BALL_RADIUS, GREEN)
    draw_gyro_buttons()

def update_gyro_ball(old_x, old_y, new_x, new_y, is_level=False):
    display.fill_circle(old_x, old_y, BALL_RADIUS + 1, BLACK)
    # Redraw crosshair if ball was near center
    if abs(old_x - 184) < 30 and abs(old_y - 220) < 30:
        draw_gyro_crosshair()
    color = WHITE if is_level else GREEN
    display.fill_circle(new_x, new_y, BALL_RADIUS, color)

def draw_gforce_app():
    """Full redraw of G-Force screen"""
    global gforce_last_bar, gforce_last_text
    display.fill(BLACK)
    # Title
    draw_text(display, "G-FORCE", 118, 15, GREY, 3, CODE_FONT)
    # Bar outline
    display.fill_rect(109, 55, 150, 230, DARK_GREY)
    display.fill_rect(112, 58, 144, 224, BLACK)
    # Scale marks on right side
    for i in range(9):
        y = 55 + 230 - int(i / 8.0 * 220) - 5
        display.fill_rect(262, y, 8, 1, DARK_GREY)
        if i % 2 == 0:
            draw_text(display, str(i), 275, y - 5, DARK_GREY, 1, CODE_FONT)
    # Current G text
    g_text = f"{gforce_current:.1f} G"
    tw = len(g_text) * 6 * 5
    draw_text(display, g_text, (368 - tw) // 2, 300, GREEN, 5, CODE_FONT)
    gforce_last_text = g_text
    # Peak and best
    pk_text = f"PEAK: {gforce_peak:.1f} G"
    draw_text(display, pk_text, 30, 350, GREY, 2, CODE_FONT)
    bs_text = f"BEST: {gforce_high:.1f} G"
    draw_text(display, bs_text, 30, 375, GREY, 2, CODE_FONT)
    # Mode buttons
    draw_gyro_buttons()
    gforce_last_bar = -1  # Force bar redraw on next update

def update_gforce_display():
    """Dirty-region update for G-Force bar and text"""
    global gforce_last_bar, gforce_last_text
    # Use display_g for bar (holds peak briefly)
    show_g = gforce_display_g
    fill_h = min(220, int(show_g / 8.0 * 220))
    if fill_h != gforce_last_bar:
        # Clear bar interior
        display.fill_rect(112, 58, 144, 224, BLACK)
        # Draw filled portion from bottom
        if fill_h > 0:
            bar_y = 58 + 224 - fill_h
            if show_g < 2.0:
                bar_c = GREEN
            elif show_g < 4.0:
                bar_c = GFORCE_ORANGE
            else:
                bar_c = GFORCE_RED
            display.fill_rect(112, bar_y, 144, fill_h, bar_c)
        # Draw peak marker
        if gforce_peak > 1.2:
            peak_h = min(220, int(gforce_peak / 8.0 * 220))
            peak_y = 58 + 224 - peak_h
            if 58 <= peak_y <= 278:
                display.fill_rect(112, peak_y, 144, 2, WHITE)
        gforce_last_bar = fill_h
    # Update current G text
    g_text = f"{gforce_current:.1f} G"
    if g_text != gforce_last_text:
        display.fill_rect(20, 295, 328, 45, BLACK)
        tw = len(g_text) * 6 * 5
        if show_g < 2.0:
            tc = GREEN
        elif show_g < 4.0:
            tc = GFORCE_ORANGE
        else:
            tc = GFORCE_RED
        draw_text(display, g_text, (368 - tw) // 2, 300, tc, 5, CODE_FONT)
        gforce_last_text = g_text
        # Also update peak/best text
        display.fill_rect(20, 345, 328, 50, BLACK)
        pk_text = f"PEAK: {gforce_peak:.1f} G"
        draw_text(display, pk_text, 30, 350, GREY, 2, CODE_FONT)
        bs_text = f"BEST: {gforce_high:.1f} G"
        draw_text(display, bs_text, 30, 375, GREY, 2, CODE_FONT)

def save_gforce_stats():
    save_all_stats()

def launch_gyro():
    global gyro_mode, ball_x, ball_y, filtered_ax, filtered_ay, gyro_was_level
    gyro_mode = 0
    draw_gyro_app()
    ball_x, ball_y = 184, 220
    filtered_ax, filtered_ay = 0.0, 0.0
    gyro_was_level = False

def handle_gyro_touch(tx, ty):
    global gyro_mode, gyro_was_level, ball_x, ball_y, filtered_ax, filtered_ay
    global gforce_current, gforce_peak, gforce_display_g, gforce_peak_time
    global gforce_last_bar, gforce_last_text

    if 405 <= ty <= 440:
        if 34 <= tx <= 179 and gyro_mode != 0:
            gyro_mode = 0
            gyro_was_level = False
            ball_x, ball_y = 184, 220
            filtered_ax, filtered_ay = 0.0, 0.0
            draw_gyro_app()
        elif 189 <= tx <= 334 and gyro_mode != 1:
            gyro_mode = 1
            gforce_current = 0.0
            gforce_peak = 0.0
            gforce_display_g = 0.0
            gforce_peak_time = 0
            gforce_last_bar = -1
            gforce_last_text = ""
            draw_gforce_app()

def loop_gyro():
    global gyro_mode, gyro_was_level, ball_x, ball_y, filtered_ax, filtered_ay
    global gforce_current, gforce_peak, gforce_high, gforce_display_g, gforce_peak_time

    if gyro_mode == 0:  # Level mode
        ax, ay, az = read_accel()
        smooth = 0.5
        filtered_ax = filtered_ax * (1 - smooth) + ax * smooth
        filtered_ay = filtered_ay * (1 - smooth) + ay * smooth
        cx, cy = 184, 220
        sensitivity = 250
        new_x = int(cx + filtered_ax * sensitivity)
        new_y = int(cy + filtered_ay * sensitivity)
        new_x = max(25, min(343, new_x))
        new_y = max(60, min(390, new_y))
        # Check if level (ball near center)
        dist = ((new_x - cx) ** 2 + (new_y - cy) ** 2) ** 0.5
        is_level = dist < GYRO_LEVEL_THRESH
        if abs(new_x - ball_x) > 2 or abs(new_y - ball_y) > 2:
            update_gyro_ball(ball_x, ball_y, new_x, new_y, is_level)
            ball_x, ball_y = new_x, new_y
        # Show/hide LEVEL text
        if is_level and not gyro_was_level:
            display.fill_rect(120, 375, 130, 25, BLACK)
            draw_text(display, "LEVEL!", 130, 378, GREEN, 3, CODE_FONT)
            gyro_was_level = True
        elif not is_level and gyro_was_level:
            display.fill_rect(120, 375, 130, 25, BLACK)
            gyro_was_level = False
    elif gyro_mode == 1:  # G-Force mode
        ax, ay, az = read_accel()
        total_g = (ax * ax + ay * ay + az * az) ** 0.5
        # Calibrate so still = 1.0G exactly
        total_g = round(total_g, 1)
        gforce_current = gforce_current * 0.7 + total_g * 0.3
        if gforce_current > gforce_peak:
            gforce_peak = gforce_current
        if gforce_current > gforce_high:
            gforce_high = gforce_current
            save_gforce_stats()
        # Hold peak display for 0.75s
        if gforce_current > gforce_display_g:
            gforce_display_g = gforce_current
            gforce_peak_time = time.ticks_ms()
        elif time.ticks_diff(time.ticks_ms(), gforce_peak_time) > GFORCE_HOLD_MS:
            gforce_display_g = gforce_current
        update_gforce_display()
