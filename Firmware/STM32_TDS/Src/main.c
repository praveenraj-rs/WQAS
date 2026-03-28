#include <stm32f4xx.h>

#include "config.h"
#include "timer.h"
#include "uart.h"

#include "tds.h"

int main(void)
{
	// Enable FPU
    SCB->CPACR |= (0xF << 20);

    UART2_Init();
    TIM3_Delay_Init();

    TDS_ADC_Init();

    while (1)
    {
    	float temperature = 25.0f;
        float ppm = TDS_GetPPM(temperature);

        UART2_SendString("TDS: ");
        UART2_SendFloat(ppm);
        UART2_SendString(" ppm\r\n");

        TIM3_Delay_ms(1000);
    }
}
