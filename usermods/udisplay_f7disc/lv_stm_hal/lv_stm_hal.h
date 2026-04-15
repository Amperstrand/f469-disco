#ifndef __LV_STM_F7_HAL_H__
#define __LV_STM_F7_HAL_H__

#ifdef __cplusplus
extern "C" {
#endif

void tft_init(void);
void touchpad_init(void);
void tft_on(void);
void tft_off(void);
void tft_fill_test(void);
bool touchpad_ready(void);

#ifdef __cplusplus
}
#endif

#endif
