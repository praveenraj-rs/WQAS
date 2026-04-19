#ifndef _DS18B20_H_
#define _DS18B20_H_

// Delay functions
void DWT_Delay_us(uint32_t us);
void DWT_Delay_Init(void);

// DS18B20 functions
float DS18B20_Read_Temp();

// OneWire functions
uint8_t Onewire_Reset();
void Onewire_Write(uint8_t data);
uint8_t Onewire_Read();

// GPIO functions
void Output_Pin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);
void Input_Pin(GPIO_TypeDef *GPIOx, uint16_t GPIO_Pin);

#endif /* _DS18B20_H_ */
