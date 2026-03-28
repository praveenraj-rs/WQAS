#include <stm32f4xx.h>
#include <stdint.h>

#include "config.h"
#include "timer.h"
#include "uart.h"

#define TURBIDITY_PIN 1U   		// PA1 for Turbidity
#define TURBIDITY_CHANNEL 1U   	// ADC Channel 1 for PA1

void Turbidity_ADC_Init(void)
{
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;      // GPIOA clock enable
    RCC->APB2ENR |= RCC_APB2ENR_ADC1EN;       // ADC1 clock enable

    // Configure PA1 as analog
    GPIOA->MODER &= ~(0x3 << (TURBIDITY_PIN * 2));
    GPIOA->MODER |=  (0x3 << (TURBIDITY_PIN * 2));

    GPIOA->PUPDR &= ~(0x3 << (TURBIDITY_PIN * 2)); // No pull-up/pull-down

    // Sample time for Channel 1
    ADC1->SMPR2 &= ~(0x7 << (3 * TURBIDITY_CHANNEL));
    ADC1->SMPR2 |=  (0x7 << (3 * TURBIDITY_CHANNEL)); // 480 cycles (safe)

    // Regular sequence: SQ1 = Channel 1
    ADC1->SQR1 &= ~ADC_SQR1_L;    // 1 conversion
    ADC1->SQR3 &= ~ADC_SQR3_SQ1;
    ADC1->SQR3 |= (TURBIDITY_CHANNEL << ADC_SQR3_SQ1_Pos);

    // ADC ON
    ADC1->CR2 |= ADC_CR2_ADON;

    for (volatile int i = 0; i < 1000; i++) {}
}

uint32_t Turbidity_ADC_Read(void)
{
    ADC1->CR2 |= ADC_CR2_SWSTART;          // Start conversion
    while (!(ADC1->SR & ADC_SR_EOC)) {}    // Wait until done
    return (ADC1->DR & 0xFFF);             // Read 12-bit ADC result
}

uint32_t Turbidity_ADC_NTU(void)
{
    uint32_t adc = 0;
    int iteration = 16;

    for (int i = 0; i < iteration; i++)
    {
        adc += Turbidity_ADC_Read();
    }

    adc = adc / iteration;

    return adc;
}

int main(void)
{
    // Enable FPU
    SCB->CPACR |= (0xF << 20);

    UART2_Init();
    TIM3_Delay_Init();
    Turbidity_ADC_Init();

    while (1)
    {
        uint32_t temp = Turbidity_ADC_NTU();
        UART2_SendString("ADC: ");
        UART2_SendInt(temp);
        UART2_SendString("\r\n");
        TIM3_Delay_ms(1000);
    }
}
