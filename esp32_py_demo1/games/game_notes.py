# ===== NOTES APP =====
# Simple text editor with on-screen keyboard, saves to notes.txt

NOTE_FILE = "notes.txt"
NOTE_MAX = 500  # Max characters

# Keyboard layout - QWERTY with numbers accessible via 123 toggle
NT_ALPHA_ROWS = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
NT_NUM_ROWS = ["1234567890", "!@#$%^&*()", "+-=.,?/'\""]

# Key sizing - bigger than Wordle (31x38)
NT_KEY_W = 33
NT_KEY_H = 42
NT_GAP = 2
NT_KB_Y = 250  # Keyboard top Y

NT_KEY_BG = make_color(25, 25, 25)
NT_KEY_HL = make_color(0, 80, 0)  # Pressed key highlight
NT_CURSOR_COLOR = GREEN

# State
nt_mode = 0  # 0=menu, 1=editing, 2=confirm_clear1, 3=confirm_clear2
nt_text = ""
nt_scroll = 0  # Scroll offset in lines
nt_cursor = 0  # Cursor position in text
nt_shift = False
nt_num_mode = False  # False=letters, True=numbers/symbols
nt_saved = True  # Track if changes saved

def nt_load():
    global nt_text, nt_saved
    try:
        with open(NOTE_FILE, 'r') as f:
            nt_text = f.read()
        if len(nt_text) > NOTE_MAX:
            nt_text = nt_text[:NOTE_MAX]
        nt_saved = True
    except:
        nt_text = ""
        nt_saved = True

def nt_save():
    global nt_saved
    try:
        with open(NOTE_FILE, 'w') as f:
            f.write(nt_text)
        nt_saved = True
    except:
        pass

# ===== TEXT DISPLAY =====
NT_CHARS_PER_LINE = 26  # 368 / (12+2) = ~26 chars at size 2 with padding
NT_TEXT_Y = 5
NT_TEXT_H = 240  # Height for text area
NT_LINES_VISIBLE = 10  # Lines visible at once (240 / 24)
NT_LINE_H = 24

def nt_get_lines():
    """Word-wrap text into lines."""
    lines = []
    for paragraph in nt_text.split('\n'):
        if not paragraph:
            lines.append("")
            continue
        while len(paragraph) > NT_CHARS_PER_LINE:
            # Find last space within limit
            brk = paragraph[:NT_CHARS_PER_LINE].rfind(' ')
            if brk <= 0:
                brk = NT_CHARS_PER_LINE
            lines.append(paragraph[:brk])
            paragraph = paragraph[brk:].lstrip()
        lines.append(paragraph)
    if not lines:
        lines = [""]
    return lines

def nt_cursor_line_col():
    """Get line and column of cursor position."""
    lines = nt_get_lines()
    pos = 0
    for i, line in enumerate(lines):
        line_len = len(line)
        # Account for the space/newline between lines
        if i < len(lines) - 1:
            end = pos + line_len + 1
        else:
            end = pos + line_len
        if nt_cursor <= end:
            return i, nt_cursor - pos
        pos = end
    return len(lines) - 1, len(lines[-1]) if lines else 0

def nt_draw_text_area():
    """Draw the text area with cursor."""
    global nt_scroll
    # Clear text area
    display.fill_rect(0, 0, 368, NT_KB_Y - 2, BLACK)

    lines = nt_get_lines()
    cur_line, cur_col = nt_cursor_line_col()

    # Auto-scroll to keep cursor visible
    if cur_line < nt_scroll:
        nt_scroll = cur_line
    if cur_line >= nt_scroll + NT_LINES_VISIBLE:
        nt_scroll = cur_line - NT_LINES_VISIBLE + 1

    # Separator line
    display.fill_rect(0, NT_KB_Y - 2, 368, 2, DARK_GREY)

    # Draw visible lines
    for i in range(NT_LINES_VISIBLE):
        li = nt_scroll + i
        if li >= len(lines):
            break
        y = NT_TEXT_Y + i * NT_LINE_H
        line = lines[li]
        if line:
            draw_text(display, line.upper(), 8, y + 4, GREY, 2, CODE_FONT)

        # Draw cursor
        if li == cur_line:
            cx = 8 + cur_col * 12
            display.fill_rect(cx, y + 2, 2, NT_LINE_H - 4, NT_CURSOR_COLOR)

    # Scroll indicators
    if nt_scroll > 0:
        for i in range(6):
            display.fill_rect(184 - i, NT_TEXT_Y - 2 + i, i * 2 + 1, 1, GREEN)
    if nt_scroll + NT_LINES_VISIBLE < len(lines):
        by = NT_KB_Y - 8
        for i in range(6):
            display.fill_rect(184 - i, by - i, i * 2 + 1, 1, GREEN)

    # Character count
    cnt = f"{len(nt_text)}/{NOTE_MAX}"
    cw = len(cnt) * 12
    draw_text(display, cnt, 368 - cw - 4, NT_KB_Y - 18, DARK_GREY, 2, CODE_FONT)

# ===== KEYBOARD DRAWING =====
def nt_draw_keyboard():
    """Draw the full keyboard."""
    display.fill_rect(0, NT_KB_Y, 368, 448 - NT_KB_Y, BLACK)
    rows = NT_NUM_ROWS if nt_num_mode else NT_ALPHA_ROWS

    for r in range(3):
        y = NT_KB_Y + r * (NT_KEY_H + NT_GAP)
        if r == 2:
            # Bottom row: special keys + letters + special keys
            # SHIFT/123 key (left)
            lbl = "123" if not nt_num_mode else "ABC"
            bg = NT_KEY_HL if (nt_shift and not nt_num_mode) else NT_KEY_BG
            display.fill_rect(2, y, 44, NT_KEY_H, bg)
            lw = len(lbl) * 12
            draw_text(display, lbl, 2 + (44 - lw) // 2, y + (NT_KEY_H - 12) // 2, WHITE, 2, CODE_FONT)

            # Letter keys
            x = 48
            for ch in rows[2]:
                display.fill_rect(x, y, NT_KEY_W, NT_KEY_H, NT_KEY_BG)
                disp_ch = ch.upper() if nt_shift and not nt_num_mode else ch
                cw = 12
                draw_text(display, disp_ch, x + (NT_KEY_W - cw) // 2, y + (NT_KEY_H - 12) // 2, WHITE, 2, CODE_FONT)
                x += NT_KEY_W + NT_GAP

            # DEL key (right)
            display.fill_rect(x, y, 44, NT_KEY_H, NT_KEY_BG)
            draw_text(display, "DEL", x + 4, y + (NT_KEY_H - 12) // 2, WHITE, 2, CODE_FONT)
        else:
            # Top two rows - center them
            row_chars = rows[r]
            total_w = len(row_chars) * (NT_KEY_W + NT_GAP) - NT_GAP
            x = (368 - total_w) // 2
            for ch in row_chars:
                display.fill_rect(x, y, NT_KEY_W, NT_KEY_H, NT_KEY_BG)
                disp_ch = ch.upper() if nt_shift and not nt_num_mode else ch
                cw = 12
                draw_text(display, disp_ch, x + (NT_KEY_W - cw) // 2, y + (NT_KEY_H - 12) // 2, WHITE, 2, CODE_FONT)
                x += NT_KEY_W + NT_GAP

    # Bottom bar: SPACE + ENTER + SAVE
    y = NT_KB_Y + 3 * (NT_KEY_H + NT_GAP)
    # Space bar
    display.fill_rect(2, y, 180, NT_KEY_H, NT_KEY_BG)
    draw_text(display, "SPACE", 2 + (180 - 60) // 2, y + (NT_KEY_H - 12) // 2, GREY, 2, CODE_FONT)
    # Enter
    display.fill_rect(184, y, 80, NT_KEY_H, NT_KEY_BG)
    draw_text(display, "ENTER", 184 + (80 - 60) // 2, y + (NT_KEY_H - 12) // 2, GREY, 2, CODE_FONT)
    # Save
    sv_bg = GREEN if not nt_saved else NT_KEY_BG
    display.fill_rect(266, y, 100, NT_KEY_H, sv_bg)
    sv_txt = "SAVED" if nt_saved else "SAVE"
    sw = len(sv_txt) * 12
    draw_text(display, sv_txt, 266 + (100 - sw) // 2, y + (NT_KEY_H - 12) // 2, WHITE, 2, CODE_FONT)

def nt_draw_all():
    """Draw everything."""
    nt_draw_text_area()
    nt_draw_keyboard()

# ===== MENU =====
def draw_nt_menu():
    display.fill(BLACK)
    draw_text(display, "NOTES", 130, 30, GREY, 4, CODE_FONT)
    # New note button
    display.fill_rect(34, 130, 300, 60, GREEN)
    txt = "NEW NOTE"
    tw = len(txt) * 12
    draw_text(display, txt, 34 + (300 - tw) // 2, 148, WHITE, 2, CODE_FONT)
    # Continue editing (if note exists)
    if nt_text:
        display.fill_rect(34, 210, 300, 60, GREEN)
        txt = "CONTINUE EDITING"
        tw = len(txt) * 12
        draw_text(display, txt, 34 + (300 - tw) // 2, 228, WHITE, 2, CODE_FONT)
    else:
        display.fill_rect(34, 210, 300, 60, DARK_GREY)
        txt = "NO SAVED NOTE"
        tw = len(txt) * 12
        draw_text(display, txt, 34 + (300 - tw) // 2, 228, GREY, 2, CODE_FONT)
    # Clear all button
    if nt_text:
        display.fill_rect(34, 310, 300, 60, make_color(100, 0, 0))
        txt = "CLEAR ALL"
        tw = len(txt) * 12
        draw_text(display, txt, 34 + (300 - tw) // 2, 328, WHITE, 2, CODE_FONT)

def draw_nt_confirm(stage):
    """Draw confirmation screen. stage=1 first ask, stage=2 second ask."""
    display.fill(BLACK)
    if stage == 1:
        draw_text(display, "CLEAR ALL", 80, 60, GREY, 4, CODE_FONT)
        draw_text(display, "NOTES?", 110, 110, GREY, 4, CODE_FONT)
        draw_text(display, "ARE YOU SURE?", 70, 200, WHITE, 3, CODE_FONT)
    else:
        draw_text(display, "REALLY", 104, 60, GREY, 4, CODE_FONT)
        draw_text(display, "DELETE?", 92, 110, GREY, 4, CODE_FONT)
        draw_text(display, "ARE YOU SURE??", 58, 200, WHITE, 3, CODE_FONT)
    display.fill_rect(25, 295, 150, 70, make_color(100, 0, 0))
    draw_text(display, "YES", 72, 318, WHITE, 3, CODE_FONT)
    display.fill_rect(193, 295, 150, 70, GAMEOVER_BTN)
    draw_text(display, "NO", 245, 318, WHITE, 3, CODE_FONT)

# ===== APP INTERFACE =====
def launch_notes():
    global nt_mode, nt_scroll, nt_cursor, nt_shift, nt_num_mode, nt_saved
    nt_load()
    nt_mode = 0
    nt_scroll = 0
    nt_cursor = len(nt_text)
    nt_shift = False
    nt_num_mode = False
    nt_saved = True
    draw_nt_menu()

def handle_notes_touch(tx, ty):
    global nt_mode, nt_text, nt_cursor, nt_scroll, nt_shift, nt_num_mode, nt_saved
    global current_screen, current_app, last_time_text

    if nt_mode == 0:  # Menu
        if 130 <= ty <= 190 and 34 <= tx <= 334:
            # New note
            nt_text = ""
            nt_cursor = 0
            nt_scroll = 0
            nt_saved = False
            nt_mode = 1
            nt_draw_all()
        elif 210 <= ty <= 270 and 34 <= tx <= 334 and nt_text:
            # Continue editing
            nt_cursor = len(nt_text)
            nt_scroll = 0
            nt_mode = 1
            nt_draw_all()
        elif 310 <= ty <= 370 and 34 <= tx <= 334 and nt_text:
            # Clear all - first confirmation
            nt_mode = 2
            draw_nt_confirm(1)
        return

    if nt_mode == 2:  # First confirmation
        if 295 <= ty <= 365:
            if 25 <= tx <= 175:
                # Yes - ask again
                nt_mode = 3
                draw_nt_confirm(2)
            elif 193 <= tx <= 343:
                # No - back to menu
                nt_mode = 0
                draw_nt_menu()
        return

    if nt_mode == 3:  # Second confirmation
        if 295 <= ty <= 365:
            if 25 <= tx <= 175:
                # Yes for real - clear everything
                nt_text = ""
                nt_cursor = 0
                nt_scroll = 0
                nt_saved = False
                nt_save()
                nt_mode = 0
                draw_nt_menu()
            elif 193 <= tx <= 343:
                # No - back to menu
                nt_mode = 0
                draw_nt_menu()
        return

    # Mode 1: Editing
    if ty < NT_KB_Y - 2:
        # Tapped in text area - move cursor
        lines = nt_get_lines()
        line_idx = nt_scroll + (ty - NT_TEXT_Y) // NT_LINE_H
        if line_idx < 0:
            line_idx = 0
        if line_idx >= len(lines):
            line_idx = len(lines) - 1
        col = (tx - 8) // 12
        if col < 0:
            col = 0
        if col > len(lines[line_idx]):
            col = len(lines[line_idx])
        # Convert line,col back to cursor position
        pos = 0
        for i in range(line_idx):
            pos += len(lines[i]) + 1
        nt_cursor = min(pos + col, len(nt_text))
        nt_draw_text_area()
        # Scroll up/down on edge taps
        if ty < NT_TEXT_Y + 10 and nt_scroll > 0:
            nt_scroll -= 1
            nt_draw_text_area()
        elif ty > NT_KB_Y - 20 and nt_scroll + NT_LINES_VISIBLE < len(lines):
            nt_scroll += 1
            nt_draw_text_area()
        return

    # Keyboard area
    rows = NT_NUM_ROWS if nt_num_mode else NT_ALPHA_ROWS
    kb_row = (ty - NT_KB_Y) // (NT_KEY_H + NT_GAP)

    if kb_row < 0 or kb_row > 3:
        return

    if kb_row == 3:
        # Bottom bar: SPACE / ENTER / SAVE
        if tx < 182:
            # Space
            if len(nt_text) < NOTE_MAX:
                nt_text = nt_text[:nt_cursor] + ' ' + nt_text[nt_cursor:]
                nt_cursor += 1
                nt_saved = False
                nt_draw_all()
        elif tx < 264:
            # Enter (newline)
            if len(nt_text) < NOTE_MAX:
                nt_text = nt_text[:nt_cursor] + '\n' + nt_text[nt_cursor:]
                nt_cursor += 1
                nt_saved = False
                nt_draw_all()
        else:
            # Save
            nt_save()
            nt_draw_keyboard()
        return

    if kb_row == 2:
        # Bottom letter row with special keys
        if tx < 46:
            # 123/ABC toggle
            if nt_num_mode:
                nt_num_mode = False
            else:
                # If already in alpha, toggle shift; if tapping 123, switch to num
                nt_num_mode = True
                nt_shift = False
            nt_draw_keyboard()
            return

        # DEL key area (right side)
        row_chars = rows[2]
        del_x = 48 + len(row_chars) * (NT_KEY_W + NT_GAP)
        if tx >= del_x:
            # Delete
            if nt_cursor > 0:
                nt_text = nt_text[:nt_cursor - 1] + nt_text[nt_cursor:]
                nt_cursor -= 1
                nt_saved = False
                nt_draw_all()
            return

        # Letter keys in bottom row
        key_idx = (tx - 48) // (NT_KEY_W + NT_GAP)
        if 0 <= key_idx < len(row_chars):
            ch = row_chars[key_idx]
            if not nt_num_mode and not nt_shift:
                ch = ch.lower()
            if len(nt_text) < NOTE_MAX:
                nt_text = nt_text[:nt_cursor] + ch + nt_text[nt_cursor:]
                nt_cursor += 1
                nt_saved = False
                nt_draw_all()
        return

    # Top two rows
    row_chars = rows[kb_row]
    total_w = len(row_chars) * (NT_KEY_W + NT_GAP) - NT_GAP
    x_start = (368 - total_w) // 2
    key_idx = (tx - x_start) // (NT_KEY_W + NT_GAP)
    if 0 <= key_idx < len(row_chars):
        ch = row_chars[key_idx]
        if not nt_num_mode and not nt_shift:
            ch = ch.lower()
        if len(nt_text) < NOTE_MAX:
            nt_text = nt_text[:nt_cursor] + ch + nt_text[nt_cursor:]
            nt_cursor += 1
            nt_saved = False
            nt_draw_all()
