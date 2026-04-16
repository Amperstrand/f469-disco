#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#include STM32_HAL_H

#include "py/runtime.h"
#include "py/mphal.h"
#include "i2c.h"

#include "lv_conf.h"
#include "lvgl.h"
#include "lv_stm_hal.h"

#define RK043FN48H_WIDTH        ((uint16_t)480)
#define RK043FN48H_HEIGHT       ((uint16_t)272)
#define RK043FN48H_HSYNC        ((uint16_t)41)
#define RK043FN48H_HBP          ((uint16_t)13)
#define RK043FN48H_HFP          ((uint16_t)32)
#define RK043FN48H_VSYNC        ((uint16_t)10)
#define RK043FN48H_VBP          ((uint16_t)2)
#define RK043FN48H_VFP          ((uint16_t)2)
#define RK043FN48H_FREQUENCY_DIVIDER 5

#define LCD_DISP_PIN            GPIO_PIN_12
#define LCD_DISP_GPIO_PORT      GPIOI
#define LCD_BL_CTRL_PIN         GPIO_PIN_3
#define LCD_BL_CTRL_GPIO_PORT   GPIOK

#define FT5336_ADDR             ((uint16_t)0x38)
#define FT5336_TD_STAT_REG      ((uint8_t)0x02)
#define FT5336_P1_XH_REG        ((uint8_t)0x03)
#define FT5336_GMODE_REG        ((uint8_t)0xA4)
#define FT5336_GMODE_POLLING    ((uint8_t)0x00)
#define FT5336_CHIP_ID_REG      ((uint8_t)0xA8)
#define FT5336_CHIP_ID_VAL      ((uint8_t)0x51)
#define FT5336_MAX_TOUCH        ((uint8_t)5)

#define PHYS_HOR_RES            RK043FN48H_WIDTH
#define PHYS_VER_RES            RK043FN48H_HEIGHT

static LTDC_HandleTypeDef hltdc;
static DMA2D_HandleTypeDef hdma2d;
static lv_disp_drv_t disp_drv;
static lv_disp_buf_t disp_buf;
static lv_color_t *framebuffer;
static lv_color_t *draw_buf;
static I2C_HandleTypeDef *touch_hi2c;
static bool display_ready;
static bool touch_ready;

static bool dma2d_ready;

static inline uint32_t phys_index_from_logical(int32_t lx, int32_t ly) {
    int32_t px = (int32_t)PHYS_HOR_RES - 1 - ly;
    int32_t py = lx;
    return (uint32_t)(py * PHYS_HOR_RES + px);
}

void tft_on(void) {
    HAL_GPIO_WritePin(LCD_DISP_GPIO_PORT, LCD_DISP_PIN, GPIO_PIN_SET);
    HAL_GPIO_WritePin(LCD_BL_CTRL_GPIO_PORT, LCD_BL_CTRL_PIN, GPIO_PIN_SET);
    __HAL_LTDC_ENABLE(&hltdc);
}

void tft_off(void) {
    __HAL_LTDC_DISABLE(&hltdc);
    HAL_GPIO_WritePin(LCD_DISP_GPIO_PORT, LCD_DISP_PIN, GPIO_PIN_RESET);
    HAL_GPIO_WritePin(LCD_BL_CTRL_GPIO_PORT, LCD_BL_CTRL_PIN, GPIO_PIN_RESET);
}

static void tft_flush(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p) {
    int32_t ax1 = area->x1;
    int32_t ay1 = area->y1;
    int32_t ax2 = area->x2;
    int32_t ay2 = area->y2;

    int32_t x1 = ax1 < 0 ? 0 : ax1;
    int32_t y1 = ay1 < 0 ? 0 : ay1;
    int32_t x2 = ax2 >= LV_HOR_RES_MAX ? LV_HOR_RES_MAX - 1 : ax2;
    int32_t y2 = ay2 >= LV_VER_RES_MAX ? LV_VER_RES_MAX - 1 : ay2;

    if (x1 > x2 || y1 > y2) {
        lv_disp_flush_ready(drv);
        return;
    }

    int32_t src_w = ax2 - ax1 + 1;
    const lv_color_t *base = color_p + (y1 - ay1) * src_w + (x1 - ax1);

    for (int32_t lx = x1; lx <= x2; lx++) {
        int32_t px = (int32_t)PHYS_HOR_RES - 1 - y1;
        int32_t py = lx;
        uint32_t dst_idx = (uint32_t)(py * PHYS_HOR_RES + px);
        const lv_color_t *src = base + (lx - x1);

        for (int32_t ly = y1; ly <= y2; ly++) {
            framebuffer[dst_idx] = *src;
            dst_idx--;
            src += src_w;
        }
    }

    uint32_t fb_size = sizeof(lv_color_t) * PHYS_HOR_RES * PHYS_VER_RES;
    SCB_CleanDCache_by_Addr((uint32_t *)((uintptr_t)framebuffer & ~(uintptr_t)31), (fb_size + 31) & ~(uint32_t)31);
    lv_disp_flush_ready(drv);
}

void HAL_DMA2D_MspInit(DMA2D_HandleTypeDef *instance) {
    (void)instance;
    __HAL_RCC_DMA2D_CLK_ENABLE();
}

void HAL_LTDC_MspInit(LTDC_HandleTypeDef *instance) {
    (void)instance;
    GPIO_InitTypeDef gpio_init = {0};

    __HAL_RCC_LTDC_CLK_ENABLE();
    __HAL_RCC_GPIOE_CLK_ENABLE();
    __HAL_RCC_GPIOG_CLK_ENABLE();
    __HAL_RCC_GPIOI_CLK_ENABLE();
    __HAL_RCC_GPIOJ_CLK_ENABLE();
    __HAL_RCC_GPIOK_CLK_ENABLE();

    gpio_init.Pin = GPIO_PIN_4;
    gpio_init.Mode = GPIO_MODE_AF_PP;
    gpio_init.Pull = GPIO_NOPULL;
    gpio_init.Speed = GPIO_SPEED_FAST;
    gpio_init.Alternate = GPIO_AF14_LTDC;
    HAL_GPIO_Init(GPIOE, &gpio_init);

    gpio_init.Pin = GPIO_PIN_12;
    gpio_init.Alternate = GPIO_AF9_LTDC;
    HAL_GPIO_Init(GPIOG, &gpio_init);

    gpio_init.Pin = GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_14 | GPIO_PIN_15;
    gpio_init.Alternate = GPIO_AF14_LTDC;
    HAL_GPIO_Init(GPIOI, &gpio_init);

    gpio_init.Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_3 |
        GPIO_PIN_4 | GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7 |
        GPIO_PIN_8 | GPIO_PIN_9 | GPIO_PIN_10 | GPIO_PIN_11 |
        GPIO_PIN_13 | GPIO_PIN_14 | GPIO_PIN_15;
    gpio_init.Alternate = GPIO_AF14_LTDC;
    HAL_GPIO_Init(GPIOJ, &gpio_init);

    gpio_init.Pin = GPIO_PIN_0 | GPIO_PIN_1 | GPIO_PIN_2 | GPIO_PIN_4 |
        GPIO_PIN_5 | GPIO_PIN_6 | GPIO_PIN_7;
    gpio_init.Alternate = GPIO_AF14_LTDC;
    HAL_GPIO_Init(GPIOK, &gpio_init);

    gpio_init.Pin = LCD_DISP_PIN;
    gpio_init.Mode = GPIO_MODE_OUTPUT_PP;
    gpio_init.Pull = GPIO_NOPULL;
    gpio_init.Speed = GPIO_SPEED_FAST;
    HAL_GPIO_Init(LCD_DISP_GPIO_PORT, &gpio_init);

    gpio_init.Pin = LCD_BL_CTRL_PIN;
    HAL_GPIO_Init(LCD_BL_CTRL_GPIO_PORT, &gpio_init);
}

static void *alloc_aligned_rooted(size_t size, void **root_slot) {
    uint8_t *raw = m_malloc(size + 31);
    *root_slot = raw;
    uintptr_t aligned = ((uintptr_t)raw + 31) & ~(uintptr_t)31;
    return (void *)aligned;
}

void tft_init(void) {
    if (display_ready) {
        return;
    }

    framebuffer = alloc_aligned_rooted(sizeof(lv_color_t) * PHYS_HOR_RES * PHYS_VER_RES, &MP_STATE_PORT(display_fb_raw));
    draw_buf = alloc_aligned_rooted(sizeof(lv_color_t) * LV_HOR_RES_MAX * 20, &MP_STATE_PORT(display_drawbuf_raw));

    memset(framebuffer, 0x00, sizeof(lv_color_t) * PHYS_HOR_RES * PHYS_VER_RES);

    RCC_PeriphCLKInitTypeDef periph_clk = {0};
    periph_clk.PeriphClockSelection = RCC_PERIPHCLK_LTDC;
    periph_clk.PLLSAI.PLLSAIN = 192;
    periph_clk.PLLSAI.PLLSAIR = RK043FN48H_FREQUENCY_DIVIDER;
    periph_clk.PLLSAIDivR = RCC_PLLSAIDIVR_4;
    HAL_RCCEx_PeriphCLKConfig(&periph_clk);

    memset(&hltdc, 0, sizeof(hltdc));
    hltdc.Instance = LTDC;
    hltdc.Init.HSPolarity = LTDC_HSPOLARITY_AL;
    hltdc.Init.VSPolarity = LTDC_VSPOLARITY_AL;
    hltdc.Init.DEPolarity = LTDC_DEPOLARITY_AL;
    hltdc.Init.PCPolarity = LTDC_PCPOLARITY_IPC;
    hltdc.Init.HorizontalSync = RK043FN48H_HSYNC - 1;
    hltdc.Init.VerticalSync = RK043FN48H_VSYNC - 1;
    hltdc.Init.AccumulatedHBP = RK043FN48H_HSYNC + RK043FN48H_HBP - 1;
    hltdc.Init.AccumulatedVBP = RK043FN48H_VSYNC + RK043FN48H_VBP - 1;
    hltdc.Init.AccumulatedActiveW = RK043FN48H_WIDTH + RK043FN48H_HSYNC + RK043FN48H_HBP - 1;
    hltdc.Init.AccumulatedActiveH = RK043FN48H_HEIGHT + RK043FN48H_VSYNC + RK043FN48H_VBP - 1;
    hltdc.Init.TotalWidth = RK043FN48H_WIDTH + RK043FN48H_HSYNC + RK043FN48H_HBP + RK043FN48H_HFP - 1;
    hltdc.Init.TotalHeigh = RK043FN48H_HEIGHT + RK043FN48H_VSYNC + RK043FN48H_VBP + RK043FN48H_VFP - 1;
    hltdc.Init.Backcolor.Blue = 0;
    hltdc.Init.Backcolor.Green = 0;
    hltdc.Init.Backcolor.Red = 0;

    HAL_LTDC_Init(&hltdc);

    LTDC_LayerCfgTypeDef layer_cfg = {0};
    layer_cfg.WindowX0 = 0;
    layer_cfg.WindowX1 = PHYS_HOR_RES;
    layer_cfg.WindowY0 = 0;
    layer_cfg.WindowY1 = PHYS_VER_RES;
    layer_cfg.PixelFormat = LTDC_PIXEL_FORMAT_ARGB8888;
    layer_cfg.FBStartAdress = (uint32_t)framebuffer;
    layer_cfg.Alpha = 255;
    layer_cfg.Alpha0 = 0;
    layer_cfg.Backcolor.Blue = 0;
    layer_cfg.Backcolor.Green = 0;
    layer_cfg.Backcolor.Red = 0;
    layer_cfg.BlendingFactor1 = LTDC_BLENDING_FACTOR1_CA;
    layer_cfg.BlendingFactor2 = LTDC_BLENDING_FACTOR2_CA;
    layer_cfg.ImageWidth = PHYS_HOR_RES;
    layer_cfg.ImageHeight = PHYS_VER_RES;
    HAL_LTDC_ConfigLayer(&hltdc, &layer_cfg, 1);

    memset(&hdma2d, 0, sizeof(hdma2d));
    hdma2d.Instance = DMA2D;
    hdma2d.Init.Mode = DMA2D_M2M;
    hdma2d.Init.ColorMode = DMA2D_OUTPUT_ARGB8888;
    hdma2d.Init.OutputOffset = 0;
    if (HAL_DMA2D_Init(&hdma2d) == HAL_OK) {
        dma2d_ready = true;
    }

    tft_on();
    SCB_CleanDCache();

    lv_disp_buf_init(&disp_buf, draw_buf, NULL, LV_HOR_RES_MAX * 20);
    lv_disp_drv_init(&disp_drv);
    disp_drv.buffer = &disp_buf;
    disp_drv.flush_cb = tft_flush;
    lv_disp_drv_register(&disp_drv);

    display_ready = true;
}

static int ft5336_read(uint8_t reg, uint8_t *dest, size_t len) {
    HAL_StatusTypeDef status = HAL_I2C_Mem_Read(touch_hi2c,
        FT5336_ADDR << 1, reg, I2C_MEMADD_SIZE_8BIT,
        dest, len, 100);
    return (status == HAL_OK) ? 0 : -1;
}

static int ft5336_write(uint8_t reg, uint8_t val) {
    HAL_StatusTypeDef status = HAL_I2C_Mem_Write(touch_hi2c,
        FT5336_ADDR << 1, reg, I2C_MEMADD_SIZE_8BIT,
        &val, 1, 100);
    return (status == HAL_OK) ? 0 : -1;
}

static bool touchpad_read(lv_indev_drv_t *drv, lv_indev_data_t *data) {
    (void)drv;
    static int16_t last_x = 0;
    static int16_t last_y = 0;

    if (!touch_ready) {
        data->point.x = last_x;
        data->point.y = last_y;
        data->state = LV_INDEV_STATE_REL;
        return false;
    }

    uint8_t touches = 0;
    if (ft5336_read(FT5336_TD_STAT_REG, &touches, 1) != 0 || touches == 0 || touches > FT5336_MAX_TOUCH) {
        data->point.x = last_x;
        data->point.y = last_y;
        data->state = LV_INDEV_STATE_REL;
        return false;
    }

    uint8_t raw[4] = {0};
    if (ft5336_read(FT5336_P1_XH_REG, raw, sizeof(raw)) != 0) {
        data->point.x = last_x;
        data->point.y = last_y;
        data->state = LV_INDEV_STATE_REL;
        return false;
    }

    uint16_t raw_x = (((uint16_t)raw[0] & 0x0F) << 8) | raw[1];
    uint16_t raw_y = (((uint16_t)raw[2] & 0x0F) << 8) | raw[3];

    int16_t x = (int16_t)raw_y;
    int16_t y = (int16_t)((int32_t)PHYS_HOR_RES - 1 - (int32_t)raw_x);
    if (x < 0) {
        x = 0;
    }
    if (x >= LV_HOR_RES_MAX) {
        x = LV_HOR_RES_MAX - 1;
    }
    if (y < 0) {
        y = 0;
    }
    if (y >= LV_VER_RES_MAX) {
        y = LV_VER_RES_MAX - 1;
    }

    last_x = x;
    last_y = y;
    data->point.x = x;
    data->point.y = y;
    data->state = LV_INDEV_STATE_PR;
    return false;
}

static void dma2d_fill_phys_rect(uint32_t color, int32_t x, int32_t y, int32_t w, int32_t h) {
    if (!dma2d_ready) {
        uint32_t *fb = (uint32_t *)framebuffer;
        for (int32_t row = y; row < y + h; row++) {
            for (int32_t col = x; col < x + w; col++) {
                fb[row * PHYS_HOR_RES + col] = color;
            }
        }
        return;
    }

    SCB_CleanDCache();
    hdma2d.Init.Mode = DMA2D_R2M;
    hdma2d.Init.ColorMode = DMA2D_OUTPUT_ARGB8888;
    hdma2d.Init.OutputOffset = (uint32_t)(PHYS_HOR_RES - w);
    HAL_DMA2D_Init(&hdma2d);
    HAL_DMA2D_Start(&hdma2d,
        color,
        (uint32_t)(framebuffer + y * PHYS_HOR_RES + x),
        (uint32_t)w,
        (uint32_t)h);
    HAL_DMA2D_PollForTransfer(&hdma2d, 100);
}

void tft_fill_test(void) {
    if (!framebuffer) {
        return;
    }

    SCB_CleanInvalidateDCache();
    memset(framebuffer, 0x00, sizeof(lv_color_t) * PHYS_HOR_RES * PHYS_VER_RES);

    int32_t hw = PHYS_HOR_RES / 2;
    int32_t hh = PHYS_VER_RES / 2;

    dma2d_fill_phys_rect(0xFFFF0000, 0, 0, hw, hh);
    dma2d_fill_phys_rect(0xFF00FF00, hw, 0, hw, hh);
    dma2d_fill_phys_rect(0xFF0000FF, 0, hh, hw, hh);
    dma2d_fill_phys_rect(0xFFFFFF00, hw, hh, hw, hh);

    SCB_CleanDCache();
}

void touchpad_init(void) {
    if (touch_ready) {
        return;
    }

    touch_hi2c = &I2CHandle3;
    pyb_i2c_init_freq(&pyb_i2c_obj[2], 400000);

    uint8_t chip_id = 0;
    ft5336_read(FT5336_CHIP_ID_REG, &chip_id, 1);
    if (chip_id == FT5336_CHIP_ID_VAL) {
        touch_ready = true;
    }

    lv_indev_drv_t indev_drv;
    lv_indev_drv_init(&indev_drv);
    indev_drv.type = LV_INDEV_TYPE_POINTER;
    indev_drv.read_cb = touchpad_read;
    lv_indev_drv_register(&indev_drv);
}

bool touchpad_ready(void) {
    return touch_ready;
}

bool touchpad_get_point(uint16_t *x, uint16_t *y, bool *pressed) {
    if (!touch_ready) {
        *x = 0;
        *y = 0;
        *pressed = false;
        return false;
    }

    uint8_t touches = 0;
    if (ft5336_read(FT5336_TD_STAT_REG, &touches, 1) != 0 || touches == 0 || touches > FT5336_MAX_TOUCH) {
        *pressed = false;
        return true;
    }

    uint8_t raw[4];
    if (ft5336_read(FT5336_P1_XH_REG, raw, sizeof(raw)) != 0) {
        *pressed = false;
        return false;
    }

    uint16_t raw_x = (uint16_t)(((raw[0] & 0x0F) << 8) | raw[1]);
    uint16_t raw_y = (uint16_t)(((raw[2] & 0x0F) << 8) | raw[3]);
    *x = raw_y;
    *y = (uint16_t)((int32_t)PHYS_HOR_RES - 1 - (int32_t)raw_x);
    *pressed = true;
    return true;
}
