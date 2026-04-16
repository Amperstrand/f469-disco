import display
import lvgl as lv
import utime as time

HOR_RES = 272
VER_RES = 480


def colored_block(parent, x, y, w, h, color_hex, label_text=""):
    cont = lv.cont(parent)
    cont.set_size(w, h)
    cont.set_pos(x, y)
    cont.set_fit(lv.FIT.NONE)
    style = lv.style_t()
    lv.style_copy(style, lv.style_plain)
    style.body.main_color = lv.color_hex(color_hex)
    style.body.grad_color = lv.color_hex(color_hex)
    style.body.border.width = 0
    cont.set_style(0, style)
    if label_text:
        lbl = lv.label(cont)
        lbl.set_text(label_text)
        lbl.set_align(lv.label.ALIGN.CENTER)
        lbl.align(cont, lv.ALIGN.CENTER, 0, 0)
    return cont


def run():
    display.init(False)

    # Phase 1: raw hardware fill test (4 colored quadrants)
    display.fill_test()
    time.sleep_ms(3000)

    # Phase 2: minimal LVGL test — theme fills screen with 0xf0f0f0 (light gray)
    # If whole screen turns light gray: rotation works.
    # If diagonal/garbled: rotation math is wrong.
    # If nothing changes: LVGL flush isn't running.
    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    scr = lv.obj()
    lv.scr_load(scr)

    title = lv.label(scr)
    title.set_text("PORTRAIT 272x480")
    title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 5)

    # Two huge blocks covering top/bottom halves — unmistakable
    half = VER_RES // 2
    colored_block(scr, 0, 30, HOR_RES, half - 30, 0xFF0000, "TOP RED")
    colored_block(scr, 0, half, HOR_RES, VER_RES - half - 10, 0x0000FF, "BOT BLUE")

    while True:
        display.update(30)
        time.sleep_ms(30)
