###################################################
###################################################
###                                             ###
###                INTRODUCCIÓN                 ###
###                                             ###
###################################################
###################################################

# Este programa forma parte de un par de scripts que
# constituyen un algoritmo para la comparación de señales,
# considerando su dominio de frecuencia, por el cual se
# emite un resultado en forma de proporción, que indica
# el grado de similitud entre dos señales electrofisiológicas.
# Para el uso de este programa, es necesario que previamente
# se hayan elaborado unas plantillas que representan las
# señales promedio con las que se compararan las señales
# entrantes. Estas plantillas se han generado por medio
# del script template_gen5.py.

# Con este programa, se lee la información de las plantillas
# y se compara con la de archivos de señales entrantes.
# Estos archivos de señales han de llegar a un carpeta específicamente
# destinada a ellos que crea este script (el nombre de la
# carpeta es "inboundSignals"). Una vez que se lee el
# contenido de esos archivos y se computa la proporción
# de similutd entre las señales, los resultados numéricos
# se guardan en un archivo TXT que se envía a la carpeta
# "results". Se generará un archivo de resultados por cada
# archivo de señales entrante.

###################################################
###################################################
###                                             ###
###               MÓDULOS USADOS                ###
###                                             ###
###################################################
###################################################

# Para lograr esto, se ha requerido de los siguiente módulos:

# - sys: Se ha usado para crear argumentos desde el 
# prompt cuando se ejecuta el programa.
# - os: Se ha usado para trazar los paths de los
# los archivos que manipula el programa y que se puedan
# leer.
# - numpy (np): Se ha usado para hacer cálculo matricial
# y aplicar algoritmos de procesamiento de señales.
# - scipy: El módulo scipy constituye un entorno con
# funciones para computar una gran variedad de operaciones.
# Una de sus secciones está destinada al cálculo
# estadístico (scipy.stats), la cual se emplea en este
# script.
# - neo: Se ha utilizado para leer archivos que contienen
# señales típicamente fisiológicas en formatos comunes
# como SMR o PLX.

import sys
import os
import numpy as np
import scipy.stats
import neo

###################################################
###################################################
###                                             ###
###              FUNCIONES CREADAS              ###
###                                             ###
###################################################
###################################################

# Se han creado las siguientes funciones:

# - reset_dir(dir_name) : Requiere del módulo os. Su argumento
# dir_name se corresponde con el nombre del directorio
# localizado en la misma carpeta donde está este programa.
# Si el directorio ya existe, se eliminan los archivos
# que contenga. Si no existe, se crea.

def reset_dir(dir_name): # requiere del módulo os.
    if dir_name in os.listdir(): # se ejecuta si existe.
        for File in os.listdir(dir_name): # bucle que enlista sus archivos.
            os.remove(dir_name + "/" + File) # se elimina el archivo.
    else: # se ejecuta si no existe.
        os.mkdir(dir_name) # se crea el directorio.

# - neo_reader(file_format, file_name): Requiere del módulo neo.
# Esta función sirve para extraer los valores que componen una
# señal que se encuentra en archivos usados para almacenar señales
# electrofisiológicas.
# Por ahora, esta función solo permite leer señales desde archivos
# SMR o PLX. Su argumento file_format es un string que debe
# corresponderse con alguno de los formatos con los que opera
# la función (SMR, PLX). Sirve para indicar las funciones
# apropiadas para extraer los datos de los archivos en cuestión.
# El argumento file_name se refiere a la localización del archivo
# del que se pretenden extraer los datos.

def neo_reader(file_format, file_name): # requiere del módulo neo.
    file_format = file_format.upper() # cambia a mayúsculas el formato.
    if file_format not in ["SMR","PLX"]: # se ejecuta si el formato no es adecuado.
        print("WARNING (from neo_reader() function): " +
              "File formats that can be processed by " +
              "neo_reader() function are: SMR, PLX. " +
              "Please, use just one of those file " +
              "formats.\n") # mensaje de error.
        quit() # se cierra el programa.
    elif file_format == "SMR": # se ejecuta si el formato es SMR.
        reader = neo.io.Spike2IO(filename = file_name) # se lee el archivo.
        data = reader.read(lazy = False)[0] # se almacenan los datos en una variable.
    elif file_format == "PLX": # se ejecuta si el formato es PLX.
        reader = neo.io.PlexonIO(filename = file_name) # se lee el archivo.
        data = reader.read(lazy = False) # se almacenan los datos en una variable.
    return data # devuelve los datos.

# - comparator(): Requiere de los módulos NumPy, SciPy,
# y neo. Esta función constituye la parte más importante
# de este script, y es crucial a la hora de generar los
# archivos TXT que contienen el resultado de la comparación
# entre señales.

# Con respecto a las operaciones que realiza, con esta función,
# se crea una matriz vacía que tiene tantas filas como canales
# tienen los archivos de las señales, y tantas columnas como el
# número de puntos estandarizado que se usó para calcular el
# dominio de frecuencia de las señales utilizadas para crear la
# plantillas. En esta matriz, se van a incorporar los
# valores de las amplitudes del dominio de frecuencia de
# todas las señales de cada archivo entrante. Después, estos
# valores se compararán con los de la plantilla. El
# valor de amplitud de una frecuencia de la señal entrante
# representa un punto en la distribución normal definida
# por los valores de media aritmética y desviación estándar
# de la frecuencia correspondiente en la plantilla. El
# máximo de la distribución estándar se alcanza en su
# dominio en el punto igual a la media de la distribución.
# Sabiendo esto, se divide el valor asociado al de la amplitud
# de la señal entrante en la distribución normal, entre
# el máximo, y esa proproción representa la similitud
# entre las dos señales para esa frecuencia (por tanto,
# si el valor de amplitud de la señal entrante para
# el de esa frecuencia, y el de la plantilla, es el
# mismo, la proproción será igual a 1. Si es más bajo
# o más alto, el valor de la proporción oscilará entre
# 0 y 1, dependiendo de la proximidad que haya entre
# ambos). Al final, para cada frecuencia habrá una
# proporción de similitud correspondiente. El resultado
# de cada comparación entre amplitudes, una a una, pasa a
# formar parte de un vector. Dependiendo de la clase
# de cómputo elegido, con todas las proporciones
# se calculará una media aritmética, o media ponderada
# (con la que se considera el valor total de la amplitud
# de la señal sobre el de la suma de las amplitudes de
# la plantillas, cuyo cociente se multiplica por el
# valor de la proporción calculada), para finalmente
# generar la propoción de similitud entre señales. La
# función itera este cómputo tantas veces como señales
# o canales haya por archivo. Los resultados se acumulan
# en una variable que los ordena como strings por filas.
# Estos resultados están destinados a que se sobreescriban
# en un archivo TXT.

# Esta función tiene cuatro argumentos: template, max_numb_pnts,
# what_file y neo. El argumento "template" debe ser un
# diccionario cuyas etiquetas se refieran al número de
# canal que haya en los archivos de las señales, y el
# valor de las etiquetas sea una matriz con dos columnas,
# que contengan los valores de media aritmética de amplitud
# de cada una de las frecuencias que forman la señal promedio
# en la primera columna, y los valores de desviación estándar
# asociados a cada una de las medias en la segunda columna
# (en resumen, la matriz contiene los mismos datos que las
# plantillas de las señales). El argumento "max_numb_pnts"
# se refiere al número de puntos estandarizado que se usó
# para calcular el dominio de frecuencia al hacer las plantillas.
# Este número proviene del cómputo que se ha realizado con el
# script que genera las plantillas. Para que las plantillas
# encajen con las señales entrantes que se quieran comparar
# con ellas, este número ha de ser constante. El argumento
# "what_file" debe ser la localización de un archivo que
# contenga las señales que se vayan a comparar con las
# señales promedio de las plantillas. Finalmente, el argumento
# "is_arith" es un string que se introduce como input desde
# el prompt desde donde se ejecuta el programa. Este argumento
# indica si a la hora de hacer el cómputo para calcular el
# porcentaje de similitud entre las señales, se usará, o bien
# una media aritmética (si el argumento es igual a "Y" o "YES"),
# o ponderada (si es "N" o "NO"), de la similitud que hay
# para cada una de las frecuencias, una por una. Hay que recordar
# que este algoritmo de comparación de señales pretende que,
# de forma ideal, los resultados sean binarios: Se busca que
# los resultados indiquen, cuando se apliquen los programas
# en la interfaz cerebro-cerebro, si las señales son iguales
# (lo que implicaría una proporción de similitud de 1), o
# se las señales son distintas (lo que supone un resultado
# de 0).

# En caso de que para una frecuencia, los valores de amplitud
# sean iguales en las señales que se están utilizando para
# hacer una plantilla, la desviación estándar al hacer la
# media de esos valores es igual al cero. Ese valor de desvación
# estándar no puede ser utilizado para crear una distribución
# normal. Por ello, se han añadido unas líneas de código por
# medio de las cuales, si la desviación estándar es igual a
# cero, se va a atribuir arbitrariamente un valor de desviación
# estándar igual a 0,1 (líneas 284 y 285). De esta manera, el
# programa si que puede trazar la distribución normal para comparar
# las frecuencias de las dos señales.

# Uno de los errores de programación que se podría considerar
# en este script, es que algunas de las variables que utiliza
# esta función son variables globales que no se incorporan
# como argumentos, y otras son locales tras haberse creado
# un argumento adecuado para la función. Para que la función
# se pueda utilizar transversalmente entre scripts, lo mejor
# sería definir más argumentos que consideraran las variables
# globales de este script que se utilizan con la función.
# Algunas de las variables que deberían de aparecer como locales
# serían la variable que contiene el formato de los archivos de
# señales usados ("Format"), y el vector con los índices de los
# canales ("file_ids") que permite que se vayan analizando las
# señales de los archivos en orden (el nombre de esta variable
# se debe a que, al hacer las plantillas de las señales, cada
# canal tiene asociada una plantilla, que está en un archivo
# distinto. Por tanto, el número de plantillas será igual al
# número de canales).

def comparator(template,max_numb_pnts,what_file,is_arith): # requiere de los módulos NumPy, SciPy y neo.
    output = "" # string vacío que registrará los resultados que se sobreescribirán en un archivo de texto.
    Format = what_file.split(".")[1] # formato del archivo que se va a leer.
    file_arr = np.zeros([channels + 1,max_numb_pnts]) # matriz vacía.
    row_idx = 1 # índice de fila de la matriz.
    
    if Format == "txt": # se ejecuta si el formato de los archivos de señales es TXT.
        inbound_file = np.transpose(np.loadtxt(what_file,
                                           delimiter = "\t")) # se transpone la matriz de datos que contiene el archivo entrante.
        for file_idx in file_ids: # bucle que itera sobre los índices de los canales.
            signal = inbound_file[int(file_idx),:] # se selecciona una señal de uno de los canales del archivo.
            fCoefs = (np.fft.fft(signal,
                                 n = max_numb_pnts)/
                      len(signal)) # se calculan sus coeficientes de Fourier.
            ampls = np.absolute(fCoefs) # se calculan los valores de amplitud del dominio de frecuencia.
            ampls[1:len(ampls)] *= 2 # se normalizan los valores de amplitud.
            file_arr[int(file_idx),:] = ampls # se introducen por orden en la matriz que se creó vacía.

    elif Format == "smr" or Format == "plx": # se ejecuta si el formato de los archivos es SMR o PLX.
        neo_data = neo_reader(file_format = Format,
                              file_name = what_file) # se leen los datos del archivo.
        if Format == "smr": # se ejecuta si el formato del archivo es SMR.
            for seg in neo_data.segments: # bucle que itera sobre cada uno de los segmentos de los datos leídos.
                for an_sig in seg.analogsignals: # bucle que itera sobre la información que hay asignada a cada canal.
                    array = np.transpose(np.array(an_sig)) # transpone la matriz que representa a la señal o señales de cada canal.
                    for ind_sig in array: # bucle que itera sobre cada una de las filas de la matriz.
                        fCoefs = (np.fft.fft(ind_sig,
                                  n = max_numb_pnts)/
                                  len(ind_sig)) # calcula los coeficientes de Fourier de la señal.
                        ampls = np.absolute(fCoefs) # calcula la amplitud a partir de los coeficientes.
                        ampls[1:len(ampls)] *= 2 # normaliza el valor de los coeficientes.
                        file_arr[row_idx,:] = ampls # las amplitudes pasan a ocupar una fila de la matriz vacía originalmente.
                        row_idx = row_idx + 1 # el índice de fila incrementa en una unidad.
        elif Format == "plx": # se ejecuta si el formato de los archivos es PLX.
            for block in neo_data: # bucle que itera sobre cada uno de los bloques de los datos.
                for seg in block.segments: # bucle que itera sobre cada uno de los segmentos de los datos.
                    for an_sig in seg.analogsignals: # bucle que itera sobre la información que hay asignada a cada canal.
                        array = np.transpose(np.array(an_sig)) # transpone la matriz que representa a la o las señales de cada canal.
                        for ind_sig in array: # bucle que itera sobre cada fila de la matriz.
                            fCoefs = (np.fft.fft(ind_sig,
                                      n = max_numb_pnts)/
                                      len(ind_sig)) # calcula los coeficientes de Fourier de la señal.
                            ampls = np.absolute(fCoefs) # calcula la amplitud a partir de los coeficientes.
                            ampls[1:len(ampls)] *= 2 # normaliza el valor de los coeficientes.
                            file_arr[row_idx,:] = ampls # las amplitudes pasan a ocupar una fila de la matriz vacía originalmente.
                            row_idx = row_idx + 1 # el índice de fila incrementa en una unidad.

    for file_idx in file_ids: # bucle que itera sobre los índices del número de canales por cada archivo de señales.
        ampls = file_arr[int(file_idx),:] # se seleccionan las amplitudes de las frecuencias de un canal del archivo de señales entrante.
        templ_mean = template["channel"+str(int(file_idx))][:,0] # se seleccionan las medias de la plantilla correspondiente.
        templ_std = template["channel"+str(int(file_idx))][:,1] # se seleccionan las desviaciones estándar de la plantilla.
        idx = 0 # índice para seleccionar a cada una de las amplitudes de la señal entrante y de la plantilla.
        gauss = np.zeros(len(templ_mean)) # vector unidimensional vacío de la longitud de la plantilla.
        templ_mean_sum = np.sum(templ_mean) # suma de todas las amplitudes de la señal promedio de la plantilla.
        for element in templ_mean: # bucle que itera sobre cada amplitud de la plantilla.
            mean = element # valor de amplitud individual de la plantilla.
            std = templ_std[idx] # desviación estándar correspondiente a esa amplitud.
            if std == 0: # se ejecuta si la desviación estándar de la plantilla es igual a cero.
                std = 1e-1 # la desviación estándar es igual a 0,1.
            input_val = ampls[idx] # valor de amplitud de la señal entrante que se quiere comparar.
            gauss_val = (scipy.stats.norm(mean,
                         std).pdf(input_val)/
                         scipy.stats.norm(mean,
                         std).pdf(mean)) # divide el valor de la señal entrante en función de distribución normal entre su máximo.
            if is_arith in ["Y","YES"]: # se ejecuta si se quiere calcular la media aritmética de las proporciones de similitud.
                gauss[idx] = gauss_val # se incorpora el valor de la proporción al vector vacío antes creado.
            if is_arith in ["N","NO"]: # se ejecuta si se calcula la media ponderada de las proporciones.
                gauss[idx] = gauss_val*(input_val/templ_mean_sum) # se calcula una proporción ponderada y se incorpora en el vector vacío.
            idx = idx + 1 # el índice de valor de la plantilla aumenta en una unidad.
        if is_arith in ["Y","YES"]: # se ejecuta si se quiere calcular la media aritmética de las proporciones de similitud.
            output = output + str(np.mean(gauss)) + "\n" # se incorpora la media aritmética del vector de proporciones a un string.
        elif is_arith in ["N","NO"]: # se ejecuta si se calcula la media ponderada de las proporciones.
            output = output + str(np.sum(gauss)) + "\n" # se incorpora la media ponderada del vector de proporciones a un string.
    
    return output # se obtiene el string con todos los resultados de las distintas señales de cada canal.

###################################################
###################################################
###                                             ###
###          LECTURA DE LA INFORMACIÓN          ###
###              DE LAS PLANTILLAS              ###
###                                             ###
###################################################
###################################################

# En esta primera parte del script, se preparan los directorios
# que alojarán los resultados del algoritmo de comparación de
# señales y que almacenarán los archivos de señales entrantes
# que serán comparadas con las señales promedio representadas
# en las plantillas. También se lee la información de las
# plantillas, y se ejecuta el algoritmo de comparación de
# señales, que irá generando los resultados simultáneamente
# a medida que llegan archivos de señales entrantes al
# directorio correspondiente.

print("\nLaunching " + sys.argv[0] + ".") # mensaje de información.

# Con el anterior script, se ha generado un archivo de texto
# (nombrado no_cols_and_channels) que contiene los datos
# del número de puntos por dominio de frecuencia estandarizado
# de las señales y el número de canales que tenía cada archivo
# de señales. Es necesario usar el número de puntos de las
# señales a la hora de calcular la transformada de Fourier
# en las señales entrantes, para luego poder comparar las
# señales, frecuencia por frecuencia. El número de canales
# se ha querido registrar para en el fututo incorporar al
# programa un sistema de verificación para asegurar que
# el número de canales de los archivos de las señales usadas
# para crear las plantillas es el mismo que el de los archivos
# de las señales que se quieren comparar con ellas. En caso
# contrario, saldría un mensaje de error, y el programa
# se cerraría.

cols_and_channels_file = open("no_cols_and_channels.txt", "r") # abre el archivo TXT.
file_data = cols_and_channels_file.read().splitlines() # lee los datos del archivo TXT.
pnts = int(file_data[0]) # número máximo de puntos por señal.
channels = int(file_data[1]) # número de canales por archivo de señales.

templ = "templates" # nombre del directorio que contiene las plantillas.

reset_dir("results") # se resetea la carpeta de resultados.
print("Resetting 'results' directory... Done.") # mensaje de información.
reset_dir("inboundSignals") # se resetea la carpeta a donde llegarán los archivos de señales entrantes.
print("Resetting 'inboundSignals' directory... Done.\n") # mensaje de información.

# Este programa permite computar la similitud entre las plantillas y
# las señales de dos formas. La primera es mediante el cálculo de la
# media aritmética de las proporciones de similitud calculadas
# entre las frecuencias, una por una. De esta manera, los valores
# de amplitud de todas las frecuencias ponderan de la misma
# forma a la hora de decidir el porcentaje de similitud. En cambio,
# también se puede indicar que, dependiendo de la amplitud de
# las frecuencias, estos valores contribuyan proporcionalmente
# al cálculo de la similitud entre las señales. Así, cuanto
# mayor sea la amplitud de una frecuencia, más contribuirá
# a la similitud y de manera proporcional. El que el programa
# vaya a emplear una forma de cálculo u otra, dependerá de una
# variable que se obtendrá como un input desde el prompt donde
# se lanza el programa.

mean_calc = input("Do you want to compute the arithmetic " +
                  "mean for the frequency amplitudes in " +
                  "order to stablish a comparison between " +
                  "signals? (If not, the weighted average " +
                  "will be computed.) [Y, n] ").upper() # variable que determina si se hará la media aritmética o ponderada.
if mean_calc not in ["Y", "YES", "N", "NO"]: # se ejecuta si la variable recién introducida no es alguna reconocida por el programa.
    print("No valid answer was entered. Shutting program " +
          "down.") # mensaje de error.
    quit() # se cierra el programa.
elif mean_calc in ["Y","YES"]: # se ejecuta si se quiere usar la media aritmética como cálculo de similitud.
    print("Arithmetic mean selected as the calculation " +
    "algorithm for computing the comparison between " +
    "signals.\n") # mensaje de información.
elif mean_calc in ["N","NO"]: # se ejecuta si se quiere usar la media ponderada como cálculo de similitud.
    print("Weighted averaging selected as the calculation " +
    "algorithm for computing the comparison between " +
    "signals.\n") # mensaje de información.

# Para comparar las señales entrantes con las señales
# promedio representadas en las plantillas, primero
# se va a leer la información de las plantillas y se
# va a guardar a modo de diccionario. De esta manera,
# la información está ordenada y resulta más práctico
# acceder a ella cuando se vaya a usar.
# Los diccionarios son una variable de Python que permiten
# guardar valores ('values') y utilizarlos, usando una etiqueta
# o 'key' para referirse a ellos. La etiqueta, como en
# el caso de su valor puede tratarse de cualquier
# tipo de variable. En este caso, se va a generar un
# diccionario que va a tener tantas etiquetas como canales
# tengan los archivos de señales que se han utilizado,
# y cada etiqueta será un string que describa al canal
# (por ejemplo: "channel1", "channel2", "channel3",
# "channel4"). Luego, el valor de cada etiqueta se
# corresponderá con una matriz de dos columnas, que
# contendrá en la primera la media de los valores de
# amplitud de las frecuencias de la señal promedio,
# y en la segunda los valores de desviación estándar
# asociados.

idx = 1 # índice del número de canal. Representa el número de canal de los archivos que se han usado para hacer las plantillas.
dic = {} # diccionario vacío. Se llenará con los valores asociados a las plantillas de cada uno de los canales.

for File in os.listdir(templ): # bucle que itera cada archivo del directorio de las plantillas.
    data = np.loadtxt(templ + "/" + File,
                      delimiter = "\t") # lee la información de las plantillas (esta información es una matriz de dos columnas).
    dic["channel"+str(idx)] = data # incorpora esa información a modo de valor ('value') de una etiqueta ('key') en el diccionario.
    idx = idx + 1 # el número de índice que informa sobre el número de canal aumenta en una unidad por cada iteración.

print("Reading templates... Done.") # mensaje de información.

###################################################
###################################################
###                                             ###
###         COMPARACIÓN DE SEÑALES Y            ###
###         GENERACIÓN DE RESULTADOS            ###
###                                             ###
###################################################
###################################################

# Para comparar las señales, debido a que este programa
# pretende formar parte de una interfaz cerebro-cerebro,
# se necesita que la comparación entre las señales y el
# resultado se produzcan simultánemente a medida que se
# reciben las señales. Para lograr esto, se ha creado un
# bucle infinito que computa el algoritmo de comparación
# solo cuando se detecta que un nuevo archivo de señales
# ha llegado a la carpeta destinada a recibirlos. Por
# medio de este bucle, los archivos que no se han analizado
# lo harán una vez y en orden de llegada, para que los
# resultados sean coherentes con el orden en el que se
# ha producido la actividad electrofisiológica. Los
# archivos que ya se han analizado no lo volverán a hacer. 

no_files = len(os.listdir(templ)) # número de plantillas en la carpeta de plantillas.
file_ids = np.linspace(1,no_files,no_files) # vector con los índices del número de plantillas o canales.

result_number = 1 # índice para el número de resultado. Servirá para nombrar los archivos TXT con los resultados e irá incrementándose.
old_files = [] # lista vacía que contendrá la localización de los archivos que ya se han comparado y no tienen que volver a hacerlo.
current_path = os.getcwd() # localización desde donde se está ejecutando el script.
inbound_signals_path = current_path + "\\inboundSignals\\" # localización de la carpeta que recibe los archivos de señales entrantes.

print("System ready to process inbound signals.\n") # mensaje de información.

while True: # bucle que se ejecuta indefinidamente.
    file_list = os.listdir("inboundSignals") # enlista los archivos de la carpeta que recibe los archivos de las señales entrantes.
    new_files = [] # lista vacía con cada iteración del bucle que contendrá los archivos cuyas señales han de compararse.

    for signal_file in file_list: # bucle que itera sobre los archivos de señales de la carpeta.
        if signal_file.split(".")[1] in ["txt","smr","plx"] and signal_file not in old_files: # se ejecuta si el archivo es de algún
        # formato reconocido por el script, y si además no se ha analizado antes.
            print("New inbound file (" + signal_file +
                  ") detected in inbound signals directory.") # mensaje de información de detección del archivo.
            file_path = inbound_signals_path + signal_file # localización del archivo de señales entrante.
            new_files.append(file_path) # se incorpora la localización del archivo a la lista de archivos no analizados.
            old_files.append(signal_file) # se incorpora la localización del archivo a la lista de archivos ya analizados.
        
    new_files.sort(key = os.path.getctime) # se ordenan los archivos todavía no analizados por su orden de llegada a la carpeta. 

    if len(new_files) > 0: # se ejecuta si hay nuevos archivos en la carpeta que todavía no se han analizado.
        for new_file in new_files: # bucle que itera sobre cada uno de los archivos no analizados.
            output_name = "result" + str(result_number) + ".txt" # se nombra el archivo que contendrá los resultados de la comparación.
            output_file = open(output_name, "w") # se crea el archivo.
            output_file.write(comparator(template = dic,
                                         max_numb_pnts = pnts,
                                         what_file = new_file,
                                         is_arith = mean_calc)) # se sobreescribe el archivo con los resultados de similitud.
            output_file.close() # se cierra el archivo.
            os.rename(output_name, "results/"+output_name) # se mueve el archivo a la carpeta destinada a acumular los resultados.
            print(output_name + " file generated from " +
                  new_file + " file is now available in " +
                  "the results directory.") # mensaje de información de que los resultados ya se han emitido en un archivo TXT.
            result_number = result_number + 1 # el número de archivo de resultados aumenta en una unidad.