def tension():
    from machine import ADC
    conversion_factor = 3.3 / (65535)
    sensor_volt = ADC(28)
    current_volt = (sensor_volt.read_u16() - 128) * conversion_factor
    print("tension =", current_volt)
