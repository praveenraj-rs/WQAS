// General Purpose Delay in (ms)
// Timer3

#include "config.h"
#include "timer.h"

// --- DELAY INIT ---
void TIM3_Delay_Init(void)
{
    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;

    // 1 ms tick
    TIM3->PSC = (SysClk / 1000) - 1;
}

// --- DELAY MS ---
void TIM3_Delay_ms(uint16_t ms)
{
    TIM3->ARR = ms - 1;
    TIM3->CNT = 0;

    TIM3->EGR |= TIM_EGR_UG;   // Update registers

    TIM3->SR &= ~TIM_SR_UIF;   // Clear flag
    TIM3->CR1 |= TIM_CR1_CEN;  // Start

    while(!(TIM3->SR & TIM_SR_UIF));

    TIM3->CR1 &= ~TIM_CR1_CEN; // Stop
}
