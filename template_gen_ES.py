import sys
import os
import numpy as np
import pandas as pd
import neo

def reset_dir(dir_name): # requires os
        if dir_name in os.listdir():
            for File in os.listdir(dir_name):
                os.remove(dir_name + "/" + File)
            os.rmdir(dir_name)
            os.mkdir(dir_name)
        else:
            os.mkdir(dir_name)

def hertzs(time_vector): # requires numpy as np
        time_len = len(time_vector)
        if len(time_vector)%2 == 0:
            hz = np.linspace(0,
                             time_len/time_vector[time_len-1],
                             time_len+1)
            return hz
        else:
            hz = np.linspace(0,
                             (time_len/time_vector[time_len-1])-1,
                             time_len)
            return hz

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

# Destined to be deleted:
def noisy_array(array): # requires numpy as np
    noisy_arr = array
    subarr_idx = 0
    for subarray in noisy_arr:
        row_idx = 0
        for row in subarray:
            row_mean = np.mean(row)
            row_std = np.std(row)
            row_len = np.shape(row)[0]
            rand_vec = np.random.uniform(
                       low = row_mean - row_std,
                       high = row_mean + row_std,
                       size = row_len)
            new_vec = row + rand_vec
            noisy_arr[subarr_idx,row_idx,:] = new_vec
            row_idx = row_idx + 1
        subarr_idx = subarr_idx + 1
    return noisy_arr

######################################
### Evaluating signal files format ###
######################################

print("\nLaunching " + sys.argv[0] + ".\n")

try:
    sample_signals_path = sys.argv[1]
except:
    print("ERROR: " + sys.argv[0] +
    " requires sample signals directory path as first" + 
    " argument so the program executes correctly. Please," +
    " insert sample signals directory path as a first " +
    "argument.")
    quit()

all_files_and_dirs = os.listdir()
dirs_only = []
for element in all_files_and_dirs:
    if "." not in element:
        dirs_only.append(element)

is_dir = False
for directory in dirs_only:
    if directory in sample_signals_path:
        is_dir = True
if is_dir == False:    
    print("ERROR: " + sys.argv[0] +
    " requires a sample signals directory path that exists" +
    " as first argument so the program executes correctly. " +
    "Please, insert a directory path as a first argument.\n")
    quit()

sample_list = os.listdir(sample_signals_path)
no_files = len(sample_list)
no_rows = no_files

if no_files == 0:
    print("No files found in signal files directory. " +
          "Shutting down program.\n")
    quit()

file_format_list = []

print("Detecting files format...")

for File in sample_list:
    file_format_list.append(File.split(".")[1])

if file_format_list.count(file_format_list[0]) == no_files:
    if file_format_list[0] in ["txt", "smr", "plx"]:
        file_format = file_format_list[0]
    else:
        print("This file format can't be proccessed by " +
              "this program. The only program files that " +
              "can be used by this algorithm are: " +
              "text (TXT), Spike2 (SMR) and Plexon (PLX)" +
              "files. Shutting down program.")
        quit()
else:
    print("Multiple file formats detected. Please, use " +
          "only one kind of format in order to generate " +
          "a result. Shutting program down.")
    quit()

print(file_format.upper() +
      " file format detected in all files.\n")

#####################################################
## Creating the signal frequencies amplitude array ##
#####################################################

Y_or_n = input("Would you like to consider the first " +
"frequencies for making the template(s)? (Else, the " +
"program will consider a proportion of the cummulative sum " +
"of the data for making them.) [Y/n] ").upper()

if Y_or_n not in ["Y","N","YES","NO"]:
    print("No appropiate input was introduced. Shutting " +
    "down " + sys.argv[0] + ".")
    quit()
if Y_or_n in ["Y","YES"]:
    print("\nMaking the templates considering first " +
    "frequencies.")
if Y_or_n in ["N","NO"]:
    print("\nMaking the templates considering the " +
    "cummulative sum of data amplitudes.")

max_time_vector = np.array([])
max_pnts = 0
no_channels = 0

first_file = True

if file_format == "txt":
    for File in sample_list:
        data = np.loadtxt(sample_signals_path +
                          "/" + File,
                          delimiter = "\t")
        data_length = np.shape(data)[0]
        if data_length > max_pnts:
            max_pnts = data_length
            if Y_or_n in ["Y","YES"]:
                data_col0 = data[:,0]
                max_time_vector = data_col0
                sampling_rate = 1/(data_col0[1]-data_col0[0])
    no_channels = np.shape(data)[1]-1

elif file_format == "smr":
    for File in sample_list:
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format)
        for seg in data.segments:
            for an_sig in seg.analogsignals:
                array = np.transpose(np.array(an_sig))
                time = an_sig.times.rescale("s").magnitude
                time_len = len(time)
                if time_len > max_pnts:
                    max_pnts = time_len
                    if Y_or_n in ["YES","Y"]:
                        max_time_vector = time
                        sampling_rate = an_sig.sampling_rate
                if first_file == True:
                    for ind_sig in array:
                        no_channels = no_channels + 1
        first_file = False

elif file_format == "plx":
    for File in sample_list:
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format)
        for block in data:
            for seg in block.segments:
                for an_sig in seg.analogsignals:
                    array = np.transpose(np.array(an_sig))
                    time = an_sig.times.rescale("s").magnitude
                    time_len = len(time)
                    if time_len > max_pnts:
                        max_pnts = time_len
                        if Y_or_n in ["YES","Y"]:
                            max_time_vector = time
                            sampling_rate = an_sig.sampling_rate
                    if first_file == True:
                        for ind_sig in array:
                            no_channels = no_channels + 1
        first_file = False

channel_list = np.linspace(1,no_channels,no_channels)
no_arr = no_channels
no_cols = max_pnts

arr = np.zeros([no_arr,no_rows,no_cols])

if file_format == "txt":
    for File in os.listdir(sample_signals_path):
        data = np.loadtxt(sample_signals_path + "/" + File,
                          delimiter = "\t")
        file_idx = os.listdir(sample_signals_path).index(File)
        no_row = file_idx
        for channel in channel_list:
            no_arr = int(channel-1)
            fCoefs = (np.fft.fft(data[:,int(channel)],
                                 n=no_cols)/
                      len(data[:,int(channel)]))
            ampls = np.absolute(fCoefs)
            ampls[1:len(ampls)] *= 2
            arr[no_arr,no_row,:] = ampls

elif file_format == "smr":
    for File in sample_list:
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format)
        file_idx = sample_list.index(File)
        no_row = file_idx
        channel_idx = 0
        for seg in data.segments:
            for an_sig in seg.analogsignals:
                array = np.transpose(np.array(an_sig))
                for ind_sig in array:
                    fCoefs = (np.fft.fft(ind_sig,
                              n = no_cols)/
                              len(ind_sig))
                    ampls = np.absolute(fCoefs)
                    ampls[1:len(ampls)] *= 2
                    arr[channel_idx,no_row,:] = ampls
                    channel_idx = channel_idx + 1

elif file_format == "plx":
    for File in sample_list:
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format)
        file_idx = sample_list.index(File)
        no_row = file_idx
        channel_idx = 0
        for block in data:
            for seg in block.segments:
                for an_sig in seg.analogsignals:
                    array = np.transpose(np.array(an_sig))
                    for ind_sig in array:
                        fCoefs = (np.fft.fft(ind_sig,
                                  n = no_cols)/
                                  len(ind_sig))
                        ampls = np.absolute(fCoefs)
                        ampls[1:len(ampls)] *= 2
                        arr[channel_idx,no_row,:] = ampls
                        channel_idx = channel_idx +1

# arr = noisy_array(arr) # introduces noise

###############################################
## Refining and creating the final templates ##
###############################################

if Y_or_n in ["Y","YES"]:
    limit_freq = input("Select the limit frequency (all " +
    "frequency amplitude data below it will be " +
    "added into the templates) (NOTE: This value must " +
    "be between 0 and " + str(int(round(sampling_rate/2))) +
    "): ")
    try:
        limit_freq = float(limit_freq)
    except:
        print("ERROR: limit frequency type detected is not " +
        "valid. Shutting down program.")
        quit()
    print("")
    hz = hertzs(time_vector = max_time_vector)
    limit_idx = np.sum(hz < limit_freq)
    arr = arr[:,:,0:limit_idx]
    mean_matrix = np.zeros([no_channels,limit_idx])
    std_matrix = np.zeros([no_channels,limit_idx])
elif Y_or_n in ["N","NO"]:
    mean_matrix = np.zeros([no_channels,max_pnts])
    std_matrix = np.zeros([no_channels,max_pnts])

for idx in channel_list:
    index = int(idx-1)
    mean = np.mean(arr[index,:,:], axis = 0) 
    mean_matrix[index,:] = mean
    std = np.std(arr[index,:,:], axis = 0)
    std_matrix[index,:] = std

if Y_or_n in ["N","NO"]:
    if max_pnts%2 == 0:
        mean_matrix = mean_matrix[:,0:int(max_pnts/2)]
    else:
        mean_matrix = mean_matrix[:,0:int(max_pnts/2)+1]

templ_dir = "templates"
reset_dir(templ_dir)

print("Resetting template directory... Done.")

if Y_or_n in ["N","NO"]:
    prop = input("Select the frequency amplitudes cumulative"+
    " sum proportion that is going to be considered (NOTE:"+
    " Value given must be a number between 0 and 1): ")
    print("")
    try:
        prop = float(prop)
    except:
        print("Input value not valid. Shutting down program.")
        quit()
    if prop < 0 or prop > 1:
        print("Input value not valid. Shutting down program.")
        quit()

row_idx = 0

for row in mean_matrix:
    if Y_or_n in ["N","NO"]:
        one_p = np.sum(row)
        wanted_cumsum = one_p * prop
        idx = np.sum(np.cumsum(row) < wanted_cumsum) + 1
        channel_template = np.zeros([2,idx])
        channel_template[0,:] = mean_matrix[row_idx,0:idx]
        channel_template[1,:] = std_matrix[row_idx,0:idx]
    elif Y_or_n in ["Y","YES"]:
        channel_template = np.zeros([2,limit_idx])
        channel_template[0,:] = mean_matrix[row_idx,:]
        channel_template[1,:] = std_matrix[row_idx,:]
    templ_trans = np.transpose(channel_template)
    templ_name = "templ_channel" + str(int(
                 channel_list[row_idx])) + ".txt"
    templ_path = templ_dir + "/" + templ_name
    pd.DataFrame(templ_trans).to_csv(templ_path,
                                     sep = "\t",
                                     index = False,
                                     header = False)
    row_idx = row_idx + 1

print("Creating templates... Done.")

output_content = str(max_pnts) + "\n" + str(no_channels)
max_output = open("no_cols_and_channels.txt", "w")
max_output.write(output_content)
max_output.close()

print("Creating file containing maximum number of points" +
      " per signal and number of channels... Done.\n")