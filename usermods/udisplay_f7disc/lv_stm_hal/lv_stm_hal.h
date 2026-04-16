#ifndef __LV_STM_F7_HAL_H__
#define __LV_STM_F7_HAL_H__

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void tft_init(void);
void touchpad_init(void);
void tft_on(void);
void tft_off(void);
void tft_fill_test(void);
bool touchpad_ready(void);
bool touchpad_get_point(uint16_t *x, uint16_t *y, bool *pressed);

#ifdef __cplusplus
}
#endif

#endif
