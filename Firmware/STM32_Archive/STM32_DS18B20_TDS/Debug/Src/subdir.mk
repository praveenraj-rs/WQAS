################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (13.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Src/ds18b20.c \
../Src/main.c \
../Src/syscalls.c \
../Src/sysmem.c \
../Src/tds.c 

OBJS += \
./Src/ds18b20.o \
./Src/main.o \
./Src/syscalls.o \
./Src/sysmem.o \
./Src/tds.o 

C_DEPS += \
./Src/ds18b20.d \
./Src/main.d \
./Src/syscalls.d \
./Src/sysmem.d \
./Src/tds.d 


# Each subdirectory must supply rules for building sources it contributes
Src/%.o Src/%.su Src/%.cyclo: ../Src/%.c Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DSTM32 -DSTM32F4 -DSTM32F407VGTx -DSTM32F401RETx -c -I../Inc -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_DS18B20_TDS/Third_Party/CMSIS/Include" -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_DS18B20_TDS/Third_Party/CMSIS/Device/ST/STM32F4xx/Include" -I"/home/praveenrajrs/Desktop/WQAS/Firmware/STM32_DS18B20_TDS/Third_Party/WS" -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Src

clean-Src:
	-$(RM) ./Src/ds18b20.cyclo ./Src/ds18b20.d ./Src/ds18b20.o ./Src/ds18b20.su ./Src/main.cyclo ./Src/main.d ./Src/main.o ./Src/main.su ./Src/syscalls.cyclo ./Src/syscalls.d ./Src/syscalls.o ./Src/syscalls.su ./Src/sysmem.cyclo ./Src/sysmem.d ./Src/sysmem.o ./Src/sysmem.su ./Src/tds.cyclo ./Src/tds.d ./Src/tds.o ./Src/tds.su

.PHONY: clean-Src

