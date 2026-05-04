# ==================== WORDLE ====================
try:
    f = open("wordle_words.txt", "r")
    WRD_WORDS = f.read().strip()
    f.close()
except:
    WRD_WORDS = "ABOUTABOVEABUSEACTORACUTE"
WRD_GREEN = make_color(0, 130, 0)
WRD_YELLOW = make_color(200, 170, 0)
WRD_GREY = make_color(50, 50, 50)
WRD_EMPTY = make_color(30, 30, 30)
WRD_KEY_BG = make_color(70, 70, 70)
wrd_mode = 0
wrd_target = ""
wrd_guesses = []
wrd_feedback = []
wrd_current = ""
wrd_key_states = {}
wrd_games = 0
wrd_wins = 0
wrd_streak = 0
wrd_max_streak = 0
wrd_last_win = ""
wrd_last_played = ""  # Track last played date (not just win)

# PvP mode variables
wrd_pvp_mode = False  # True if in PvP mode
wrd_pvp_best_of = 1  # 1, 3, or 5
wrd_pvp_p1_score = 0  # Rounds won by P1
wrd_pvp_p2_score = 0  # Rounds won by P2
wrd_pvp_round = 0  # Current round number
wrd_pvp_current_player = 1  # Who is choosing word (1 or 2)
wrd_pvp_p1_guesses = 0  # Guesses used by P1 this round
wrd_pvp_p2_guesses = 0  # Guesses used by P2 this round
wrd_pvp_p1_wins = 0  # Total PvP matches won by P1
wrd_pvp_p2_wins = 0  # Total PvP matches won by P2
wrd_pvp_draws = 0  # Total PvP matches drawn

def save_wrd_stats():
    save_all_stats()

def wrd_get_daily_word():
    """Get daily word using date-seeded random selection (no repeats)"""
    year, month, day = read_date_rtc()
    count = len(WRD_WORDS) // 5
    # Use date as random seed for consistent daily word
    seed = year * 10000 + month * 100 + day
    random.seed(seed)
    # Generate list of all word indices
    indices = list(range(count))
    # Shuffle based on seed
    for i in range(count - 1, 0, -1):
        j = random.randint(0, i)
        indices[i], indices[j] = indices[j], indices[i]
    # Pick first word from shuffled list
    idx = indices[0]
    # Reseed with non-deterministic value so other games aren't affected
    random.seed(time.ticks_ms())
    return WRD_WORDS[idx * 5:(idx + 1) * 5]

def wrd_is_today(last_str, y, m, d):
    if not last_str:
        return False
    try:
        parts = last_str.split("-")
        return int(parts[0]) == y and int(parts[1]) == m and int(parts[2]) == d
    except:
        return False

def wrd_is_yesterday(last_str, y, m, d):
    if not last_str:
        return False
    try:
        parts = last_str.split("-")
        ly, lm, ld = int(parts[0]), int(parts[1]), int(parts[2])
    except:
        return False
    d -= 1
    if d == 0:
        m -= 1
        if m == 0:
            y -= 1
            m = 12
        if m in (1, 3, 5, 7, 8, 10, 12):
            d = 31
        elif m in (4, 6, 9, 11):
            d = 30
        elif m == 2:
            if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0):
                d = 29
            else:
                d = 28
    return ly == y and lm == m and ld == d

def wrd_compute_feedback(guess, target):
    feedback = [0, 0, 0, 0, 0]
    counts = {}
    for c in target:
        counts[c] = counts.get(c, 0) + 1
    for i in range(5):
        if guess[i] == target[i]:
            feedback[i] = 2
            counts[guess[i]] -= 1
    for i in range(5):
        if feedback[i] == 0 and guess[i] in counts and counts[guess[i]] > 0:
            feedback[i] = 1
            counts[guess[i]] -= 1
    return feedback

def wrd_is_valid_word(word):
    """Check if word exists in word list"""
    if len(word) != 5:
        return False
    # Check if word exists in WRD_WORDS (each word is 5 chars)
    for i in range(0, len(WRD_WORDS), 5):
        if WRD_WORDS[i:i+5] == word:
            return True
    return False

def wrd_can_play_today():
    """Check if user can play today (haven't played yet)"""
    year, month, day = read_date_rtc()
    return not wrd_is_today(wrd_last_played, year, month, day)

def wrd_start_game():
    global wrd_mode, wrd_target, wrd_guesses, wrd_feedback, wrd_current, wrd_key_states
    if not wrd_can_play_today():
        # Already played today - show message
        wrd_mode = 4  # New mode: already played
        return
    wrd_target = wrd_get_daily_word()
    wrd_guesses = []
    wrd_feedback = []
    wrd_current = ""
    wrd_key_states = {}
    wrd_mode = 1

def draw_wrd_mode_select():
    """Mode 5: Choose DAILY or PVP"""
    display.fill(BLACK)
    tw = len("WORDLE") * 6 * 5
    draw_text(display, "WORDLE", (368 - tw) // 2, 50, GREY, 5, CODE_FONT)
    # DAILY button
    display.fill_rect(34, 150, 300, 70, GAMEOVER_BTN)
    daily_text = "DAILY WORD"
    daily_w = len(daily_text) * 6 * 2
    draw_text(display, daily_text, 34 + (300 - daily_w) // 2, 172, WHITE, 2, CODE_FONT)
    # PVP button
    display.fill_rect(34, 250, 300, 70, GAMEOVER_BTN)
    pvp_text = "PLAYER VS PLAYER"
    pvp_w = len(pvp_text) * 6 * 2
    draw_text(display, pvp_text, 34 + (300 - pvp_w) // 2, 272, WHITE, 2, CODE_FONT)

def draw_wrd_best_of():
    """Mode 6: Choose best of 1, 3, or 5"""
    display.fill(BLACK)
    draw_text(display, "PVP MODE", 104, 30, GREY, 4, CODE_FONT)
    draw_text(display, "SELECT", 116, 80, GREY, 4, CODE_FONT)
    # Best of 1
    display.fill_rect(34, 160, 300, 60, GAMEOVER_BTN)
    draw_text(display, "BEST OF 1", 104, 178, WHITE, 3, CODE_FONT)
    # Best of 3
    display.fill_rect(34, 240, 300, 60, GAMEOVER_BTN)
    draw_text(display, "BEST OF 3", 104, 258, WHITE, 3, CODE_FONT)
    # Best of 5
    display.fill_rect(34, 320, 300, 60, GAMEOVER_BTN)
    draw_text(display, "BEST OF 5", 104, 338, WHITE, 3, CODE_FONT)

def draw_wrd_cell(row, col):
    x_start = 81
    y_start = 5
    cell = 38
    gap = 4
    x = x_start + col * (cell + gap)
    y = y_start + row * (cell + gap)
    if row < len(wrd_guesses):
        fb = wrd_feedback[row]
        if fb[col] == 2:
            bg = WRD_GREEN
        elif fb[col] == 1:
            bg = WRD_YELLOW
        else:
            bg = WRD_GREY
        display.fill_rect(x, y, cell, cell, bg)
        ch = wrd_guesses[row][col]
        cw = 6 * 3
        draw_text(display, ch, x + (cell - cw) // 2, y + (cell - 18) // 2, WHITE, 3, CODE_FONT)
    elif row == len(wrd_guesses):
        display.fill_rect(x, y, cell, cell, BLACK)
        display.fill_rect(x, y, cell, 2, WRD_EMPTY)
        display.fill_rect(x, y + cell - 2, cell, 2, WRD_EMPTY)
        display.fill_rect(x, y, 2, cell, WRD_EMPTY)
        display.fill_rect(x + cell - 2, y, 2, cell, WRD_EMPTY)
        if col < len(wrd_current):
            ch = wrd_current[col]
            cw = 6 * 3
            draw_text(display, ch, x + (cell - cw) // 2, y + (cell - 18) // 2, WHITE, 3, CODE_FONT)
    else:
        display.fill_rect(x, y, cell, cell, BLACK)
        display.fill_rect(x, y, cell, 2, WRD_EMPTY)
        display.fill_rect(x, y + cell - 2, cell, 2, WRD_EMPTY)
        display.fill_rect(x, y, 2, cell, WRD_EMPTY)
        display.fill_rect(x + cell - 2, y, 2, cell, WRD_EMPTY)

def draw_wrd_word_entry():
    """Mode 7: Player enters word for opponent"""
    display.fill(BLACK)
    player_text = f"PLAYER {wrd_pvp_current_player}"
    ptw = len(player_text) * 6 * 4
    draw_text(display, player_text, (368 - ptw) // 2, 20, GREY, 4, CODE_FONT)
    inst_text = "ENTER WORD FOR"
    itw = len(inst_text) * 6 * 2
    draw_text(display, inst_text, (368 - itw) // 2, 70, GREY, 2, CODE_FONT)
    opp_text = f"PLAYER {3 - wrd_pvp_current_player}"
    otw = len(opp_text) * 6 * 2
    draw_text(display, opp_text, (368 - otw) // 2, 95, WRD_GREEN, 2, CODE_FONT)
    # Draw word entry (large)
    word_y = 140
    if len(wrd_current) > 0:
        for i, ch in enumerate(wrd_current):
            x = 81 + i * 42
            display.fill_rect(x, word_y, 38, 38, WRD_GREEN)
            draw_text(display, ch, x + 13, word_y + 10, WHITE, 3, CODE_FONT)
    # Draw empty squares for remaining letters
    for i in range(len(wrd_current), 5):
        x = 81 + i * 42
        display.fill_rect(x, word_y, 38, 2, WRD_EMPTY)
        display.fill_rect(x, word_y + 36, 38, 2, WRD_EMPTY)
        display.fill_rect(x, word_y, 2, 38, WRD_EMPTY)
        display.fill_rect(x + 36, word_y, 2, 38, WRD_EMPTY)
    # Draw keyboard
    draw_wrd_keyboard()

def draw_wrd_keyboard():
    rows_keys = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
    key_w = 31
    key_h = 38
    gap = 3
    y_pos = [268, 309, 350]
    x_starts = [15, 32]
    for r in range(3):
        y = y_pos[r]
        if r == 2:
            display.fill_rect(15, y, 48, key_h, WRD_KEY_BG)
            draw_text(display, "ENT", 15 + 6, y + (key_h - 12) // 2, WHITE, 2, CODE_FONT)
            x = 15 + 48 + gap
            for ch in rows_keys[2]:
                state = wrd_key_states.get(ch, -1)
                if state == 2:
                    bg = WRD_GREEN
                elif state == 1:
                    bg = WRD_YELLOW
                elif state == 0:
                    bg = WRD_GREY
                else:
                    bg = WRD_KEY_BG
                display.fill_rect(x, y, key_w, key_h, bg)
                cw = 6 * 2
                draw_text(display, ch, x + (key_w - cw) // 2, y + (key_h - 12) // 2, WHITE, 2, CODE_FONT)
                x += key_w + gap
            display.fill_rect(x, y, 48, key_h, WRD_KEY_BG)
            draw_text(display, "DEL", x + 6, y + (key_h - 12) // 2, WHITE, 2, CODE_FONT)
        else:
            x = x_starts[r]
            for ch in rows_keys[r]:
                state = wrd_key_states.get(ch, -1)
                if state == 2:
                    bg = WRD_GREEN
                elif state == 1:
                    bg = WRD_YELLOW
                elif state == 0:
                    bg = WRD_GREY
                else:
                    bg = WRD_KEY_BG
                display.fill_rect(x, y, key_w, key_h, bg)
                cw = 6 * 2
                draw_text(display, ch, x + (key_w - cw) // 2, y + (key_h - 12) // 2, WHITE, 2, CODE_FONT)
                x += key_w + gap

def draw_wrd_game():
    display.fill(BLACK)
    for row in range(6):
        for col in range(5):
            draw_wrd_cell(row, col)
    draw_wrd_keyboard()

def wrd_submit_guess():
    global wrd_current, wrd_mode, wrd_games, wrd_wins, wrd_streak, wrd_max_streak, wrd_last_win, wrd_last_played
    global wrd_pvp_current_player, wrd_pvp_p1_guesses, wrd_pvp_p2_guesses, wrd_pvp_p1_score, wrd_pvp_p2_score, wrd_pvp_round
    global wrd_target, wrd_guesses, wrd_feedback, wrd_key_states
    guess = wrd_current
    fb = wrd_compute_feedback(guess, wrd_target)
    wrd_guesses.append(guess)
    wrd_feedback.append(fb)
    wrd_current = ""
    for i, ch in enumerate(guess):
        old_state = wrd_key_states.get(ch, -1)
        new_state = fb[i]
        if new_state > old_state:
            wrd_key_states[ch] = new_state
    row = len(wrd_guesses) - 1
    for col in range(5):
        draw_wrd_cell(row, col)
    draw_wrd_keyboard()

    if wrd_pvp_mode:
        # PvP mode - track guesses and handle round completion
        if fb == [2, 2, 2, 2, 2] or len(wrd_guesses) >= 6:
            # Player finished - record guesses
            # current_player = who CHOSE the word, so the guesser is the OTHER player
            if wrd_pvp_current_player == 1:  # P1 chose word, P2 guessed
                wrd_pvp_p2_guesses = len(wrd_guesses) if fb == [2, 2, 2, 2, 2] else 7
            else:  # P2 chose word, P1 guessed
                wrd_pvp_p1_guesses = len(wrd_guesses) if fb == [2, 2, 2, 2, 2] else 7

            # Check if both players have played this round
            if wrd_pvp_p1_guesses > 0 and wrd_pvp_p2_guesses > 0:
                # Round over - determine winner
                if wrd_pvp_p1_guesses < wrd_pvp_p2_guesses:
                    wrd_pvp_p1_score += 1
                elif wrd_pvp_p2_guesses < wrd_pvp_p1_guesses:
                    wrd_pvp_p2_score += 1
                # Draw - no score change
                wrd_pvp_round += 1
                time.sleep_ms(500)
                wrd_mode = 8
                draw_wrd_round_complete()
            else:
                # Switch to other player
                wrd_pvp_current_player = 3 - wrd_pvp_current_player
                wrd_guesses = []
                wrd_feedback = []
                wrd_key_states = {}
                time.sleep_ms(500)
                wrd_mode = 7
                wrd_current = ""
                draw_wrd_word_entry()
    else:
        # Daily mode - original logic
        year, month, day = read_date_rtc()
        today = f"{year}-{month:02d}-{day:02d}"
        if fb == [2, 2, 2, 2, 2]:
            wrd_mode = 2
            wrd_games += 1
            wrd_wins += 1
            wrd_last_played = today  # Mark as played today
            if not wrd_is_today(wrd_last_win, year, month, day):
                if wrd_is_yesterday(wrd_last_win, year, month, day):
                    wrd_streak += 1
                else:
                    wrd_streak = 1
                wrd_last_win = today
                if wrd_streak > wrd_max_streak:
                    wrd_max_streak = wrd_streak
            save_wrd_stats()
            time.sleep_ms(500)
            draw_wrd_gameover()
        elif len(wrd_guesses) >= 6:
            wrd_mode = 3
            wrd_games += 1
            wrd_last_played = today  # Mark as played today
            wrd_streak = 0  # Streak broken
            save_wrd_stats()
            time.sleep_ms(500)
            draw_wrd_gameover()

def draw_wrd_gameover():
    display.fill(BLACK)
    if wrd_mode == 2:
        title = "YOU WIN!"
    else:
        title = "GAME OVER"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    tw2 = len(wrd_target) * 6 * 3
    draw_text(display, wrd_target, (368 - tw2) // 2, 140, WRD_GREEN, 3, CODE_FONT)
    if wrd_mode == 2:
        info = f"{len(wrd_guesses)}/6  STREAK: {wrd_streak}"
    else:
        info = f"STREAK: {wrd_streak}"
    iw = len(info) * 6 * 2
    draw_text(display, info, (368 - iw) // 2, 180, GREY, 2, CODE_FONT)
    # Show when next word available
    next_msg = "NEXT WORD AT MIDNIGHT"
    nmw = len(next_msg) * 6 * 2
    draw_text(display, next_msg, (368 - nmw) // 2, 220, GREY, 2, CODE_FONT)
    # Only MENU button (no RETRY)
    display.fill_rect(109, 270, 150, 70, GAMEOVER_BTN)
    mtw = len("MENU") * 6 * 3
    draw_text(display, "MENU", 109 + (150 - mtw) // 2, 290, WHITE, 3, CODE_FONT)

def draw_wrd_round_complete():
    """Mode 8: Show round results (and match results if match is over)"""
    display.fill(BLACK)
    wins_needed = (wrd_pvp_best_of // 2) + 1
    match_over = wrd_pvp_p1_score >= wins_needed or wrd_pvp_p2_score >= wins_needed
    if match_over:
        # Standard game over layout
        if wrd_pvp_p1_score > wrd_pvp_p2_score:
            title = "P1 WINS!"
        elif wrd_pvp_p2_score > wrd_pvp_p1_score:
            title = "P2 WINS!"
        else:
            title = "DRAW!"
        ttw = len(title) * 6 * 5
        draw_text(display, title, (368 - ttw) // 2, 80, GREY, 5, CODE_FONT)
        # Guess summary
        p1_text = f"P1: {wrd_pvp_p1_guesses} GUESSES" if wrd_pvp_p1_guesses < 7 else "P1: FAILED"
        p2_text = f"P2: {wrd_pvp_p2_guesses} GUESSES" if wrd_pvp_p2_guesses < 7 else "P2: FAILED"
        p1w = len(p1_text) * 6 * 2
        draw_text(display, p1_text, (368 - p1w) // 2, 150, GREY, 2, CODE_FONT)
        p2w = len(p2_text) * 6 * 2
        draw_text(display, p2_text, (368 - p2w) // 2, 178, GREY, 2, CODE_FONT)
        # Final score
        score_text = f"SCORE: {wrd_pvp_p1_score} - {wrd_pvp_p2_score}"
        stw = len(score_text) * 6 * 3
        draw_text(display, score_text, (368 - stw) // 2, 215, WRD_GREEN, 3, CODE_FONT)
        # Standard buttons at Y=280
        display.fill_rect(25, 280, 150, 70, GAMEOVER_BTN)
        etw = len("EXIT") * 6 * 2
        draw_text(display, "EXIT", 25 + (150 - etw) // 2, 303, WHITE, 2, CODE_FONT)
        display.fill_rect(193, 280, 150, 70, GAMEOVER_BTN)
        rtw = len("REMATCH") * 6 * 2
        draw_text(display, "REMATCH", 193 + (150 - rtw) // 2, 303, WHITE, 2, CODE_FONT)
    else:
        # Round continues - compact layout
        draw_text(display, "ROUND OVER", 80, 40, GREY, 4, CODE_FONT)
        p1_text = f"P1: {wrd_pvp_p1_guesses} GUESSES" if wrd_pvp_p1_guesses < 7 else "P1: FAILED"
        p2_text = f"P2: {wrd_pvp_p2_guesses} GUESSES" if wrd_pvp_p2_guesses < 7 else "P2: FAILED"
        draw_text(display, p1_text, 50, 100, GREY, 2, CODE_FONT)
        draw_text(display, p2_text, 50, 130, GREY, 2, CODE_FONT)
        if wrd_pvp_p1_guesses < wrd_pvp_p2_guesses:
            winner_text = "P1 WINS ROUND!"
        elif wrd_pvp_p2_guesses < wrd_pvp_p1_guesses:
            winner_text = "P2 WINS ROUND!"
        else:
            winner_text = "ROUND DRAW!"
        wtw = len(winner_text) * 6 * 3
        draw_text(display, winner_text, (368 - wtw) // 2, 170, WRD_GREEN, 3, CODE_FONT)
        score_text = f"SCORE: {wrd_pvp_p1_score} - {wrd_pvp_p2_score}"
        stw = len(score_text) * 6 * 3
        draw_text(display, score_text, (368 - stw) // 2, 220, GREY, 3, CODE_FONT)
        display.fill_rect(109, 290, 150, 60, GAMEOVER_BTN)
        ctw = len("CONTINUE") * 6 * 2
        draw_text(display, "CONTINUE", 109 + (150 - ctw) // 2, 310, WHITE, 2, CODE_FONT)

def draw_wrd_match_complete():
    """Mode 9: Show match winner"""
    display.fill(BLACK)
    # Determine match winner
    if wrd_pvp_p1_score > wrd_pvp_p2_score:
        title = "PLAYER 1"
        subtitle = "WINS!"
    elif wrd_pvp_p2_score > wrd_pvp_p1_score:
        title = "PLAYER 2"
        subtitle = "WINS!"
    else:
        title = "MATCH"
        subtitle = "DRAW!"
    ttw = len(title) * 6 * 5
    draw_text(display, title, (368 - ttw) // 2, 80, GREY, 5, CODE_FONT)
    stw = len(subtitle) * 6 * 5
    draw_text(display, subtitle, (368 - stw) // 2, 140, WRD_GREEN, 5, CODE_FONT)
    # Final score
    score_text = f"FINAL: {wrd_pvp_p1_score} - {wrd_pvp_p2_score}"
    sctw = len(score_text) * 6 * 2
    draw_text(display, score_text, (368 - sctw) // 2, 210, GREY, 2, CODE_FONT)
    # Buttons
    display.fill_rect(25, 270, 150, 60, GAMEOVER_BTN)
    mtw = len("MENU") * 6 * 3
    draw_text(display, "MENU", 25 + (150 - mtw) // 2, 288, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 270, 150, 60, GAMEOVER_BTN)
    rtw = len("REMATCH") * 6 * 2
    draw_text(display, "REMATCH", 193 + (150 - rtw) // 2, 290, WHITE, 2, CODE_FONT)

def draw_wrd_already_played():
    """Show screen when user already played today"""
    display.fill(BLACK)
    title = "COME BACK"
    tw = len(title) * 6 * 5
    draw_text(display, title, (368 - tw) // 2, 80, GREY, 5, CODE_FONT)
    title2 = "TOMORROW!"
    tw2 = len(title2) * 6 * 5
    draw_text(display, title2, (368 - tw2) // 2, 140, GREY, 5, CODE_FONT)
    msg = "YOU ALREADY PLAYED TODAY"
    mw = len(msg) * 6 * 2
    draw_text(display, msg, (368 - mw) // 2, 200, GREY, 2, CODE_FONT)
    msg2 = "NEXT WORD AT MIDNIGHT"
    m2w = len(msg2) * 6 * 2
    draw_text(display, msg2, (368 - m2w) // 2, 230, GREY, 2, CODE_FONT)
    # Only MENU button
    display.fill_rect(109, 290, 150, 70, GAMEOVER_BTN)
    mtw = len("MENU") * 6 * 3
    draw_text(display, "MENU", 109 + (150 - mtw) // 2, 310, WHITE, 3, CODE_FONT)

def draw_wrd_stats():
    display.fill(BLACK)
    draw_text(display, "WORDLE STATS", 72, 15, GREY, 3, CODE_FONT)
    y = 60
    rh = 40
    # Daily stats
    draw_text(display, "DAILY:", 30, y, WRD_GREEN, 2, CODE_FONT)
    y += 30
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"GAMES: {wrd_games}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"WINS: {wrd_wins}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"STREAK: {wrd_streak}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"BEST: {wrd_max_streak}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh + 10
    # PvP stats
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, "PVP:", 30, y + 10, WRD_GREEN, 2, CODE_FONT)
    y += 30
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"P1 WINS: {wrd_pvp_p1_wins}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"P2 WINS: {wrd_pvp_p2_wins}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)
    draw_text(display, f"DRAWS: {wrd_pvp_draws}", 30, y + 10, GREY, 2, CODE_FONT)
    y += rh
    display.fill_rect(20, y, 328, 2, DARK_GREY)

def launch_wordle():
    global wrd_mode, wrd_pvp_mode
    wrd_mode = 5  # Mode select
    wrd_pvp_mode = False
    draw_wrd_mode_select()

def handle_wordle_touch(tx, ty):
    global wrd_mode, wrd_current, wrd_pvp_mode, wrd_pvp_best_of, wrd_pvp_current_player
    global wrd_pvp_p1_score, wrd_pvp_p2_score, wrd_pvp_round, wrd_pvp_p1_guesses, wrd_pvp_p2_guesses
    global wrd_target, wrd_guesses, wrd_feedback, wrd_key_states
    global current_screen, current_app, last_time_text

    if wrd_mode == 5:  # Mode select: DAILY vs PVP
        if 150 <= ty <= 220 and 34 <= tx <= 334:  # DAILY
            wrd_pvp_mode = False
            wrd_start_game()
            if wrd_mode == 4:  # Already played
                draw_wrd_already_played()
            else:
                draw_wrd_game()
        elif 250 <= ty <= 320 and 34 <= tx <= 334:  # PVP
            wrd_pvp_mode = True
            wrd_mode = 6
            draw_wrd_best_of()

    elif wrd_mode == 6:  # Best-of select
        if 34 <= tx <= 334:
            if 160 <= ty <= 220:  # Best of 1
                wrd_pvp_best_of = 1
                wrd_pvp_p1_score = 0
                wrd_pvp_p2_score = 0
                wrd_pvp_round = 0
                wrd_pvp_current_player = 1
                wrd_mode = 7
                wrd_current = ""
                draw_wrd_word_entry()
            elif 240 <= ty <= 300:  # Best of 3
                wrd_pvp_best_of = 3
                wrd_pvp_p1_score = 0
                wrd_pvp_p2_score = 0
                wrd_pvp_round = 0
                wrd_pvp_current_player = 1
                wrd_mode = 7
                wrd_current = ""
                draw_wrd_word_entry()
            elif 320 <= ty <= 380:  # Best of 5
                wrd_pvp_best_of = 5
                wrd_pvp_p1_score = 0
                wrd_pvp_p2_score = 0
                wrd_pvp_round = 0
                wrd_pvp_current_player = 1
                wrd_mode = 7
                wrd_current = ""
                draw_wrd_word_entry()

    elif wrd_mode == 7:  # Word entry - reuse keyboard handling
        key_h = 38
        if 268 <= ty < 268 + key_h:
            x = 15
            for ch in "QWERTYUIOP":
                if x <= tx < x + 31:
                    if len(wrd_current) < 5:
                        wrd_current += ch
                        draw_wrd_word_entry()
                    break
                x += 34
        elif 309 <= ty < 309 + key_h:
            x = 32
            for ch in "ASDFGHJKL":
                if x <= tx < x + 31:
                    if len(wrd_current) < 5:
                        wrd_current += ch
                        draw_wrd_word_entry()
                    break
                x += 34
        elif 350 <= ty < 350 + key_h:
            if 15 <= tx < 63:  # ENTER
                if len(wrd_current) == 5:
                    # Word entered - start opponent's turn
                    wrd_target = wrd_current
                    wrd_guesses = []
                    wrd_feedback = []
                    wrd_current = ""
                    wrd_key_states = {}
                    wrd_mode = 1
                    draw_wrd_game()
            else:
                x = 66
                for ch in "ZXCVBNM":
                    if x <= tx < x + 31:
                        if len(wrd_current) < 5:
                            wrd_current += ch
                            draw_wrd_word_entry()
                        break
                    x += 34
                if tx >= 304 and tx < 352:  # DELETE
                    if len(wrd_current) > 0:
                        wrd_current = wrd_current[:-1]
                        draw_wrd_word_entry()

    elif wrd_mode == 1:  # Playing
        key_h = 38
        if 268 <= ty < 268 + key_h:
            # Row 0: QWERTYUIOP
            x = 15
            for ch in "QWERTYUIOP":
                if x <= tx < x + 31:
                    if len(wrd_current) < 5:
                        wrd_current += ch
                        draw_wrd_cell(len(wrd_guesses), len(wrd_current) - 1)
                    break
                x += 34
        elif 309 <= ty < 309 + key_h:
            # Row 1: ASDFGHJKL
            x = 32
            for ch in "ASDFGHJKL":
                if x <= tx < x + 31:
                    if len(wrd_current) < 5:
                        wrd_current += ch
                        draw_wrd_cell(len(wrd_guesses), len(wrd_current) - 1)
                    break
                x += 34
        elif 350 <= ty < 350 + key_h:
            # Row 2: ENT + ZXCVBNM + DEL
            if 15 <= tx < 63:
                if len(wrd_current) == 5:
                    wrd_submit_guess()
            else:
                x = 66
                for ch in "ZXCVBNM":
                    if x <= tx < x + 31:
                        if len(wrd_current) < 5:
                            wrd_current += ch
                            draw_wrd_cell(len(wrd_guesses), len(wrd_current) - 1)
                        break
                    x += 34
                if tx >= 304 and tx < 352:
                    if len(wrd_current) > 0:
                        wrd_current = wrd_current[:-1]
                        draw_wrd_cell(len(wrd_guesses), len(wrd_current))
    elif wrd_mode == 2 or wrd_mode == 3:  # Game over
        if 270 <= ty <= 340:
            if 109 <= tx <= 259:  # MENU (centered button)
                track_app_exit("WORDLE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
    elif wrd_mode == 4:  # Already played today
        if 290 <= ty <= 360:
            if 109 <= tx <= 259:  # MENU (centered button)
                track_app_exit("WORDLE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
    elif wrd_mode == 8:  # Round complete
        wins_needed = (wrd_pvp_best_of // 2) + 1
        match_over = wrd_pvp_p1_score >= wins_needed or wrd_pvp_p2_score >= wins_needed
        if match_over:
            if 280 <= ty <= 350:
                if 25 <= tx <= 175:  # EXIT
                    if wrd_pvp_p1_score > wrd_pvp_p2_score:
                        wrd_pvp_p1_wins += 1
                    elif wrd_pvp_p2_score > wrd_pvp_p1_score:
                        wrd_pvp_p2_wins += 1
                    else:
                        wrd_pvp_draws += 1
                    save_wrd_stats()
                    track_app_exit("WORDLE")
                    current_screen = SCREEN_MENU
                    current_app = -1
                    draw_menu_screen()
                    last_time_text = ""
                elif 193 <= tx <= 343:  # REMATCH
                    if wrd_pvp_p1_score > wrd_pvp_p2_score:
                        wrd_pvp_p1_wins += 1
                    elif wrd_pvp_p2_score > wrd_pvp_p1_score:
                        wrd_pvp_p2_wins += 1
                    else:
                        wrd_pvp_draws += 1
                    save_wrd_stats()
                    wrd_pvp_p1_score = 0
                    wrd_pvp_p2_score = 0
                    wrd_pvp_round = 0
                    wrd_pvp_p1_guesses = 0
                    wrd_pvp_p2_guesses = 0
                    wrd_pvp_current_player = 1
                    wrd_mode = 7
                    wrd_current = ""
                    draw_wrd_word_entry()
        else:
            if 290 <= ty <= 350:
                if 109 <= tx <= 259:  # CONTINUE
                    wrd_pvp_p1_guesses = 0
                    wrd_pvp_p2_guesses = 0
                    wrd_pvp_current_player = 3 - wrd_pvp_current_player
                    wrd_current = ""
                    wrd_mode = 7
                    draw_wrd_word_entry()
    elif wrd_mode == 9:  # Match complete
        if 270 <= ty <= 330:
            if 25 <= tx <= 175:  # MENU
                track_app_exit("WORDLE")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
            elif 193 <= tx <= 343:  # REMATCH
                # Restart with same best-of setting
                wrd_pvp_p1_score = 0
                wrd_pvp_p2_score = 0
                wrd_pvp_round = 0
                wrd_pvp_current_player = 1
                wrd_mode = 7
                wrd_current = ""
                draw_wrd_word_entry()
