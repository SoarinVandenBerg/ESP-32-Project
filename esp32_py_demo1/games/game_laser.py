# ===== LASER =====
from machine import Pin, PWM

laser_pwm = PWM(Pin(18), freq=1000, duty=0)
laser_on = False
laser_brightness = 3  # 0-3 index
laser_on_start = 0
laser_last_timer = ""

LASER_DUTY = [256, 512, 768, 1023]
LASER_PCT = ["25%", "50%", "75%", "100%"]

def draw_laser_screen():
    display.fill(BLACK)
    draw_text(display, "LASER", 140, 15, GREY, 3, CODE_FONT)
    # Big on/off circle
    if laser_on:
        display.fill_circle(184, 200, 80, GREEN)
        tw = len("ON") * 6 * 5
        draw_text(display, "ON", (368 - tw) // 2, 178, BLACK, 5, CODE_FONT)
    else:
        display.fill_circle(184, 200, 80, DARK_GREY)
        tw = len("OFF") * 6 * 5
        draw_text(display, "OFF", (368 - tw) // 2, 178, GREY, 5, CODE_FONT)
    # Brightness bar - 4 segments
    draw_laser_brightness()
    # Timer area
    display.fill_rect(0, 390, 368, 40, BLACK)
    if laser_on:
        draw_text(display, "00:00", 139, 398, GREEN, 3, CODE_FONT)
    else:
        draw_text(display, "--:--", 139, 398, DARK_GREY, 3, CODE_FONT)

def draw_laser_brightness():
    """Draw the 4-segment brightness bar"""
    bx = 34
    bw = 70
    gap = 10
    by = 320
    bh = 40
    for i in range(4):
        x = bx + i * (bw + gap)
        if i == laser_brightness:
            display.fill_rect(x, by, bw, bh, DARK_GREY)
            tw = len(LASER_PCT[i]) * 12
            draw_text(display, LASER_PCT[i], x + (bw - tw) // 2, by + 12, GREY, 2, CODE_FONT)
        else:
            display.fill_rect(x, by, bw, bh, BLACK)
            tw = len(LASER_PCT[i]) * 12
            draw_text(display, LASER_PCT[i], x + (bw - tw) // 2, by + 12, DARK_GREY, 2, CODE_FONT)

def launch_laser():
    global laser_on, laser_on_start, laser_last_timer
    laser_on = False
    laser_on_start = 0
    laser_last_timer = ""
    laser_pwm.duty(0)
    draw_laser_screen()

def laser_off():
    global laser_on
    laser_on = False
    laser_pwm.duty(0)

def handle_laser_touch(tx, ty):
    global laser_on, laser_on_start, laser_last_timer, laser_brightness
    # Check brightness bar tap (y=320-360)
    if 320 <= ty <= 360:
        bx = 34
        bw = 70
        gap = 10
        for i in range(4):
            x = bx + i * (bw + gap)
            if x <= tx <= x + bw:
                laser_brightness = i
                if laser_on:
                    laser_pwm.duty(LASER_DUTY[laser_brightness])
                draw_laser_brightness()
                return
    # Check big circle tap
    dx = tx - 184
    dy = ty - 200
    if dx * dx + dy * dy <= 6400:
        laser_on = not laser_on
        if laser_on:
            laser_pwm.duty(LASER_DUTY[laser_brightness])
            laser_on_start = time.ticks_ms()
            laser_last_timer = ""
        else:
            laser_pwm.duty(0)
        draw_laser_screen()

def laser_update_timer():
    global laser_last_timer
    if not laser_on:
        return
    elapsed = time.ticks_diff(time.ticks_ms(), laser_on_start) // 1000
    mins = elapsed // 60
    secs = elapsed % 60
    t = f"{mins:02d}:{secs:02d}"
    if t != laser_last_timer:
        display.fill_rect(139, 398, 90, 25, BLACK)
        draw_text(display, t, 139, 398, GREEN, 3, CODE_FONT)
        laser_last_timer = t
