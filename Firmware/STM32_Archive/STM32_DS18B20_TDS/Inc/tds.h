#ifndef TDS_H_
#define TDS_H_

#include <stdint.h>

// -----------------------------
// Configuration Macros
// -----------------------------
#define ADC_RESOLUTION 4095.0f   // 12-bit ADC
#define VREF           3.3f      // ADC reference voltage
#define TDS_FACTOR     0.5f      // Conversion factor EC -> TDS
#define K_VALUE        1.0f      // Calibration factor
#define DEFAULT_TEMP   25.0f     // Default temperature

// -----------------------------
// Function Prototypes
// -----------------------------

// Initialize ADC for TDS sensor
void TDS_ADC_Init(void);

// Read raw ADC value
uint16_t TDS_ADC_Read(void);

// Get sensor voltage
float TDS_GetVoltage(void);

// Get TDS value in ppm
float TDS_GetPPM(float temperature);

#endif /* TDS_H_ */
