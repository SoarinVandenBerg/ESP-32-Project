# ===== FLAPPY BIRD =====
FLAPPY_BIRD_X = 80
FLAPPY_BIRD_R = 10
FLAPPY_GRAVITY = 0.6
FLAPPY_FLAP = -7
FLAPPY_PIPE_W = 45
FLAPPY_PIPE_SPEED = 3
FLAPPY_GAP_START = 130
FLAPPY_GAP_MIN = 75
FLAPPY_GROUND_Y = 420
FLAPPY_PIPE_SPACE = 180
FLAPPY_GREEN = make_color(0, 180, 0)      # Pipes - medium green
FLAPPY_DARK_GREEN = make_color(0, 120, 0) # Pipe shadows - dark green
FLAPPY_GROUND_C = make_color(0, 100, 0)   # Ground - darker green
FLAPPY_BIRD_C = make_color(50, 220, 50)   # Bird body - bright lime green
FLAPPY_BEAK_C = make_color(100, 255, 100) # Beak - very bright green
FLAPPY_WING_C = make_color(0, 160, 0)     # Wing - medium-dark green
FLAPPY_EYE_C = WHITE

flappy_y = 200.0
flappy_vy = 0.0
flappy_pipes = []
flappy_score = 0
flappy_running = False
flappy_high = 0
flappy_games = 0
flappy_last_score_text = ""
flappy_tapped = False  # Track if already flapped this touch

def flappy_reset():
    global flappy_y, flappy_vy, flappy_pipes, flappy_score, flappy_running
    global flappy_last_score_text, flappy_tapped
    flappy_y = 200.0
    flappy_vy = 0.0
    flappy_pipes = []
    flappy_score = 0
    flappy_running = False
    flappy_last_score_text = ""
    flappy_tapped = False

def flappy_get_gap():
    return max(FLAPPY_GAP_MIN, FLAPPY_GAP_START - flappy_score * 3)

def flappy_get_speed():
    return min(6, FLAPPY_PIPE_SPEED + flappy_score // 10)

def flappy_spawn_pipe():
    gap_h = flappy_get_gap()
    min_y = 60 + gap_h // 2
    max_y = FLAPPY_GROUND_Y - 20 - gap_h // 2
    gap_y = random.randint(min_y, max_y)
    flappy_pipes.append([368, gap_y, gap_h])

def flappy_draw_bird(y, color=None):
    if color is None:
        color = FLAPPY_BIRD_C
    bx = FLAPPY_BIRD_X
    by = int(y)
    # Main body
    display.fill_circle(bx, by, FLAPPY_BIRD_R, color)
    # Wing (darker green shade on side)
    if color != BLACK:
        display.fill_circle(bx - 3, by + 2, 5, FLAPPY_WING_C)
    # Beak
    display.fill_rect(bx + FLAPPY_BIRD_R, by - 2, 7, 4, color if color == BLACK else FLAPPY_BEAK_C)
    # Eye
    if color != BLACK:
        display.fill_circle(bx + 4, by - 3, 3, WHITE)
        display.fill_circle(bx + 5, by - 3, 2, BLACK)

def draw_flappy_menu():
    display.fill(BLACK)
    draw_text(display, "FLAPPY", (368 - 180) // 2, 50, FLAPPY_GREEN, 5, CODE_FONT)
    draw_text(display, "BIRD", (368 - 120) // 2, 110, FLAPPY_GREEN, 5, CODE_FONT)
    if flappy_high > 0:
        hs_text = f"HIGH SCORE: {flappy_high}"
        draw_text(display, hs_text, (368 - len(hs_text) * 12) // 2, 210, GREY, 2, CODE_FONT)
    display.fill_rect(84, 320, 200, 60, FLAPPY_GREEN)
    draw_text(display, "START", 84 + (200 - 90) // 2, 338, WHITE, 3, CODE_FONT)

def draw_flappy_game():
    global flappy_running, flappy_last_score_text
    display.fill(BLACK)
    display.fill_rect(0, FLAPPY_GROUND_Y, 368, 28, FLAPPY_GROUND_C)
    flappy_running = True
    flappy_spawn_pipe()
    flappy_draw_bird(flappy_y)
    flappy_last_score_text = "0"
    draw_text(display, "0", (368 - 30) // 2, 10, GREY, 3, CODE_FONT)

def draw_flappy_gameover():
    global flappy_games, flappy_high
    flappy_games += 1
    if flappy_score > flappy_high:
        flappy_high = flappy_score
    save_flappy_stats()
    display.fill(BLACK)
    draw_text(display, "GAME OVER", 64, 80, GREY, 5, CODE_FONT)
    score_text = f"SCORE: {flappy_score}"
    draw_text(display, score_text, (368 - len(score_text) * 18) // 2, 160, GREY, 3, CODE_FONT)
    best_text = f"BEST: {flappy_high}"
    draw_text(display, best_text, (368 - len(best_text) * 18) // 2, 200, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "MENU", 61, 268, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "RETRY", 223, 268, WHITE, 3, CODE_FONT)

def flappy_update():
    global flappy_y, flappy_vy, flappy_score, flappy_running
    global flappy_last_score_text
    speed = flappy_get_speed()
    old_y = flappy_y
    flappy_vy += FLAPPY_GRAVITY
    flappy_y += flappy_vy
    if flappy_y < FLAPPY_BIRD_R:
        flappy_y = FLAPPY_BIRD_R
        flappy_vy = 0
    # Move pipes and check scoring
    scored = False
    for pipe in flappy_pipes:
        old_px = pipe[0]
        pipe[0] -= speed
        if old_px > FLAPPY_BIRD_X and pipe[0] <= FLAPPY_BIRD_X:
            flappy_score += 1
            scored = True
    # Remove off-screen pipes
    while flappy_pipes and flappy_pipes[0][0] < -FLAPPY_PIPE_W:
        flappy_pipes.pop(0)
    # Spawn new pipes
    if not flappy_pipes or flappy_pipes[-1][0] < 368 - FLAPPY_PIPE_SPACE:
        flappy_spawn_pipe()
    # Collision detection
    by = int(flappy_y)
    if by + FLAPPY_BIRD_R >= FLAPPY_GROUND_Y:
        flappy_running = False
        return
    for pipe in flappy_pipes:
        px = int(pipe[0])
        gap_y = pipe[1]
        gh = pipe[2]
        if px < FLAPPY_BIRD_X + FLAPPY_BIRD_R and px + FLAPPY_PIPE_W > FLAPPY_BIRD_X - FLAPPY_BIRD_R:
            if by - FLAPPY_BIRD_R < gap_y - gh // 2 or by + FLAPPY_BIRD_R > gap_y + gh // 2:
                flappy_running = False
                return
    # Draw pipes - clear trailing edge, redraw full pipe
    for pipe in flappy_pipes:
        px = int(pipe[0])
        gap_y = pipe[1]
        gh = pipe[2]
        top_h = gap_y - gh // 2
        bot_y = gap_y + gh // 2
        bot_h = FLAPPY_GROUND_Y - bot_y
        # Clear trailing edge with safety margin
        trail_x = px + FLAPPY_PIPE_W
        if trail_x < 368:
            cx = max(0, trail_x)
            cw = min(speed + 2, 368 - cx)
            if cw > 0:
                if top_h > 0:
                    display.fill_rect(cx, 0, cw, top_h, BLACK)
                if bot_h > 0:
                    display.fill_rect(cx, bot_y, cw, bot_h, BLACK)
        # Draw full visible pipe (overwrites any stale pixels)
        if px < 368 and px + FLAPPY_PIPE_W > 0:
            dx = max(0, px)
            dw = min(px + FLAPPY_PIPE_W, 368) - dx
            if dw > 0:
                if top_h > 0:
                    display.fill_rect(dx, 0, dw, top_h, FLAPPY_GREEN)
                    if top_h > 4:
                        display.fill_rect(dx, top_h - 4, dw, 4, FLAPPY_DARK_GREEN)
                if bot_h > 0:
                    display.fill_rect(dx, bot_y, dw, bot_h, FLAPPY_GREEN)
                    if bot_h > 4:
                        display.fill_rect(dx, bot_y, dw, 4, FLAPPY_DARK_GREEN)
    # Erase old bird then immediately draw new bird (minimal flicker)
    flappy_draw_bird(old_y, BLACK)
    flappy_draw_bird(flappy_y)
    # Redraw ground edge
    display.fill_rect(0, FLAPPY_GROUND_Y, 368, 2, FLAPPY_GROUND_C)
    # Update score display
    if scored:
        score_text = str(flappy_score)
        old_text = flappy_last_score_text
        old_w = len(old_text) * 18
        new_w = len(score_text) * 18
        display.fill_rect((368 - old_w) // 2, 10, old_w, 25, BLACK)
        draw_text(display, score_text, (368 - new_w) // 2, 10, GREY, 3, CODE_FONT)
        flappy_last_score_text = score_text

def save_flappy_stats():
    save_all_stats()

def launch_flappy():
    flappy_reset()
    draw_flappy_menu()

def handle_flappy_touch(tx, ty):
    global current_screen, current_app, last_time_text

    if not flappy_running:
        if flappy_score == 0 and not flappy_pipes:
            # Menu screen
            if 320 <= ty <= 380 and 84 <= tx <= 284:
                flappy_reset()
                draw_flappy_game()
        else:
            # Game over screen
            if 245 <= ty <= 315:
                if 25 <= tx <= 175:  # MENU
                    track_app_exit("FLAPPY BIRD")
                    current_screen = SCREEN_MENU
                    current_app = -1
                    draw_menu_screen()
                    last_time_text = ""
                elif 193 <= tx <= 343:  # RETRY
                    flappy_reset()
                    draw_flappy_game()

def loop_flappy():
    global flappy_vy, flappy_running, last_activity, flappy_tapped

    t = read_touch()
    # Only flap on initial tap, not while held
    if (t is not None or touch_pressed) and not flappy_tapped:
        flappy_vy = FLAPPY_FLAP
        flappy_tapped = True
        last_activity = time.ticks_ms()
    elif t is None and not touch_pressed:
        # Touch released - allow next flap
        flappy_tapped = False

    flappy_update()
    if not flappy_running:
        draw_flappy_gameover()
    else:
        time.sleep_ms(10)

def draw_flappy_stats():
    display.fill(BLACK)
    draw_text(display, "FLAPPY BIRD", 80, 15, GREY, 3, CODE_FONT)
    y = 80
    rh = 50
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"HIGH SCORE: {flappy_high}", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"GAMES: {flappy_games}", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
