# ===== 2048 GAME =====
import random
import gc

TILE_COLORS = {
    0: make_color(40, 40, 40),
    2: make_color(0, 130, 0),      # starting green
    4: make_color(0, 118, 0),
    8: make_color(0, 107, 0),
    16: make_color(0, 95, 0),
    32: make_color(0, 83, 0),
    64: make_color(0, 72, 0),
    128: make_color(0, 60, 0),
    256: make_color(0, 48, 0),
    512: make_color(0, 37, 0),
    1024: make_color(0, 25, 0),
    2048: make_color(200, 170, 0), # gold
    4096: make_color(185, 156, 0),
    8192: make_color(170, 142, 0),
    16384: make_color(155, 128, 0),
    32768: make_color(140, 115, 0), # darker gold
}

game_grid = [[0]*4 for _ in range(4)]
game_score = 0
game_won = False
game_continuing = False

def init_2048():
    global game_grid, game_score, game_won, game_continuing
    game_grid = [[0]*4 for _ in range(4)]
    game_score = 0
    game_won = False
    game_continuing = False
    add_new_tile()
    add_new_tile()

def add_new_tile():
    empty = []
    for r in range(4):
        for c in range(4):
            if game_grid[r][c] == 0:
                empty.append((r, c))
    if empty:
        r, c = random.choice(empty)
        game_grid[r][c] = 2 if random.random() < 0.9 else 4

def get_board_score():
    total = 0
    for r in range(4):
        for c in range(4):
            total += game_grid[r][c]
    return total

def get_max_tile():
    max_val = 0
    for r in range(4):
        for c in range(4):
            if game_grid[r][c] > max_val:
                max_val = game_grid[r][c]
    return max_val

def check_has_2048():
    for r in range(4):
        for c in range(4):
            if game_grid[r][c] >= 2048:
                return True
    return False

def can_move():
    for r in range(4):
        for c in range(4):
            if game_grid[r][c] == 0:
                return True
            if c < 3 and game_grid[r][c] == game_grid[r][c+1]:
                return True
            if r < 3 and game_grid[r][c] == game_grid[r+1][c]:
                return True
    return False

def draw_2048_app():
    display.fill(BLACK)
    draw_text(display, "2048", 150, 10, GREY, 3, CODE_FONT)
    score = get_board_score()
    score_text = f"{score}"
    draw_text(display, score_text, 15, 15, GREY, 2, CODE_FONT)
    grid_size = 320
    tile_size = 76
    gap = 4
    start_x = (368 - grid_size) // 2
    start_y = 70
    for r in range(4):
        for c in range(4):
            x = start_x + c * (tile_size + gap)
            y = start_y + r * (tile_size + gap)
            val = game_grid[r][c]
            color = TILE_COLORS.get(val, TILE_COLORS[2048])
            display.fill_rect(x, y, tile_size, tile_size, color)
            if val > 0:
                val_str = str(val)
                if val < 10:
                    scale = 4
                elif val < 100:
                    scale = 3
                else:
                    scale = 2
                text_w = len(val_str) * 6 * scale
                text_h = 7 * scale
                tx = x + (tile_size - text_w) // 2
                ty = y + (tile_size - text_h) // 2
                draw_text(display, val_str, tx, ty, WHITE, scale, CODE_FONT)

def draw_2048_win_screen():
    display.fill(BLACK)
    title = "YOU WIN"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    score = get_board_score()
    score_text = f"SCORE: {score}"
    score_w = len(score_text) * 6 * 3
    draw_text(display, score_text, (368 - score_w) // 2, 160, GREY, 3, CODE_FONT)
    # Buttons: 150 wide, 70 tall
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "CONTINUE"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def draw_2048_death_screen():
    display.fill(BLACK)
    title = "GAME OVER"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    score = get_board_score()
    score_text = f"SCORE: {score}"
    score_w = len(score_text) * 6 * 3
    draw_text(display, score_text, (368 - score_w) // 2, 160, GREY, 3, CODE_FONT)
    # Buttons: 150 wide, 70 tall
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def slide_row_left(row):
    tiles = [x for x in row if x != 0]
    new_row = []
    points = 0
    i = 0
    while i < len(tiles):
        if i + 1 < len(tiles) and tiles[i] == tiles[i+1]:
            merged = tiles[i] * 2
            new_row.append(merged)
            points += merged
            i += 2
        else:
            new_row.append(tiles[i])
            i += 1
    while len(new_row) < 4:
        new_row.append(0)
    return new_row, points

def move_2048(direction):
    global game_grid, game_score, high_score_2048, highest_tile_2048
    old_grid = [row[:] for row in game_grid]
    points = 0
    if direction == 3:
        for r in range(4):
            game_grid[r], p = slide_row_left(game_grid[r])
            points += p
    elif direction == 1:
        for r in range(4):
            row = game_grid[r][::-1]
            new_row, p = slide_row_left(row)
            game_grid[r] = new_row[::-1]
            points += p
    elif direction == 0:
        for c in range(4):
            col = [game_grid[r][c] for r in range(4)]
            new_col, p = slide_row_left(col)
            for r in range(4):
                game_grid[r][c] = new_col[r]
            points += p
    elif direction == 2:
        for c in range(4):
            col = [game_grid[r][c] for r in range(3, -1, -1)]
            new_col, p = slide_row_left(col)
            for r in range(4):
                game_grid[3-r][c] = new_col[r]
            points += p
    moved = game_grid != old_grid
    if moved:
        game_score += points
        add_new_tile()
        current_score = get_board_score()
        max_tile = get_max_tile()
        stats_changed = False
        if current_score > high_score_2048:
            high_score_2048 = current_score
            stats_changed = True
        if max_tile > highest_tile_2048:
            highest_tile_2048 = max_tile
            stats_changed = True
        if stats_changed:
            save_stats()
    return moved

def launch_2048():
    init_2048()
    draw_2048_app()

def handle_2048_touch(tx, ty):
    global showing_win_screen, showing_death_screen, game_continuing, current_screen, current_app, last_time_text
    if showing_win_screen:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:
                showing_win_screen = False
                game_continuing = True
                draw_2048_app()
            elif 193 <= tx <= 343:
                showing_win_screen = False
                track_app_exit("2048")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
    elif showing_death_screen:
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:
                showing_death_screen = False
                init_2048()
                draw_2048_app()
            elif 193 <= tx <= 343:
                showing_death_screen = False
                track_app_exit("2048")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
    else:
        direction = get_swipe_direction(swipe_start_x, swipe_start_y, tx, ty)
        if direction >= 0:
            move_2048(direction)
            if not game_continuing and check_has_2048():
                showing_win_screen = True
                draw_2048_win_screen()
            elif not can_move():
                showing_death_screen = True
                draw_2048_death_screen()
            else:
                draw_2048_app()

def draw_2048_stats():
    display.fill(BLACK)
    draw_text(display, "2048 STATS", 100, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    hs_text = f"HIGH SCORE: {high_score_2048}"
    draw_text(display, hs_text, 30, y_start + 15, GREY, 3, CODE_FONT)
    y2 = y_start + row_height
    display.fill_rect(20, y2, 328, 3, DARK_GREY)
    ht_text = f"HIGHEST TILE: {highest_tile_2048}"
    draw_text(display, ht_text, 30, y2 + 15, GREY, 3, CODE_FONT)
    y_final = y2 + row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)
