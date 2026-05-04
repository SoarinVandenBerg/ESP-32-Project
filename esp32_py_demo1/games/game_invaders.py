# ===== SPACE INVADERS =====
import random

# Constants
SI_COLS = 11
SI_ROWS = 5
SI_ALIEN_W = 20
SI_ALIEN_H = 14
SI_GAP_X = 6
SI_GAP_Y = 8
SI_GRID_START_X = 44
SI_GRID_START_Y = 55
SI_SHIP_Y = 370
SI_SHIP_W = 30
SI_SHIP_H = 14
SI_SHIP_SPEED = 6
SI_BULLET_W = 3
SI_BULLET_H = 8
SI_BULLET_SPEED = 12
SI_ALIEN_BULLET_SPEED = 4
SI_SHIELD_Y = 300
SI_DROP = 10
SI_STEP = 4

# Colors
SI_COLOR_1 = GREEN                    # Large aliens (rows 3-4)
SI_COLOR_2 = make_color(0, 180, 0)    # Medium aliens (rows 1-2)
SI_COLOR_3 = make_color(0, 255, 0)    # Small aliens (row 0)
SI_UFO_COLOR = make_color(200, 0, 0)
SI_SHIELD_COLOR = GREEN
SI_SHIP_COLOR = GREEN
SI_BULLET_COLOR = WHITE

# Shield layout: 4 shields, each 7x7 grid of 4x3px blocks = 28x21px
SI_SHIELD_XS = [38, 120, 202, 284]
SI_SHIELD_BCOLS = 7
SI_SHIELD_BROWS = 7
SI_SHIELD_BW = 4
SI_SHIELD_BH = 3

# Game state
si_mode = 0
si_aliens = []
si_grid_x = 0
si_grid_y = 0
si_dir = 1
si_ship_x = 169
si_bullet = None
si_alien_bullets = []
si_shields = []
si_ufo_x = -1
si_ufo_dir = 1
si_ufo_timer = 0
si_score = 0
si_lives = 3
si_wave = 1
si_alive_count = 55
si_last_move = 0
si_extra_life_given = False
si_old_ship_x = 169
si_prev_score = -1
si_prev_lives = -1
si_touching = False
si_touch_start = 0

# Stats (persistent)
si_high_score = 0
si_total_kills = 0
si_total_games = 0
si_best_wave = 0

# ===== INIT =====

def si_init_aliens():
    global si_aliens, si_alive_count
    # Scale rows by wave: 2 rows wave 1, 3 rows wave 2, 4 wave 3, 5 wave 4+
    num_rows = min(SI_ROWS, si_wave + 1)
    skip = SI_ROWS - num_rows  # Skip top rows
    si_aliens = []
    for r in range(SI_ROWS):
        row = []
        for c in range(SI_COLS):
            if r < skip:
                row.append(0)  # Empty row
            else:
                rel = r - skip  # Relative row within active aliens
                if rel == 0:
                    row.append(3)  # Small (top)
                elif rel <= 2:
                    row.append(2)  # Medium
                else:
                    row.append(1)  # Large (bottom)
        si_aliens.append(row)
    si_alive_count = num_rows * SI_COLS

def si_init_shields():
    global si_shields
    si_shields = []
    for s in range(4):
        grid = []
        for r in range(SI_SHIELD_BROWS):
            row = []
            for c in range(SI_SHIELD_BCOLS):
                # Arch shape: cut bottom corners and top corners
                if r >= SI_SHIELD_BROWS - 2 and (c <= 1 or c >= SI_SHIELD_BCOLS - 2):
                    row.append(False)
                elif r == 0 and (c == 0 or c == SI_SHIELD_BCOLS - 1):
                    row.append(False)
                else:
                    row.append(True)
            grid.append(row)
        si_shields.append(grid)

def si_init_wave():
    global si_grid_x, si_grid_y, si_dir, si_bullet, si_alien_bullets
    global si_last_move, si_ufo_x, si_ufo_timer
    si_init_aliens()
    si_init_shields()
    si_grid_x = 0
    si_grid_y = 0
    si_dir = 1
    si_bullet = None
    si_alien_bullets = []
    si_last_move = time.ticks_ms()
    si_ufo_x = -1
    si_ufo_timer = time.ticks_ms()

def si_alien_color(atype):
    if atype == 1:
        return SI_COLOR_1
    if atype == 2:
        return SI_COLOR_2
    return SI_COLOR_3

def si_alien_points(atype):
    if atype == 1:
        return 10
    if atype == 2:
        return 20
    return 30

# ===== DRAWING =====

def draw_si_header():
    global si_prev_score, si_prev_lives
    if si_score != si_prev_score or si_lives != si_prev_lives:
        display.fill_rect(0, 0, 368, 25, BLACK)
        draw_text(display, "SCORE:" + str(si_score), 20, 5, GREEN, 2, CODE_FONT)
        draw_text(display, "W" + str(si_wave), 170, 5, GREY, 2, CODE_FONT)
        for i in range(si_lives):
            display.fill_rect(300 + i * 20, 8, 15, 10, GREEN)
        si_prev_score = si_score
        si_prev_lives = si_lives

def draw_si_aliens():
    for r in range(SI_ROWS):
        for c in range(SI_COLS):
            ax = SI_GRID_START_X + si_grid_x + c * (SI_ALIEN_W + SI_GAP_X)
            ay = SI_GRID_START_Y + si_grid_y + r * (SI_ALIEN_H + SI_GAP_Y)
            if si_aliens[r][c] != 0:
                display.fill_rect(ax, ay, SI_ALIEN_W, SI_ALIEN_H, si_alien_color(si_aliens[r][c]))

def draw_si_shields():
    for s in range(4):
        sx = SI_SHIELD_XS[s]
        for r in range(SI_SHIELD_BROWS):
            for c in range(SI_SHIELD_BCOLS):
                if si_shields[s][r][c]:
                    bx = sx + c * SI_SHIELD_BW
                    by = SI_SHIELD_Y + r * SI_SHIELD_BH
                    display.fill_rect(bx, by, SI_SHIELD_BW, SI_SHIELD_BH, SI_SHIELD_COLOR)

def draw_si_ship():
    global si_old_ship_x
    if si_old_ship_x != si_ship_x:
        display.fill_rect(si_old_ship_x, SI_SHIP_Y - 4, SI_SHIP_W, SI_SHIP_H + 4, BLACK)
    display.fill_rect(si_ship_x, SI_SHIP_Y, SI_SHIP_W, SI_SHIP_H, SI_SHIP_COLOR)
    display.fill_rect(si_ship_x + SI_SHIP_W // 2 - 2, SI_SHIP_Y - 4, 4, 4, SI_SHIP_COLOR)
    si_old_ship_x = si_ship_x

def draw_si_full():
    display.fill(BLACK)
    si_prev_score_reset()
    draw_si_header()
    draw_si_aliens()
    draw_si_shields()
    draw_si_ship()

def si_prev_score_reset():
    global si_prev_score, si_prev_lives
    si_prev_score = -1
    si_prev_lives = -1

# ===== UFO =====

def draw_si_ufo():
    if si_ufo_x >= 0:
        display.fill_rect(si_ufo_x, 32, 30, 12, SI_UFO_COLOR)
        draw_text(display, "?", si_ufo_x + 9, 33, WHITE, 1, CODE_FONT)

def erase_si_ufo(old_x):
    if old_x >= 0:
        display.fill_rect(old_x, 32, 30, 12, BLACK)

def si_update_ufo():
    global si_ufo_x, si_ufo_dir, si_ufo_timer
    if si_ufo_x < 0:
        if time.ticks_diff(time.ticks_ms(), si_ufo_timer) > 25000:
            si_ufo_dir = 1 if random.randint(0, 1) == 0 else -1
            si_ufo_x = -30 if si_ufo_dir == 1 else 368
            si_ufo_timer = time.ticks_ms()
    else:
        old_x = si_ufo_x
        si_ufo_x += si_ufo_dir * 3
        if si_ufo_x < -30 or si_ufo_x > 368:
            erase_si_ufo(old_x)
            si_ufo_x = -1
            si_ufo_timer = time.ticks_ms()
        else:
            erase_si_ufo(old_x)
            draw_si_ufo()

# ===== COLLISION =====

def si_check_shield_hit(bx, by, going_up):
    for s in range(4):
        sx = SI_SHIELD_XS[s]
        sw = SI_SHIELD_BCOLS * SI_SHIELD_BW
        sh = SI_SHIELD_BROWS * SI_SHIELD_BH
        if bx + SI_BULLET_W < sx or bx > sx + sw:
            continue
        if by + SI_BULLET_H < SI_SHIELD_Y or by > SI_SHIELD_Y + sh:
            continue
        col = (bx - sx + SI_BULLET_W // 2) // SI_SHIELD_BW
        if going_up:
            row = (by + SI_BULLET_H - SI_SHIELD_Y) // SI_SHIELD_BH
        else:
            row = (by - SI_SHIELD_Y) // SI_SHIELD_BH
        if 0 <= row < SI_SHIELD_BROWS and 0 <= col < SI_SHIELD_BCOLS:
            if si_shields[s][row][col]:
                si_shields[s][row][col] = False
                bx_d = sx + col * SI_SHIELD_BW
                by_d = SI_SHIELD_Y + row * SI_SHIELD_BH
                display.fill_rect(bx_d, by_d, SI_SHIELD_BW, SI_SHIELD_BH, BLACK)
                return True
    return False

def si_check_alien_hit(bx, by):
    global si_alive_count, si_total_kills
    for r in range(SI_ROWS):
        for c in range(SI_COLS):
            if si_aliens[r][c] == 0:
                continue
            ax = SI_GRID_START_X + si_grid_x + c * (SI_ALIEN_W + SI_GAP_X)
            ay = SI_GRID_START_Y + si_grid_y + r * (SI_ALIEN_H + SI_GAP_Y)
            if (bx + SI_BULLET_W > ax and bx < ax + SI_ALIEN_W and
                by < ay + SI_ALIEN_H and by + SI_BULLET_H > ay):
                pts = si_alien_points(si_aliens[r][c])
                si_aliens[r][c] = 0
                si_alive_count -= 1
                si_total_kills += 1
                display.fill_rect(ax, ay, SI_ALIEN_W, SI_ALIEN_H, BLACK)
                return pts
    return 0

# ===== BULLET UPDATES =====

def si_update_bullet():
    global si_bullet, si_score, si_ufo_x, si_ufo_timer
    if si_bullet is None:
        return
    display.fill_rect(si_bullet[0], si_bullet[1], SI_BULLET_W, SI_BULLET_H, BLACK)
    si_bullet[1] -= SI_BULLET_SPEED
    if si_bullet[1] < 0:
        si_bullet = None
        return
    # Check UFO hit
    if si_ufo_x >= 0 and si_bullet[1] < 44:
        if (si_bullet[0] + SI_BULLET_W > si_ufo_x and
            si_bullet[0] < si_ufo_x + 30 and
            si_bullet[1] < 44 and si_bullet[1] + SI_BULLET_H > 32):
            ufo_vals = [50, 100, 100, 150, 200, 300]
            ufo_pts = ufo_vals[random.randint(0, 5)]
            si_score += ufo_pts
            erase_si_ufo(si_ufo_x)
            draw_text(display, str(ufo_pts), si_ufo_x + 2, 33, GREEN, 1, CODE_FONT)
            si_ufo_x = -1
            si_ufo_timer = time.ticks_ms()
            si_bullet = None
            return
    # Check shield hit
    if si_check_shield_hit(si_bullet[0], si_bullet[1], True):
        si_bullet = None
        return
    # Check alien hit
    pts = si_check_alien_hit(si_bullet[0], si_bullet[1])
    if pts > 0:
        si_score += pts
        si_bullet = None
        return
    display.fill_rect(si_bullet[0], si_bullet[1], SI_BULLET_W, SI_BULLET_H, SI_BULLET_COLOR)

def si_update_alien_bullets():
    global si_alien_bullets
    new_bullets = []
    for b in si_alien_bullets:
        display.fill_rect(b[0], b[1], SI_BULLET_W, SI_BULLET_H, BLACK)
        b[1] += SI_ALIEN_BULLET_SPEED
        if b[1] > 448:
            continue
        if si_check_shield_hit(b[0], b[1], False):
            continue
        if (b[0] + SI_BULLET_W > si_ship_x and b[0] < si_ship_x + SI_SHIP_W and
            b[1] + SI_BULLET_H > SI_SHIP_Y and b[1] < SI_SHIP_Y + SI_SHIP_H):
            si_player_hit()
            continue
        display.fill_rect(b[0], b[1], SI_BULLET_W, SI_BULLET_H, GREY)
        new_bullets.append(b)
    si_alien_bullets = new_bullets

def si_alien_shoot():
    global si_alien_bullets
    max_bullets = min(si_wave, 3)  # Wave 1: 1, wave 2: 2, wave 3+: 3
    if len(si_alien_bullets) >= max_bullets:
        return
    shoot_chance = max(40, 90 - si_wave * 10)  # Wave 1: 1/80, wave 2: 1/70, ... wave 5+: 1/40
    if random.randint(1, shoot_chance) != 1:
        return
    alive_cols = []
    for c in range(SI_COLS):
        for r in range(SI_ROWS - 1, -1, -1):
            if si_aliens[r][c] != 0:
                alive_cols.append((r, c))
                break
    if not alive_cols:
        return
    r, c = alive_cols[random.randint(0, len(alive_cols) - 1)]
    ax = SI_GRID_START_X + si_grid_x + c * (SI_ALIEN_W + SI_GAP_X) + SI_ALIEN_W // 2 - SI_BULLET_W // 2
    ay = SI_GRID_START_Y + si_grid_y + r * (SI_ALIEN_H + SI_GAP_Y) + SI_ALIEN_H
    si_alien_bullets.append([ax, ay])

# ===== ALIEN MOVEMENT =====

def si_get_bounds():
    left_col = SI_COLS
    right_col = -1
    for r in range(SI_ROWS):
        for c in range(SI_COLS):
            if si_aliens[r][c] != 0:
                if c < left_col:
                    left_col = c
                if c > right_col:
                    right_col = c
    if right_col < 0:
        return 0, 0
    left_x = SI_GRID_START_X + si_grid_x + left_col * (SI_ALIEN_W + SI_GAP_X)
    right_x = SI_GRID_START_X + si_grid_x + right_col * (SI_ALIEN_W + SI_GAP_X) + SI_ALIEN_W
    return left_x, right_x

def si_get_bottom():
    for r in range(SI_ROWS - 1, -1, -1):
        for c in range(SI_COLS):
            if si_aliens[r][c] != 0:
                return SI_GRID_START_Y + si_grid_y + r * (SI_ALIEN_H + SI_GAP_Y) + SI_ALIEN_H
    return 0

def si_update_aliens():
    global si_grid_x, si_grid_y, si_dir, si_last_move, si_mode
    move_delay = max(50, si_alive_count * 10)
    now = time.ticks_ms()
    if time.ticks_diff(now, si_last_move) < move_delay:
        return
    si_last_move = now

    old_gx = si_grid_x
    old_gy = si_grid_y

    left_x, right_x = si_get_bounds()
    next_left = left_x + si_dir * SI_STEP
    next_right = right_x + si_dir * SI_STEP

    if next_right > 360 or next_left < 5:
        si_grid_y += SI_DROP
        si_dir = -si_dir
    else:
        si_grid_x += si_dir * SI_STEP

    # Check if aliens reached bottom
    if si_get_bottom() >= SI_SHIP_Y - 5:
        si_mode = 1

    # Erase old, draw new for each alive alien
    for r in range(SI_ROWS):
        for c in range(SI_COLS):
            if si_aliens[r][c] != 0:
                old_ax = SI_GRID_START_X + old_gx + c * (SI_ALIEN_W + SI_GAP_X)
                old_ay = SI_GRID_START_Y + old_gy + r * (SI_ALIEN_H + SI_GAP_Y)
                display.fill_rect(old_ax, old_ay, SI_ALIEN_W, SI_ALIEN_H, BLACK)
                new_ax = SI_GRID_START_X + si_grid_x + c * (SI_ALIEN_W + SI_GAP_X)
                new_ay = SI_GRID_START_Y + si_grid_y + r * (SI_ALIEN_H + SI_GAP_Y)
                display.fill_rect(new_ax, new_ay, SI_ALIEN_W, SI_ALIEN_H, si_alien_color(si_aliens[r][c]))

# ===== GAME STATE =====

def si_player_hit():
    global si_lives, si_mode, si_alien_bullets, si_bullet, si_ship_x
    si_lives -= 1
    if si_lives <= 0:
        si_mode = 1
        return
    # Erase all bullets from screen before clearing them
    if si_bullet is not None:
        display.fill_rect(si_bullet[0], si_bullet[1], SI_BULLET_W, SI_BULLET_H, BLACK)
    for b in si_alien_bullets:
        display.fill_rect(b[0], b[1], SI_BULLET_W, SI_BULLET_H, BLACK)
    # Flash red
    display.fill_rect(si_ship_x, SI_SHIP_Y - 4, SI_SHIP_W, SI_SHIP_H + 4, make_color(200, 0, 0))
    time.sleep_ms(300)
    display.fill_rect(si_ship_x, SI_SHIP_Y - 4, SI_SHIP_W, SI_SHIP_H + 4, BLACK)
    si_ship_x = 169
    si_bullet = None
    si_alien_bullets = []
    time.sleep_ms(500)
    draw_si_ship()
    draw_si_header()

def si_wave_clear():
    global si_wave
    si_wave += 1
    draw_text(display, "WAVE " + str(si_wave), 110, 200, GREEN, 4, CODE_FONT)
    time.sleep_ms(1500)
    si_init_wave()
    draw_si_full()

def si_check_extra_life():
    global si_lives, si_extra_life_given
    if not si_extra_life_given and si_score >= 1500:
        si_lives += 1
        si_extra_life_given = True

# ===== GAME OVER =====

def draw_si_game_over():
    global si_high_score, si_best_wave, si_total_games
    si_total_games += 1
    if si_score > si_high_score:
        si_high_score = si_score
    if si_wave > si_best_wave:
        si_best_wave = si_wave
    save_invaders_stats()

    display.fill(BLACK)
    draw_text(display, "GAME OVER", 34, 80, GREY, 5, CODE_FONT)
    score_text = "SCORE: " + str(si_score)
    sw = len(score_text) * 18
    draw_text(display, score_text, (368 - sw) // 2, 150, GREY, 3, CODE_FONT)
    wave_text = "WAVE: " + str(si_wave)
    ww = len(wave_text) * 12
    draw_text(display, wave_text, (368 - ww) // 2, 195, GREY, 2, CODE_FONT)
    if si_score >= si_high_score and si_score > 0:
        hi_text = "NEW HIGH SCORE!"
        hw = len(hi_text) * 12
        draw_text(display, hi_text, (368 - hw) // 2, 220, GREEN, 2, CODE_FONT)
    # Standard buttons
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "MENU"
    bw = len(btn_text) * 12
    draw_text(display, btn_text, 25 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "RETRY"
    bw = len(btn_text) * 12
    draw_text(display, btn_text, 193 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)

# ===== STATS =====

def draw_invaders_stats():
    display.fill(BLACK)
    draw_text(display, "SPACE INVADERS", 30, 15, GREY, 3, CODE_FONT)
    y = 80
    rh = 50
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "HIGH SCORE: " + str(si_high_score), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "BEST WAVE: " + str(si_best_wave), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "ALIENS KILLED: " + str(si_total_kills), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "GAMES PLAYED: " + str(si_total_games), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)

# ===== ENTRY POINTS =====

def launch_invaders():
    global si_mode, si_score, si_lives, si_wave, si_ship_x, si_extra_life_given
    global si_old_ship_x, si_touching, si_touch_start
    si_mode = 0
    si_score = 0
    si_lives = 3
    si_wave = 1
    si_ship_x = 169
    si_old_ship_x = 169
    si_extra_life_given = False
    si_touching = False
    si_touch_start = 0
    si_init_wave()
    draw_si_full()

def handle_invaders_touch(tx, ty):
    global si_mode, current_screen, current_app, last_time_text
    if si_mode == 1:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:
                track_app_exit("SPACE INVADERS")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:
                launch_invaders()

def loop_invaders():
    global si_ship_x, si_bullet, si_mode, si_touching, si_touch_start

    # Read touch - tap to fire, hold 0.4s to move
    t = read_touch()
    if t is not None:
        tx, ty = t
        if not si_touching:
            # Touch just started - fire immediately
            si_touching = True
            si_touch_start = time.ticks_ms()
            if si_bullet is None:
                si_bullet = [si_ship_x + SI_SHIP_W // 2 - SI_BULLET_W // 2, SI_SHIP_Y - 4 - SI_BULLET_H]
        else:
            # Holding - move after 400ms delay
            if time.ticks_diff(time.ticks_ms(), si_touch_start) >= 150:
                if tx < 184:
                    si_ship_x = max(5, si_ship_x - SI_SHIP_SPEED)
                else:
                    si_ship_x = min(368 - SI_SHIP_W - 5, si_ship_x + SI_SHIP_SPEED)
                # Auto-fire while moving
                if si_bullet is None:
                    si_bullet = [si_ship_x + SI_SHIP_W // 2 - SI_BULLET_W // 2, SI_SHIP_Y - 4 - SI_BULLET_H]
    else:
        si_touching = False

    # Update bullets
    si_update_bullet()
    si_update_alien_bullets()

    # Update alien grid
    si_update_aliens()

    # Alien shooting
    si_alien_shoot()

    # UFO
    si_update_ufo()

    # Extra life check
    si_check_extra_life()

    # Wave clear check
    if si_alive_count <= 0:
        si_wave_clear()
        return

    # Draw ship (dirty-region)
    draw_si_ship()
    draw_si_header()

    # Game over check
    if si_mode == 1:
        draw_si_game_over()
        return

    time.sleep_ms(16)
