import display
import lvgl as lv
import utime as time

HOR_RES = 480
VER_RES = 272

ADDRESSES = [
    "tb1q7kn55l0m4u8f9k0c8g6u8xqj0s7w0c9d3m3u8g",
    "tb1q2e4n5m7a8p9z0j6s4y3r2w8u1c5k6v7n8x9m2p",
    "tb1q4m8u2x7r9s0p3k6n1c5v8a2d4e7h9j0l3q6w5t",
]


def on_release(callback):
    def cb(obj, event):
        if event == lv.EVENT.RELEASED:
            callback()
    return cb


class SpecterDemo:
    def __init__(self):
        self.address_index = 0

    def button(self, screen, text, x, y, w, h, callback):
        btn = lv.btn(screen)
        btn.set_pos(x, y)
        btn.set_size(w, h)
        btn.set_event_cb(on_release(callback))
        label = lv.label(btn)
        label.set_text(text)
        label.set_align(lv.label.ALIGN.CENTER)
        label.align(btn, lv.ALIGN.CENTER, 0, 0)
        return btn

    def title(self, screen, text, y=8):
        label = lv.label(screen)
        label.set_text(text)
        label.align(screen, lv.ALIGN.IN_TOP_MID, 0, y)
        return label

    def body(self, screen, text, y, width=430):
        label = lv.label(screen)
        label.set_long_mode(lv.label.LONG.BREAK)
        label.set_width(width)
        label.set_text(text)
        label.set_align(lv.label.ALIGN.CENTER)
        label.align(screen, lv.ALIGN.IN_TOP_MID, 0, y)
        return label

    def message_screen(self, title, message):
        screen = lv.obj()
        self.title(screen, title)
        self.body(screen, message, 48)
        self.button(screen, lv.SYMBOL.LEFT + " Back", 20, 220, 120, 40, self.show_home)
        lv.scr_load(screen)

    def show_home(self):
        screen = lv.obj()
        self.title(screen, "Specter DIY F746 Demo")
        self.body(screen, "Boot path, display and touch are real. Storage, QR and PSBT parsing stay stubbed in this first vertical slice.", 34)

        status = lv.label(screen)
        status.set_text("touch_ready: %s" % ("YES" if display.touch_ready() else "NO"))
        status.align(screen, lv.ALIGN.IN_TOP_MID, 0, 82)

        self.button(screen, "Receive", 25, 116, 135, 54, self.show_receive)
        self.button(screen, "Master XPUB", 172, 116, 135, 54, self.show_master_xpub)
        self.button(screen, "PSBT Demo", 319, 116, 136, 54, self.show_psbt_stub)

        footer = lv.label(screen)
        footer.set_text("Next step: replace stub data with embit + QR")
        footer.align(screen, lv.ALIGN.IN_BOTTOM_MID, 0, -10)

        lv.scr_load(screen)

    def show_receive(self):
        screen = lv.obj()
        self.title(screen, "Receive")

        addr = ADDRESSES[self.address_index % len(ADDRESSES)]

        index_label = lv.label(screen)
        index_label.set_text("Address #%d" % (self.address_index + 1))
        index_label.align(screen, lv.ALIGN.IN_TOP_MID, 0, 34)

        addr_label = lv.label(screen)
        addr_label.set_long_mode(lv.label.LONG.BREAK)
        addr_label.set_width(430)
        addr_label.set_text(addr)
        addr_label.set_align(lv.label.ALIGN.CENTER)
        addr_label.align(screen, lv.ALIGN.IN_TOP_MID, 0, 78)

        hint = lv.label(screen)
        hint.set_text("Stub receive screen with deterministic demo addresses")
        hint.align(screen, lv.ALIGN.IN_BOTTOM_MID, 0, -58)

        self.button(screen, lv.SYMBOL.LEFT, 18, 220, 54, 40, self.prev_address)
        self.button(screen, "Home", 84, 220, 120, 40, self.show_home)
        self.button(screen, lv.SYMBOL.RIGHT, 398, 220, 54, 40, self.next_address)

        lv.scr_load(screen)

    def prev_address(self):
        if self.address_index > 0:
            self.address_index -= 1
        self.show_receive()

    def next_address(self):
        self.address_index += 1
        self.show_receive()

    def show_master_xpub(self):
        self.message_screen(
            "Master XPUB",
            "[stubbed demo]\n\nThe next step is to replace this with a real embit-derived xpub once the minimal boot path is validated on hardware.",
        )

    def show_psbt_stub(self):
        self.message_screen(
            "PSBT Demo",
            "PSBT import/export is postponed for now. This screen exists to prove menu flow and touch navigation on the F746 target.",
        )


def run():
    display.init(False)

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    demo = SpecterDemo()
    demo.show_home()

    while True:
        display.update(30)
        time.sleep_ms(30)
