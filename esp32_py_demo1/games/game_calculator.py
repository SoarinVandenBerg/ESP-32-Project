# ===== CALCULATOR APP =====
# Extracted from main.py - all globals from main.py are available via exec()

calc_display = "0"
calc_prev = 0
calc_op = None
calc_new_num = True
calc_secret_mode = False  # Secret dice roller!
calc_secret_type = 0  # 0=coin, 1=d6, 2=1-100
calc_secret_result = ""
calc_usage_mode = False  # Secret usage tracker!
calc_usage_page = 0

def calc_clear():
    global calc_display, calc_prev, calc_op, calc_new_num
    calc_display = "0"
    calc_prev = 0
    calc_op = None
    calc_new_num = True

def calc_input_digit(d):
    global calc_display, calc_new_num
    if calc_new_num:
        calc_display = d
        calc_new_num = False
    else:
        if len(calc_display) < 10:
            calc_display = calc_display + d if calc_display != "0" else d

def calc_input_op(op):
    global calc_prev, calc_op, calc_new_num, calc_display
    if calc_display == "ERROR":
        return
    calc_prev = float(calc_display)
    calc_op = op
    calc_new_num = True

def calc_equals():
    global calc_display, calc_prev, calc_op, calc_new_num
    if calc_op is None:
        return
    curr = float(calc_display)
    if calc_op == '+':
        result = calc_prev + curr
    elif calc_op == '-':
        result = calc_prev - curr
    elif calc_op == '*':
        result = calc_prev * curr
    elif calc_op == '/':
        if curr == 0:
            calc_display = "ERROR"
            calc_new_num = True
            calc_op = None
            return
        result = calc_prev / curr
    # Format result
    if result == int(result):
        calc_display = str(int(result))
    else:
        calc_display = f"{result:.6g}"
    if len(calc_display) > 10:
        calc_display = calc_display[:10]
    calc_new_num = True
    calc_op = None

CALC_BTN_GREY = make_color(35, 35, 35)  # Slightly darker than DARK_GREY

def draw_calculator():
    display.fill(BLACK)
    draw_text(display, "CALCULATOR", 90, 15, GREY, 3, CODE_FONT)

    # Simple 4x5 button grid
    btn_w = 82
    btn_h = 55
    gap = 6
    start_x = 14
    start_y = 125

    # Display area - green accent (same width as button panel)
    panel_width = btn_w * 4 + gap * 3
    display.fill_rect(start_x, 55, panel_width, 60, GREEN)
    # Show current display value
    disp_text = calc_display
    text_w = len(disp_text) * 6 * 4
    draw_text(display, disp_text, start_x + panel_width - text_w - 8, 70, WHITE, 4, CODE_FONT)

    buttons = [
        ['C', '/', '.', '-'],
        ['7', '8', '9', '+'],
        ['4', '5', '6', '*'],
        ['1', '2', '3', '='],
        ['0', '0', '0', '0'],  # Wide zero button
    ]

    for row in range(5):
        for col in range(4):
            x = start_x + col * (btn_w + gap)
            y = start_y + row * (btn_h + gap)
            btn = buttons[row][col]

            # Wide zero button spans all 4 columns
            if row == 4:
                if col == 0:
                    display.fill_rect(x, y, btn_w * 4 + gap * 3, btn_h, CALC_BTN_GREY)
                    draw_text(display, "0", x + btn_w * 2 - 10, y + 12, GREY, 4, CODE_FONT)
                continue

            # Regular button
            display.fill_rect(x, y, btn_w, btn_h, CALC_BTN_GREY)
            # Center the text
            char_w = 6 * 3  # scale 3
            tx = x + (btn_w - char_w) // 2
            draw_text(display, btn, tx, y + 12, GREY, 3, CODE_FONT)

# ===== SECRET DICE APP =====
def draw_secret_dice():
    """Draw the secret dice roller app"""
    display.fill(BLACK)
    draw_text(display, "???", 155, 15, GREEN, 3, CODE_FONT)

    # Result area
    display.fill_rect(34, 80, 300, 150, DARK_GREY)

    # Show result if we have one
    if calc_secret_result:
        # Center the result text
        text_w = len(calc_secret_result) * 6 * 6
        x = (368 - text_w) // 2
        draw_text(display, calc_secret_result, x, 130, GREEN, 6, CODE_FONT)

    # Roll button below result area
    display.fill_rect(34, 250, 300, 50, GREEN)
    draw_text(display, "ROLL!", 140, 262, WHITE, 3, CODE_FONT)

    # Draw buttons at bottom
    draw_secret_buttons()

def draw_secret_buttons():
    """Draw the mode selection buttons"""
    # Coin button
    if calc_secret_type == 0:
        display.fill_rect(20, 400, 100, 40, GREEN)
        draw_text(display, "COIN", 45, 410, WHITE, 2, CODE_FONT)
    else:
        display.fill_rect(20, 400, 100, 40, DARK_GREY)
        draw_text(display, "COIN", 45, 410, GREY, 2, CODE_FONT)

    # D6 button
    if calc_secret_type == 1:
        display.fill_rect(134, 400, 100, 40, GREEN)
        draw_text(display, "D6", 168, 410, WHITE, 2, CODE_FONT)
    else:
        display.fill_rect(134, 400, 100, 40, DARK_GREY)
        draw_text(display, "D6", 168, 410, GREY, 2, CODE_FONT)

    # 1-100 button
    if calc_secret_type == 2:
        display.fill_rect(248, 400, 100, 40, GREEN)
        draw_text(display, "1-100", 262, 410, WHITE, 2, CODE_FONT)
    else:
        display.fill_rect(248, 400, 100, 40, DARK_GREY)
        draw_text(display, "1-100", 262, 410, GREY, 2, CODE_FONT)

def secret_roll():
    """Roll based on current type"""
    global calc_secret_result
    if calc_secret_type == 0:  # Coin
        calc_secret_result = "HEADS" if random.randint(0, 1) == 0 else "TAILS"
    elif calc_secret_type == 1:  # D6
        calc_secret_result = str(random.randint(1, 6))
    else:  # 1-100
        calc_secret_result = str(random.randint(1, 100))

    # Redraw result area
    display.fill_rect(34, 80, 300, 150, DARK_GREY)
    text_w = len(calc_secret_result) * 6 * 6
    x = (368 - text_w) // 2
    draw_text(display, calc_secret_result, x, 130, GREEN, 6, CODE_FONT)

def draw_usage_screen():
    """Draw the secret usage tracker screen"""
    display.fill(BLACK)
    draw_text(display, "USAGE", 145, 10, GREEN, 3, CODE_FONT)

    y = 55
    row_h = 35
    per_page = 9

    # Sort apps by usage (most used first)
    sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)
    start = calc_usage_page * per_page
    page_apps = sorted_apps[start:start + per_page]

    for app_name, secs in page_apps:
        # Convert seconds to hours with 1 decimal
        hours = secs / 3600
        if hours >= 0.1:
            time_str = f"{hours:.1f}H"
        else:
            # Show minutes if less than 0.1 hours
            mins = secs / 60
            time_str = f"{mins:.0f}M"

        display.fill_rect(20, y, 328, 2, DARK_GREY)
        draw_text(display, app_name[:20], 25, y + 8, GREY, 2, CODE_FONT)
        draw_text(display, time_str, 280, y + 8, GREEN, 2, CODE_FONT)
        y += row_h

    if not sorted_apps:
        draw_text(display, "NO DATA YET", 100, 200, GREY, 2, CODE_FONT)

    # Navigation arrows
    cx = 184
    if calc_usage_page > 0:
        # Up arrow
        for i in range(12):
            display.fill_rect(cx - i, 410 + i, i * 2 + 1, 2, GREY)
    if start + per_page < len(sorted_apps):
        # Down arrow
        for i in range(12):
            display.fill_rect(cx - i, 430 + 12 - i, i * 2 + 1, 2, GREY)

def launch_calculator():
    global calc_secret_mode, calc_usage_mode
    calc_clear()
    calc_secret_mode = False
    calc_usage_mode = False
    draw_calculator()

def handle_calculator_touch(tx, ty):
    global calc_secret_mode, calc_secret_type, calc_secret_result, calc_usage_mode, calc_usage_page, calc_display, calc_new_num, calc_prev, calc_op
    # Check if in secret modes
    if calc_usage_mode:
        if ty > 400:
            # Arrow area - toggle page
            sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)
            max_pages = (len(sorted_apps) + 8) // 9
            if ty < 425 and calc_usage_page > 0:
                calc_usage_page -= 1
                draw_usage_screen()
            elif ty >= 425 and calc_usage_page < max_pages - 1:
                calc_usage_page += 1
                draw_usage_screen()
            else:
                calc_usage_page = 0
                calc_usage_mode = False
                calc_clear()
                draw_calculator()
        else:
            # Tap elsewhere to exit
            calc_usage_page = 0
            calc_usage_mode = False
            calc_clear()
            draw_calculator()
    elif calc_secret_mode:
        if ty >= 400:  # Button area
            if tx < 130:  # Coin
                calc_secret_type = 0
            elif tx < 240:  # D6
                calc_secret_type = 1
            else:  # 1-100
                calc_secret_type = 2
            calc_secret_result = ""
            draw_secret_dice()
        elif 250 <= ty <= 300:  # Roll button
            secret_roll()
    else:
        # Calculator touch handling - simple 4x5 grid
        btn_w = 82
        btn_h = 55
        gap = 6
        start_x = 14
        start_y = 125
        buttons = [
            ['C', '/', '.', '-'],
            ['7', '8', '9', '+'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '='],
        ]

        # Check row 4 (wide zero button) first
        zero_y = start_y + 4 * (btn_h + gap)
        if zero_y <= ty <= zero_y + btn_h:
            calc_input_digit('0')
            draw_calculator()
        else:
            # Check rows 0-3
            for row in range(4):
                for col in range(4):
                    bx = start_x + col * (btn_w + gap)
                    by = start_y + row * (btn_h + gap)
                    if bx <= tx <= bx + btn_w and by <= ty <= by + btn_h:
                        btn = buttons[row][col]
                        if btn == 'C':
                            calc_clear()
                        elif btn in '0123456789':
                            calc_input_digit(btn)
                        elif btn == '.':
                            if '.' not in calc_display:
                                calc_input_digit('.')
                        elif btn in '+-*/':
                            calc_input_op(btn)
                        elif btn == '=':
                            # Check for secret codes BEFORE equals
                            if calc_display == "4242":
                                calc_secret_mode = True
                                calc_secret_result = ""
                                draw_secret_dice()
                                break
                            elif calc_display == "3.14159":
                                calc_usage_mode = True
                                draw_usage_screen()
                                break
                            elif calc_display == "2143":
                                toggle_safe_mode()
                                break
                            elif calc_display == "54321":
                                toggle_docs_mode()
                                break
                            calc_equals()
                        draw_calculator()
                        break
                else:
                    continue
                break

def toggle_safe_mode():
    global safe_mode
    safe_mode = not safe_mode
    save_safe_mode()
    display.fill(BLACK)
    if safe_mode:
        t = "SAFE MODE"
        draw_text(display, t, (368 - len(t) * 18) // 2, 180, GREEN, 3, CODE_FONT)
        t2 = "ACTIVATED"
        draw_text(display, t2, (368 - len(t2) * 18) // 2, 220, GREEN, 3, CODE_FONT)
    else:
        t = "SAFE MODE"
        draw_text(display, t, (368 - len(t) * 18) // 2, 180, GREY, 3, CODE_FONT)
        t2 = "OFF"
        draw_text(display, t2, (368 - len(t2) * 18) // 2, 220, GREY, 3, CODE_FONT)
    time.sleep_ms(500)
    calc_clear()
    draw_calculator()

def toggle_docs_mode():
    global docs_mode
    docs_mode = not docs_mode
    save_docs_mode()
    display.fill(BLACK)
    if docs_mode:
        t = "DRIVE MODE"
        draw_text(display, t, (368 - len(t) * 18) // 2, 180, GREEN, 3, CODE_FONT)
        t2 = "ENABLED"
        draw_text(display, t2, (368 - len(t2) * 18) // 2, 220, GREEN, 3, CODE_FONT)
    else:
        t = "DRIVE MODE"
        draw_text(display, t, (368 - len(t) * 18) // 2, 180, GREY, 3, CODE_FONT)
        t2 = "DISABLED"
        draw_text(display, t2, (368 - len(t2) * 18) // 2, 220, GREY, 3, CODE_FONT)
    time.sleep_ms(500)
    calc_clear()
    draw_calculator()
