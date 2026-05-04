# ===== WORD SEARCH GAME =====

# Word lists by length per difficulty
WS_WORDS_4 = ["CAKE","FIRE","RAIN","SNOW","WIND","LAKE","ROCK","GOLD","KING","BLUE",
    "BEAR","LION","FROG","SHIP","BOAT","BALL","KITE","DRUM","FLAG","LAMP",
    "RING","ROSE","SEED","LEAF","NEST","DEER","WOLF","HAWK","CRAB","SEAL",
    "PEAR","DUCK","COIN","FORK","DOOR","BELL","BONE","CORN","DICE","FERN",
    "GIFT","GOAT","HARE","HORN","IRON","JADE","KNOT","LIME","MASK","NAIL",
    "OPAL","PALM","PEAK","RUBY","SAND","TOAD","VINE","WAVE","YARN","ZINC",
    "ARCH","BARN","CAVE","DAWN","ECHO","FAWN","GLOW","HAZE","ISLE","JAZZ",
    "KELP","LAVA","MAZE","NOVA","ORCA","PINE","REEF","SAGE","TUSK","VENT",
    "WREN","APEX","BOLT","CROW","DUSK","EDGE","FOAM","GUST","HIVE","CLAM",
    "MOTH","PLUM","SILK","TWIG","YAWN","BEAD","DUNE","GLEN","IRIS","MIST"]
WS_WORDS_6 = ["PLANET","FROZEN","CASTLE","FOREST","STREAM","BRIDGE","FLOWER","GARDEN",
    "ISLAND","JUNGLE","KNIGHT","LAGOON","MARBLE","NEEDLE","ORANGE","PARROT",
    "QUARTZ","RIBBON","SADDLE","TEMPLE","URCHIN","VALLEY","WALNUT","YELLOW",
    "BREEZE","CANDLE","DONKEY","EMPIRE","FALCON","GOBLIN","HAMMER","INSECT",
    "JACKET","KITTEN","LIZARD","MIRROR","NAPKIN","OYSTER","PEPPER","RACKET",
    "SILVER","THRONE","VELVET","WINTER","ANCHOR","BASKET","CHERRY","DRAGON",
    "ENGINE","GRAVEL","HARBOR","JIGSAW","KERNEL","LOCKER","MAGNET","NECTAR",
    "ORCHID","PENCIL","RABBIT","SHIELD","TIMBER","TURTLE","VACUUM","WAFFLE",
    "ZENITH","BADGER","COBALT","DESERT","FOSSIL","GUITAR","HELMET","IGUANA",
    "JUMBLE","KETTLE","LOCKET","MUFFIN","NICKEL","OUTLET","PIRATE","QUIVER",
    "ROCKET","SUNSET","TOMATO","VOYAGE","WINDOW","BISHOP","CLOVER","DAGGER",
    "ERASER","FLORAL","GEYSER","SPIRIT","HERMIT","ICICLE","JASPER","MYRTLE",
    "NUTMEG","PICKLE","TROPHY","TUXEDO"]
WS_WORDS_8 = ["BATHROOM","CALENDAR","DARKNESS","ELEPHANT","FIREWOOD","GOLDFISH","KEYBOARD",
    "ICECREAM","LANDLORD","MANDARIN","NOTEBOOK","OVERCAST","PAINTING","QUARTERS",
    "RAILROAD","SANDWICH","TEAMMATE","UMBRELLA","VACATION","WARDROBE","YEARBOOK",
    "ABSOLUTE","BACKYARD","CAMPFIRE","DINOSAUR","ENVELOPE","FOOTWEAR","GEMSTONE",
    "HIGHLAND","IGNORANT","JUNKYARD","KNOCKOUT","LIFEBOAT","MUSHROOM","NECKLACE",
    "OBSTACLE","PLATFORM","QUICKEST","REINDEER","YEARNING","BANKRUPT","CARDINAL",
    "DOGHOUSE","EARNINGS","FOOTBALL","GUARDIAN","HOMEWORK","INVENTOR","JUNCTION",
    "KEEPSAKE","LAVENDER","MAINLAND","NUISANCE","OUTDOORS","PANCAKES","QUESTION",
    "REMEMBER","SOFTWOOD","THIRTEEN","TWILIGHT","UNDERDOG","VITAMINS","WRESTLER",
    "ABUNDANT","CHAPLAIN","DOORBELL","EQUATION","FEARLESS","HANDBOOK","BOOKMARK",
    "COMPLETE","CRIMINAL","EXPLORER","FIREWORK","GUNSMITH","HAPPENED","IMPORTED",
    "KINDNESS","LEMONADE","MISTAKEN","NINETEEN","OBSERVER","PARADISE","RESTLESS",
    "SEASHORE","BLIZZARD","CONVERGE","DRIVEWAY","ELEPHANT","FREEZING","GRACEFUL",
    "HANDMADE","INITIALS","JEWELLER","KANGAROO","LIFELINE","MECHANIC","NONSENSE"]

# Colors
WS_FOUND_BG = make_color(0, 80, 0)
WS_CELL_BG = make_color(25, 25, 30)
WS_SEL_COLOR = make_color(0, 180, 0)

# State
ws_mode = 0          # 0=difficulty, 1=playing, 2=won
ws_difficulty = 0    # 0=easy, 1=med, 2=hard
ws_grid_n = 8
ws_board = []        # flat list of chars
ws_words = []        # words to find
ws_found = []        # which words found (bool list)
ws_found_cells = []  # list of (row,col) that are part of found words
ws_selected = []     # list of (row,col) currently selected by player
ws_timer_start = 0
ws_last_timer = ""
ws_cell_size = 40
ws_grid_x = 0
ws_grid_y = 42
ws_word_positions = []  # list of [(r,c), ...] for each word

# Stats
ws_easy_wins = 0
ws_med_wins = 0
ws_hard_wins = 0
ws_easy_best = 0
ws_med_best = 0
ws_hard_best = 0

def save_ws_stats():
    save_all_stats()

def ws_place_words():
    """Place words on grid, return True if all placed."""
    global ws_board, ws_word_positions
    n = ws_grid_n
    ws_board = [' '] * (n * n)
    ws_word_positions = []
    count = len(ws_words)
    placed = 0
    for wi in range(count):
        word = ws_words[wi]
        wlen = len(word)
        ok = False
        # 8 directions: (dr, dc)
        # right, left, down, up, down-right, down-left, up-right, up-left
        dirs = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
        for attempt in range(40):
            # 33% horizontal, 33% vertical, 33% diagonal
            cat = random.randint(0, 2)
            if cat == 0:
                # Horizontal: 60% forward, 40% backward
                dr = 0
                dc = 1 if random.randint(1, 10) <= 6 else -1
            elif cat == 1:
                # Vertical: 60% forward (down), 40% backward (up)
                dc = 0
                dr = 1 if random.randint(1, 10) <= 6 else -1
            else:
                # Diagonal: 50/50 which diagonal, 60/40 forward/backward each
                if random.randint(0, 1) == 0:
                    # Down-right / Up-left
                    if random.randint(1, 10) <= 6:
                        dr, dc = 1, 1
                    else:
                        dr, dc = -1, -1
                else:
                    # Down-left / Up-right
                    if random.randint(1, 10) <= 6:
                        dr, dc = 1, -1
                    else:
                        dr, dc = -1, 1
            # Pick start so word fits in grid
            if dc == 1:
                c = random.randint(0, n - wlen)
            elif dc == -1:
                c = random.randint(wlen - 1, n - 1)
            else:
                c = random.randint(0, n - 1)
            if dr == 1:
                r = random.randint(0, n - wlen)
            elif dr == -1:
                r = random.randint(wlen - 1, n - 1)
            else:
                r = random.randint(0, n - 1)
            # Check fit
            fits = True
            for k in range(wlen):
                cr = r + k * dr
                cc = c + k * dc
                existing = ws_board[cr * n + cc]
                if existing != ' ' and existing != word[k]:
                    fits = False
                    break
            if fits:
                cells = []
                for k in range(wlen):
                    cr = r + k * dr
                    cc = c + k * dc
                    ws_board[cr * n + cc] = word[k]
                    cells.append((cr, cc))
                ws_word_positions.append(cells)
                placed += 1
                ok = True
                break
        if not ok:
            ws_word_positions.append([])  # empty = not placed
    # Remove words that couldn't be placed
    i = len(ws_words) - 1
    while i >= 0:
        if not ws_word_positions[i]:
            ws_words.pop(i)
            ws_word_positions.pop(i)
        i -= 1
    # Fill blanks with random letters
    for i in range(n * n):
        if ws_board[i] == ' ':
            ws_board[i] = chr(65 + random.randint(0, 25))

def ws_pick_words(count):
    """Pick count random words from difficulty-appropriate list."""
    if ws_difficulty == 0:
        src = WS_WORDS_4
    elif ws_difficulty == 1:
        src = WS_WORDS_6
    else:
        src = WS_WORDS_8
    pool = list(range(len(src)))
    # Shuffle pool
    for i in range(len(pool) - 1, 0, -1):
        j = random.randint(0, i)
        pool[i], pool[j] = pool[j], pool[i]
    result = []
    for i in range(min(count, len(pool))):
        w = src[pool[i]]
        if len(w) <= ws_grid_n:
            result.append(w)
    return result

def ws_start_game():
    global ws_mode, ws_board, ws_words, ws_found, ws_found_cells
    global ws_selected, ws_timer_start, ws_last_timer, ws_cell_size, ws_grid_x
    global ws_grid_n
    if ws_difficulty == 0:
        ws_grid_n = 8
        num_words = 4
    elif ws_difficulty == 1:
        ws_grid_n = 10
        num_words = 6
    else:
        ws_grid_n = 12
        num_words = 8
    # Cell size to fit 368px width
    ws_cell_size = 368 // ws_grid_n
    ws_grid_x = (368 - ws_grid_n * ws_cell_size) // 2
    ws_words = ws_pick_words(num_words)
    ws_place_words()
    ws_found = [False] * len(ws_words)
    ws_found_cells = []
    ws_selected = []
    ws_timer_start = time.ticks_ms()
    ws_last_timer = ""
    ws_mode = 1
    ws_draw_board()

def ws_is_selected(r, c):
    """Check if cell is in selected list."""
    for sr, sc in ws_selected:
        if sr == r and sc == c:
            return True
    return False

def ws_draw_board():
    """Full redraw of the game board."""
    display.fill(BLACK)
    n = ws_grid_n
    sz = ws_cell_size
    txt_size = 2 if n <= 10 else 1
    char_w = 12 if txt_size == 2 else 6
    char_h = 14 if txt_size == 2 else 7
    for r in range(n):
        for c in range(n):
            x = ws_grid_x + c * sz
            y = ws_grid_y + r * sz
            is_found = False
            for fr, fc in ws_found_cells:
                if fr == r and fc == c:
                    is_found = True
                    break
            is_sel = ws_is_selected(r, c)
            if is_found:
                bg = WS_FOUND_BG
            elif is_sel:
                bg = WS_SEL_COLOR
            else:
                bg = WS_CELL_BG
            display.fill_rect(x + 1, y + 1, sz - 2, sz - 2, bg)
            ch = ws_board[r * n + c]
            tx = x + (sz - char_w) // 2
            ty = y + (sz - char_h) // 2
            tc = BLACK if is_sel and not is_found else WHITE
            draw_text(display, ch, tx, ty, tc, txt_size, CODE_FONT)
    ws_draw_word_list()
    ws_draw_timer()

def ws_draw_word_list():
    """Draw word list below the grid."""
    n = ws_grid_n
    sz = ws_cell_size
    list_y = ws_grid_y + n * sz + 6
    # Clear word list area
    display.fill_rect(0, list_y, 368, 448 - list_y, BLACK)
    wc = len(ws_words)
    if wc <= 4:
        cols = 2
    elif wc <= 6:
        cols = 3
    else:
        cols = 4
    # Use smaller text for long words
    tsz = 1 if ws_difficulty == 2 else 2
    cw = 6 * tsz  # char width
    rh = 8 * tsz + 4  # row height
    col_w = 368 // cols
    for i in range(len(ws_words)):
        col = i % cols
        row = i // cols
        x = col * col_w + (col_w - len(ws_words[i]) * cw) // 2
        y = list_y + row * rh
        if ws_found[i]:
            draw_text(display, ws_words[i], x, y, GREEN, tsz, CODE_FONT)
            tw = len(ws_words[i]) * cw
            display.fill_rect(x, y + (4 * tsz), tw, 2, GREEN)
        else:
            draw_text(display, ws_words[i], x, y, GREY, tsz, CODE_FONT)

def ws_draw_timer():
    global ws_last_timer
    elapsed = time.ticks_diff(time.ticks_ms(), ws_timer_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    t = "{:02d}:{:02d}".format(mins, secs)
    if t != ws_last_timer:
        display.fill_rect(270, 10, 90, 22, BLACK)
        draw_text(display, t, 270, 10, GREY, 2, CODE_FONT)
        ws_last_timer = t

def ws_draw_cell(r, c):
    """Redraw a single cell."""
    n = ws_grid_n
    sz = ws_cell_size
    txt_size = 2 if n <= 10 else 1
    char_w = 12 if txt_size == 2 else 6
    char_h = 14 if txt_size == 2 else 7
    x = ws_grid_x + c * sz
    y = ws_grid_y + r * sz
    is_found = False
    for fr, fc in ws_found_cells:
        if fr == r and fc == c:
            is_found = True
            break
    is_sel = ws_is_selected(r, c)
    if is_found:
        bg = WS_FOUND_BG
    elif is_sel:
        bg = WS_SEL_COLOR
    else:
        bg = WS_CELL_BG
    display.fill_rect(x + 1, y + 1, sz - 2, sz - 2, bg)
    ch = ws_board[r * n + c]
    tx = x + (sz - char_w) // 2
    ty = y + (sz - char_h) // 2
    tc = BLACK if is_sel and not is_found else WHITE
    draw_text(display, ch, tx, ty, tc, txt_size, CODE_FONT)

def ws_check_selected():
    """Check if currently selected cells + found cells match any unfound word. Return index or -1."""
    if len(ws_selected) < 1:
        return -1
    for i in range(len(ws_words)):
        if ws_found[i]:
            continue
        wpos = ws_word_positions[i]
        # Check if every cell in word is either selected or already found
        all_match = True
        non_found = 0
        for wr, wc in wpos:
            is_found_cell = False
            for fr, fc in ws_found_cells:
                if fr == wr and fc == wc:
                    is_found_cell = True
                    break
            if is_found_cell:
                continue
            non_found += 1
            in_sel = False
            for sr, sc in ws_selected:
                if sr == wr and sc == wc:
                    in_sel = True
                    break
            if not in_sel:
                all_match = False
                break
        # Must have selected exactly the non-found cells
        if all_match and non_found == len(ws_selected):
            return i
    return -1

def ws_get_elapsed():
    return time.ticks_diff(time.ticks_ms(), ws_timer_start) // 1000

def ws_show_win():
    global ws_mode
    ws_mode = 2
    elapsed = ws_get_elapsed()
    mins = elapsed // 60
    secs = elapsed % 60
    # Update stats
    if ws_difficulty == 0:
        global ws_easy_wins, ws_easy_best
        ws_easy_wins += 1
        if ws_easy_best == 0 or elapsed < ws_easy_best:
            ws_easy_best = elapsed
    elif ws_difficulty == 1:
        global ws_med_wins, ws_med_best
        ws_med_wins += 1
        if ws_med_best == 0 or elapsed < ws_med_best:
            ws_med_best = elapsed
    else:
        global ws_hard_wins, ws_hard_best
        ws_hard_wins += 1
        if ws_hard_best == 0 or elapsed < ws_hard_best:
            ws_hard_best = elapsed
    # Free game data to make room for stats save + screen draw
    global ws_board, ws_found_cells, ws_selected, ws_word_positions, ws_words, ws_found
    ws_board = []
    ws_found_cells = []
    ws_selected = []
    ws_word_positions = []
    ws_words = []
    ws_found = []
    gc.collect()
    save_ws_stats()
    gc.collect()
    time.sleep_ms(50)
    display.fill(BLACK)
    time.sleep_ms(30)
    draw_text(display, "ALL", 128, 70, GREY, 4, CODE_FONT)
    time.sleep_ms(30)
    draw_text(display, "FOUND!", 80, 125, GREY, 4, CODE_FONT)
    time.sleep_ms(30)
    t_str = "{:02d}:{:02d}".format(mins, secs)
    draw_text(display, "TIME " + t_str, 80, 210, GREY, 3, CODE_FONT)
    time.sleep_ms(30)
    display.fill_rect(25, 295, 150, 70, GAMEOVER_BTN)
    draw_text(display, "PLAY", 60, 307, WHITE, 3, CODE_FONT)
    draw_text(display, "AGAIN", 48, 333, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 295, 150, 70, GAMEOVER_BTN)
    draw_text(display, "EXIT", 233, 320, WHITE, 3, CODE_FONT)

def draw_ws_difficulty():
    display.fill(BLACK)
    draw_text(display, "WORD", 116, 20, GREY, 5, CODE_FONT)
    draw_text(display, "SEARCH", 80, 70, GREY, 5, CODE_FONT)
    display.fill_rect(34, 180, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 198, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 260, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 278, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 340, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 358, WHITE, 3, CODE_FONT)

def launch_wordsearch():
    global ws_mode
    ws_mode = 0
    draw_ws_difficulty()

def handle_wordsearch_touch(tx, ty):
    global ws_mode, ws_difficulty, ws_selected

    if ws_mode == 0:
        # Difficulty select
        if 34 <= tx <= 334:
            if 180 <= ty <= 240:
                ws_difficulty = 0
                ws_start_game()
            elif 260 <= ty <= 320:
                ws_difficulty = 1
                ws_start_game()
            elif 340 <= ty <= 400:
                ws_difficulty = 2
                ws_start_game()
        return

    if ws_mode == 2:
        # Win screen buttons
        if 295 <= ty <= 365:
            if 25 <= tx <= 175:
                ws_start_game()
            elif 193 <= tx <= 343:
                global current_screen, current_app, last_time_text
                track_app_exit()
                current_screen = SCREEN_MENU
                current_app = -1
                last_time_text = ""
                draw_menu_screen()
        return

    if ws_mode == 1:
        n = ws_grid_n
        sz = ws_cell_size
        # Get tapped cell
        c = (tx - ws_grid_x) // sz
        r = (ty - ws_grid_y) // sz
        if not (0 <= r < n and 0 <= c < n):
            return
        # Don't allow selecting already-found cells
        for fr, fc in ws_found_cells:
            if fr == r and fc == c:
                return
        # Toggle selection
        already = False
        for idx in range(len(ws_selected)):
            if ws_selected[idx][0] == r and ws_selected[idx][1] == c:
                already = True
                ws_selected.pop(idx)
                ws_draw_cell(r, c)
                break
        if not already:
            ws_selected.append((r, c))
            ws_draw_cell(r, c)
        # Check if selected cells match any word
        match = ws_check_selected()
        if match >= 0:
            ws_found[match] = True
            for cr, cc in ws_word_positions[match]:
                found_already = False
                for fr, fc in ws_found_cells:
                    if fr == cr and fc == cc:
                        found_already = True
                        break
                if not found_already:
                    ws_found_cells.append((cr, cc))
            # Clear selection
            ws_selected = []
            # Redraw affected cells and word list
            for cr, cc in ws_word_positions[match]:
                ws_draw_cell(cr, cc)
            ws_draw_word_list()
            if all(ws_found):
                ws_show_win()

def draw_ws_stats():
    display.fill(BLACK)
    draw_text(display, "WORD SEARCH", 70, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32
    for label, wins, best in [("EASY", ws_easy_wins, ws_easy_best),
                               ("MEDIUM", ws_med_wins, ws_med_best),
                               ("HARD", ws_hard_wins, ws_hard_best)]:
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, label, 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        if best > 0:
            bm = best // 60
            bs = best % 60
            bt = "{:02d}:{:02d}".format(bm, bs)
        else:
            bt = "--:--"
        draw_text(display, f"BEST TIME: {bt}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
