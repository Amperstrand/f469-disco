#include "py/obj.h"
#include "py/runtime.h"
#include "py/builtin.h"

#include "lvgl.h"
#include "lv_stm_hal.h"

STATIC mp_obj_t display_init(void) {
    lv_init();
    tft_init();
    touchpad_init();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(display_init_obj, display_init);

STATIC mp_obj_t display_update(mp_obj_t dt_obj) {
    uint32_t dt = mp_obj_get_int(dt_obj);
    lv_tick_inc(dt);
    lv_task_handler();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(display_update_obj, display_update);

STATIC mp_obj_t display_on(void) {
    tft_on();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(display_on_obj, display_on);

STATIC mp_obj_t display_off(void) {
    tft_off();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(display_off_obj, display_off);

STATIC mp_obj_t display_fill_test(void) {
    tft_fill_test();
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(display_fill_test_obj, display_fill_test);

STATIC mp_obj_t display_set_rotation(mp_obj_t rot_obj) {
    int rot = mp_obj_get_int(rot_obj);
    if (rot < 0 || rot > 1) {
        mp_raise_ValueError("Rotation can be 0 or 1");
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(display_set_rotation_obj, display_set_rotation);

STATIC mp_obj_t display_touch_ready(void) {
    return mp_obj_new_bool(touchpad_ready());
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(display_touch_ready_obj, display_touch_ready);

STATIC const mp_rom_map_elem_t display_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_display) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&display_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_update), MP_ROM_PTR(&display_update_obj) },
    { MP_ROM_QSTR(MP_QSTR_on), MP_ROM_PTR(&display_on_obj) },
    { MP_ROM_QSTR(MP_QSTR_off), MP_ROM_PTR(&display_off_obj) },
    { MP_ROM_QSTR(MP_QSTR_fill_test), MP_ROM_PTR(&display_fill_test_obj) },
    { MP_ROM_QSTR(MP_QSTR_touch_ready), MP_ROM_PTR(&display_touch_ready_obj) },
    { MP_ROM_QSTR(MP_QSTR_set_rotation), MP_ROM_PTR(&display_set_rotation_obj) },
};
STATIC MP_DEFINE_CONST_DICT(display_module_globals, display_module_globals_table);

const mp_obj_module_t display_user_cmodule = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&display_module_globals,
};

#include "../udisplay_f469/lv_mpy_example.c"

MP_REGISTER_MODULE(MP_QSTR_udisplay, display_user_cmodule, MODULE_DISPLAY_ENABLED);
MP_REGISTER_MODULE(MP_QSTR_lvgl, mp_module_lvgl, MODULE_DISPLAY_ENABLED);
