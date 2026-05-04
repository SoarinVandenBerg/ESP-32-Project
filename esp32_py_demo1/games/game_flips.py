# ===== UNFAIR FLIPS =====
import random

# Upgrade tables
FLIPS_CHANCE_VALS = [20, 25, 30, 35, 40, 45, 50, 55]
FLIPS_CHANCE_COSTS = [10, 25, 50, 100, 200, 400, 800]
FLIPS_VALUE_VALS = [1, 2, 3, 5, 8, 12]
FLIPS_VALUE_COSTS = [15, 40, 80, 150, 300]
FLIPS_COMBO_VALS = [1, 2, 3, 5]
FLIPS_COMBO_COSTS = [50, 150, 400]

FLIPS_COIN_CX = 184
FLIPS_COIN_CY = 220
FLIPS_COIN_R = 70

# Game state
flips_mode = 0          # 0=ready, 1=showing result, 2=shop, 3=win
flips_coins = 0
flips_streak = 0
flips_best_streak = 0
flips_total_flips = 0
flips_total_heads = 0
flips_wins = 0
flips_last_result = -1  # -1=none, 0=tails, 1=heads
flips_last_earn = 0
flips_chance_lv = 0
flips_value_lv = 0
flips_combo_lv = 0

def flips_get_chance():
    return FLIPS_CHANCE_VALS[flips_chance_lv]

def flips_get_value():
    return FLIPS_VALUE_VALS[flips_value_lv]

def flips_get_combo():
    return FLIPS_COMBO_VALS[flips_combo_lv]

def flips_calc_earn():
    base = flips_get_value()
    combo = flips_get_combo() if flips_streak >= 3 else 1
    return base * combo

# ===== DRAWING =====

def draw_flips_header():
    display.fill_rect(0, 0, 368, 42, BLACK)
    coin_text = "$ " + str(flips_coins)
    draw_text(display, coin_text, 15, 10, GREEN, 3, CODE_FONT)
    # Best streak top right
    best_text = "BEST:" + str(flips_best_streak)
    tw = len(best_text) * 12
    draw_text(display, best_text, 368 - tw - 25, 15, GREY, 2, CODE_FONT)

def draw_flips_streak():
    display.fill_rect(0, 44, 368, 50, BLACK)
    streak_text = "STREAK: " + str(flips_streak) + "/10"
    tw = len(streak_text) * 18
    draw_text(display, streak_text, (368 - tw) // 2, 48, GREY, 3, CODE_FONT)
    # Progress bar
    bar_x = 34
    bar_y = 78
    bar_w = 300
    bar_h = 10
    display.fill_rect(bar_x, bar_y, bar_w, bar_h, DARK_GREY)
    fill_w = (bar_w * flips_streak) // 10
    if fill_w > 0:
        display.fill_rect(bar_x, bar_y, fill_w, bar_h, GREEN)

def draw_flips_chance():
    display.fill_rect(0, 92, 368, 25, BLACK)
    chance_text = "CHANCE: " + str(flips_get_chance()) + "%"
    tw = len(chance_text) * 12
    draw_text(display, chance_text, (368 - tw) // 2, 96, GREY, 2, CODE_FONT)

def draw_flips_coin_ready():
    cx = FLIPS_COIN_CX
    cy = FLIPS_COIN_CY
    r = FLIPS_COIN_R
    # Clear coin area
    display.fill_rect(cx - r - 5, cy - r - 5, r * 2 + 10, r * 2 + 10, BLACK)
    # Green outline circle
    display.fill_circle(cx, cy, r, GREEN)
    display.fill_circle(cx, cy, r - 4, BLACK)
    # TAP text
    draw_text(display, "TAP", cx - 27, cy - 10, GREEN, 3, CODE_FONT)

def draw_flips_coin_heads():
    cx = FLIPS_COIN_CX
    cy = FLIPS_COIN_CY
    r = FLIPS_COIN_R
    display.fill_rect(cx - r - 5, cy - r - 5, r * 2 + 10, r * 2 + 10, BLACK)
    display.fill_circle(cx, cy, r, GAMEOVER_BTN)
    # Big H
    draw_text(display, "H", cx - 24, cy - 28, WHITE, 8, CODE_FONT)

def draw_flips_coin_tails():
    cx = FLIPS_COIN_CX
    cy = FLIPS_COIN_CY
    r = FLIPS_COIN_R
    display.fill_rect(cx - r - 5, cy - r - 5, r * 2 + 10, r * 2 + 10, BLACK)
    display.fill_circle(cx, cy, r, DARK_GREY)
    # Big T
    draw_text(display, "T", cx - 24, cy - 28, WHITE, 8, CODE_FONT)

def flips_animate():
    cx = FLIPS_COIN_CX
    cy = FLIPS_COIN_CY
    r = FLIPS_COIN_R
    clear = (cx - r - 5, cy - r - 5, r * 2 + 10, r * 2 + 10)
    # Spin while held, minimum 5 frames, 3 extra after release
    frame = 0
    extra = 0
    while True:
        display.fill_rect(clear[0], clear[1], clear[2], clear[3], BLACK)
        if frame % 2 == 0:
            display.fill_circle(cx, cy, r, GREY)
            draw_text(display, "?", cx - 24, cy - 28, WHITE, 8, CODE_FONT)
        else:
            display.fill_rect(cx - 4, cy - r, 8, r * 2, GREY)
        time.sleep_ms(80)
        frame += 1
        if frame >= 5 and read_touch() is None:
            extra += 1
            if extra >= 3:
                break

def draw_flips_result():
    display.fill_rect(0, 310, 368, 40, BLACK)
    if flips_last_result == 1:
        txt = "HEADS! +" + str(flips_last_earn)
        tw = len(txt) * 18
        draw_text(display, txt, (368 - tw) // 2, 320, GREEN, 3, CODE_FONT)
    elif flips_last_result == 0:
        txt = "TAILS! STREAK LOST"
        tw = len(txt) * 12
        draw_text(display, txt, (368 - tw) // 2, 325, GREY, 2, CODE_FONT)

def draw_flips_bottom():
    display.fill_rect(0, 395, 368, 53, BLACK)
    # Shop button at bottom center
    display.fill_rect(134, 400, 100, 40, GAMEOVER_BTN)
    draw_text(display, "SHOP", 149, 410, WHITE, 2, CODE_FONT)

def draw_flips_game():
    display.fill(BLACK)
    draw_text(display, "UNFAIR FLIPS", 55, 10, GREY, 3, CODE_FONT)
    draw_flips_header()
    draw_flips_streak()
    draw_flips_chance()
    draw_flips_coin_ready()
    draw_flips_bottom()

# ===== SHOP =====

def draw_flips_shop():
    display.fill(BLACK)
    draw_text(display, "SHOP", 140, 10, GREY, 4, CODE_FONT)
    coin_text = "$ " + str(flips_coins)
    draw_text(display, coin_text, 15, 18, GREEN, 2, CODE_FONT)

    # Upgrade rows
    draw_flips_upgrade_row(80, "HEADS CHANCE",
        FLIPS_CHANCE_VALS, FLIPS_CHANCE_COSTS, flips_chance_lv, "%")
    draw_flips_upgrade_row(180, "COIN VALUE",
        FLIPS_VALUE_VALS, FLIPS_VALUE_COSTS, flips_value_lv, "/FLIP")
    draw_flips_upgrade_row(280, "COMBO BONUS",
        FLIPS_COMBO_VALS, FLIPS_COMBO_COSTS, flips_combo_lv, "X")

    # Back button
    display.fill_rect(84, 390, 200, 50, GAMEOVER_BTN)
    draw_text(display, "BACK", 156, 405, WHITE, 3, CODE_FONT)

def draw_flips_upgrade_row(y, title, vals, costs, level, suffix):
    draw_text(display, title, 30, y, GREEN, 2, CODE_FONT)

    current = vals[level]
    if suffix == "X":
        cur_text = "X" + str(current)
    else:
        cur_text = str(current) + suffix

    if level < len(costs):
        nxt = vals[level + 1]
        if suffix == "X":
            nxt_text = "X" + str(nxt)
        else:
            nxt_text = str(nxt) + suffix
        desc = "LV " + str(level) + ": " + cur_text + " > " + nxt_text
        draw_text(display, desc, 30, y + 25, GREY, 2, CODE_FONT)
        # Buy button
        cost = costs[level]
        btn_color = GAMEOVER_BTN if flips_coins >= cost else DARK_GREY
        display.fill_rect(84, y + 55, 200, 35, btn_color)
        buy_text = "BUY: " + str(cost)
        tw = len(buy_text) * 12
        draw_text(display, buy_text, 84 + (200 - tw) // 2, y + 62, WHITE, 2, CODE_FONT)
    else:
        desc = "LV " + str(level) + ": " + cur_text + " (MAX)"
        draw_text(display, desc, 30, y + 25, GREY, 2, CODE_FONT)
        display.fill_rect(84, y + 55, 200, 35, DARK_GREY)
        draw_text(display, "MAXED", 84 + 70, y + 62, GREY, 2, CODE_FONT)

# ===== WIN SCREEN =====

def draw_flips_win():
    display.fill(BLACK)
    title = "YOU WIN!"
    tw = len(title) * 30
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    info = "10 HEADS IN A ROW!"
    iw = len(info) * 12
    draw_text(display, info, (368 - iw) // 2, 160, GREEN, 2, CODE_FONT)
    coins_text = "COINS: " + str(flips_coins)
    cw = len(coins_text) * 12
    draw_text(display, coins_text, (368 - cw) // 2, 200, GREY, 2, CODE_FONT)
    # Buttons
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "MENU"
    bw = len(btn_text) * 12
    draw_text(display, btn_text, 25 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "CONTINUE"
    bw = len(btn_text) * 12
    draw_text(display, btn_text, 193 + (150 - bw) // 2, 273, WHITE, 2, CODE_FONT)

# ===== GAME LOGIC =====

def flips_do_flip():
    global flips_streak, flips_coins, flips_total_flips, flips_total_heads
    global flips_best_streak, flips_wins, flips_last_result, flips_last_earn, flips_mode

    flips_total_flips += 1
    flips_animate()
    chance = flips_get_chance()
    roll = random.randint(1, 100)

    if roll <= chance:
        # HEADS!
        flips_total_heads += 1
        flips_streak += 1
        earn = flips_calc_earn()
        flips_coins += earn
        flips_last_result = 1
        flips_last_earn = earn
        if flips_streak > flips_best_streak:
            flips_best_streak = flips_streak
        # Check for win
        if flips_streak >= 10:
            flips_wins += 1
            flips_mode = 3
            save_flips_stats()
            draw_flips_win()
            return
    else:
        # TAILS
        flips_streak = 0
        flips_last_result = 0
        flips_last_earn = 0

    save_flips_stats()
    # Update display (dirty-region style)
    draw_flips_header()
    draw_flips_streak()
    if flips_last_result == 1:
        draw_flips_coin_heads()
    else:
        draw_flips_coin_tails()
    draw_flips_result()
    draw_flips_bottom()

def flips_buy_upgrade(upgrade_type):
    global flips_coins, flips_chance_lv, flips_value_lv, flips_combo_lv
    if upgrade_type == 0:
        if flips_chance_lv < len(FLIPS_CHANCE_COSTS):
            cost = FLIPS_CHANCE_COSTS[flips_chance_lv]
            if flips_coins >= cost:
                flips_coins -= cost
                flips_chance_lv += 1
                save_flips_stats()
                return True
    elif upgrade_type == 1:
        if flips_value_lv < len(FLIPS_VALUE_COSTS):
            cost = FLIPS_VALUE_COSTS[flips_value_lv]
            if flips_coins >= cost:
                flips_coins -= cost
                flips_value_lv += 1
                save_flips_stats()
                return True
    elif upgrade_type == 2:
        if flips_combo_lv < len(FLIPS_COMBO_COSTS):
            cost = FLIPS_COMBO_COSTS[flips_combo_lv]
            if flips_coins >= cost:
                flips_coins -= cost
                flips_combo_lv += 1
                save_flips_stats()
                return True
    return False

# ===== STATS =====

def draw_flips_stats():
    display.fill(BLACK)
    draw_text(display, "UNFAIR FLIPS", 60, 15, GREY, 3, CODE_FONT)
    y = 80
    rh = 50
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "COINS: " + str(flips_coins), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "BEST STREAK: " + str(flips_best_streak), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "TOTAL FLIPS: " + str(flips_total_flips), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "TOTAL HEADS: " + str(flips_total_heads), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    draw_text(display, "WINS (10+): " + str(flips_wins), 30, y + 15, GREY, 3, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)

# ===== ENTRY POINTS =====

def launch_flips():
    global flips_mode, flips_streak, flips_last_result
    flips_mode = 0
    flips_streak = 0
    flips_last_result = -1
    draw_flips_game()

def handle_flips_touch(tx, ty):
    global flips_mode, current_screen, current_app, last_time_text

    if flips_mode == 0 or flips_mode == 1:
        # Main game screen
        # Check SHOP button (bottom center)
        if 400 <= ty <= 440 and 134 <= tx <= 234:
            flips_mode = 2
            draw_flips_shop()
            return
        # Tap anywhere else = flip
        flips_do_flip()
        if flips_mode != 3:
            flips_mode = 1

    elif flips_mode == 2:
        # Shop screen
        # Back button
        if 390 <= ty <= 440 and 84 <= tx <= 284:
            flips_mode = 0
            draw_flips_game()
            return
        # Buy buttons (centered x=84-284)
        if 84 <= tx <= 284:
            if 135 <= ty <= 170:
                if flips_buy_upgrade(0):
                    draw_flips_shop()
            elif 235 <= ty <= 270:
                if flips_buy_upgrade(1):
                    draw_flips_shop()
            elif 335 <= ty <= 370:
                if flips_buy_upgrade(2):
                    draw_flips_shop()

    elif flips_mode == 3:
        # Win screen
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:
                track_app_exit("UNFAIR FLIPS")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:
                flips_mode = 1
                flips_streak = 0
                draw_flips_game()
