import lvgl as lv
import display
import utime as time

HOR_RES = 480
VER_RES = 272


def run():
    display.init(False)

    display.fill_test()
    time.sleep_ms(3000)

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    scr = lv.obj()
    lv.scr_load(scr)

    title = lv.label(scr)
    title.set_text("F746G-DISCO TOUCH PoC")
    title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 5)

    diag_lbl = lv.label(scr)
    tr = display.touch_ready()
    diag_lbl.set_text("touch_ready: %s" % ("YES" if tr else "NO"))
    diag_lbl.align(scr, lv.ALIGN.IN_TOP_MID, 0, 25)

    obj = {"counter": 0}

    count_lbl = lv.label(scr)
    count_lbl.set_text("Counter: 0")
    count_lbl.align(scr, lv.ALIGN.IN_TOP_MID, 0, 45)

    def on_plus(btn, e):
        if e == lv.EVENT.RELEASED:
            obj["counter"] += 1
            count_lbl.set_text("Counter: %d" % obj["counter"])

    def on_minus(btn, e):
        if e == lv.EVENT.RELEASED:
            obj["counter"] -= 1
            count_lbl.set_text("Counter: %d" % obj["counter"])

    def on_reset(btn, e):
        if e == lv.EVENT.RELEASED:
            obj["counter"] = 0
            count_lbl.set_text("Counter: %d" % obj["counter"])

    btn_w = 130
    btn_h = 60
    gap = 20
    total_w = 3 * btn_w + 2 * gap
    start_x = (HOR_RES - total_w) // 2
    btn_y = VER_RES // 2 + 20

    btn_plus = lv.btn(scr)
    btn_plus.set_size(btn_w, btn_h)
    btn_plus.set_pos(start_x, btn_y)
    lbl_p = lv.label(btn_plus)
    lbl_p.set_text("+1")
    lbl_p.set_align(lv.label.ALIGN.CENTER)
    lbl_p.align(btn_plus, lv.ALIGN.CENTER, 0, 0)
    btn_plus.set_event_cb(on_plus)

    btn_reset = lv.btn(scr)
    btn_reset.set_size(btn_w, btn_h)
    btn_reset.set_pos(start_x + btn_w + gap, btn_y)
    lbl_r = lv.label(btn_reset)
    lbl_r.set_text("RESET")
    lbl_r.set_align(lv.label.ALIGN.CENTER)
    lbl_r.align(btn_reset, lv.ALIGN.CENTER, 0, 0)
    btn_reset.set_event_cb(on_reset)

    btn_minus = lv.btn(scr)
    btn_minus.set_size(btn_w, btn_h)
    btn_minus.set_pos(start_x + 2 * (btn_w + gap), btn_y)
    lbl_m = lv.label(btn_minus)
    lbl_m.set_text("-1")
    lbl_m.set_align(lv.label.ALIGN.CENTER)
    lbl_m.align(btn_minus, lv.ALIGN.CENTER, 0, 0)
    btn_minus.set_event_cb(on_minus)

    hint = lv.label(scr)
    hint.set_text("Touch buttons to change counter")
    hint.align(scr, lv.ALIGN.IN_BOTTOM_MID, 0, -10)

    while True:
        display.update(30)
        time.sleep_ms(30)


run()
