import lvgl as lv
import display
import utime as time
from machine import I2C

HOR_RES = 480
VER_RES = 272

FT5336_ADDR = 0x38
FT5336_TD_STAT = 0x02
FT5336_P1_XH = 0x03
FT5336_CHIP_ID = 0xA8
FT5336_GMODE = 0xA4


class TouchReader:
    def __init__(self):
        self.i2c = I2C(3, freq=400000)
        self.chip_id = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_CHIP_ID, 1)[0]
        if self.chip_id != 0x51:
            raise OSError("FT5336 chip ID mismatch: 0x%02X" % self.chip_id)
        self.i2c.writeto_mem(FT5336_ADDR, FT5336_GMODE, b'\x00')
        self.last_x = 0
        self.last_y = 0
        self.last_td = 0
        self.last_raw_x = 0
        self.last_raw_y = 0
        self.touching = False

    def read(self):
        td = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_TD_STAT, 1)[0] & 0x0F
        self.last_td = td
        if td == 0 or td > 5:
            self.touching = False
            return self.last_x, self.last_y, False
        raw = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_P1_XH, 4)
        raw_x = ((raw[0] & 0x0F) << 8) | raw[1]
        raw_y = ((raw[2] & 0x0F) << 8) | raw[3]
        self.last_raw_x = raw_x
        self.last_raw_y = raw_y
        self.last_x = raw_y
        self.last_y = raw_x
        self.touching = True
        return self.last_x, self.last_y, True


def make_colored_block(parent, x, y, w, h, color_hex, label_text=""):
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

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    scr = lv.obj()
    lv.scr_load(scr)

    row_h = VER_RES // 2
    col_w = HOR_RES // 3

    make_colored_block(scr, 0, 0, col_w, row_h, 0xFF0000, "RED")
    make_colored_block(scr, col_w, 0, col_w, row_h, 0x00FF00, "GREEN")
    make_colored_block(scr, 2 * col_w, 0, col_w, row_h, 0x0000FF, "BLUE")
    make_colored_block(scr, 0, row_h, col_w, row_h, 0xFFFF00, "YELLOW")
    make_colored_block(scr, col_w, row_h, col_w, row_h, 0xFF00FF, "MAGENTA")
    make_colored_block(scr, 2 * col_w, row_h, col_w, row_h, 0x00FFFF, "CYAN")

    title_lbl = lv.label(scr)
    title_lbl.set_text("F746G-DISCO SMOKE TEST")
    title_lbl.align(scr, lv.ALIGN.IN_TOP_MID, 0, 5)

    chip_lbl = lv.label(scr)
    chip_lbl.set_text("FT5336: probing...")
    chip_lbl.align(scr, lv.ALIGN.IN_TOP_LEFT, 8, 8)

    coord_lbl = lv.label(scr)
    coord_lbl.set_text("Touch the screen...")
    coord_lbl.align(scr, lv.ALIGN.CENTER, 0, 0)

    raw_lbl = lv.label(scr)
    raw_lbl.set_text("RAW: --")
    raw_lbl.align(scr, lv.ALIGN.IN_TOP_LEFT, 8, 28)

    status_lbl = lv.label(scr)
    status_lbl.set_text("Waiting for touch...")
    status_lbl.align(scr, lv.ALIGN.IN_BOTTOM_MID, 0, -5)

    for _ in range(20):
        display.update(30)

    try:
        touch = TouchReader()
        chip_lbl.set_text("FT5336 ID: 0x%02X" % touch.chip_id)
    except Exception as exc:
        chip_lbl.set_text("FT5336 init failed")
        raw_lbl.set_text(str(exc))
        while True:
            display.update(30)
            time.sleep_ms(30)

    touch_count = 0
    while True:
        x, y, touching = touch.read()
        raw_lbl.set_text("TD:%d RX:%d RY:%d" % (touch.last_td, touch.last_raw_x, touch.last_raw_y))
        if touching:
            touch_count += 1
            coord_lbl.set_text("X:%d Y:%d" % (x, y))
            status_lbl.set_text("Touch #%d" % touch_count)
        else:
            status_lbl.set_text("Waiting for touch...")
        display.update(30)
        time.sleep_ms(30)


if __name__ == "__main__":
    run()
