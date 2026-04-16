import display
import lvgl as lv
import utime as time

from embit import bip32, ec, script, networks, hashes
from binascii import hexlify

HOR_RES = 480
VER_RES = 272

# Deterministic test seed — BIP32 vector 1 extended to 64 bytes
SEED = bytes(range(16)) + b'\x00' * 48

NET = networks.NETWORKS["test"]
BECH32_HRP = NET["bech32"]
DERIVATION = "m/84h/1h/0h"


def p2wpkh_address(pubkey):
    h = hashes.hash160(pubkey.sec())
    s = script.Script(b"\x00\x14" + h)
    return s.address(NET)


def on_release(callback):
    def cb(obj, event):
        if event == lv.EVENT.RELEASED:
            callback()
    return cb


class SpecterCrypto:
    def __init__(self):
        self.root = bip32.HDKey.from_seed(SEED, version=NET["xprv"])
        self.account = self.root.derive(DERIVATION)
        self.xpub = self.account.to_public().to_base58()
        self.address_index = 0
        self.cached_addresses = {}
        self.sig_hex = None

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

    def message_screen(self, title_text, message, extra_btns=None):
        screen = lv.obj()
        self.title(screen, title_text)
        self.body(screen, message, 48)
        self.button(screen, lv.SYMBOL.LEFT + " Home", 20, 220, 120, 40, self.show_home)
        if extra_btns:
            for text, x, cb in extra_btns:
                self.button(screen, text, x, 220, 120, 40, cb)
        lv.scr_load(screen)

    def show_home(self):
        screen = lv.obj()
        self.title(screen, "Specter DIY F746")

        loaded = "secp256k1 + embit: OK"
        self.body(screen, "Full Bitcoin crypto stack running on F746 hardware.\n%s\nAccount: %s" % (loaded, DERIVATION), 34)

        status = lv.label(screen)
        status.set_text("Crypto: REAL  |  Touch: %s" % ("YES" if display.touch_ready() else "NO"))
        status.align(screen, lv.ALIGN.IN_TOP_MID, 0, 88)

        self.button(screen, "Receive", 25, 116, 135, 54, self.show_receive)
        self.button(screen, "Master XPUB", 172, 116, 135, 54, self.show_xpub)
        self.button(screen, "Sign Test", 319, 116, 136, 54, self.show_sign_test)

        footer = lv.label(screen)
        footer.set_text("Real HD keys from embit + secp256k1 C module")
        footer.align(screen, lv.ALIGN.IN_BOTTOM_MID, 0, -10)

        lv.scr_load(screen)

    def show_receive(self):
        screen = lv.obj()
        self.title(screen, "Receive (testnet)")

        addr = self.get_address(self.address_index)

        index_label = lv.label(screen)
        index_label.set_text("Address #%d" % (self.address_index + 1))
        index_label.align(screen, lv.ALIGN.IN_TOP_MID, 0, 34)

        addr_label = lv.label(screen)
        addr_label.set_long_mode(lv.label.LONG.BREAK)
        addr_label.set_width(430)
        addr_label.set_text(addr)
        addr_label.set_align(lv.label.ALIGN.CENTER)
        addr_label.align(screen, lv.ALIGN.IN_TOP_MID, 0, 60)

        path_label = lv.label(screen)
        path_label.set_text("Path: %s/0/%d" % (DERIVATION, self.address_index))
        path_label.align(screen, lv.ALIGN.IN_BOTTOM_MID, 0, -58)

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

    def show_xpub(self):
        if len(self.xpub) > 50:
            mid = len(self.xpub) // 2
            display_text = self.xpub[:mid] + "\n" + self.xpub[mid:]
        else:
            display_text = self.xpub
        self.message_screen(
            "Master XPUB (testnet)",
            display_text + "\n\nReal account xpub derived on-device.",
        )

    def show_sign_test(self):
        if self.sig_hex is None:
            self.do_sign_test()

        sig_display = self.sig_hex
        if len(sig_display) > 60:
            mid = len(sig_display) // 2
            sig_display = sig_display[:mid] + "\n" + sig_display[mid:]

        self.message_screen(
            "ECDSA Sign Test",
            "Signed a test hash with root key.\n\nDER sig:\n" + sig_display + "\n\nsecp256k1 signing works on F746!",
        )


def run():
    display.init(False)

    th = lv.theme_material_init(210, lv.font_roboto_16)
    lv.theme_set_current(th)

    app = SpecterCrypto()
    app.show_home()

    while True:
        display.update(30)
        time.sleep_ms(30)
