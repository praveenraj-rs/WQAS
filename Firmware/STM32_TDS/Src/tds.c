#include <stm32f4xx.h>
#include <stdint.h>

#include "tds.h"
#include "timer.h"

// PA1 -> ADC1 Channel 1
#define TDS_PIN        1U
#define TDS_CHANNEL    1U

void TDS_ADC_Init(void)
{
    // Enable clocks
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;

    // Configure PA1 as analog mode
    GPIOA->MODER &= ~(0x3 << (TDS_PIN * 2));
    GPIOA->MODER |=  (0x3 << (TDS_PIN * 2));

    // No pull-up / pull-down
    GPIOA->PUPDR &= ~(0x3 << (TDS_PIN * 2));

    // Set sample time for Channel 1
    ADC1->SMPR2 &= ~(0x7 << (3 * TDS_CHANNEL));
    ADC1->SMPR2 |=  (0x7 << (3 * TDS_CHANNEL));   // 480 cycles

    // Configure regular sequence (1 conversion)
    ADC1->SQR1 &= ~ADC_SQR1_L;
    ADC1->SQR3 &= ~ADC_SQR3_SQ1;
    ADC1->SQR3 |= (TDS_CHANNEL << ADC_SQR3_SQ1_Pos);

    // Enable ADC
    ADC1->CR2 |= ADC_CR2_ADON;

    for (volatile int i = 0; i < 1000; i++);
}

uint16_t TDS_ADC_Read(void)
{
    ADC1->CR2 |= ADC_CR2_SWSTART;

    while (!(ADC1->SR & ADC_SR_EOC));

    return (uint16_t)(ADC1->DR & 0x0FFF);
}

float TDS_GetVoltage(void)
{
    uint32_t adc_sum = 0;
    const int samples = 30;

    for (int i = 0; i < samples; i++)
    {
        adc_sum += TDS_ADC_Read();
        TIM3_Delay_ms(5);
    }

    float adc_avg = (float)adc_sum / samples;

    return (adc_avg / ADC_RESOLUTION) * VREF;
}

float TDS_GetPPM(float temperature)
{
    float voltage = TDS_GetVoltage();

    // Cubic polynomial conversion
    float ecValue =
        (133.42f * voltage * voltage * voltage) -
        (255.86f * voltage * voltage) +
        (857.39f * voltage);

    ecValue *= K_VALUE;

    // Temperature compensation
    float ecValue25 =
        ecValue / (1.0f + 0.02f * (temperature - 25.0f));

    // Convert EC to TDS
    float tdsValue = ecValue25 * TDS_FACTOR;

    return tdsValue;
}
