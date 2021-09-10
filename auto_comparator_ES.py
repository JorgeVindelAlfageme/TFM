import sys
import os
import numpy as np
import scipy.stats
import neo

def reset_dir(dir_name): # requires os
    if dir_name in os.listdir():
        for File in os.listdir(dir_name):
            os.remove(dir_name + "/" + File)
        os.rmdir(dir_name)
        os.mkdir(dir_name)
    else:
        os.mkdir(dir_name)

def neo_reader(file_format, file_name): # requires neo
    file_format = file_format.upper()
    if file_format not in ["SMR","PLX"]:
        print("WARNING (from neo_reader() function): " +
              "File formats that can be processed by " +
              "neo_reader() function are: SMR, PLX. " +
              "Please, use just one of those file " +
              "formats.\n")
        quit()
    elif file_format == "SMR":
        reader = neo.io.Spike2IO(filename = file_name)
        data = reader.read(lazy = False)[0]
    elif file_format == "PLX":
        reader = neo.io.PlexonIO(filename = file_name)
        data = reader.read(lazy = False)
    return data

print("\nLaunching " + sys.argv[0] + ".")

cols_and_channels_file = open("no_cols_and_channels.txt", "r")
file_data = cols_and_channels_file.read().splitlines()
pnts = int(file_data[0])
channels = int(file_data[1])

templ = "templates"

reset_dir("results")
print("Resetting 'results' directory... Done.")
reset_dir("inboundSignals")
print("Resetting 'inboundSignals' directory... Done.\n")

mean_calc = input("Do you want to compute the arithmetic " +
                  "mean for the frequency amplitudes in " +
                  "order to stablish a comparison between " +
                  "signals? (If not, the weighted average " +
                  "will be computed.) [Y, n] ").upper()
if mean_calc not in ["Y", "YES", "N", "NO"]:
    print("No valid answer was entered. Shutting program " +
          "down.")
    quit()
elif mean_calc in ["Y","YES"]:
    print("Arithmetic mean selected as the calculation " +
    "algorithm for computing the comparison between " +
    "signals.\n")
elif mean_calc in ["N","NO"]:
    print("Weighted averaging selected as the calculation " +
    "algorithm for computing the comparison between " +
    "signals.\n")

idx = 1
dic = {}

for File in os.listdir(templ):
    data = np.loadtxt(templ + "/" + File,
                      delimiter = "\t")
    dic["channel"+str(idx)] = data
    idx = idx + 1

no_files = len(os.listdir(templ))
file_ids = np.linspace(1,no_files,no_files)

print("Reading templates... Done.")

def comparator(template,max_numb_pnts,what_file,is_arith):

    output = ""
    Format = what_file.split(".")[1]
    file_arr = np.zeros([channels + 1,pnts])
    row_idx = 1
    
    if Format == "txt":
        inbound_file = np.transpose(np.loadtxt(what_file,
                                           delimiter = "\t"))
        for file_idx in file_ids:
            signal = inbound_file[int(file_idx),:]
            fCoefs = (np.fft.fft(signal,
                                 n = max_numb_pnts)/
                      len(signal))
            ampls = np.absolute(fCoefs)
            ampls[1:len(ampls)] *= 2
            file_arr[int(file_idx),:] = ampls

    elif Format == "smr" or Format == "plx":
        neo_data = neo_reader(file_format = Format,
                              file_name = what_file)
        if Format == "smr":
            for seg in neo_data.segments:
                for an_sig in seg.analogsignals:
                    array = np.transpose(np.array(an_sig))
                    for ind_sig in array:
                        fCoefs = (np.fft.fft(ind_sig,
                                  n = max_numb_pnts)/
                                  len(ind_sig))
                        ampls = np.absolute(fCoefs)
                        ampls[1:len(ampls)] *= 2
                        file_arr[row_idx,:] = ampls
                        row_idx = row_idx + 1
        elif Format == "plx":
            for block in neo_data:
                for seg in block.segments:
                    for an_sig in seg.analogsignals:
                        array = np.transpose(np.array(an_sig))
                        for ind_sig in array:
                            fCoefs = (np.fft.fft(ind_sig,
                                      n = max_numb_pnts)/
                                      len(ind_sig))
                            ampls = np.absolute(fCoefs)
                            ampls[1:len(ampls)] *= 2
                            file_arr[row_idx,:] = ampls
                            row_idx = row_idx + 1

    for file_idx in file_ids:
        ampls = file_arr[int(file_idx),:]
        templ_mean = template["channel"+str(int(file_idx))][:,0]
        templ_std = template["channel"+str(int(file_idx))][:,1]
        idx = 0
        gauss = np.zeros(len(templ_mean))
        templ_mean_sum = np.sum(templ_mean)
        for element in templ_mean:
            mean = element
            std = templ_std[idx]
            if std == 0:
                std = 1e-1
            input_val = ampls[idx]
            gauss_val = (scipy.stats.norm(mean,
                         std).pdf(input_val)/
                         scipy.stats.norm(mean,
                         std).pdf(mean))
            if is_arith in ["Y","YES"]:
                gauss[idx] = gauss_val
            if is_arith in ["N","NO"]:
                gauss[idx] = gauss_val*(input_val/templ_mean_sum)
            idx = idx + 1
        if is_arith in ["Y","YES"]:
            output = output + str(np.mean(gauss)) + "\n"
        elif is_arith in ["N","NO"]:
            output = output + str(np.sum(gauss)) + "\n"
    
    return output

result_number = 1
old_files = []
current_path = os.getcwd()
inbound_signals_path = current_path + "\\inboundSignals\\"

print("System ready to process inbound signals.\n")

while True:
    file_list = os.listdir("inboundSignals")
    new_files = []

    for signal_file in file_list:
        if signal_file.split(".")[1] in ["txt","smr","plx"] and signal_file not in old_files:
            print("New inbound file (" + signal_file +
                  ") detected in inbound signals directory.")
            file_path = inbound_signals_path + signal_file
            new_files.append(file_path)
            old_files.append(signal_file)
        
    new_files.sort(key = os.path.getctime)

    if len(new_files) > 0:
        for new_file in new_files:
            output_name = "result" + str(result_number) + ".txt"
            output_file = open(output_name, "w")
            output_file.write(comparator(template = dic,
                                         max_numb_pnts = pnts,
                                         what_file = new_file,
                                         is_arith = mean_calc))
            output_file.close()
            os.rename(output_name, "results/"+output_name)
            print(output_name + " file generated from " +
                  new_file + " file is now available in " +
                  "the results directory.")
            result_number = result_number + 1