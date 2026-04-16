import display
import lvgl as lv
import utime as time

from embit import bip32, script, networks, hashes
from binascii import hexlify

HOR_RES = 272
VER_RES = 480
PADDING = 12
BTN_H = 64
BTN_GAP = 14

SEED = bytes(range(16)) + b'\x00' * 48
NET = networks.NETWORKS["test"]
DERIVATION = "m/84h/1h/0h"


def p2wpkh_address(pubkey):
    h = hashes.hash160(pubkey.sec())
    s = script.Script(b"\x00\x14" + h)
    return s.address(NET)


class PopupScreen(lv.obj):
    def __init__(self, app, title="Title"):
        super().__init__()
        self.app = app
        self.old_screen = lv.scr_act()
        self.title = lv.label(self)
        self.title.set_text(title)
        self.title.align(self, lv.ALIGN.IN_TOP_MID, 0, 18)

        self.back_btn = lv.btn(self)
        self.back_btn.set_size(120, 44)
        self.back_btn.align(self, lv.ALIGN.IN_BOTTOM_MID, 0, -18)
        self.back_btn.set_event_cb(self.close)
        lbl = lv.label(self.back_btn)
        lbl.set_text(lv.SYMBOL.LEFT + " Back")
        lbl.align(self.back_btn, lv.ALIGN.CENTER, 0, 0)

        self.app.active_screen = self
        lv.scr_load(self)

    def close(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        self.app.active_screen = self.old_screen
        lv.scr_load(self.old_screen)
        self.del_async()


class MessageScreen(PopupScreen):
    def __init__(self, app, title="Title", message="Text"):
        super().__init__(app, title)
        self.lbl = lv.label(self)
        self.lbl.set_long_mode(lv.label.LONG.BREAK)
        self.lbl.set_width(HOR_RES - 2 * PADDING)
        self.lbl.set_align(lv.label.ALIGN.CENTER)
        self.lbl.set_text(message)
        self.lbl.align(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 28)


class AddressScreen(PopupScreen):
    def __init__(self, app):
        super().__init__(app, "Receive (testnet)")
        self.index = app.address_index

        self.index_lbl = lv.label(self)
        self.index_lbl.align(self.title, lv.ALIGN.OUT_BOTTOM_MID, 0, 18)

        self.addr_lbl = lv.label(self)
        self.addr_lbl.set_long_mode(lv.label.LONG.BREAK)
        self.addr_lbl.set_width(HOR_RES - 2 * PADDING)
        self.addr_lbl.set_align(lv.label.ALIGN.CENTER)
        self.addr_lbl.align(self.index_lbl, lv.ALIGN.OUT_BOTTOM_MID, 0, 18)

        self.path_lbl = lv.label(self)
        self.path_lbl.align(self, lv.ALIGN.IN_BOTTOM_MID, 0, -82)

        self.prev_btn = lv.btn(self)
        self.prev_btn.set_size(56, 44)
        self.prev_btn.align(self, lv.ALIGN.IN_BOTTOM_LEFT, PADDING, -18)
        self.prev_btn.set_event_cb(self.prev_address)
        lv.label(self.prev_btn).set_text(lv.SYMBOL.LEFT)

        self.next_btn = lv.btn(self)
        self.next_btn.set_size(56, 44)
        self.next_btn.align(self, lv.ALIGN.IN_BOTTOM_RIGHT, -PADDING, -18)
        self.next_btn.set_event_cb(self.next_address)
        lv.label(self.next_btn).set_text(lv.SYMBOL.RIGHT)

        self.home_btn = lv.btn(self)
        self.home_btn.set_size(120, 44)
        self.home_btn.align(self, lv.ALIGN.IN_BOTTOM_MID, 0, -18)
        self.home_btn.set_event_cb(self.go_home)
        lbl = lv.label(self.home_btn)
        lbl.set_text("Menu")
        lbl.align(self.home_btn, lv.ALIGN.CENTER, 0, 0)

        self.refresh()

    def refresh(self):
        addr = self.app.get_address(self.index)
        self.index_lbl.set_text("Address #%d" % (self.index + 1))
        self.addr_lbl.set_text(addr)
        self.path_lbl.set_text("Path: %s/0/%d" % (DERIVATION, self.index))
        self.prev_btn.set_state(lv.btn.STATE.INA if self.index == 0 else lv.btn.STATE.REL)

    def prev_address(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        if self.index > 0:
            self.index -= 1
            self.app.address_index = self.index
        self.refresh()

    def next_address(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        self.index += 1
        self.app.address_index = self.index
        self.refresh()

    def go_home(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        self.app.show_main_menu()


class SpecterMenuApp:
    def __init__(self):
        self.root = bip32.HDKey.from_seed(SEED, version=NET["xprv"])
        self.account = self.root.derive(DERIVATION)
        self.xpub = self.account.to_public().to_base58()
        self.address_index = 0
        self.cached_addresses = {}
        self.sig_hex = None
        self.active_screen = None

    def get_address(self, index):
        if index not in self.cached_addresses:
            child = self.account.derive("m/0/%d" % index)
            pub = child.get_public_key()
            self.cached_addresses[index] = p2wpkh_address(pub)
        return self.cached_addresses[index]

    def do_sign_test(self):
        msg_hash = bytes(range(32))
        sig = self.root.sign(msg_hash)
        self.sig_hex = hexlify(sig.serialize()).decode()

    def add_menu_button(self, screen, anchor, text, callback):
        btn = lv.btn(screen)
        btn.set_size(HOR_RES - 2 * PADDING, BTN_H)
        btn.align(anchor, lv.ALIGN.OUT_BOTTOM_MID, 0, BTN_GAP)
        btn.set_event_cb(callback)
        lbl = lv.label(btn)
        lbl.set_text(text)
        lbl.align(btn, lv.ALIGN.CENTER, 0, 0)
        return btn

    def show_main_menu(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return

        scr = lv.obj()
        self.active_screen = scr

        title = lv.label(scr)
        title.set_text("Specter DIY")
        title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 18)

        subtitle = lv.label(scr)
        subtitle.set_long_mode(lv.label.LONG.BREAK)
        subtitle.set_width(HOR_RES - 2 * PADDING)
        subtitle.set_align(lv.label.ALIGN.CENTER)
        subtitle.set_text("STM32F746G-DISCO checkpoint\nPortrait Specter-style menu flow")
        subtitle.align(title, lv.ALIGN.OUT_BOTTOM_MID, 0, 20)

        status = lv.label(scr)
        status.set_text("Touch: %s   Crypto: REAL" % ("YES" if display.touch_ready() else "NO"))
        status.align(subtitle, lv.ALIGN.OUT_BOTTOM_MID, 0, 16)

        btn1 = self.add_menu_button(scr, status, "Wallets", self.show_wallet_menu)
        btn2 = self.add_menu_button(scr, btn1, "Receive address", self.show_addresses)
        btn3 = self.add_menu_button(scr, btn2, "Settings / About", self.show_settings)

        footer = lv.label(scr)
        footer.set_long_mode(lv.label.LONG.BREAK)
        footer.set_width(HOR_RES - 2 * PADDING)
        footer.set_align(lv.label.ALIGN.CENTER)
        footer.set_text("Portrait LVGL mode on top of the proven F746 hardware path")
        footer.align(scr, lv.ALIGN.IN_BOTTOM_MID, 0, -18)

        self._menu_widgets = (title, subtitle, status, btn1, btn2, btn3, footer)
        lv.scr_load(scr)

    def show_wallet_menu(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        scr = lv.obj()
        self.active_screen = scr

        title = lv.label(scr)
        title.set_text("Wallet")
        title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 18)

        body = lv.label(scr)
        body.set_long_mode(lv.label.LONG.BREAK)
        body.set_width(HOR_RES - 2 * PADDING)
        body.set_align(lv.label.ALIGN.CENTER)
        body.set_text("Real HD account loaded from embit\nDerivation: %s" % DERIVATION)
        body.align(title, lv.ALIGN.OUT_BOTTOM_MID, 0, 24)

        btn1 = self.add_menu_button(scr, body, "Show master XPUB", self.show_xpub)
        btn2 = self.add_menu_button(scr, btn1, "Run sign test", self.show_sign_test)

        back = lv.btn(scr)
        back.set_size(120, 44)
        back.align(scr, lv.ALIGN.IN_BOTTOM_MID, 0, -18)
        back.set_event_cb(self.show_main_menu)
        lbl = lv.label(back)
        lbl.set_text(lv.SYMBOL.LEFT + " Menu")
        lbl.align(back, lv.ALIGN.CENTER, 0, 0)

        self._wallet_widgets = (title, body, btn1, btn2, back)
        lv.scr_load(scr)

    def show_addresses(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        AddressScreen(self)

    def show_xpub(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        xpub = self.xpub
        if len(xpub) > 50:
            mid = len(xpub) // 2
            xpub = xpub[:mid] + "\n" + xpub[mid:]
        MessageScreen(self, "Master XPUB", xpub + "\n\nReal account xpub derived on-device.")

    def show_sign_test(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        if self.sig_hex is None:
            self.do_sign_test()
        sig = self.sig_hex
        if len(sig) > 60:
            mid = len(sig) // 2
            sig = sig[:mid] + "\n" + sig[mid:]
        MessageScreen(self, "ECDSA Sign Test", "Signed a test hash with root key.\n\nDER sig:\n%s" % sig)

    def show_settings(self, obj=None, event=None):
        if event is not None and event != lv.EVENT.RELEASED:
            return
        MessageScreen(
            self,
            "Settings / About",
            "Board: STM32F746G-DISCO\nDisplay: 272x480 portrait (logical)\nStyle target: Specter-DIY menu flow\n\nPortrait mode is implemented above the fixed 480x272 panel path.",
        )


def run():
    display.init(False)
    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    app = SpecterMenuApp()
    app.show_main_menu()

    while True:
        display.update(30)
        time.sleep_ms(30)
