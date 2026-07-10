import os

simulator = False
version = 'unknown'
i2c = None
bootloader_locked = None
build_type = 'f7-specter-external-poc'


def maybe_mkdir(path):
    try:
        os.mkdir(path)
    except OSError:
        pass
    try:
        os.sync()
    except OSError:
        pass


def delete_recursively(path, include_self=False):
    if path is None:
        raise RuntimeError('Path is not specified')
    path = path.rstrip('/')
    for entry in os.ilistdir(path):
        name = entry[0]
        if name in ['.', '..']:
            continue
        target = '%s/%s' % (path, name)
        if entry[1] == 0x8000:
            os.remove(target)
        elif entry[1] == 0x4000:
            delete_recursively(target, include_self=True)
    if include_self:
        os.rmdir(path)
