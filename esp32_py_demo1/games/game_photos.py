# ===== PHOTOS APP =====
import os
import gc

photo_folders = []   # folder names in /sd/Pics/
photo_files = []     # filenames in current folder
photo_folder = ""    # current folder name
photo_idx = -1
photo_scroll = 0
photo_view = 0       # 0=folders, 1=files, 2=photo

def photo_clean_name(name):
    """Clean name for CODE_FONT display"""
    if '.' in name:
        name = name[:name.rfind('.')]
    name = name.replace('_', ' ').upper()
    clean = ""
    for c in name:
        if ('A' <= c <= 'Z') or ('0' <= c <= '9') or c in ' -/()':
            clean += c
    if len(clean) > 22:
        clean = clean[:19] + "..."
    return clean.strip()

def photo_scan_folders():
    """Find subfolders (and check for loose jpgs) in /sd/Pics/"""
    global photo_folders
    photo_folders = []
    if sd_card is None:
        return
    try:
        os.mount(sd_card, '/sd')
        entries = os.listdir('/sd/Pics')
        has_loose = False
        for e in entries:
            fl = e.lower()
            if fl.endswith('.jpg') or fl.endswith('.jpeg'):
                has_loose = True
            elif '.' not in e:
                try:
                    st = os.stat('/sd/Pics/' + e)
                    if st[0] & 0x4000:
                        photo_folders.append(e)
                except:
                    pass
        del entries
        photo_folders.sort()
        if has_loose:
            photo_folders.insert(0, "")
        os.umount('/sd')
    except:
        pass
    gc.collect()

def photo_scan_files(folder):
    """Find jpg files in a specific folder under /sd/Pics/"""
    global photo_files
    photo_files = []
    if sd_card is None:
        return
    path = '/sd/Pics/' + folder if folder else '/sd/Pics'
    try:
        os.mount(sd_card, '/sd')
        entries = os.listdir(path)
        for e in entries:
            fl = e.lower()
            if fl.endswith('.jpg') or fl.endswith('.jpeg'):
                photo_files.append(e)
        del entries
        photo_files.sort()
        os.umount('/sd')
    except:
        pass
    gc.collect()

def photo_parse_size(data):
    """Parse JPEG dimensions from bytes buffer"""
    w, h = 0, 0
    if len(data) < 4:
        return w, h
    pos = 2
    while pos < len(data) - 9:
        if data[pos] != 0xFF:
            break
        m = data[pos + 1]
        if m == 0xC0 or m == 0xC2:
            h = (data[pos + 5] << 8) | data[pos + 6]
            w = (data[pos + 7] << 8) | data[pos + 8]
            break
        elif m == 0xD9:
            break
        elif m == 0xD8 or (0xD0 <= m <= 0xD7) or m == 0x01:
            pos += 2
        else:
            if pos + 3 < len(data):
                ln = (data[pos + 2] << 8) | data[pos + 3]
                pos += 2 + ln
            else:
                break
    return w, h

def photo_show(idx):
    """Display photo from current folder"""
    if idx < 0 or idx >= len(photo_files):
        return
    filename = photo_files[idx]
    if photo_folder:
        sd_path = '/sd/Pics/' + photo_folder + '/' + filename
    else:
        sd_path = '/sd/Pics/' + filename

    # Show loading indicator
    display.fill(BLACK)
    draw_text(display, "LOADING...", 100, 200, GREEN, 3, CODE_FONT)

    ok = False
    try:
        os.mount(sd_card, '/sd')
        # Stream copy: read first chunk to check size, then copy rest
        with open(sd_path, 'rb') as src:
            first = src.read(4096)
            w, h = photo_parse_size(first)
            if w > 368 or h > 448:
                del first
                os.umount('/sd')
                display.fill(BLACK)
                draw_text(display, "TOO LARGE", 100, 150, GREY, 3, CODE_FONT)
                sz = f"{w}x{h}"
                draw_text(display, sz, (368 - len(sz) * 18) // 2, 200, GREY, 3, CODE_FONT)
                draw_text(display, "MAX 368X448", 75, 270, GREEN, 2, CODE_FONT)
                return
            # Stream to temp file in chunks (saves RAM)
            with open('_tmp.jpg', 'wb') as dst:
                dst.write(first)
                del first
                while True:
                    chunk = src.read(4096)
                    if not chunk:
                        break
                    dst.write(chunk)
        os.umount('/sd')
        display.fill(BLACK)
        display.jpg('_tmp.jpg', 0, 0)
        ok = True
        try:
            os.remove('_tmp.jpg')
        except:
            pass
    except Exception as e:
        print(f"Photo error: {e}")
        try:
            os.umount('/sd')
        except:
            pass
        try:
            os.remove('_tmp.jpg')
        except:
            pass
    if not ok:
        display.fill(BLACK)
        draw_text(display, "ERROR", 130, 200, GREY, 3, CODE_FONT)
    # Filename at bottom
    display.fill_rect(0, 425, 368, 23, BLACK)
    name = photo_clean_name(filename)
    nw = len(name) * 12
    draw_text(display, name, (368 - nw) // 2, 430, GREEN, 2, CODE_FONT)

def draw_folder_list():
    """Draw folder selection screen"""
    display.fill(BLACK)
    draw_text(display, "PHOTOS", 130, 15, GREY, 3, CODE_FONT)
    if not photo_folders:
        draw_text(display, "NO PHOTOS FOUND", 55, 160, GREY, 2, CODE_FONT)
        draw_text(display, "PUT .JPG FILES IN", 45, 200, GREY, 2, CODE_FONT)
        draw_text(display, "/SD/PICS/", 110, 240, GREEN, 2, CODE_FONT)
        return
    y = 65
    rh = 50
    visible = 7
    for i in range(visible):
        fi = photo_scroll + i
        if fi >= len(photo_folders):
            break
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        fname = photo_folders[fi]
        name = photo_clean_name(fname) if fname else "OTHER"
        draw_text(display, name, 30, y + 15, GREY, 2, CODE_FONT)
        y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    cx = 184
    if photo_scroll > 0:
        for i in range(10):
            display.fill_rect(cx - i, 50 + i, i * 2 + 1, 2, GREEN)
    if photo_scroll + visible < len(photo_folders):
        for i in range(10):
            display.fill_rect(cx - i, 430 + 10 - i, i * 2 + 1, 2, GREEN)

def draw_file_list():
    """Draw file list for current folder"""
    display.fill(BLACK)
    # Folder name as header
    fname = photo_clean_name(photo_folder) if photo_folder else "PHOTOS"
    nw = len(fname) * 18
    draw_text(display, fname, max(0, (368 - nw) // 2), 15, GREY, 3, CODE_FONT)
    if not photo_files:
        draw_text(display, "NO PHOTOS", 100, 200, GREY, 2, CODE_FONT)
        return
    y = 65
    rh = 50
    visible = 7
    for i in range(visible):
        fi = photo_scroll + i
        if fi >= len(photo_files):
            break
        display.fill_rect(20, y, 328, 3, DARK_GREY)
        name = photo_clean_name(photo_files[fi])
        draw_text(display, name, 30, y + 15, GREY, 2, CODE_FONT)
        y += rh
    display.fill_rect(20, y, 328, 3, DARK_GREY)
    # Scroll arrows
    cx = 184
    if photo_scroll > 0:
        for i in range(10):
            display.fill_rect(cx - i, 50 + i, i * 2 + 1, 2, GREEN)
    if photo_scroll + visible < len(photo_files):
        for i in range(10):
            display.fill_rect(cx - i, 430 + 10 - i, i * 2 + 1, 2, GREEN)

def launch_photos():
    global photo_view, photo_scroll, photo_idx
    photo_view = 0
    photo_scroll = 0
    photo_idx = -1
    if sd_card is None:
        init_sd_card()
    display.fill(BLACK)
    draw_text(display, "PHOTOS", 130, 15, GREY, 3, CODE_FONT)
    draw_text(display, "SCANNING...", 90, 200, GREEN, 3, CODE_FONT)
    photo_scan_folders()
    draw_folder_list()

def handle_photos_touch(tx, ty):
    global photo_view, photo_scroll, photo_idx, photo_folder

    if photo_view == 2:
        # Photo viewing - left/right/center
        if tx < 123:
            if photo_idx > 0:
                photo_idx -= 1
                photo_show(photo_idx)
        elif tx > 245:
            if photo_idx < len(photo_files) - 1:
                photo_idx += 1
                photo_show(photo_idx)
        else:
            photo_view = 1
            photo_scroll = 0
            draw_file_list()

    elif photo_view == 1:
        # File list
        visible = 7
        if ty < 55:
            if photo_scroll > 0:
                photo_scroll = max(0, photo_scroll - visible)
                draw_file_list()
            else:
                # At top and already at scroll 0 = back to folders
                photo_view = 0
                photo_scroll = 0
                draw_folder_list()
        elif ty > 420:
            if photo_scroll + visible < len(photo_files):
                photo_scroll += visible
                draw_file_list()
            else:
                # At bottom with no more to scroll = back to folders
                photo_view = 0
                photo_scroll = 0
                draw_folder_list()
        elif 65 <= ty <= 415:
            row = (ty - 65) // 50
            fi = photo_scroll + row
            if 0 <= fi < len(photo_files):
                photo_idx = fi
                photo_view = 2
                photo_show(photo_idx)

    else:
        # Folder list
        if not photo_folders:
            return
        visible = 7
        if ty < 55 and photo_scroll > 0:
            photo_scroll = max(0, photo_scroll - visible)
            draw_folder_list()
        elif ty > 420 and photo_scroll + visible < len(photo_folders):
            photo_scroll += visible
            draw_folder_list()
        elif 65 <= ty <= 415:
            row = (ty - 65) // 50
            fi = photo_scroll + row
            if 0 <= fi < len(photo_folders):
                photo_folder = photo_folders[fi]
                photo_scroll = 0
                display.fill(BLACK)
                draw_text(display, "LOADING...", 100, 200, GREEN, 3, CODE_FONT)
                photo_scan_files(photo_folder)
                photo_view = 1
                draw_file_list()
