// UART_2 Serial Communication Nucleo

// UART_2 Tx -> PA2
// UART_2 Rx -> PA3

#ifndef UART_H_
#define UART_H_

#include <stm32f4xx.h>
#include <stdio.h>

// Initialize UART2 (PA2 TX, PA3 RX)
void UART2_Init(void);

// Send single character
void UART2_SendChar(char c);

// Send string
void UART2_SendString(char *s);

// Send Integer Number
void UART2_SendInt(int num);

// Receive UART2 Available (Any Data)
int UART2_Available(void);

// Receive UART2 Char
char UART2_Read(void);

#endif // UART_H_
