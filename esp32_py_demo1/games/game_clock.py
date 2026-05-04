# ===== CLOCK APP =====
# Extracted from main.py - all globals from main.py are available via exec()

clock_mode = 0  # 0=clock, 1=stopwatch, 2=timer
stopwatch_running = False
stopwatch_start = 0
stopwatch_elapsed = 0  # in milliseconds
timer_running = False
timer_target = 0  # target time in ms
timer_remaining = 60000  # default 1 minute
last_clock_display = ""  # For dirty-rect updates

def draw_clock_app_full():
    """Full redraw of clock app"""
    display.fill(BLACK)

    # Mode tabs - smaller to fit screen
    modes = ["TIME", "STOP", "TIMER"]
    tab_w = 100
    tab_h = 35
    for i, mode in enumerate(modes):
        x = 24 + i * (tab_w + 10)
        y = 15
        if i == clock_mode:
            display.fill_rect(x, y, tab_w, tab_h, GREEN)
            draw_text(display, mode, x + 15, y + 8, WHITE, 2, CODE_FONT)
        else:
            display.fill_rect(x, y, tab_w, tab_h, DARK_GREY)
            draw_text(display, mode, x + 15, y + 8, GREY, 2, CODE_FONT)

    if clock_mode == 0:
        # Clock mode - big green time in center
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        draw_text(display, time_text, 28, 150, GREEN, 6, SEVEN_SEG_FONT)
        # Show date
        year, month, day = read_date_rtc()
        date_text = f"{year}-{month:02d}-{day:02d}"
        text_w = len(date_text) * 6 * 3
        draw_text(display, date_text, (368 - text_w) // 2, 260, GREY, 3, CODE_FONT)

    elif clock_mode == 1:
        # Stopwatch mode - green time at top
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        text_w = len(time_text) * 6 * 3
        draw_text(display, time_text, (368 - text_w) // 2, 65, GREEN, 3, CODE_FONT)

        # Stopwatch display
        if stopwatch_running:
            elapsed = stopwatch_elapsed + time.ticks_diff(time.ticks_ms(), stopwatch_start)
        else:
            elapsed = stopwatch_elapsed
        secs = elapsed // 1000
        mins = secs // 60
        secs = secs % 60
        ms = (elapsed % 1000) // 10
        sw_text = f"{mins:02d}:{secs:02d}.{ms:02d}"
        text_w = len(sw_text) * 6 * 5
        draw_text(display, sw_text, (368 - text_w) // 2, 160, GREY, 5, CODE_FONT)

        # Buttons
        if stopwatch_running:
            display.fill_rect(50, 300, 130, 60, DARK_GREY)
            draw_text(display, "STOP", 80, 318, GREY, 3, CODE_FONT)
        else:
            display.fill_rect(50, 300, 130, 60, GREEN)
            draw_text(display, "START", 70, 318, WHITE, 3, CODE_FONT)
        display.fill_rect(195, 300, 130, 60, DARK_GREY)
        draw_text(display, "RESET", 220, 318, GREY, 3, CODE_FONT)

    elif clock_mode == 2:
        # Timer mode - green time at top
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        text_w = len(time_text) * 6 * 3
        draw_text(display, time_text, (368 - text_w) // 2, 65, GREEN, 3, CODE_FONT)

        # Timer display
        if timer_running:
            remaining = timer_target - time.ticks_ms()
            if remaining < 0:
                remaining = 0
        else:
            remaining = timer_remaining
        secs_total = remaining // 1000
        mins = secs_total // 60
        secs = secs_total % 60
        timer_text = f"{mins:02d}:{secs:02d}"
        text_w = len(timer_text) * 6 * 6
        draw_text(display, timer_text, (368 - text_w) // 2, 150, GREY, 6, CODE_FONT)

        # Up/down arrows for setting time (only when not running)
        if not timer_running:
            cx = 184
            # Up arrow
            for i in range(15):
                display.fill_rect(cx - i, 120 + i, i * 2 + 1, 2, GREY)
            # Down arrow
            for i in range(15):
                display.fill_rect(cx - i, 250 - i, i * 2 + 1, 2, GREY)

        # Buttons
        if timer_running:
            display.fill_rect(50, 310, 130, 60, DARK_GREY)
            draw_text(display, "STOP", 80, 328, GREY, 3, CODE_FONT)
        else:
            display.fill_rect(50, 310, 130, 60, GREEN)
            draw_text(display, "START", 70, 328, WHITE, 3, CODE_FONT)
        display.fill_rect(195, 310, 130, 60, DARK_GREY)
        draw_text(display, "RESET", 220, 328, GREY, 3, CODE_FONT)

def update_clock_display():
    """Update only the changing parts to reduce flicker"""
    global last_clock_display, timer_remaining, timer_running

    if clock_mode == 0:
        # Clock mode - update time only
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        if time_text != last_clock_display:
            # Clear old time area and redraw
            display.fill_rect(25, 145, 320, 60, BLACK)
            draw_text(display, time_text, 28, 150, GREEN, 6, SEVEN_SEG_FONT)
            last_clock_display = time_text

    elif clock_mode == 1:
        # Stopwatch - update time at top and stopwatch
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        # Update top time
        display.fill_rect(100, 60, 170, 30, BLACK)
        text_w = len(time_text) * 6 * 3
        draw_text(display, time_text, (368 - text_w) // 2, 65, GREEN, 3, CODE_FONT)

        # Update stopwatch
        if stopwatch_running:
            elapsed = stopwatch_elapsed + time.ticks_diff(time.ticks_ms(), stopwatch_start)
        else:
            elapsed = stopwatch_elapsed
        secs = elapsed // 1000
        mins = secs // 60
        secs = secs % 60
        ms = (elapsed % 1000) // 10
        sw_text = f"{mins:02d}:{secs:02d}.{ms:02d}"
        display.fill_rect(60, 155, 250, 50, BLACK)
        text_w = len(sw_text) * 6 * 5
        draw_text(display, sw_text, (368 - text_w) // 2, 160, GREY, 5, CODE_FONT)

    elif clock_mode == 2:
        # Timer - update time at top and timer
        hours, minutes, seconds = read_rtc()
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        # Update top time
        display.fill_rect(100, 60, 170, 30, BLACK)
        text_w = len(time_text) * 6 * 3
        draw_text(display, time_text, (368 - text_w) // 2, 65, GREEN, 3, CODE_FONT)

        # Update timer
        if timer_running:
            remaining = timer_target - time.ticks_ms()
            if remaining < 0:
                remaining = 0
                timer_running = False
            timer_remaining = remaining
        else:
            remaining = timer_remaining
        secs_total = remaining // 1000
        mins = secs_total // 60
        secs = secs_total % 60
        timer_text = f"{mins:02d}:{secs:02d}"
        display.fill_rect(80, 145, 210, 60, BLACK)
        text_w = len(timer_text) * 6 * 6
        draw_text(display, timer_text, (368 - text_w) // 2, 150, GREY, 6, CODE_FONT)

def launch_clock():
    global clock_mode, last_clock_display
    clock_mode = 0
    last_clock_display = ""
    draw_clock_app_full()

def handle_clock_touch(tx, ty):
    global clock_mode, stopwatch_running, stopwatch_start, stopwatch_elapsed, timer_running, timer_target, timer_remaining
    # Clock app touch handling
    # Check mode tabs (y=15 to y=50, smaller tabs)
    if 15 <= ty <= 50:
        tab_w = 100
        for i in range(3):
            tab_x = 24 + i * (tab_w + 10)
            if tab_x <= tx <= tab_x + tab_w:
                clock_mode = i
                draw_clock_app_full()
                break
    elif clock_mode == 1:
        # Stopwatch controls
        if 300 <= ty <= 360:
            if 50 <= tx <= 180:
                # Start/Stop
                if stopwatch_running:
                    stopwatch_elapsed += time.ticks_diff(time.ticks_ms(), stopwatch_start)
                    stopwatch_running = False
                else:
                    stopwatch_start = time.ticks_ms()
                    stopwatch_running = True
                draw_clock_app_full()
            elif 195 <= tx <= 325:
                # Reset
                stopwatch_elapsed = 0
                stopwatch_running = False
                draw_clock_app_full()
    elif clock_mode == 2:
        # Timer controls
        if not timer_running:
            if 105 <= ty <= 150:
                # Up arrow - add time
                timer_remaining += 60000  # Add 1 minute
                if timer_remaining > 5940000:  # Max 99 minutes
                    timer_remaining = 5940000
                draw_clock_app_full()
            elif 235 <= ty <= 280:
                # Down arrow - subtract time
                timer_remaining -= 60000
                if timer_remaining < 60000:
                    timer_remaining = 60000  # Min 1 minute
                draw_clock_app_full()
        if 310 <= ty <= 370:
            if 50 <= tx <= 180:
                # Start/Stop
                if timer_running:
                    timer_running = False
                else:
                    timer_target = time.ticks_ms() + timer_remaining
                    timer_running = True
                draw_clock_app_full()
            elif 195 <= tx <= 325:
                # Reset
                timer_running = False
                timer_remaining = 60000
                draw_clock_app_full()

def loop_clock():
    update_clock_display()
