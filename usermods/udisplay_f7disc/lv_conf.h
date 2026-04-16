#include "../udisplay_f469/lv_conf.h"
#undef LV_HOR_RES_MAX
#undef LV_VER_RES_MAX
#define LV_HOR_RES_MAX (272)
#define LV_VER_RES_MAX (480)

#ifdef CRYPTO_BUILD
#undef LV_USE_ANIMATION
#define LV_USE_ANIMATION        0
#undef LV_USE_SHADOW
#define LV_USE_SHADOW           0
#undef LV_USE_FILESYSTEM
#define LV_USE_FILESYSTEM       0
#undef LV_USE_LOG
#define LV_USE_LOG              0
#undef LV_IMG_CF_INDEXED
#define LV_IMG_CF_INDEXED       0
#undef LV_IMG_CF_ALPHA
#define LV_IMG_CF_ALPHA         0
#undef LV_THEME_LIVE_UPDATE
#define LV_THEME_LIVE_UPDATE    0
#undef LV_USE_THEME_TEMPL
#define LV_USE_THEME_TEMPL      0
#undef LV_USE_THEME_DEFAULT
#define LV_USE_THEME_DEFAULT    0
#undef LV_USE_THEME_ALIEN
#define LV_USE_THEME_ALIEN      0
#undef LV_USE_THEME_NIGHT
#define LV_USE_THEME_NIGHT      0
#undef LV_USE_THEME_MONO
#define LV_USE_THEME_MONO       0
#undef LV_USE_THEME_ZEN
#define LV_USE_THEME_ZEN        0
#undef LV_USE_THEME_NEMO
#define LV_USE_THEME_NEMO       0
#undef LV_FONT_ROBOTO_12
#define LV_FONT_ROBOTO_12       0
#undef LV_FONT_ROBOTO_22
#define LV_FONT_ROBOTO_22       0
#undef LV_FONT_ROBOTO_28
#define LV_FONT_ROBOTO_28       0
#undef LV_FONT_UNSCII_8
#define LV_FONT_UNSCII_8        0
#undef LV_USE_ARC
#define LV_USE_ARC              0
#undef LV_USE_BAR
#define LV_USE_BAR              0
#undef LV_BTN_INK_EFFECT
#define LV_BTN_INK_EFFECT       0
#undef LV_USE_BTNM
#define LV_USE_BTNM             0
#undef LV_USE_CALENDAR
#define LV_USE_CALENDAR         0
#undef LV_USE_CANVAS
#define LV_USE_CANVAS           0
#undef LV_USE_CB
#define LV_USE_CB               0
#undef LV_USE_CHART
#define LV_USE_CHART            0
#undef LV_USE_DDLIST
#define LV_USE_DDLIST           0
#undef LV_USE_GAUGE
#define LV_USE_GAUGE            0
#undef LV_USE_IMG
#define LV_USE_IMG              0
#undef LV_USE_IMGBTN
#define LV_USE_IMGBTN           0
#undef LV_USE_KB
#define LV_USE_KB               0
#undef LV_USE_LED
#define LV_USE_LED              0
#undef LV_USE_LINE
#define LV_USE_LINE             0
#undef LV_USE_LIST
#define LV_USE_LIST             0
#undef LV_USE_LMETER
#define LV_USE_LMETER           0
#undef LV_USE_MBOX
#define LV_USE_MBOX             0
#undef LV_USE_PRELOAD
#define LV_USE_PRELOAD          0
#undef LV_USE_ROLLER
#define LV_USE_ROLLER           0
#undef LV_USE_SLIDER
#define LV_USE_SLIDER           0
#undef LV_USE_SPINBOX
#define LV_USE_SPINBOX          0
#undef LV_USE_SW
#define LV_USE_SW               0
#undef LV_USE_TA
#define LV_USE_TA               0
#undef LV_USE_TABLE
#define LV_USE_TABLE            0
#undef LV_USE_TABVIEW
#define LV_USE_TABVIEW          0
#undef LV_USE_TILEVIEW
#define LV_USE_TILEVIEW         0
#undef LV_USE_WIN
#define LV_USE_WIN              0
#endif
