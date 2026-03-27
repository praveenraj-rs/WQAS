#include <stm32f4xx.h>
#include <stdint.h>

#include "config.h"
#include "timer.h"
#include "ds18b20.h"

// --- CONFIG ---
#define ONEWIRE_PORT GPIOA
#define ONEWIRE_PIN  1   // PA1

// --- DWT DELAY ---
void DWT_Delay_Init(void) {
    CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
    DWT->CYCCNT = 0;
    DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
}

void DWT_Delay_us(uint32_t us) {
    uint32_t cycles = (SysClk / 1000000) * us;
    uint32_t start = DWT->CYCCNT;

    while ((DWT->CYCCNT - start) < cycles);
}

// --- GPIO CONTROL ---
// INPUT (floating)
void Input_Pin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin) {
    uint8_t pos = __builtin_ctz(GPIO_Pin);

    // MODER = 00 (input)
    GPIOx->MODER &= ~(3 << (pos * 2));

    // No pull-up / pull-down
    GPIOx->PUPDR &= ~(3 << (pos * 2));
}

// OUTPUT (push-pull)
void Output_Pin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin) {
    uint8_t pos = __builtin_ctz(GPIO_Pin);

    // MODER = 01 (output)
    GPIOx->MODER &= ~(3 << (pos * 2));
    GPIOx->MODER |=  (1 << (pos * 2));

    // Push-pull
    GPIOx->OTYPER &= ~(1 << pos);

    // Medium speed
    GPIOx->OSPEEDR |= (1 << (pos * 2));

    // No pull-up/pull-down
    GPIOx->PUPDR &= ~(3 << (pos * 2));
}

// --- ONEWIRE ---
// Reset
uint8_t Onewire_Reset(void) {
    uint8_t present = 0;

    Output_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
    ONEWIRE_PORT->BSRR = (1 << (ONEWIRE_PIN + 16)); // LOW
    DWT_Delay_us(480);

    Input_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
    DWT_Delay_us(60);

    if (!(ONEWIRE_PORT->IDR & (1 << ONEWIRE_PIN))) {
        present = 1;
    }

    DWT_Delay_us(420);
    return present;
}

// Write byte
void Onewire_Write(uint8_t data) {
    for (int i = 0; i < 8; i++) {

        Output_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
        ONEWIRE_PORT->BSRR = (1 << (ONEWIRE_PIN + 16)); // LOW

        if (data & (1 << i)) {
            DWT_Delay_us(6);
            Input_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
            DWT_Delay_us(64);
        } else {
            DWT_Delay_us(60);
            Input_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
            DWT_Delay_us(10);
        }
    }
}

// Read byte
uint8_t Onewire_Read(void) {
    uint8_t value = 0;

    for (int i = 0; i < 8; i++) {

        Output_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
        ONEWIRE_PORT->BSRR = (1 << (ONEWIRE_PIN + 16)); // LOW
        DWT_Delay_us(6);

        Input_Pin(ONEWIRE_PORT, (1 << ONEWIRE_PIN));
        DWT_Delay_us(9);

        if (ONEWIRE_PORT->IDR & (1 << ONEWIRE_PIN)) {
            value |= (1 << i);
        }

        DWT_Delay_us(55);
    }

    return value;
}

// --- DS18B20 ---
float DS18B20_Read_Temp(void) {
    uint8_t lsb, msb;
    int16_t raw;

    Onewire_Reset();
    Onewire_Write(0xCC);  // Skip ROM
    Onewire_Write(0x44);  // Convert T

    // ~750ms delay (approx for 84MHz)
    TIM3_Delay_ms(750);

    Onewire_Reset();
    Onewire_Write(0xCC);
    Onewire_Write(0xBE);

    lsb = Onewire_Read();
    msb = Onewire_Read();

    raw = (msb << 8) | lsb;

    return (float)raw / 16.0;
}
