from udisplay import update, on, off, set_rotation, fill_test, touch_ready


def init(autoupdate=True):
    import udisplay

    udisplay.init()
    if autoupdate:
        import micropython
        import pyb

        def schedule(_):
            try:
                micropython.schedule(udisplay.update, 30)
            except RuntimeError:
                return

        timer = pyb.Timer(4)
        timer.init(freq=30)
        timer.callback(schedule)
