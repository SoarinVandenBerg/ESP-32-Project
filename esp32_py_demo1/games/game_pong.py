# ===== PONG GAME =====
# Game constants
PONG_BALL_SIZE = 10
PONG_PADDLE_W = 10
PONG_PADDLE_H = 60
PONG_PADDLE_X_PLAYER = 25   # Left side
PONG_PADDLE_X_AI = 333      # Right side
PONG_WIN_SCORE = 5

# Game state variables
pong_mode = 0  # 0=mode_select, 1=playing, 2=game_over, 3=difficulty_select
pong_vs_ai = True  # True = vs AI, False = PvP
pong_difficulty = 1  # 0=easy, 1=medium, 2=hard
pong_ball_x = 184
pong_ball_y = 224
pong_ball_dx = 4
pong_ball_dy = 3
pong_player_y = 194  # Player paddle Y (top of paddle)
pong_ai_y = 194      # AI paddle Y
pong_player_score = 0
pong_ai_score = 0
pong_winner = 0  # 0=player, 1=ai
pong_player_h = PONG_PADDLE_H  # Player paddle height (shrinks in impossible)
pong_serving = False  # True when ball is on player's paddle waiting to launch
pong_server = 0  # 0=player serves, 1=AI/P2 serves

def pong_get_speed():
    if pong_vs_ai:
        if pong_difficulty == 0:
            return 4
        elif pong_difficulty == 1:
            return 6
        elif pong_difficulty == 2:
            return 7
        else:
            return 9
    return 6

def pong_reset_ball(direction=1):
    """Reset ball. direction: 1=towards P2/AI, -1=towards P1"""
    global pong_ball_x, pong_ball_y, pong_ball_dx, pong_ball_dy, pong_serving
    if direction == 1 and pong_server == 0:
        # Player serves: ball sits on player paddle
        pong_ball_x = PONG_PADDLE_X_PLAYER + PONG_PADDLE_W + 2
        pong_ball_y = pong_player_y + pong_player_h // 2 - PONG_BALL_SIZE // 2
        pong_ball_dx = 0
        pong_ball_dy = 0
        pong_serving = True
    elif direction == -1 and pong_server == 1 and not pong_vs_ai:
        # P2 serves in PvP: ball sits on P2 paddle
        pong_ball_x = PONG_PADDLE_X_AI - PONG_BALL_SIZE - 2
        pong_ball_y = pong_ai_y + PONG_PADDLE_H // 2 - PONG_BALL_SIZE // 2
        pong_ball_dx = 0
        pong_ball_dy = 0
        pong_serving = True
    else:
        # AI serves or other: launch toward player
        pong_ball_x = 184
        pong_ball_y = 224
        speed = pong_get_speed()
        pong_ball_dx = speed * direction
        pong_ball_dy = random.choice([-4, -3, 3, 4])
        pong_serving = False

def pong_launch_serve():
    """Launch ball from player's paddle"""
    global pong_ball_dx, pong_ball_dy, pong_serving
    speed = pong_get_speed()
    if pong_ball_x < 184:
        pong_ball_dx = speed
    else:
        pong_ball_dx = -speed
    pong_ball_dy = random.choice([-4, -3, 3, 4])
    pong_serving = False

def pong_reset_game():
    """Reset for new game"""
    global pong_player_score, pong_ai_score, pong_player_y, pong_ai_y, pong_mode, pong_player_h, pong_server
    pong_player_score = 0
    pong_ai_score = 0
    pong_player_y = 194
    pong_ai_y = 194
    pong_player_h = PONG_PADDLE_H
    pong_server = 0  # Player serves first
    pong_reset_ball(1)
    pong_mode = 1  # Playing

def draw_pong_menu():
    """Draw mode selection menu"""
    display.fill(BLACK)
    title = "PONG"
    title_w = len(title) * 6 * 4
    draw_text(display, title, (368 - title_w) // 2, 30, GREY, 4, CODE_FONT)
    display.fill_rect(34, 150, 300, 70, GREEN)
    btn_text = "PLAYER VS PLAYER"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 34 + (300 - btn_w) // 2, 172, WHITE, 2, CODE_FONT)
    display.fill_rect(34, 250, 300, 70, GREEN)
    btn_text = "PLAYER VS AI"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 34 + (300 - btn_w) // 2, 272, WHITE, 2, CODE_FONT)

def draw_pong_difficulty():
    """Draw difficulty selection screen"""
    display.fill(BLACK)
    draw_text(display, "SELECT", 116, 20, GREY, 4, CODE_FONT)
    draw_text(display, "DIFFICULTY", 68, 65, GREY, 4, CODE_FONT)
    display.fill_rect(34, 160, 300, 60, GREEN)
    draw_text(display, "EASY", 148, 178, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 240, 300, 60, GREEN)
    draw_text(display, "MEDIUM", 124, 258, WHITE, 3, CODE_FONT)
    display.fill_rect(34, 320, 300, 60, GREEN)
    draw_text(display, "HARD", 148, 338, WHITE, 3, CODE_FONT)

def draw_pong_game():
    """Draw the full pong game screen"""
    display.fill(BLACK)

    # Draw scores
    if pong_vs_ai:
        draw_text(display, f"P:{pong_player_score}", 30, 15, GREY, 3, CODE_FONT)
        draw_text(display, f"AI:{pong_ai_score}", 268, 15, GREY, 3, CODE_FONT)
    else:
        draw_text(display, f"P1:{pong_player_score}", 30, 15, GREY, 3, CODE_FONT)
        draw_text(display, f"P2:{pong_ai_score}", 268, 15, GREY, 3, CODE_FONT)

    # Draw center line (dashed)
    for y in range(60, 440, 20):
        display.fill_rect(182, y, 4, 10, GREY)

    # Draw paddles
    display.fill_rect(PONG_PADDLE_X_PLAYER, pong_player_y, PONG_PADDLE_W, pong_player_h, GREEN)
    display.fill_rect(PONG_PADDLE_X_AI, pong_ai_y, PONG_PADDLE_W, PONG_PADDLE_H, GREEN)

    # Draw ball
    display.fill_rect(pong_ball_x, pong_ball_y, PONG_BALL_SIZE, PONG_BALL_SIZE, GREEN)

def draw_pong_ball(old_x, old_y, new_x, new_y):
    """Update just the ball position"""
    display.fill_rect(old_x, old_y, PONG_BALL_SIZE, PONG_BALL_SIZE, BLACK)

    # Redraw center line if ball was over it (center line is at x=182, width 4)
    if old_x < 186 and old_x + PONG_BALL_SIZE > 182:
        # Ball was overlapping center line, redraw affected segments
        for line_y in range(60, 440, 20):
            # Check if this line segment overlaps with old ball position
            if old_y < line_y + 10 and old_y + PONG_BALL_SIZE > line_y:
                display.fill_rect(182, line_y, 4, 10, GREY)

    display.fill_rect(new_x, new_y, PONG_BALL_SIZE, PONG_BALL_SIZE, GREEN)

def draw_pong_paddle_player(old_y, new_y):
    """Update player paddle position"""
    if old_y < new_y:
        # Moving down - clear top part
        display.fill_rect(PONG_PADDLE_X_PLAYER, old_y, PONG_PADDLE_W, new_y - old_y, BLACK)
    elif old_y > new_y:
        # Moving up - clear bottom part
        display.fill_rect(PONG_PADDLE_X_PLAYER, new_y + pong_player_h, PONG_PADDLE_W, old_y - new_y, BLACK)
    display.fill_rect(PONG_PADDLE_X_PLAYER, new_y, PONG_PADDLE_W, pong_player_h, GREEN)

def draw_pong_paddle_ai(old_y, new_y):
    """Update AI paddle position"""
    if old_y < new_y:
        display.fill_rect(PONG_PADDLE_X_AI, old_y, PONG_PADDLE_W, new_y - old_y, BLACK)
    elif old_y > new_y:
        display.fill_rect(PONG_PADDLE_X_AI, new_y + PONG_PADDLE_H, PONG_PADDLE_W, old_y - new_y, BLACK)
    display.fill_rect(PONG_PADDLE_X_AI, new_y, PONG_PADDLE_W, PONG_PADDLE_H, GREEN)

def draw_pong_score():
    """Update score display"""
    display.fill_rect(30, 15, 100, 25, BLACK)
    display.fill_rect(268, 15, 90, 25, BLACK)
    if pong_vs_ai:
        draw_text(display, f"P:{pong_player_score}", 30, 15, GREY, 3, CODE_FONT)
        draw_text(display, f"AI:{pong_ai_score}", 268, 15, GREY, 3, CODE_FONT)
    else:
        draw_text(display, f"P1:{pong_player_score}", 30, 15, GREY, 3, CODE_FONT)
        draw_text(display, f"P2:{pong_ai_score}", 268, 15, GREY, 3, CODE_FONT)

def draw_pong_gameover():
    """Draw game over screen"""
    display.fill(BLACK)
    if pong_vs_ai:
        if pong_winner == 0:
            title = "YOU WIN!"
        else:
            title = "AI WINS!"
    else:
        title = f"P{pong_winner + 1} WINS!"
    title_w = len(title) * 6 * 5
    draw_text(display, title, (368 - title_w) // 2, 80, GREY, 5, CODE_FONT)
    score_text = f"FINAL: {pong_player_score} - {pong_ai_score}"
    score_w = len(score_text) * 6 * 3
    draw_text(display, score_text, (368 - score_w) // 2, 160, GREY, 3, CODE_FONT)
    display.fill_rect(25, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "PLAY AGAIN"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 25 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    display.fill_rect(193, 245, 150, 70, GAMEOVER_BTN)
    btn_text = "EXIT"
    btn_w = len(btn_text) * 6 * 2
    draw_text(display, btn_text, 193 + (150 - btn_w) // 2, 273, WHITE, 2, CODE_FONT)
    # Show IMPOSSIBLE button if player beat Hard 5-0
    if pong_vs_ai and pong_difficulty == 2 and pong_winner == 0 and pong_ai_score == 0:
        display.fill_rect(34, 340, 300, 50, make_color(180, 0, 0))
        btn_text = "IMPOSSIBLE MODE"
        btn_w = len(btn_text) * 6 * 2
        draw_text(display, btn_text, 34 + (300 - btn_w) // 2, 357, WHITE, 2, CODE_FONT)

def pong_update_ai():
    """Update AI paddle position based on difficulty

    Uses reaction delays and error factors based on real Pong AI research:
    - AI only reacts some percentage of frames (reaction delay)
    - AI has error in predicting where ball will land
    - AI drifts to center when ball going away
    Even hard mode needs SOME error to be beatable!
    """
    global pong_ai_y

    ai_center = pong_ai_y + PONG_PADDLE_H // 2
    ball_center = pong_ball_y + PONG_BALL_SIZE // 2

    if pong_difficulty == 0:  # Easy
        speed = 5
        # React ~60% of frames, only when ball past 1/3 of screen
        if pong_ball_dx > 0 and pong_ball_x > 120:
            if random.randint(0, 4) < 3:  # React 3/5 of the time
                # Add error to target (+/- up to 30 pixels)
                error = random.randint(-30, 30)
                target = ball_center + error
                if target < ai_center - 12:
                    pong_ai_y = max(60, pong_ai_y - speed)
                elif target > ai_center + 12:
                    pong_ai_y = min(388, pong_ai_y + speed)
        else:
            # Ball going away - drift towards center
            if ai_center < 214:
                pong_ai_y += 2
            elif ai_center > 234:
                pong_ai_y -= 2

    elif pong_difficulty == 1:  # Medium
        speed = 5
        # React ~70% of frames when ball coming
        if pong_ball_dx > 0:
            if random.randint(0, 9) < 7:  # React 7/10 of the time
                # Add error (+/- 20 pixels)
                error = random.randint(-20, 20)
                target = ball_center + error
                if target < ai_center - 8:
                    pong_ai_y = max(60, pong_ai_y - speed)
                elif target > ai_center + 8:
                    pong_ai_y = min(388, pong_ai_y + speed)
        else:
            # Drift to center
            if ai_center < 215:
                pong_ai_y += 2
            elif ai_center > 233:
                pong_ai_y -= 2

    elif pong_difficulty == 2:  # Hard
        speed = 5
        # React ~70% of frames, use prediction but with significant error
        if pong_ball_dx > 0:
            if random.randint(0, 9) < 7:  # React 7/10 of the time
                # Predict where ball will land
                steps_to_ai = (PONG_PADDLE_X_AI - pong_ball_x) / pong_ball_dx
                predicted_y = pong_ball_y + pong_ball_dy * steps_to_ai

                # Simulate bounces
                while predicted_y < 60 or predicted_y > 428:
                    if predicted_y < 60:
                        predicted_y = 120 - predicted_y
                    elif predicted_y > 428:
                        predicted_y = 856 - predicted_y

                # Larger error (+/- 35 pixels) - actually beatable now!
                error = random.randint(-35, 35)
                target = predicted_y + error

                if target < ai_center - 8:
                    pong_ai_y = max(60, pong_ai_y - speed)
                elif target > ai_center + 8:
                    pong_ai_y = min(388, pong_ai_y + speed)
        else:
            # Drift to center
            if ai_center < 220:
                pong_ai_y += 2
            elif ai_center > 228:
                pong_ai_y -= 2

    else:  # Impossible - slightly harder than hard, paddle shrinks
        speed = 5
        if pong_ball_dx > 0:
            if random.randint(0, 9) < 8:  # React 8/10 of the time
                steps_to_ai = (PONG_PADDLE_X_AI - pong_ball_x) / pong_ball_dx
                predicted_y = pong_ball_y + pong_ball_dy * steps_to_ai
                while predicted_y < 60 or predicted_y > 428:
                    if predicted_y < 60:
                        predicted_y = 120 - predicted_y
                    elif predicted_y > 428:
                        predicted_y = 856 - predicted_y
                error = random.randint(-25, 25)
                target = predicted_y + error
                if target < ai_center - 6:
                    pong_ai_y = max(60, pong_ai_y - speed)
                elif target > ai_center + 6:
                    pong_ai_y = min(388, pong_ai_y + speed)
        else:
            if ai_center < 220:
                pong_ai_y += 2
            elif ai_center > 228:
                pong_ai_y -= 2

def pong_update_ball():
    """Update ball position and handle collisions. Returns: 0=continue, 1=player scored, 2=AI scored"""
    global pong_ball_x, pong_ball_y, pong_ball_dx, pong_ball_dy

    # Move ball
    new_x = pong_ball_x + pong_ball_dx
    new_y = pong_ball_y + pong_ball_dy

    # Top/bottom wall bounce
    if new_y <= 60:
        new_y = 60
        pong_ball_dy = -pong_ball_dy
    elif new_y >= 438 - PONG_BALL_SIZE:
        new_y = 438 - PONG_BALL_SIZE
        pong_ball_dy = -pong_ball_dy

    # Player paddle collision (left side)
    if new_x <= PONG_PADDLE_X_PLAYER + PONG_PADDLE_W:
        if pong_player_y <= new_y + PONG_BALL_SIZE and new_y <= pong_player_y + pong_player_h:
            # Hit paddle - bounce
            new_x = PONG_PADDLE_X_PLAYER + PONG_PADDLE_W
            pong_ball_dx = abs(pong_ball_dx)  # Go right

            # Add angle based on where ball hit paddle
            hit_pos = (new_y + PONG_BALL_SIZE // 2) - (pong_player_y + pong_player_h // 2)
            pong_ball_dy = hit_pos // 6  # More angle variation
            if pong_ball_dy == 0:
                pong_ball_dy = random.choice([-2, -1, 1, 2])

            # Speed up slightly
            if pong_vs_ai:
                max_speed = (10, 12, 14, 16)[min(pong_difficulty, 3)]
            else:
                max_speed = 12
            if abs(pong_ball_dx) < max_speed:
                pong_ball_dx += 1 if pong_ball_dx > 0 else -1
        elif new_x < 0:
            # P2/AI scores
            pong_ball_x = new_x
            pong_ball_y = new_y
            return 2

    # AI paddle collision (right side)
    if new_x + PONG_BALL_SIZE >= PONG_PADDLE_X_AI:
        if pong_ai_y <= new_y + PONG_BALL_SIZE and new_y <= pong_ai_y + PONG_PADDLE_H:
            # Hit paddle - bounce
            new_x = PONG_PADDLE_X_AI - PONG_BALL_SIZE
            pong_ball_dx = -abs(pong_ball_dx)  # Go left

            # Add angle based on where ball hit paddle
            hit_pos = (new_y + PONG_BALL_SIZE // 2) - (pong_ai_y + PONG_PADDLE_H // 2)
            pong_ball_dy = hit_pos // 6  # More angle variation
            if pong_ball_dy == 0:
                pong_ball_dy = random.choice([-2, -1, 1, 2])

            # Speed up slightly
            if pong_vs_ai:
                max_speed = (10, 12, 14, 16)[min(pong_difficulty, 3)]
            else:
                max_speed = 12
            if abs(pong_ball_dx) < max_speed:
                pong_ball_dx += 1 if pong_ball_dx > 0 else -1
        elif new_x > 368:
            # Player scores
            pong_ball_x = new_x
            pong_ball_y = new_y
            return 1

    pong_ball_x = new_x
    pong_ball_y = new_y
    return 0

def launch_pong():
    global pong_mode
    pong_mode = 0
    draw_pong_menu()

def handle_pong_touch(tx, ty):
    global pong_mode, pong_vs_ai, pong_difficulty, current_screen, current_app, last_time_text
    if pong_mode == 0:  # Mode select
        if 150 <= ty <= 220:  # Player vs Player
            pong_vs_ai = False
            pong_reset_game()
            draw_pong_game()
        elif 250 <= ty <= 320:  # Player vs AI
            pong_vs_ai = True
            pong_mode = 3
            draw_pong_difficulty()
    elif pong_mode == 3:  # Difficulty select
        if 160 <= ty <= 220:  # Easy
            pong_difficulty = 0
            pong_reset_game()
            draw_pong_game()
        elif 240 <= ty <= 300:  # Medium
            pong_difficulty = 1
            pong_reset_game()
            draw_pong_game()
        elif 320 <= ty <= 380:  # Hard
            pong_difficulty = 2
            pong_reset_game()
            draw_pong_game()
    elif pong_mode == 2:  # Game over
        if 245 <= ty <= 315:
            if 25 <= tx <= 175:  # Play Again
                pong_mode = 0
                draw_pong_menu()
            elif 193 <= tx <= 343:  # Exit
                track_app_exit("PONG")
                current_screen = SCREEN_MENU
                current_app = -1
                draw_menu_screen()
                last_time_text = ""
        elif 340 <= ty <= 390 and 34 <= tx <= 334:
            # IMPOSSIBLE button (only visible after Hard 5-0 win)
            if pong_vs_ai and pong_difficulty == 2 and pong_winner == 0 and pong_ai_score == 0:
                pong_difficulty = 3
                pong_reset_game()
                draw_pong_game()

def loop_pong():
    global pong_ball_x, pong_ball_y, pong_ball_dx, pong_ball_dy
    global pong_ai_y, pong_player_y, pong_player_score, pong_ai_score
    global pong_mode, pong_winner, pong_serving, pong_server, pong_player_h
    global pong_easy_wins, pong_med_wins, pong_hard_wins, pong_imp_wins
    global pong_easy_losses, pong_med_losses, pong_hard_losses, pong_imp_losses
    global pong_p1_wins, pong_p2_wins
    global hold_start_time, current_screen, current_app, last_time_text

    # Store old positions
    old_ball_x, old_ball_y = pong_ball_x, pong_ball_y
    old_ai_y = pong_ai_y
    old_player_y = pong_player_y

    # Handle touch for paddle movement (continuous)
    touch = read_touch()
    pong_tapped = False
    if touch is not None:
        tx, ty = touch
        if pong_vs_ai:
            if ty < 250:
                pong_player_y = max(60, pong_player_y - 6)
            else:
                pong_player_y = min(448 - pong_player_h, pong_player_y + 6)
        else:
            if tx < 184:
                if ty < 250:
                    pong_player_y = max(60, pong_player_y - 6)
                else:
                    pong_player_y = min(448 - pong_player_h, pong_player_y + 6)
            else:
                if ty < 250:
                    pong_ai_y = max(60, pong_ai_y - 6)
                else:
                    pong_ai_y = min(448 - PONG_PADDLE_H, pong_ai_y + 6)
        if hold_start_time is None:
            hold_start_time = time.ticks_ms()
            pong_tapped = True
        elif time.ticks_diff(time.ticks_ms(), hold_start_time) > 10000:
            track_app_exit("PONG")
            current_screen = SCREEN_MENU
            current_app = -1
            hold_start_time = None
            draw_menu_screen()
            last_time_text = ""
    else:
        hold_start_time = None

    # Serve: ball follows paddle until tapped
    if pong_serving:
        if pong_ball_x < 184:
            pong_ball_y = pong_player_y + pong_player_h // 2 - PONG_BALL_SIZE // 2
        else:
            pong_ball_y = pong_ai_y + PONG_PADDLE_H // 2 - PONG_BALL_SIZE // 2
        if pong_tapped:
            pong_launch_serve()

    # Continue Pong updates only if still playing
    if pong_mode == 1:
        if not pong_serving:
            # Update AI (only in vs AI mode)
            if pong_vs_ai:
                pong_update_ai()
            # Update ball
            result = pong_update_ball()
        else:
            result = 0

        # Draw updates
        if old_ball_x != pong_ball_x or old_ball_y != pong_ball_y:
            draw_pong_ball(old_ball_x, old_ball_y, pong_ball_x, pong_ball_y)
        if old_ai_y != pong_ai_y:
            draw_pong_paddle_ai(old_ai_y, pong_ai_y)
        if old_player_y != pong_player_y:
            draw_pong_paddle_player(old_player_y, pong_player_y)

        # Handle scoring
        if result == 1:  # P1 scored
            pong_player_score += 1
            # Shrink player paddle in impossible mode when player scores
            if pong_vs_ai and pong_difficulty == 3:
                pong_player_h = max(15, pong_player_h - 8)
            draw_pong_score()
            if pong_player_score >= PONG_WIN_SCORE:
                pong_mode = 2
                pong_winner = 0
                if pong_vs_ai:
                    if pong_difficulty == 0:
                        pong_easy_wins += 1
                    elif pong_difficulty == 1:
                        pong_med_wins += 1
                    elif pong_difficulty == 2:
                        pong_hard_wins += 1
                    else:
                        pong_imp_wins += 1
                else:
                    pong_p1_wins += 1
                save_pong_stats()
                draw_pong_gameover()
            else:
                time.sleep_ms(500)
                pong_server = 1  # AI/P2 serves next
                pong_reset_ball(-1)  # Ball towards P1
                draw_pong_game()
        elif result == 2:  # P2/AI scored
            pong_ai_score += 1
            draw_pong_score()
            if pong_ai_score >= PONG_WIN_SCORE:
                pong_mode = 2
                pong_winner = 1
                if pong_vs_ai:
                    if pong_difficulty == 0:
                        pong_easy_losses += 1
                    elif pong_difficulty == 1:
                        pong_med_losses += 1
                    elif pong_difficulty == 2:
                        pong_hard_losses += 1
                    else:
                        pong_imp_losses += 1
                else:
                    pong_p2_wins += 1
                save_pong_stats()
                draw_pong_gameover()
            else:
                time.sleep_ms(500)
                pong_server = 0  # Player serves next
                pong_reset_ball(1)  # Ball towards P2/AI
                draw_pong_game()

        time.sleep_ms(20)  # Game speed control

def draw_pong_stats():
    display.fill(BLACK)
    draw_text(display, "PONG STATS", 100, 15, GREY, 3, CODE_FONT)
    y = 55
    rh = 32  # Row height

    if pong_stats_page == 0:
        # EASY section
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (EASY)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {pong_easy_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {pong_easy_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh

        # MEDIUM section
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (MED)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {pong_med_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {pong_med_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh

        # HARD section
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (HARD)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {pong_hard_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {pong_hard_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)

        # Down arrow
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + 12 - i, i * 2 + 1, 2, GREY)
    else:
        # IMPOSSIBLE section
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS AI (IMP)", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"WINS: {pong_imp_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"LOSSES: {pong_imp_losses}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh

        # PVP section
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, "PLAYER VS PLAYER", 30, y + 8, GREEN, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"P1 WINS: {pong_p1_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        draw_text(display, f"P2 WINS: {pong_p2_wins}", 30, y + 8, GREY, 2, CODE_FONT)
        y += rh
        display.fill_rect(20, y, 328, 3, DARK_GREY)

        # Up arrow
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 410 + i, i * 2 + 1, 2, GREY)
