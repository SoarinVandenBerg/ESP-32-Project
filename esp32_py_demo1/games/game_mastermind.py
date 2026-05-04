# ===== MASTERMIND GAME =====
# Extracted from main.py - all globals from main.py are available via exec()

# Colors - greens and greys only
MM_COLORS = [
    make_color(0, 200, 0),    # Bright green
    make_color(0, 120, 0),    # Dark green
    make_color(100, 180, 50), # Lime green
    make_color(0, 80, 40),    # Forest green
    make_color(140, 140, 140),# Light grey
    make_color(60, 60, 60),   # Dark grey
]
# Feedback colors (green theme)
MM_FB_CORRECT = make_color(0, 100, 0)  # Dark green = right color & right spot
MM_FB_WRONG_POS = make_color(0, 200, 0)  # Bright green = right color, wrong spot
MM_FB_WRONG = make_color(25, 25, 25)  # Very dark = wrong color entirely

# Game constants
MM_CODE_LEN = 4
MM_MAX_GUESSES = 5
MM_SLOT_SIZE = 40
MM_SLOT_GAP = 8
MM_COLOR_BTN_SIZE = 50

# Game state
mm_mode = 0  # 0=playing, 1=won, 2=lost
mm_secret = [0, 0, 0, 0]
mm_guesses = []  # List of guesses (each is list of 4 color indices)
mm_feedback = []  # List of feedback (each is list of 4: 0=wrong, 1=wrong pos, 2=correct)
mm_current_guess = [-1, -1, -1, -1]  # -1 = empty slot
mm_current_slot = 0  # Which slot is selected (0-3)

def mm_generate_secret():
    """Generate secret code - 6 colors, duplicates allowed"""
    global mm_secret
    mm_secret = [random.randint(0, 5) for _ in range(MM_CODE_LEN)]

def mm_reset_game():
    """Reset for new game"""
    global mm_guesses, mm_feedback, mm_current_guess, mm_current_slot, mm_mode
    mm_guesses = []
    mm_feedback = []
    mm_current_guess = [-1, -1, -1, -1]
    mm_current_slot = 0
    mm_generate_secret()
    mm_mode = 0  # Playing

def mm_check_guess(guess):
    """Check guess against secret, return list of 4 feedback values per slot.
    0 = wrong color, 1 = right color wrong position, 2 = correct (right color & position)"""
    feedback = [0, 0, 0, 0]  # Start with all wrong
    secret_copy = mm_secret[:]
    guess_copy = guess[:]

    # First pass: find exact matches (correct position)
    for i in range(MM_CODE_LEN):
        if guess_copy[i] == secret_copy[i]:
            feedback[i] = 2  # Correct!
            secret_copy[i] = -1
            guess_copy[i] = -2

    # Second pass: find color matches in wrong position
    for i in range(MM_CODE_LEN):
        if guess_copy[i] >= 0:  # Not already matched
            if guess_copy[i] in secret_copy:
                feedback[i] = 1  # Right color, wrong spot
                secret_copy[secret_copy.index(guess_copy[i])] = -1

    return feedback

def draw_mm_game():
    """Draw the main game screen"""
    display.fill(BLACK)

    # Title at top
    draw_text(display, "MASTERMIND", 80, 15, GREY, 3, CODE_FONT)

    # Guesses remaining
    remaining = MM_MAX_GUESSES - len(mm_guesses)
    draw_text(display, f"{remaining} LEFT", 145, 50, GREY, 2, CODE_FONT)

    # Layout for guess/result columns
    slot_size = 38
    slot_gap = 4
    col_width = MM_CODE_LEN * slot_size + (MM_CODE_LEN - 1) * slot_gap  # ~164
    guess_x = 10
    result_x = 195

    # Draw column headers - centered over columns
    draw_text(display, "GUESS", guess_x + 35, 75, GREY, 3, CODE_FONT)
    draw_text(display, "RESULT", result_x + 25, 75, GREY, 3, CODE_FONT)

    # Draw previous guesses and per-slot feedback
    guess_start_y = 105
    row_height = 38
    for g_idx, guess in enumerate(mm_guesses):
        y = guess_start_y + g_idx * row_height
        fb = mm_feedback[g_idx]
        # Draw guess colors
        for i in range(MM_CODE_LEN):
            x = guess_x + i * (slot_size + slot_gap)
            display.fill_rect(x, y, slot_size - 2, slot_size - 6, MM_COLORS[guess[i]])
        # Draw feedback colors (per-slot, same positions)
        for i in range(MM_CODE_LEN):
            x = result_x + i * (slot_size + slot_gap)
            if fb[i] == 2:  # Correct
                display.fill_rect(x, y, slot_size - 2, slot_size - 6, MM_FB_CORRECT)
            elif fb[i] == 1:  # Right color, wrong spot
                display.fill_rect(x, y, slot_size - 2, slot_size - 6, MM_FB_WRONG_POS)
            else:  # Wrong
                display.fill_rect(x, y, slot_size - 2, slot_size - 6, MM_FB_WRONG)

    # Draw current guess row
    current_y = guess_start_y + len(mm_guesses) * row_height
    for i in range(MM_CODE_LEN):
        x = guess_x + i * (slot_size + slot_gap)
        if mm_current_guess[i] >= 0:
            display.fill_rect(x, current_y, slot_size - 2, slot_size - 6, MM_COLORS[mm_current_guess[i]])
        else:
            display.fill_rect(x, current_y, slot_size - 2, slot_size - 6, DARK_GREY)
        # Highlight selected slot
        if i == mm_current_slot and mm_mode == 0:
            display.rect(x - 2, current_y - 2, slot_size + 2, slot_size - 2, GREEN)

    # Draw color picker at bottom (6 colors)
    picker_y = 400
    picker_start = (368 - 6 * MM_COLOR_BTN_SIZE) // 2
    for i in range(6):
        x = picker_start + i * MM_COLOR_BTN_SIZE
        display.fill_rect(x + 2, picker_y, MM_COLOR_BTN_SIZE - 4, 40, MM_COLORS[i])

def draw_mm_gameover():
    """Draw win/lose screen"""
    display.fill(BLACK)
    if mm_mode == 1:  # Won
        title = "YOU WIN!"
        title_w = len(title) * 6 * 5
        draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
        info_text = f"GUESSES: {len(mm_guesses)}"
        info_w = len(info_text) * 6 * 3
        draw_text(display, info_text, (368 - info_w) // 2, 160, GREY, 3, CODE_FONT)
    else:  # Lost (mm_mode == 2)
        title = "GAME OVER"
        title_w = len(title) * 6 * 5
        draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
        secret_text = "SECRET WAS:"
        secret_w = len(secret_text) * 6 * 2
        draw_text(display, secret_text, (368 - secret_w) // 2, 155, GREY, 2, CODE_FONT)
        start_x = (368 - (MM_CODE_LEN * 50)) // 2
        for i in range(MM_CODE_LEN):
            x = start_x + i * 50
            display.fill_rect(x, 185, 45, 45, MM_COLORS[mm_secret[i]])
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)

def draw_mm_stats():
    display.fill(BLACK)
    draw_text(display, "MASTERMIND", 90, 15, GREY, 3, CODE_FONT)
    y_start = 80
    row_height = 50
    # Wins
    display.fill_rect(20, y_start, 328, 3, DARK_GREY)
    draw_text(display, f"WINS: {mm_wins}", 30, y_start + 15, GREY, 3, CODE_FONT)
    y2 = y_start + row_height
    # Losses
    display.fill_rect(20, y2, 328, 3, DARK_GREY)
    draw_text(display, f"LOSSES: {mm_losses}", 30, y2 + 15, GREY, 3, CODE_FONT)
    y3 = y2 + row_height
    # Best (fewest guesses)
    display.fill_rect(20, y3, 328, 3, DARK_GREY)
    best_text = f"BEST: {mm_best} GUESSES" if mm_best > 0 else "BEST: -"
    draw_text(display, best_text, 30, y3 + 15, GREY, 3, CODE_FONT)
    y_final = y3 + row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)

def launch_mastermind():
    mm_reset_game()
    draw_mm_game()

def handle_mastermind_touch(tx, ty):
    global mm_mode, mm_current_guess, mm_current_slot, mm_guesses, mm_feedback, mm_wins, mm_losses, mm_best, current_screen, current_app, last_time_text
    if mm_mode == 0:  # Playing
        # Check if tapped on color picker (bottom)
        picker_y = 400
        picker_start = (368 - 6 * MM_COLOR_BTN_SIZE) // 2
        if ty >= picker_y:
            for i in range(6):
                btn_x = picker_start + i * MM_COLOR_BTN_SIZE
                if btn_x <= tx <= btn_x + MM_COLOR_BTN_SIZE:
                    # Set current slot to this color
                    mm_current_guess[mm_current_slot] = i
                    # Move to next slot
                    mm_current_slot = (mm_current_slot + 1) % MM_CODE_LEN
                    # Check if guess is complete
                    if -1 not in mm_current_guess:
                        # Submit guess
                        guess = mm_current_guess[:]
                        feedback = mm_check_guess(guess)
                        mm_guesses.append(guess)
                        mm_feedback.append(feedback)
                        if all(f == 2 for f in feedback):  # All correct!
                            mm_mode = 1  # Won
                            num_guesses = len(mm_guesses)
                            mm_wins += 1
                            if mm_best == 0 or num_guesses < mm_best:
                                mm_best = num_guesses
                            save_mm_stats()
                            draw_mm_gameover()
                        elif len(mm_guesses) >= MM_MAX_GUESSES:
                            mm_mode = 2  # Lost
                            mm_losses += 1
                            save_mm_stats()
                            draw_mm_gameover()
                        else:
                            mm_current_guess = [-1, -1, -1, -1]
                            mm_current_slot = 0
                            draw_mm_game()
                    else:
                        draw_mm_game()
                    break
        else:
            # Check if tapped on a slot to select it
            guess_x = 10
            slot_size = 38
            slot_gap = 4
            current_y = 105 + len(mm_guesses) * 38
            if current_y <= ty <= current_y + 35:
                for i in range(MM_CODE_LEN):
                    slot_x = guess_x + i * (slot_size + slot_gap)
                    if slot_x <= tx <= slot_x + slot_size:
                        mm_current_slot = i
                        draw_mm_game()
    elif mm_mode in [1, 2]:  # Game over - buttons
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                mm_reset_game()
                draw_mm_game()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("MASTERMIND")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
