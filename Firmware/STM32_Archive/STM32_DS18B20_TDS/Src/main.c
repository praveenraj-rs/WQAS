#include <stm32f4xx.h>
#include <stdint.h>

#include "config.h"
#include "timer.h"
#include "uart.h"
#include "ds18b20.h"
#include "tds.h"

// --- MAIN ---
int main(void){

	// General Functions
	UART2_Init();
	TIM3_Delay_Init();

	// Specific Functions
	DS18B20_Init();
	TDS_ADC_Init();

    while (1) {

//		float temperature = DS18B20_Read_Temp();
//		UART2_SendString("Temperature: ");
//		UART2_SendFloat(temperature);
//		UART2_SendString("\n\n");
//
//		// TDS PPM
//		float ppm = TDS_GetPPM(temperature);
//        UART2_SendString("TDS: ");
//        UART2_SendFloat(ppm);
//        UART2_SendString(" ppm\r\n");
//
//        TIM3_Delay_ms(1000);

		float temperature = DS18B20_Read_Temp();
		//UART2_SendString("Temperature: ");
		UART2_SendFloat(temperature);
		UART2_SendString(", ");

		// TDS PPM
		float ppm = TDS_GetPPM(temperature);
//		UART2_SendString("TDS: ");
		UART2_SendFloat(ppm);
		UART2_SendString("\n");

		TIM3_Delay_ms(500);


    }
    return 0;
}
