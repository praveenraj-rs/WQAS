// UART_2 Serial Communication Nucleo

// UART_2 Tx -> PA2
// UART_2 Rx -> PA3

#include "config.h"
#include "uart.h"


// --- Initialize UART2 ---
void UART2_Init(void)
{
    // UART2 Config
    // Tx -> PA2
    // Rx -> PA3

    // Enable clocks
    RCC->AHB1ENR |= RCC_AHB1ENR_GPIOAEN;
    RCC->APB1ENR |= RCC_APB1ENR_USART2EN;

    // PA2 -> TX, PA3 -> RX (Alternate Function)
    GPIOA->MODER &= ~((3<<(2*2)) | (3<<(3*2)));
    GPIOA->MODER |=  ((2<<(2*2)) | (2<<(3*2)));

    // AF7 for USART2
    GPIOA->AFR[0] &= ~((0xF<<(2*4)) | (0xF<<(3*4)));
    GPIOA->AFR[0] |=  ((7<<(2*4)) | (7<<(3*4)));

    // Baud rate
    USART2->BRR = UART2_BAUD_RATE;

    // Enable TX + UART
    USART2->CR1 = USART_CR1_TE | USART_CR1_RE; // Enable TX + RX
    USART2->CR1 |= USART_CR1_UE;
}

// --- SEND CHAR ---
void UART2_SendChar(char c)
{
    while(!(USART2->SR & USART_SR_TXE));
    USART2->DR = c;
}

// --- SEND STRING ---
void UART2_SendString(char *s)
{
    while(*s)
    {
        UART2_SendChar(*s++);
    }
}

// --- SEND INT ---
void UART2_SendInt(int num)
{
    char buffer[20];
    sprintf(buffer, "%d", num);
    UART2_SendString(buffer);
}

void UART2_SendFloat(float value) {
    int intPart = (int)value;
    int decPart = (int)((value - intPart) * 100);

    if (decPart < 0) decPart *= -1; // handle negative

    UART2_SendInt(intPart);
    UART2_SendChar('.');

    // Ensure leading zero (e.g., 36.05 instead of 36.5)
    if (decPart < 10) UART2_SendChar('0');

    UART2_SendInt(decPart);
}

// --- CHECK UART2 RX ---
int UART2_Available(void)
{
    return (USART2->SR & USART_SR_RXNE);
}

// --- READ CHAR ---
char UART2_Read(void)
{
    return (char)(USART2->DR);
}
