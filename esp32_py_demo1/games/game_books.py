# ===== BOOKS APP =====
# Extracted from main.py - all globals from main.py are available via exec()
import os

book_list = []
current_book = ""
book_position = 0  # Current byte position in file
next_page_position = 0  # Position after current page
book_at_eof = False  # Whether we've reached end of file
book_progress = {}  # {filename: byte_position}
book_scroll = 0  # Scroll offset for book list
lines_per_page = 14  # Bigger text = fewer lines
chars_per_line = 19  # Bigger text = fewer chars

def load_book_progress():
    global book_progress
    try:
        with open("books_progress.txt", "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 2:
                    book_progress[parts[0]] = int(parts[1])
        print(f"Loaded book progress: {len(book_progress)} books")
    except:
        print("No saved book progress")

def save_book_progress():
    try:
        with open("books_progress.txt", "w") as f:
            for filename, page in book_progress.items():
                f.write(f"{filename}|{page}\n")
    except Exception as e:
        print(f"Failed to save book progress: {e}")

def load_book_list():
    global book_list
    book_list = []
    try:
        os.mount(sd_card, '/sd')
        try:
            files = os.listdir('/sd/Books')
            for f in files:
                if f.endswith('.txt') or f.endswith('.TXT'):
                    book_list.append(f)
            book_list.sort()
        except:
            print("No Books folder on SD card")
        os.umount('/sd')
    except Exception as e:
        print(f"Failed to load book list: {e}")
    return book_list

def load_book(filename):
    global current_book, book_position
    current_book = filename
    book_position = book_progress.get(filename, 0)
    print(f"Opening book: {filename} at position {book_position}")
    return True

def read_page_from_file(start_pos):
    """Read one page worth of text starting from byte position.
    Returns (lines_list, next_position, is_end_of_file)"""
    lines = []

    if sd_card is None:
        return lines, start_pos, True

    try:
        os.mount(sd_card, '/sd')
        with open(f'/sd/Books/{current_book}', 'r') as f:
            f.seek(start_pos)
            current_line = ""
            current_word = ""
            word_start_pos = start_pos  # Track where current word started (absolute byte position)

            while len(lines) < lines_per_page:
                pos_before = f.tell()  # Byte position before reading
                char = f.read(1)
                if not char:
                    # End of file - flush remaining word and line
                    if current_word:
                        if len(current_line) + len(current_word) + 1 <= chars_per_line:
                            current_line = current_line + " " + current_word if current_line else current_word
                        else:
                            if current_line:
                                lines.append(current_line)
                            current_line = current_word
                    if current_line:
                        lines.append(current_line)
                    os.umount('/sd')
                    return lines, f.tell(), True

                if char == '\r':
                    continue
                elif char == '\n' or char == ' ':
                    # End of word - add word to line
                    if current_word:
                        if len(current_line) + len(current_word) + 1 <= chars_per_line:
                            # Word fits on current line
                            current_line = current_line + " " + current_word if current_line else current_word
                        else:
                            # Word doesn't fit - start new line
                            if current_line:
                                lines.append(current_line)
                                if len(lines) >= lines_per_page:
                                    # Page full - back up to start of this word
                                    os.umount('/sd')
                                    return lines, word_start_pos, False
                            current_line = current_word
                        current_word = ""

                    # Handle newline as paragraph break
                    if char == '\n' and current_line:
                        lines.append(current_line)
                        current_line = ""
                else:
                    # Building a word
                    if not current_word:
                        word_start_pos = pos_before  # Mark start of word (byte position)
                    current_word += char

            # Page is full - back up to not cut a word
            if current_word:
                # We have a partial word, back up to its start
                os.umount('/sd')
                return lines, word_start_pos, False
            else:
                os.umount('/sd')
                return lines, f.tell(), False

    except Exception as e:
        print(f"Read error: {e}")
        try:
            os.umount('/sd')
        except:
            pass
        return [], start_pos, True

def read_prev_page_position(target_pos):
    """Find the starting position of the previous page.
    Read backwards to find a good starting point."""
    if target_pos <= 0:
        return 0

    # Estimate: go back roughly two pages worth of characters
    estimate_chars = lines_per_page * chars_per_line * 3
    new_pos = max(0, target_pos - estimate_chars)

    # Read forward from there to find page boundaries
    if sd_card is None:
        return 0

    try:
        os.mount(sd_card, '/sd')
        with open(f'/sd/Books/{current_book}', 'r') as f:
            f.seek(new_pos)

            # Find positions of page boundaries using same word-aware logic
            positions = [new_pos]
            current_line = ""
            current_word = ""
            line_count = 0
            word_start_pos = new_pos  # Absolute byte position

            while f.tell() < target_pos:
                pos_before = f.tell()  # Byte position before reading
                char = f.read(1)
                if not char:
                    break

                if char == '\r':
                    continue
                elif char == '\n' or char == ' ':
                    # End of word
                    if current_word:
                        if len(current_line) + len(current_word) + 1 <= chars_per_line:
                            current_line = current_line + " " + current_word if current_line else current_word
                        else:
                            if current_line:
                                line_count += 1
                                if line_count >= lines_per_page:
                                    positions.append(word_start_pos)
                                    line_count = 0
                            current_line = current_word
                        current_word = ""

                    if char == '\n' and current_line:
                        line_count += 1
                        current_line = ""
                        if line_count >= lines_per_page:
                            positions.append(f.tell())
                            line_count = 0
                else:
                    if not current_word:
                        word_start_pos = pos_before  # Absolute byte position
                    current_word += char

        os.umount('/sd')

        # Return the second-to-last position (previous page start)
        if len(positions) >= 2:
            return positions[-2]
        return 0
    except Exception as e:
        print(f"Prev page error: {e}")
        try:
            os.umount('/sd')
        except:
            pass
        return 0

def draw_book_select():
    display.fill(BLACK)
    draw_text(display, "BOOKS", 140, 15, GREY, 3, CODE_FONT)

    if not book_list:
        draw_text(display, "NO BOOKS FOUND", 60, 200, GREY, 2, CODE_FONT)
        draw_text(display, "ADD TXT FILES TO", 50, 240, GREY, 2, CODE_FONT)
        draw_text(display, "SD CARD BOOKS FOLDER", 30, 270, GREY, 2, CODE_FONT)
        return

    y_start = 70
    row_height = 45
    max_visible = 7  # Reduced to leave room for scroll indicators

    # Draw up arrow if we can scroll up
    if book_scroll > 0:
        cx = 184
        for i in range(12):
            display.fill_rect(cx - i, 55 + i, i * 2 + 1, 2, GREY)

    # Draw visible books
    visible_books = book_list[book_scroll:book_scroll + max_visible]
    for i, filename in enumerate(visible_books):
        y = y_start + i * row_height
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        # Show filename without .txt, truncate if too long
        name = filename[:-4] if filename.endswith('.txt') else filename
        if len(name) > 25:
            name = name[:24] + "."
        draw_text(display, name.upper(), 30, y + 12, GREY, 2, CODE_FONT)
        # Show progress indicator if we have saved progress
        if filename in book_progress:
            draw_text(display, "*", 340, y + 12, GREY, 2, CODE_FONT)

    y_final = y_start + len(visible_books) * row_height
    display.fill_rect(20, y_final, 328, 3, DARK_GREY)

    # Draw down arrow if we can scroll down
    if book_scroll + max_visible < len(book_list):
        cx = 184
        arrow_y = y_final + 15
        for i in range(12):
            display.fill_rect(cx - i, arrow_y + 12 - i, i * 2 + 1, 2, GREY)

def draw_book_reader():
    global book_position
    display.fill(BLACK)

    # Read current page from file
    lines, next_pos, is_eof = read_page_from_file(book_position)

    # Draw page content with bigger text (scale 3) - safe from rounded corners
    y = 12
    line_height = 28
    for line in lines:
        draw_text(display, line, 10, y, GREY, 3, BOOK_FONT)
        y += line_height

    # Draw position indicator at bottom
    if book_position == 0:
        pos_text = "START"
    elif is_eof:
        pos_text = "END"
    else:
        pos_text = f"POS {book_position}"
    text_w = len(pos_text) * 6 * 2
    draw_text(display, pos_text, (368 - text_w) // 2, 420, DARK_GREY, 2, CODE_FONT)

    # Store next position for navigation
    return next_pos, is_eof

load_book_progress()

def launch_books():
    global reading_book, book_scroll
    reading_book = False
    book_scroll = 0
    if sd_card is None:
        init_sd_card()
    if sd_card is not None:
        load_book_list()
    draw_book_select()

def handle_books_touch(tx, ty):
    global reading_book, book_position, next_page_position, book_at_eof, book_scroll, book_progress, current_screen, current_app, last_time_text
    # Books app touch handling
    if not reading_book:
        # Book selection screen
        print(f"Books touch: ty={ty}, book_list len={len(book_list)}")
        if book_list:
            y_start = 70
            row_height = 45
            max_visible = 7
            visible_count = len(book_list[book_scroll:book_scroll + max_visible])
            y_end = y_start + visible_count * row_height
            print(f"y_start={y_start}, y_end={y_end}, visible={visible_count}")

            # Check for scroll up (tap above book list)
            if ty < y_start and book_scroll > 0:
                book_scroll = max(0, book_scroll - max_visible)
                draw_book_select()
            # Check for scroll down (tap below book list)
            elif ty > y_end and book_scroll + max_visible < len(book_list):
                book_scroll = min(len(book_list) - max_visible, book_scroll + max_visible)
                draw_book_select()
            # Check for book selection
            elif y_start <= ty <= y_end:
                for i in range(visible_count):
                    item_top = y_start + i * row_height
                    item_bottom = item_top + row_height
                    if item_top <= ty < item_bottom:
                        book_idx = book_scroll + i
                        print(f"Selected book index {book_idx}")
                        if book_idx < len(book_list):
                            filename = book_list[book_idx]
                            print(f"Opening: {filename}")
                            if load_book(filename):
                                reading_book = True
                                next_pos, is_eof = draw_book_reader()
                                next_page_position = next_pos
                                book_at_eof = is_eof
                        break
    else:
        # Reading screen - tap left/right to change page
        if tx < 184:
            # Left side - previous page
            if book_position > 0:
                book_position = read_prev_page_position(book_position)
                book_progress[current_book] = book_position
                save_book_progress()
                next_pos, is_eof = draw_book_reader()
                next_page_position = next_pos
                book_at_eof = is_eof
        else:
            # Right side - next page
            if not book_at_eof:
                book_position = next_page_position
                book_progress[current_book] = book_position
                save_book_progress()
                next_pos, is_eof = draw_book_reader()
                next_page_position = next_pos
                book_at_eof = is_eof
