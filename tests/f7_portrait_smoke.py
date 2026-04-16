import display
import udisplay as ud
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

    display.fill_test()
    time.sleep_ms(3000)

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    scr = lv.obj()
    lv.scr_load(scr)

    bw = 2
    colored_block(scr, 0, 0, HOR_RES, bw, 0x00FF00)
    colored_block(scr, 0, VER_RES - bw, HOR_RES, bw, 0x00FF00)
    colored_block(scr, 0, 0, bw, VER_RES, 0x00FF00)
    colored_block(scr, HOR_RES - bw, 0, bw, VER_RES, 0x00FF00)

    colored_block(scr, 4, 8, 60, 30, 0xFF0000, "TL")
    colored_block(scr, HOR_RES - 64, 8, 60, 30, 0x0000FF, "TR")
    colored_block(scr, 4, VER_RES - 38, 60, 30, 0xFFFF00, "BL")
    colored_block(scr, HOR_RES - 64, VER_RES - 38, 60, 30, 0xFF00FF, "BR")

    title = lv.label(scr)
    title.set_text("TOUCH TEST")
    title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 12)

    touch_label = lv.label(scr)
    touch_label.set_text("Touch the screen...")
    touch_label.align(scr, lv.ALIGN.CENTER, 0, -20)

    coord_label = lv.label(scr)
    coord_label.set_text("X:--- Y:---")
    coord_label.align(scr, lv.ALIGN.CENTER, 0, 10)

    dot = colored_block(scr, HOR_RES // 2 - 10, VER_RES // 2 + 30, 20, 20, 0xFFFFFF)

    while True:
        display.update(30)
        result = ud.touch_point()
        if result is not None and result[0]:
            x, y = result[1], result[2]
            coord_label.set_text("X:%d Y:%d" % (x, y))
            if 0 <= x < HOR_RES and 0 <= y < VER_RES:
                dot.set_pos(x - 10, y - 10)
        time.sleep_ms(30)
