import display
import lvgl as lv
import utime as time

from binascii import hexlify


HOR_RES = 272
VER_RES = 480
PADDING = 12


def _set_body(label, text, anchor, y_offset):
    label.set_long_mode(lv.label.LONG.BREAK)
    label.set_width(HOR_RES - 2 * PADDING)
    label.set_align(lv.label.ALIGN.CENTER)
    label.set_text(text)
    label.align(anchor, lv.ALIGN.OUT_BOTTOM_MID, 0, y_offset)


def _screen(title_text, body_text):
    scr = lv.obj()
    scr.set_size(HOR_RES, VER_RES)

    title = lv.label(scr)
    title.set_text(title_text)
    title.align(scr, lv.ALIGN.IN_TOP_MID, 0, 18)

    body = lv.label(scr)
    _set_body(body, body_text, title, 24)

    lv.scr_load(scr)


def run():
    display.init(False)

    try:
        import platform
        import rng
        from app import BaseApp
        from errors import BaseError

        BaseApp.TEMPDIR = '/flash/specter-ext-poc-tmp'
        base_app = BaseApp('/flash/specter-ext-poc')
        tempdir = base_app.tempdir or 'none'
        sample = hexlify(rng.get_random_bytes(12)).decode()

        _screen(
            'Specter external PoC',
            'Loaded external specter-diy modules from sibling checkout.\n\n'
            'BaseError: %s\n'
            'build_type: %s\n'
            'tempdir: %s\n'
            'rng: %s' % (BaseError.NAME, platform.build_type, tempdir, sample),
        )
    except Exception as exc:
        _screen('Specter external PoC', '%s: %s' % (type(exc).__name__, exc))

    while True:
        display.update(30)
        time.sleep_ms(30)
