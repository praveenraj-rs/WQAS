#include <stm32f4xx.h>
#include <stdint.h>

#include "config.h"
#include "timer.h"
#include "uart.h"
#include "ds18b20.h"

// --- MAIN ---
int main(void) {

    // Enable GPIOA clock
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;

	SCB->CPACR |= (0xF << 20);  // Enable CP10 and CP11 (FPU)

    UART2_Init();
    TIM3_Delay_Init();

    // Init DWT
    DWT_Delay_Init();

    while (1) {

       float temp = DS18B20_Read_Temp();
        UART2_SendString("Temperature: ");
        UART2_SendFloat(temp);
        UART2_SendString("\n\n");
        TIM3_Delay_ms(1000);
    }
}
