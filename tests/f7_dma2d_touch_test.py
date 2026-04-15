import display
import lvgl as lv
import utime as time
from machine import I2C

HOR = 480
VER = 272

FT5336_ADDR = 0x38
FT5336_TD_STAT = 0x02
FT5336_P1_XH = 0x03
FT5336_CHIP_ID = 0xA8
FT5336_GMODE = 0xA4


class TouchReader:
    def __init__(self):
        self.i2c = I2C(3, freq=400000)
        chip_id = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_CHIP_ID, 1)[0]
        if chip_id != 0x51:
            raise OSError("FT5336 chip ID mismatch: 0x%02X" % chip_id)
        self.i2c.writeto_mem(FT5336_ADDR, FT5336_GMODE, b'\x00')
        self.last_x = 0
        self.last_y = 0
        self.touching = False

    def read(self):
        td = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_TD_STAT, 1)[0] & 0x0F
        if td == 0 or td > 5:
            self.touching = False
            return self.last_x, self.last_y, False
        raw = self.i2c.readfrom_mem(FT5336_ADDR, FT5336_P1_XH, 4)
        raw_x = ((raw[0] & 0x0F) << 8) | raw[1]
        raw_y = ((raw[2] & 0x0F) << 8) | raw[3]
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

    display.fill_test()
    time.sleep_ms(3000)

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    scr = lv.obj()
    lv.scr_load(scr)

    row_h = VER // 2
    col_w = HOR // 3

    make_colored_block(scr, 0, 0, col_w, row_h, 0xFF0000, "RED")
    make_colored_block(scr, col_w, 0, col_w, row_h, 0x00FF00, "GREEN")
    make_colored_block(scr, 2 * col_w, 0, col_w, row_h, 0x0000FF, "BLUE")
    make_colored_block(scr, 0, row_h, col_w, row_h, 0xFFFF00, "YELLOW")
    make_colored_block(scr, col_w, row_h, col_w, row_h, 0xFF00FF, "MAGENTA")
    make_colored_block(scr, 2 * col_w, row_h, col_w, row_h, 0x00FFFF, "CYAN")

    title = lv.label(scr)
    title.set_text("F746G-DISCO DMA2D+TOUCH TEST")
    title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 5)

    coord = lv.label(scr)
    coord.set_text("Touch the screen...")
    coord.align(scr, lv.ALIGN.CENTER, 0, 0)

    status = lv.label(scr)
    status.set_text("Waiting...")
    status.align(scr, lv.ALIGN.IN_BOTTOM_MID, 0, -5)

    for _ in range(20):
        display.update(30)

    touch = TouchReader()

    count = 0
    while True:
        x, y, touching = touch.read()
        if touching:
            count += 1
            coord.set_text("X:%d Y:%d" % (x, y))
            status.set_text("Touch #%d" % count)
        display.update(30)
        time.sleep_ms(30)


run()
