import math
import os
import pyvisa
import time
import pandas as pd


def setup_devices():
    print("Setting parameters on devices..")
    mm.write('*RST')
    ps.write('*RST')
    time.sleep(5);

    ps.write(f"FREQ {start_freq}")
    ps.write(f"VOLT {amplitude_psu}")
    ps.write("OUTP ON")

    mm.write("VOLTage:AC:RANGe:AUTO 1")
    print(mm.query('Measure:voltage:ac?'))

def measure_range(start_f,stop_f):
    current_freq = start_f
    frequencies_temp = []
    voltages_temp = []
    index = 0
    while(current_freq < stop_f):
        frequencies_temp.append(float(current_freq))
        print(frequencies_temp[index].__str__()+ "Hz")
        ps.write(f"FREQ {current_freq}")
        time.sleep(settling_time_psu)
        voltages_temp.append(float(mm.query('Measure:voltage:ac?'))*math.sqrt(2)) #to get amplitude
        print(voltages_temp[index].__str__() + "V")
        current_freq *=freq_multiplyer
        time.sleep(delay_between_measurements)
        index +=1
    return frequencies_temp,voltages_temp

def measure_bodeplot():
    print("Starting bodeplot measurement..")
    frequencies, voltages = measure_range(start_freq,stop_freq)

    voltages_db = []
    index = 0
    for voltage in voltages:
        voltages_db.append(20*math.log10(voltage/(amplitude_psu/2)))
        print(voltages_db[index].__str__() + "VdB")
        index +=1

    df = pd.DataFrame()
    df["Frequencies"] = frequencies
    df["Voltages"] = voltages
    df["Voltages_db"] = voltages_db
    df.to_csv(file_name,sep="\t")# andere delimiter? voor komma problemen
    ps.write("OUTP OFF")
    print("Finished!")

if __name__ == "__main__":

    file_name = 'bodeplot_1.csv'

    if os.path.exists(file_name):
        print('The file name you choose already exists!')
        exit()


    delay_between_measurements = 1  # delay between measurments
    settling_time_psu = 2.5
    start_freq = 100  # Hz
    stop_freq = 500000  # Hz
    amplitude_psu = 0.1 #this is peak to peak value
    freq_multiplyer = 1.2

    rm = pyvisa.ResourceManager()
    print("List of available devices: " + rm.list_resources().__str__())
    try:
        mm = rm.open_resource('ASRL8::INSTR')
        print("Multimeter: " + mm.query("*IDN?"))

    except:
        print("The multimeter isnt connected or couldnt be identified!")
        exit()

    try:
        ps = rm.open_resource('ASRL9::INSTR')
        print("Powersupply: " + ps.query("*IDN?"))
    except:
        print("The powersupply isnt connected or couldnt be identified!")
        exit()

    setup_devices()
    measure_bodeplot()
