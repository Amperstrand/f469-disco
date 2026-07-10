import os

include('f7_display.py')

SPECTER_DIY_DIR = os.path.abspath(os.environ.get('SPECTER_DIY_DIR', '../../specter-diy'))

freeze(SPECTER_DIY_DIR + '/src', ('app.py', 'errors.py', 'rng.py'))
freeze('../tests/f7_specter_external_support', 'platform.py')
freeze('../tests', 'f7_specter_external_poc.py')
freeze('f7_specter_external_poc_boot', 'main.py')
