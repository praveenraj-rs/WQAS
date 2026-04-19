################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Third_Party/WS/timer.c \
../Third_Party/WS/uart.c 

OBJS += \
./Third_Party/WS/timer.o \
./Third_Party/WS/uart.o 

C_DEPS += \
./Third_Party/WS/timer.d \
./Third_Party/WS/uart.d 


# Each subdirectory must supply rules for building sources it contributes
Third_Party/WS/%.o Third_Party/WS/%.su Third_Party/WS/%.cyclo: ../Third_Party/WS/%.c Third_Party/WS/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DSTM32 -DSTM32F4 -DSTM32F407VGTx -DSTM32F401RETx -c -I../Inc -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_Turbidity/Third_Party/CMSIS/Include" -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_Turbidity/Third_Party/CMSIS/Device/ST/STM32F4xx/Include" -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_Turbidity/Third_Party/WS" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Third_Party-2f-WS

clean-Third_Party-2f-WS:
	-$(RM) ./Third_Party/WS/timer.cyclo ./Third_Party/WS/timer.d ./Third_Party/WS/timer.o ./Third_Party/WS/timer.su ./Third_Party/WS/uart.cyclo ./Third_Party/WS/uart.d ./Third_Party/WS/uart.o ./Third_Party/WS/uart.su

.PHONY: clean-Third_Party-2f-WS

