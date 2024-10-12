import machine
from machine import ADC
import uasyncio as asyncio
import time
import random
import os

# Create LED
led = machine.Pin(25, machine.Pin.OUT)

# 内蔵温度センサーのADCチャンネル
TEMP_SENSOR_CHANNEL = 4

# ADCオブジェクトの作成
adc = ADC(TEMP_SENSOR_CHANNEL)

SLEEP_PERIOD = 10

# Reset LED
led.value(0)

def write_csv(count, temperature):
    time_data = (SLEEP_PERIOD + 60) * count
    with open("data.csv", "a") as file:
        file.write("{},{}\n".format(time_data, temperature))

# 温度センサーのADC値を温度に変換する関数
def convert_to_temperature(adc_value):
    # 温度を計算する式はRP2040のデータシートから取得します
    conversion_factor = 3.3 / (65535)
    voltage = adc_value * conversion_factor
    temperature_celsius = 27 - (voltage - 0.706) / 0.001721
    fix_num = 0 - 2.5
    return temperature_celsius + fix_num

async def blink():
    while True:
        led.toggle()
        await asyncio.sleep(random.randint(1, 5) / 10)

def get_count():
    count = 0
    
    if machine.reset_cause() == machine.DEEPSLEEP_RESET:
        try:
            with open("count.txt", "r") as file:
                count = int(file.read())
        except Exception:
            pass

        with open("count.txt", "w") as file:
            file.write(str(count + 1))
    else:
        try:
            os.remove("count.txt")
            
            files = [
                f for f in os.listdir() if f.endswith(".old")
            ]
            sorted_files = sorted(files)
            next = f"{int(sorted_files[0].split(".")[0])}.data.csv.old"

            os.rename("data.csv", "{}.old".format(next))

        except Exception:
            pass

    return count

async def main():
    machine.freq(50000000)
    print("CPU Freq:", machine.freq() / 1000000, "MHz")
    # start blinking 
    start_time = time.time()
    loop = asyncio.get_event_loop()
    loop.create_task(blink())
    print("Starting Task")

    #---Write your code here---
    count = get_count()

    sensor_value = adc.read_u16()
    temperature = convert_to_temperature(sensor_value)

    print("Count: {}, Temperature: {:.2f} Celsius".format(count, temperature))

    write_csv(count, temperature)

    #--------------------------

    while time.time() - start_time < 10:
        await asyncio.sleep(1)

    loop.stop()
    print("Task Completed")
    led.off()
    machine.deepsleep(SLEEP_PERIOD * 1000)

if __name__ == "__main__":
    asyncio.run(main())

