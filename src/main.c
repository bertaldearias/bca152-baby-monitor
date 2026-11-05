
#include <stdio.h>
#include <stdint.h>
#include "esp_log.h"
#include "esp_err.h"
#include "driver/i2s_std.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_check.h"

#define MIC_BCLK_GPIO GPIO_NUM_4
#define MIC_WS_GPIO   GPIO_NUM_5
#define MIC_DATA_GPIO GPIO_NUM_6

#define SAMPLE_RATE 16000
#define AUDIO_SAMPLES 512

static const char *TAG = "BABY_MONITOR";
static i2s_chan_handle_t rx_channel = NULL;

static esp_err_t microphone_init(void)
{
    i2s_chan_config_t channel_config =
        I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);

    ESP_RETURN_ON_ERROR(
        i2s_new_channel(&channel_config, NULL, &rx_channel),
        TAG,
        "Cannot create I2S channel"
    );

    i2s_std_config_t standard_config = {
        .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(SAMPLE_RATE),
        .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(
            I2S_DATA_BIT_WIDTH_32BIT,
            I2S_SLOT_MODE_MONO
        ),
        .gpio_cfg = {
            .mclk = I2S_GPIO_UNUSED,
            .bclk = MIC_BCLK_GPIO,
            .ws = MIC_WS_GPIO,
            .dout = I2S_GPIO_UNUSED,
            .din = MIC_DATA_GPIO,
            .invert_flags = {
                .mclk_inv = false,
                .bclk_inv = false,
                .ws_inv = false
            }
        }
    };

    standard_config.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;

    ESP_RETURN_ON_ERROR(
        i2s_channel_init_std_mode(rx_channel, &standard_config),
        TAG,
        "Cannot initialize I2S"
    );

    return i2s_channel_enable(rx_channel);
}

static void microphone_task(void *parameter)
{
    int32_t samples[AUDIO_SAMPLES];
    size_t bytes_read = 0;

    while (true) {
        esp_err_t result = i2s_channel_read(
            rx_channel,
            samples,
            sizeof(samples),
            &bytes_read,
            pdMS_TO_TICKS(1000)
        );

        if (result == ESP_OK && bytes_read > 0) {
            size_t count = bytes_read / sizeof(int32_t);
            int32_t peak = 0;

            for (size_t i = 0; i < count; i++) {
                int32_t sample = samples[i] >> 8;
                int32_t magnitude =
                    sample == INT32_MIN ? INT32_MAX :
                    (sample < 0 ? -sample : sample);

                if (magnitude > peak) {
                    peak = magnitude;
                }
            }

            ESP_LOGI(TAG, "Audio captured: %u samples, peak: %ld",
                     (unsigned int)count, (long)peak);
        } else if (result != ESP_ERR_TIMEOUT) {
            ESP_LOGE(TAG, "Microphone read failed: %s",
                     esp_err_to_name(result));
            vTaskDelay(pdMS_TO_TICKS(1000));
        }
    }
}

void app_main(void)
{
    ESP_LOGI(TAG, "BCA152 Baby Monitor starting...");

    esp_err_t result = microphone_init();

    if (result != ESP_OK) {
        ESP_LOGE(TAG, "Microphone initialization failed");
        return;
    }

    xTaskCreate(
        microphone_task,
        "microphone_task",
        4096,
        NULL,
        5,
        NULL
    );
}
