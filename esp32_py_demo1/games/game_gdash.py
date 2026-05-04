# ===== GEOMETRY DASH =====

# Stats
gd_attempts = 0
gd_completions = 0
gd_best_pct = 0

# Constants
GD_GY = 370  # Ground Y
GD_SZ = 26
GD_GRAV = 0.9
GD_JVEL = -10.0
GD_LLEN = 200

# Colors
GD_GND = make_color(0, 50, 0)
GD_CUBE = make_color(0, 130, 0)
GD_CBRD = make_color(0, 180, 0)
GD_EYE = make_color(200, 200, 200)
GD_SP1 = make_color(0, 95, 0)
GD_SP2 = make_color(0, 140, 0)
GD_PL1 = make_color(0, 60, 10)
GD_PL2 = make_color(0, 100, 20)
GD_PRG = make_color(0, 120, 0)
GD_PBG = make_color(25, 25, 25)

# State
gd_mode = 0
gd_cy = 0.0
gd_vy = 0.0
gd_og = True
gd_sx = 0
gd_lv = None
gd_pct = 0
gd_lpct = -1
gd_spd = 4
gd_tap = False
gd_pcy = 0
gd_dif = 0

def gd_gen():
    """Generate level. 1=spike, 2=big spike, 5=tall spike. Physics-guaranteed beatable."""
    global gd_lv
    gd_lv = bytearray(GD_LLEN)
    # Gap = empty slots after each obstacle/group (guarantees time to land + re-jump)
    if gd_dif == 0: mn, mx = 4, 7
    elif gd_dif == 1: mn, mx = 3, 5
    else: mn, mx = 2, 4
    p = 12
    while p < GD_LLEN - 10:
        sec = min(3, p * 4 // GD_LLEN)
        r = random.randint(0, 99)
        # Spike type based on level section (gets harder as you progress)
        if sec == 0:
            gd_lv[p] = 1
        elif sec == 1:
            gd_lv[p] = 1 if r < 60 else 2
        elif sec == 2:
            gd_lv[p] = 1 if r < 40 else (2 if r < 70 else 5)
        else:
            gd_lv[p] = 2 if r < 30 else (5 if r < 55 else 1)
        # Spike pair on medium+ in later sections (2 slot gap = clearable at speed 4+)
        if gd_dif >= 1 and sec >= 2 and r < 35:
            if p + 2 < GD_LLEN - 10:
                gd_lv[p + 2] = 1
                p += 2
        # Random chance to skip for breathing room
        if random.randint(0, 99) < 15:
            gd_lv[p] = 0
        p += random.randint(mn, mx)

def gd_spk(x, by, w, h):
    """Fast spike: 3 overlapping rects, no gaps"""
    cx = x + w // 2
    h3 = h // 3
    # Base - full width
    display.fill_rect(cx - w // 2, by - h3, w, h3 + 1, GD_SP1)
    # Middle - overlaps base
    mw = w * 2 // 3
    display.fill_rect(cx - mw // 2, by - h3 * 2 - 1, mw, h3 + 3, GD_SP1)
    # Tip - overlaps middle
    tw = max(4, w // 3)
    display.fill_rect(cx - tw // 2, by - h, tw, h3 + 3, GD_SP2)

def gd_draw():
    """Draw frame - dirty region only"""
    global gd_lpct

    # 1. Clear old cube position (small area)
    oy = int(gd_pcy)
    display.fill_rect(58, oy - 1, GD_SZ + 4, GD_SZ + 3, BLACK)

    # 2. Clear obstacle band only (not entire screen!)
    display.fill_rect(0, GD_GY - 60, 368, 60, BLACK)

    # 3. Draw ground
    display.fill_rect(0, GD_GY, 368, 78, GD_GND)

    # 4. Draw obstacles
    ss = gd_sx // GD_SZ
    po = gd_sx % GD_SZ
    for i in range(15):
        sl = ss + i
        if sl < 0 or sl >= GD_LLEN: continue
        ob = gd_lv[sl]
        if ob == 0: continue
        ox = i * GD_SZ - po + 60
        if ox < -30 or ox > 400: continue
        if ob == 1:
            gd_spk(ox, GD_GY, GD_SZ, GD_SZ)
        elif ob == 2:
            gd_spk(ox - 3, GD_GY, GD_SZ + 6, 30)
        elif ob == 3:
            py = GD_GY - GD_SZ
            display.fill_rect(ox, py, GD_SZ, GD_SZ, GD_PL1)
            display.fill_rect(ox, py, GD_SZ, 3, GD_PL2)
        elif ob == 4:
            py = GD_GY - GD_SZ
            display.fill_rect(ox, py, GD_SZ, GD_SZ, GD_PL1)
            display.fill_rect(ox, py, GD_SZ, 3, GD_PL2)
            gd_spk(ox, py, GD_SZ, GD_SZ)
        elif ob == 5:
            gd_spk(ox - 2, GD_GY, GD_SZ + 4, 34)

    # 5. Draw cube
    ct = int(gd_cy)
    display.fill_rect(60, ct, GD_SZ, GD_SZ, GD_CUBE)
    display.fill_rect(60, ct, GD_SZ, 2, GD_CBRD)
    display.fill_rect(60, ct, 2, GD_SZ, GD_CBRD)
    display.fill_rect(60 + GD_SZ - 2, ct, 2, GD_SZ, GD_CBRD)
    display.fill_rect(60, ct + GD_SZ - 2, GD_SZ, 2, GD_CBRD)
    display.fill_rect(74, ct + 8, 8, 8, GD_EYE)
    display.fill_rect(78, ct + 11, 4, 4, BLACK)

    # 6. Progress bar (only on change)
    pct = min(100, gd_sx * 100 // max(1, (GD_LLEN - 8) * GD_SZ))
    if pct != gd_lpct:
        gd_lpct = pct
        display.fill_rect(34, 6, 240, 14, GD_PBG)
        bw = pct * 238 // 100
        if bw > 0:
            display.fill_rect(35, 7, bw, 12, GD_PRG)
        # Clear text area then draw
        display.fill_rect(280, 4, 70, 18, BLACK)
        draw_text(display, f"{pct}%", 282, 6, GREEN, 2, CODE_FONT)

def gd_update():
    global gd_cy, gd_vy, gd_og, gd_sx, gd_mode, gd_pct, gd_pcy

    gd_pcy = gd_cy
    gd_vy += GD_GRAV
    gd_cy += gd_vy

    gt = GD_GY - GD_SZ
    on_p = False

    # Platform landing
    wl = gd_sx
    wr = gd_sx + GD_SZ
    sl = wl // GD_SZ
    sr = wr // GD_SZ
    for s in range(max(0, sl), min(sr + 1, GD_LLEN)):
        if gd_lv[s] in (3, 4):
            ps = GD_GY - GD_SZ * 2
            if gd_vy >= 0 and gd_cy >= ps and gd_pcy <= ps + 4:
                gd_cy = ps
                gd_vy = 0
                gd_og = True
                on_p = True
                break

    if not on_p:
        if gd_cy >= gt:
            gd_cy = gt
            gd_vy = 0
            gd_og = True
        else:
            gd_og = False

    gd_sx += gd_spd

    if gd_sx >= (GD_LLEN - 8) * GD_SZ:
        gd_mode = 3
        gd_pct = 100
        return

    # Collision
    cl = gd_sx + 4
    cr = gd_sx + GD_SZ - 4
    ctp = int(gd_cy) + 4
    cb = int(gd_cy) + GD_SZ - 2
    s0 = cl // GD_SZ
    s1 = cr // GD_SZ

    for s in range(max(0, s0), min(s1 + 1, GD_LLEN)):
        ob = gd_lv[s]
        if ob == 0: continue
        ol = s * GD_SZ
        orr = ol + GD_SZ
        if ob == 1:
            scx = ol + GD_SZ // 2
            if cb > GD_GY - GD_SZ + 6 and ctp < GD_GY:
                d = min(1.0, (GD_GY - ctp) / GD_SZ)
                hw = max(2, int(GD_SZ // 2 * d))
                if cr > scx - hw and cl < scx + hw:
                    gd_mode = 2; return
        elif ob == 2:
            scx = ol + GD_SZ // 2
            if cb > GD_GY - 24 and ctp < GD_GY:
                d = min(1.0, (GD_GY - ctp) / 30)
                hw = max(2, int(14 * d))
                if cr > scx - hw and cl < scx + hw:
                    gd_mode = 2; return
        elif ob == 3:
            pt = GD_GY - GD_SZ
            if cr > ol and cl < orr and cb > pt + 6 and gd_cy > pt - GD_SZ + 4:
                gd_mode = 2; return
        elif ob == 4:
            pt = GD_GY - GD_SZ
            if cr > ol and cl < orr and cb > pt + 6 and gd_cy > pt - GD_SZ + 4:
                gd_mode = 2; return
            scx2 = ol + GD_SZ // 2
            if cb > pt - GD_SZ + 6 and ctp < pt:
                d = min(1.0, (pt - ctp) / GD_SZ)
                hw = max(2, int(GD_SZ // 2 * d))
                if cr > scx2 - hw and cl < scx2 + hw:
                    gd_mode = 2; return
        elif ob == 5:
            scx = ol + GD_SZ // 2
            if cb > GD_GY - 28 and ctp < GD_GY:
                d = min(1.0, (GD_GY - ctp) / 34)
                hw = max(2, int(14 * d))
                if cr > scx - hw and cl < scx + hw:
                    gd_mode = 2; return

    gd_pct = min(100, gd_sx * 100 // max(1, (GD_LLEN - 8) * GD_SZ))

def gd_draw_menu():
    display.fill(BLACK)
    tw = len("GEOMETRY DASH") * 18
    draw_text(display, "GEOMETRY DASH", (368 - tw) // 2, 50, GREY, 3, CODE_FONT)
    cx, cy = 158, 120
    display.fill_rect(cx, cy, 50, 50, GD_CUBE)
    display.fill_rect(cx, cy, 50, 3, GD_CBRD)
    display.fill_rect(cx, cy, 3, 50, GD_CBRD)
    display.fill_rect(cx + 47, cy, 3, 50, GD_CBRD)
    display.fill_rect(cx, cy + 47, 50, 3, GD_CBRD)
    display.fill_rect(cx + 24, cy + 12, 18, 18, GD_EYE)
    display.fill_rect(cx + 32, cy + 18, 8, 10, BLACK)
    display.fill_rect(84, 210, 200, 55, GAMEOVER_BTN)
    tw = len("PLAY") * 24
    draw_text(display, "PLAY", (368 - tw) // 2, 222, WHITE, 4, CODE_FONT)
    if gd_completions > 0:
        t = f"COMPLETED: {gd_completions}"
        draw_text(display, t, (368 - len(t) * 12) // 2, 395, GREEN, 2, CODE_FONT)
    elif gd_best_pct > 0:
        t = f"BEST: {gd_best_pct}%"
        draw_text(display, t, (368 - len(t) * 12) // 2, 395, GREEN, 2, CODE_FONT)
    if gd_attempts > 0:
        t = f"ATTEMPTS: {gd_attempts}"
        draw_text(display, t, (368 - len(t) * 12) // 2, 420, GREY, 2, CODE_FONT)

def gd_draw_diff():
    display.fill(BLACK)
    tw = len("SELECT") * 24
    draw_text(display, "SELECT", (368 - tw) // 2, 20, GREY, 4, CODE_FONT)
    tw = len("DIFFICULTY") * 24
    draw_text(display, "DIFFICULTY", (368 - tw) // 2, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", (368 - len("EASY") * 18) // 2, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", (368 - len("MEDIUM") * 18) // 2, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", (368 - len("HARD") * 18) // 2, 338, WHITE, 3, CODE_FONT)

def gd_init():
    global gd_mode, gd_cy, gd_vy, gd_og, gd_sx
    global gd_lpct, gd_attempts, gd_spd, gd_pcy, gd_tap
    gd_mode = 1
    gd_cy = float(GD_GY - GD_SZ)
    gd_vy = 0
    gd_og = True
    gd_sx = 0
    gd_lpct = -1
    gd_pcy = gd_cy
    gd_tap = False
    gd_attempts += 1
    if gd_dif == 0: gd_spd = 3
    elif gd_dif == 1: gd_spd = 4
    else: gd_spd = 5
    gd_gen()
    display.fill(BLACK)
    display.fill_rect(0, GD_GY, 368, 78, GD_GND)

def gd_restart():
    global gd_mode, gd_cy, gd_vy, gd_og, gd_sx
    global gd_lpct, gd_attempts, gd_pcy, gd_tap
    gd_mode = 1
    gd_cy = float(GD_GY - GD_SZ)
    gd_vy = 0
    gd_og = True
    gd_pcy = gd_cy
    gd_tap = False
    gd_sx = 0
    gd_lpct = -1
    gd_attempts += 1
    display.fill(BLACK)
    display.fill_rect(0, GD_GY, 368, 78, GD_GND)

def gd_draw_death():
    global gd_pct, gd_best_pct
    gd_pct = min(100, gd_sx * 100 // max(1, (GD_LLEN - 8) * GD_SZ))
    if gd_pct > gd_best_pct:
        gd_best_pct = gd_pct
        save_all_stats()
    display.fill(BLACK)
    tw = len("CRASH!") * 30
    draw_text(display, "CRASH!", (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    info = f"PROGRESS: {gd_pct}%"
    draw_text(display, info, (368 - len(info) * 18) // 2, 160, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "RETRY", 25 + (150 - len("RETRY") * 18) // 2, 273, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "EXIT", 193 + (150 - len("EXIT") * 18) // 2, 273, WHITE, 3, CODE_FONT)

def gd_draw_win():
    global gd_best_pct, gd_completions
    gd_best_pct = 100
    gd_completions += 1
    save_all_stats()
    display.fill(BLACK)
    tw = len("COMPLETE!") * 30
    draw_text(display, "COMPLETE!", (368 - tw) // 2, 80, GREEN, 5, CODE_FONT)
    info = f"ATTEMPTS: {gd_attempts}"
    draw_text(display, info, (368 - len(info) * 18) // 2, 160, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "AGAIN", 25 + (150 - len("AGAIN") * 18) // 2, 273, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    draw_text(display, "EXIT", 193 + (150 - len("EXIT") * 18) // 2, 273, WHITE, 3, CODE_FONT)

def draw_gd_stats():
    display.fill(BLACK)
    draw_text(display, "GDASH STATS", 85, 15, GREY, 3, CODE_FONT)
    y = 80
    rh = 50
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"ATTEMPTS: {gd_attempts}", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"COMPLETED: {gd_completions}", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, f"BEST: {gd_best_pct}%", 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)

def launch_gdash():
    global gd_mode
    gd_mode = 0
    gd_draw_menu()

def handle_gdash_touch(tx, ty):
    global gd_mode, gd_dif
    if gd_mode == 0:
        if 84 <= tx <= 284 and 210 <= ty <= 265:
            gd_mode = 4; gd_draw_diff()
    elif gd_mode == 4:
        if 34 <= tx <= 334:
            if 160 <= ty <= 220: gd_dif = 0
            elif 240 <= ty <= 300: gd_dif = 1
            elif 320 <= ty <= 380: gd_dif = 2
            else: return
            gd_init()
    elif gd_mode == 2:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175: gd_restart()
            elif 193 <= tx <= 343: gd_mode = 0; gd_draw_menu()
    elif gd_mode == 3:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175: gd_init()
            elif 193 <= tx <= 343: gd_mode = 0; gd_draw_menu()

def loop_gdash():
    global gd_tap, gd_vy, gd_og

    if gd_mode != 1: return

    t = read_touch()
    if (t is not None or touch_pressed) and not gd_tap:
        if gd_og:
            gd_vy = GD_JVEL
            gd_og = False
        gd_tap = True
    elif t is None and not touch_pressed:
        gd_tap = False

    gd_update()

    if gd_mode == 1:
        gd_draw()
    elif gd_mode == 2:
        gd_draw_death()
    elif gd_mode == 3:
        gd_draw_win()
