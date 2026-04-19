#include <stm32f4xx.h>
#include <stdint.h>

#include "config.h"
#include "timer.h"
#include "uart.h"

#include "ds18b20.h"

// --- MAIN ---
int main(void) {

    TIM3_Delay_Init();
    UART2_Init();

    // DS18B20 Temperature Initialisation
    DS18B20_Init();

    while (1)
    {
		float temp = DS18B20_Read_Temp();
		UART2_SendString("Temperature: ");
		UART2_SendFloat(temp);
		UART2_SendString("\n");
		TIM3_Delay_ms(1000);
    }
}
