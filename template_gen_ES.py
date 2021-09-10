###################################################
###################################################
###                                             ###
###                INTRODUCCIÓN                 ###
###                                             ###
###################################################
###################################################

# Este programa se ha hecho con motivo de crear un
# algoritmo para la comparación de señales, de modo
# que se compute la similitud que hay entre dos
# señales, que vendrá representada como una proporción.
# Para este fin, también se ha tenido que elaborar un
# segundo script con el se realiza el último cálculo
# del algoritmo.

# Con este programa, se van a generar una serie de archivos
# a partir de un conjunto de señales, que representarán
# plantillas promedio de todas las señales que han contribuido
# a su generación. Luego, se usarán estas plantillas
# para compararlas con señales entrantes, y se emitirá
# el resultado del algoritmo en otro archivo TXT.

# Cada una de las plantillas va a estar formada por
# dos columnas, que constituyen dos vectores de números.
# La primera columna contendrá los valores de media
# aritmética de la amplitud de cada frecuencia específica
# de las señales que se han utilizado para hacer las
# plantillas. Por otro lado, la segunda columna
# contendrá los valores de desviación estándar de la
# frecuencia correspondiente en cada caso.

# A partir de los valores de media aritmética y de
# desviación estándar asignados a cada frecuencia, se
# puede trazar una distribución normal que servirá para
# comparar cada frecuencia de la plantilla con las
# del dominio de frecuencia de las señales entrantes.
# Dependiendo de cómo de próximos estén los valores de
# amplitud de las frecuencias de la señal entrante a
# las de la media de la plantilla promedio, considerando
# la distribución normal, se le atribuirá una proporción
# de similitud u otra a esa frecuencia. Cuando se ha computado
# esta comparación para todas las frecuencias, se calcula
# una media final para establecer la proporción de parecido
# entre la señal promedio y la señal entrante.

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
# - pandas (pd): Se ha usado para emitir las plantillas
# promedio de las señales como archivos TXT.
# - neo: Se ha utilizado para leer archivos que contienen
# señales típicamente fisiológicas en formatos comunes
# como SMR o PLX.

import sys
import os
import numpy as np
import pandas as pd
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

# - hertzs(time_vector): requiere del módulo NumPy (np). Esta función
# necesita de un argumento (time_vector) que consiste en un vector que
# representa puntos en el tiempo. A partir de este vector,
# se crea un vector de frecuencias. Este vector de frecuencias
# es útil para representar el dominio de frecuencia de una señal
# a partir de su dominio de tiempo.

# Los vectores de frecuencias se han generado usando la función
# linspace() del módulo NumPy (np). Para crear un vector con esta
# función se indica, primero, el valor inicial, luego el
# valor final del vector y por último el número de puntos que
# va a contener. El vector producido es un vector lineal y
# la diferencia entre dos puntos consecutivos es siempre la misma.

# Si el vector de tiempo tiene un número de puntos par,
# el vector de frecuencia correspondiente se elabora con la función
# linspace() a partir del cociente entre la longitud del vector de
# tiempo y el último valor del mismo, como punto final en el vector
# de frecuencias, y considerando un número de puntos igual a la
# longitud del vector de tiempo más uno. En cambio, si el vector de
# tiempo tiene un número de puntos impar, el vector de frecuencia se
# elabora a partir del cociente entre la longitud del vector de
# tiempo y el último valor del mismo, como punto final en el vector
# de frecuencias, menos uno, y el número de puntos será igual a la
# longitud del vector de tiempo.

def hertzs(time_vector): # requiere del módulo NumPy (np).
    time_len = len(time_vector) # longitud del vector de tiempo.
    if len(time_vector)%2 == 0: # se ejecuta si la longitud es un número par.
        hz = np.linspace(0,
                        time_len/time_vector[time_len-1],
                        time_len + 1) # vector de frecuencias.
        return hz # devuelve el vector de frecuencias.
    else: # se ejecuta si la longitud es un número impar.
        hz = np.linspace(0,
                         (time_len/time_vector[time_len-1])-1,
                         time_len) # vector de frecuencias.
        return hz # devuelve el vector de frecuencias.

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

###################################################
###################################################
###                                             ###
###    EVALUACIÓN DEL FORMATO DE LOS ARCHIVOS   ###
###                                             ###
###################################################
###################################################

# En esta primera parte del programa, se hacen varias comprobaciones
# para ver si se pueden crear las plantillas a partir de los archivos
# de las señales. Las comprobaciones que se hacen son las siguientes
# y en este orden:

# 1) Se comprueba si se ha indicado en el prompt la localización
# de los archivos de las señales que se van a analizar.

# 2) Si la carpeta de los archivos de las señales existe.

# 3) Si la carpeta realmente contiene archivos.

# 4) Si los archivos de las señales tienen un formato reconocido para
# señales electrofisiológicas y si tienen todos el mismo formato
# para asegurar que todas las señales vienen del mismo experimento.

# Como se puede observar, en el apartado 3) se crea una variable
# (no_rows) que alberga la misma información que la variable que
# contiene el número de archivos que se vayan a usar para crear
# las plantillas (no_files). Esto se debe a que, para generar las
# plantillas, se creará una matriz cuyas dimensiones vendrán
# determinadas por el número de archivos, el número de datos por
# cada señal, y el número de señales por cada archivo. De esta
# forma, queda más clara la utilidad de las variables.

#####################################################################
## 1) Se comprueba si se ha indicado en el prompt la localización  ##
## de los archivos de las señales que se van a computar.           ##
#####################################################################

print("\nLaunching " + sys.argv[0] + ".\n") # mensaje de inicialización.

try: # se trata de ejecutar. No se terminará de ejecutar si da error.
    sample_signals_path = sys.argv[1] # path del directorio de las señales.
except: # se ejecuta si no hay un argumento al lanzar el programa.
    print("ERROR: " + sys.argv[0] +
    " requires sample signals directory path as first" + 
    " argument so the program executes correctly. Please," +
    " insert sample signals directory path as a first " +
    "argument.") # mensaje de error.
    quit() # se cierra el programa.

###########################################################
## 2) Se comprueba si la carpeta de los archivos de las  ##
## señales existe.                                       ##
###########################################################

all_files_and_dirs = os.listdir() # lista de todo lo de la carpeta donde está el programa.
dirs_only = [] # lista vacía. Contendrá el nombre de solo los directorios.
for element in all_files_and_dirs: # bucle sobre todos los elementos.
    if "." not in element: # se ejecuta si su nombre no tiene un punto.
        dirs_only.append(element) # se añade en la carpeta de directorios.

is_dir = False # variable booleana. 
for directory in dirs_only: # itera con los nombres de los directorios.
    if directory in sample_signals_path: # se ejecuta si el directorio de las señales existe.
        is_dir = True # la variable booleana pasa a ser True.
if is_dir == False: # se ejecuta si la variable booleana es False.
    print("ERROR: " + sys.argv[0] +
    " requires a sample signals directory path that exists" +
    " as first argument so the program executes correctly. " +
    "Please, insert a directory path as a first argument.\n") # mensaje de error.
    quit() # se cierra el programa.

#################################################################
## 3) Se comprueba si la carpeta realmente contiene archivos.  ##
#################################################################

sample_list = os.listdir(sample_signals_path) # enlista archivos de las señales.
no_files = len(sample_list) # número de archivos.
no_rows = no_files # el número de archivos es igual al número de filas de las submatrices.

if no_files == 0: # se ejcuta si no hay archivos.
    print("No files found in signal files directory. " +
          "Shutting down program.\n") # mensaje de error.
    quit() # se cierra el programa.

#####################################################################
## 4) Se comprueba si los archivos de las señales tienen un        ##
## formato reconocido para señales electrofisiológicas y si tienen ##
## todos el mismo formato para asegurar que todas las señales      ##
## vienen del mismo experimento.                                   ##
#####################################################################

file_format_list = [] # lista vacía que acumulará los tipos de formatos.

print("Detecting files format...") # mensaje de información de que se va a comprobar el formato de los archivos de señales.

for File in sample_list: # bucle que itera sobre todos los archivos.
    file_format_list.append(File.split(".")[1]) # guarda el formato del archivo en la lista vacía.

if file_format_list.count(file_format_list[0]) == no_files: # se ejecuta si todos los archivos tienen un mismo formato.
    if file_format_list[0] in ["txt", "smr", "plx"]: # se ejecuta si ese formato es uno de los reconocidos por el script.
        file_format = file_format_list[0] # se guarda el formato en una variable.
    else: # se ejecuta si el script no reconoce alguno de los formatos detectados.
        print("This file format can't be proccessed by " +
              "this program. The only program files that " +
              "can be used by this algorithm are: " +
              "text (TXT), Spike2 (SMR) and Plexon (PLX)" +
              "files. Shutting down program.") # mensaje de error.
        quit() # se cierra el programa.
else: # se ejecuta si no todos los archivos tienen un mismo formato.
    print("Multiple file formats detected. Please, use " +
          "only one kind of format in order to generate " +
          "a result. Shutting program down.") # mensaje de error.
    quit() # se cierra el programa.

print(file_format.upper() +
      " file format detected in all files.\n") # mensaje que informa sobre el formato de los archivos.

###################################################
###################################################
###                                             ###
###    CREACIÓN DE LA MATRIZ DE AMPLITUDES      ###
###       DE FRECUENCIAS DE LAS SEÑALES         ###
###                                             ###
###################################################
###################################################

# La manera que tienen de generarse las plantillas consiste en
# extraer los datos de las señales, aplicar la transformada de
# Fourier para obtener los coeficientes de Fourier, después
# calcular los valores de amplitud a partir de los coeficientes
# para así obtener el dominio de frecuencia de las señales, y por
# último hallar la media y la desviación estándar del valor de
# amplitud, frecuencia por frecuencia, usando como muestra el
# dominio de frecuencia de todas las señales.

# Con respecto al número de frecuencias que se van a considerar
# para elaborar las plantillas, se han ideado dos cálculos
# diferentes. El primero consiste en crear la plantilla
# considerando un porcentaje de la suma acumulada de las amplitudes
# del dominio de frecuencia, para de esa forma analizar el
# porcentaje de la información de la señales que se seleccione.
# Esta forma de crear las plantillas se basa en que las señales
# electrofisiológicas han demostrado estar compuestas por
# ondas con frecuencias muy bajas, y de las cuales las mayores
# amplitudes las poseen las frecuencias más bajas, de en torno
# a 1 Hz. El otro consiste en utilizar solo las primeras 'n'
# frecuencias, partiendo desde la frecuencia de 0 Hz. Además de
# que con este algoritmo se tiene en cuenta que las señales
# estarán formadas por ondas de frecuencias muy bajas, de esta
# manera se pueden elaborar plantillas de señales electrofisiológicas
# que no detectan apenas actividad, para que solo consideren un número
# reducido de frecuencias, en contraposición al número elevado de
# frecuencias que contemplaría una plantilla creada a partir de
# la suma acumulada de las amplitudes en el dominio de frecuencia
# si no se está registrando actividad electrofisiológica.
# Considerando siempre la naturaleza particular de las señales
# electrofisiológicas por estar formadas por ondas de frecuencias
# muy bajas, ambos algoritmos para la generación de las plantillas
# persiguen que el número de frecuencias que contengan en ellas
# sea relativamente pequeño, siempre sin ocasionar una pérdida de
# información tal que las señales promedio que quedan registradas
# pierdan sus características, debido a que la comparación
# de señales que se realizará por medio del segundo programa
# utiliza un bucle para comparar la similitud entre la señal
# de la plantilla y una señal entrante, comparando frecuencia
# por frecuencia, para luego calcular un valor final de
# similitud entre ambas.

Y_or_n = input("Would you like to consider the first " +
"'n' frequencies for making the template(s)? (Else, the " +
"program will consider a proportion of the cummulative sum " +
"of the data for making them.) [Y/n] ").upper() # variable para considerar la suma acumulada de los datos o las primeras frecuencias.

if Y_or_n not in ["Y","N","YES","NO"]: # se ejecuta si la variable introducida no es la esperada.
    print("No appropiate input was introduced. Shutting " +
    "down " + sys.argv[0] + ".") # mensaje de error.
    quit() # se cierra el programa.
if Y_or_n in ["Y","YES"]: # se ejecuta si se pretenden usar las 'n' primeras frecuencias para hacer la matriz.
    print("\nMaking the templates considering first " +
    "'n' frequencies.") # mensaje de información.
if Y_or_n in ["N","NO"]: # se ejecuta si se pretende usar la suma acumulada de las amplitudes para hacer la matriz.
    print("\nMaking the templates considering the " +
    "cummulative sum of data amplitudes.") # mensaje de información.

# El número de coeficientes de Fourier es igual al número de
# datos de cada señal. Los coeficientes de cada señal se acumulan
# en forma de vectores lineales. Para calcular la media aritmética
# y la desviación estándar, punto por punto, de todos los vectores,
# se necesita que el número de puntos entre vectores sea el mismo.
# Para ello, al aplicar la transformada de Fourier, se estandariza
# el número de coeficientes que se van a obtener a partir del mayor
# número de puntos, determinado por la señal que más puntos contenga.
# De este modo, la transformada de Fourier puede aplicarse minimizando
# el número de coeficientes con los que se tendrá que operar sin que
# haya pérdida de información.

max_time_vector = np.array([]) # vector vacío que acumulará el vector de tiempo con más puntos de todas las señales.
max_pnts = 0 # variable que contendrá cuál es el mayor número de puntos.
no_channels = 0 # variable que contendrá cuál es el número de canales.

# Las señales están grabadas en archivos cuyos formatos son
# habituales en el registro de señales electrofisiológicas. Estos
# archivos se generan por medio del instrumental que se utiliza
# para registrar señales que proceden de actividad biológica.
# Entre los formatos de archivos que contienen información de
# señales biológicas, se encuentran por ejemplo los formatos SMR o
# PLX. Estos archivos contienen metadatos sobre las condiciones de
# registro de las señales (como la frecuencia de muestreo o el tiempo
# de duración de las señales) además de los valores de amplitud
# de las señales a lo largo del tiempo.

# En esta clase de archivos, se pueden registrar simultáneamente
# varias señales procedentes del mismo experimento. Las señales
# electrofisiológicas se obtienen tras colocar uno o varios
# electrodos sobre el animal sometido a los experimentos.
# Utilizando varios electrodos dispuestos en diferentes partes
# del mismo organismo, se pueden registrar varias señales para
# analizar la actividad electrofisiológica diferencial que sucede
# en un animal cuando éste está sometido a las mismas condiciones
# experimentales. En este caso, se dice que cada señal proviene de
# un canal diferente.

# En los archivos de tipo SMR y PLX, a veces se registran dos o
# más señales diferentes en un mismo canal. Las señales registradas
# aparecen formando parte de una matriz, donde los datos de cada
# señal constituye una columna. Para extraer las señales individuales
# de aquí, con este programa se transpone la matriz, y después se
# itera sobre cada fila para obtener sus datos por separado.

# Para calcular el número de canales que hay en total, hay una
# operación que se hace dentro de un bucle solo en uno de los archivos
# de señales, contando todos los canales o señales que posee, dando por
# hecho que todos los archivos contendrán el mismo número de canales.
# De esta manera, se obtiene el número de canales que hay por cada archivo,
# necesario para construir las plantillas.

# También hay una parte del código dentro de los bucles que solo se
# ejecuta si se van a calcular las plantillas considerando las
# 'n' primeras frecuencias de las señales. Por medio de esa sección
# del código, se guarda en una variable el vector de tiempo de la
# señal que contenga más puntos. El número de puntos de una señal
# y del vector de tiempo dependen tanto de su duración, como de la
# tasa de muestreo. A partir del vector de tiempo, se obtiene el vector
# de frecuencias, con el que se puede calcular el número de puntos
# en el dominio de frecuencia que están abarcados hasta una frecuencia
# límite ('n'). Esta forma de generar las plantillas, como se ha indicado
# antes, se aprovecha de la naturaleza de las señales electrofisiológicas,
# formadas principalmente por ondas con frecuencias muy bajas (de en torno
# a 0 y 15 Hz). Así, las plantillas que representan señales promedio se
# compararán con otras señales entrantes solo considerando el valor
# de amplitud de las frecuencias comprendidas entre los 0 Hz y los
# 'n' Hz.

# A pesar de la similaridad entre los dos trozos de código para
# analizar los archivos SMR y PLX, cuando se analizan los archivos
# PLX, las líneas de código que son iguales se encuentran iterándose
# en otro bucle anterior (comparar líneas 447 y 448, con las
# líneas 466, 467 y 468). Esa es la razón por la que no se ha
# abreviado el código de otra forma.

first_file = True # variable booleana que sirve para ejecutar una parte del código dentro de un bucle solo una vez.

if file_format == "txt": # se ejecuta si el formato de los archivos es TXT.
    for File in sample_list: # bucle que itera sobre cada archivo.
        data = np.loadtxt(sample_signals_path +
                          "/" + File,
                          delimiter = "\t") # se lee el contenido del archivo usando una función de NumPy.
        data_length = np.shape(data)[0] # longitud de la señal.
        if data_length > max_pnts: # se ejecuta si la variable max_pnts es menor que la longitud de la señal.
            max_pnts = data_length # se sobreescribe la variable max_pnts.
            if Y_or_n in ["Y","YES"]: # se ejecuta si se van a usar las primeras 'n' frecuencias para hacer la plantilla.
                max_time_vector = data[:,0] # vector del tiempo.
                sampling_rate = 1/(max_time_vector[1]-max_time_vector[0]) # tasa de muestreo.
    no_channels = np.shape(data)[1]-1 # número de señales en el archivo (número de canales).

elif file_format == "smr": # se ejecuta si el formato de los archivos es SMR.
    for File in sample_list: # bucle que itera sobre cada archivo.
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format) # se lee el archivo.
        for seg in data.segments: # se itera sobre cada una de las partes del archivo.
            for an_sig in seg.analogsignals: # se itera sobre cada una de las señales del archivo.
                array = np.transpose(np.array(an_sig)) # se transpone la matriz que contiene a las señales.
                time = an_sig.times.rescale("s").magnitude # se genera el vector de tiempo de la señal.
                time_len = len(time) # se mide la longitud de la señal.
                if time_len > max_pnts: # se ejecuta si la longitud de la señal es mayor que la variable max_pnts.
                    max_pnts = time_len # max_pnts se sobreescribe con esa longitud.
                    if Y_or_n in ["YES","Y"]: # se ejecuta si se quiere hacer las plantillas usando las primeras 'n' frecuencias.
                        max_time_vector = time # se guarda el vector de tiempo.
                        sampling_rate = an_sig.sampling_rate # se registra su tasa de muestreo.
                if first_file == True: # se ejecuta si el bucle está iterando sobre el primer archivo.
                    for ind_sig in array: # bucle que itera cada una de las señales registradas en cada canal.
                        no_channels = no_channels + 1 # aumenta el número de canales en una unidad.
        first_file = False # la variable booleana pasa a ser igual a False.

elif file_format == "plx": # se ejecuta si el formato de los archivos es PLX.
    for File in sample_list: # bucle que itera sobre cada archivo.
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format) # se lee el archivo.
        for block in data: # se itera sobre cada uno de los bloques de datos.
            for seg in block.segments: # se itera sobre cada una de las partes del archivo.
                for an_sig in seg.analogsignals: # se itera sobre cada una de las señales del archivo.
                    array = np.transpose(np.array(an_sig)) # se transpone la matriz que contiene a las señales.
                    time = an_sig.times.rescale("s").magnitude # se genera el vector de tiempo de la señal.
                    time_len = len(time) # se mide la longitud de la señal.
                    if time_len > max_pnts: # se ejecuta si la longitud de la señal es mayor que la variable max_pnts.
                        max_pnts = time_len # max_pnts se sobreescribe con esa longitud.
                        if Y_or_n in ["YES","Y"]: # se ejecuta si se quiere hacer las plantillas usando las primeras 'n' frecuencias.
                            max_time_vector = time # se guarda el vector de tiempo.
                            sampling_rate = an_sig.sampling_rate # se registra su tasa de muestreo.
                    if first_file == True: # se ejecuta si el bucle está iterando sobre el primer archivo.
                        for ind_sig in array: # bucle que itera cada una de las señales registradas en cada canal.
                            no_channels = no_channels + 1 # aumenta el número de canales en una unidad.
        first_file = False # la variable booleana pasa a ser igual a False.

channel_list = np.linspace(1,no_channels,no_channels) # vector que contiene el número de los canales.
no_arr = no_channels # el número de submatrices será igual al número de canales.
no_cols = max_pnts # el número de columnas en la matriz será igual al número máximo de puntos de las señales.

# En este proyecto, el número de plantillas será igual al número de
# canales usados para registrar las señales que provienen de
# electrodos dispuestos en distintas regiones anatómicas.

# Esto nos deja con tres variables de las que dependerá el volumen de los
# resultados: el número de archivos a procesar para hacer las plantillas,
# la longitud de las señales en función de su número de puntos y el número
# de señales o de canales por archivo.

# NumPy es un módulo de Python que permite realizar un plétora de cálculos
# matemáticos, entre los que encontramos algoritmos para hacer cálculo
# matricial y de procesamiento de señales, como la transformada de
# Fourier. Este módulo introduce un nuevo tipo de variable: Las matrices.
# Las matrices son variables que permiten almacenar otras variables a lo
# largo de tantas dimensiones como se quiera y siempre respetando el
# tamaño de cada dimensión.

# Para computar todas las plantillas de manera rápida y eficiente, se
# han decidido emplear matrices tridimensionales, donde existen tantas
# submatrices como número de canales haya en los archivos, tantas filas
# por matriz como número de archivos haya, y tantas columnas como
# número de puntos tenga la señal con más puntos. De esta forma, cada
# submatriz albergará todos los datos necesarios para calcular cada
# una de las plantillas necesarias, y al poder aplicárseles el cálculo
# matricial por medio de las funciones del módulo NumPy, el cómputo
# de las plantillas se hará mucho más rápido.

arr = np.zeros([no_arr,no_rows,no_cols]) # se genera la matriz tridimensional vacía que contendrá los datos para las plantillas.

if file_format == "txt": # se ejecuta si el formato de los archivos es TXT.
    for File in os.listdir(sample_signals_path): # bucle que itera sobre los archivos de señales.
        data = np.loadtxt(sample_signals_path + "/" + File,
                          delimiter = "\t") # se lee el archivo.
        file_idx = os.listdir(sample_signals_path).index(File) # registra el índice del archivo en la lista de archivos.
        no_row = file_idx # atribuye el índice de archivo a un índice de fila de la matriz.
        for channel in channel_list: # bucle que itera sobre cada índice de cada canal del vector de canales.
            no_arr = int(channel-1) # se genera un índice de submatriz a partir del índice de cada canal.
            fCoefs = (np.fft.fft(data[:,int(channel)],
                                 n=no_cols)/
                      len(data[:,int(channel)])) # se calculan los coeficientes de Fourier con la señal.
            ampls = np.absolute(fCoefs) # se calcula la amplitud de las frecuencias a partir de los coeficientes.
            ampls[1:len(ampls)] *= 2 # se normaliza el valor de la amplitud.
            arr[no_arr,no_row,:] = ampls # se insertan los valores de amplitud por orden en la matriz.

elif file_format == "smr": # se ejecuta si el formato de los archivos es SMR.
    for File in sample_list: # bucle que itera sobre los archivos de señales.
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format) # se lee el archivo.
        file_idx = sample_list.index(File) # registra el índice del archivo en la lista de archivos.
        no_row = file_idx # atribuye el índice de archivo a un índice de fila de la matriz.
        channel_idx = 0 # índice del canal inicial.
        for seg in data.segments: # bucle que itera sobre las partes del archivo.
            for an_sig in seg.analogsignals: # bucle que itera sobre cada canal.
                array = np.transpose(np.array(an_sig)) # se transpone la matriz que contiene la señal o señales.
                for ind_sig in array: # bucle que itera sobre cada una de las filas de la matriz o señal.
                    fCoefs = (np.fft.fft(ind_sig,
                              n = no_cols)/
                              len(ind_sig)) # se calculan los coeficientes de Fourier de una señal.
                    ampls = np.absolute(fCoefs) # se calculan las amplitudes de las frecuencias.
                    ampls[1:len(ampls)] *= 2 # se normalizan las amplitudes.
                    arr[channel_idx,no_row,:] = ampls # se insertan los valores de amplitud por orden en la matriz.
                    channel_idx = channel_idx + 1 # se incrementa en uno el índice del canal.

elif file_format == "plx": # se ejecuta si el formato de los archivos es PLX.
    for File in sample_list: # bucle que itera sobre los archivos de señales.
        data = neo_reader(file_name = sample_signals_path + File,
                          file_format = file_format) # se lee el archivo.
        file_idx = sample_list.index(File) # registra el índice del archivo en la lista de archivos.
        no_row = file_idx # atribuye el índice de archivo a un índice de fila de la matriz.
        channel_idx = 0 # índice del canal inicial.
        for block in data: # bucle que itera sobre los bloques de datos del archivo.
            for seg in block.segments: # bucle que itera sobre las partes del archivo.
                for an_sig in seg.analogsignals: # bucle que itera sobre cada canal.
                    array = np.transpose(np.array(an_sig)) # se transpone la matriz que contiene la señal o señales.
                    for ind_sig in array: # bucle que itera sobre cada señal.
                        fCoefs = (np.fft.fft(ind_sig,
                                  n = no_cols)/
                                  len(ind_sig)) # se calculan los coeficientes de Fourier.
                        ampls = np.absolute(fCoefs) # se calculan las amplitudes de las frecuencias.
                        ampls[1:len(ampls)] *= 2 # se normalizan las amplitudes.
                        arr[channel_idx,no_row,:] = ampls # se insertan los valores de amplitud por orden en la matriz.
                        channel_idx = channel_idx + 1 # se incrementa en uno el índice del canal. 

###################################################
###################################################
###                                             ###
### REFINANDO Y CREANDO LAS PLANTILLAS FINALES  ###
###                                             ###
###################################################
###################################################

if Y_or_n in ["Y","YES"]: # se ejecuta si se quiere crear las plantillas usando los datos de las 'n' primeras frecuencias.
    limit_freq = input("Select the limit frequency (all " +
    "frequency amplitude data below it will be " +
    "added into the templates) (NOTE: This value must " +
    "be between 0 and " + str(int(round(sampling_rate/2))) +
    "): ") # variable que se introduce para determinar hasta qué frecuencia se tendrá en cuenta para hacer las plantillas.
    try: # se ejecutará el siguiente fragmento de código si no hay errores.
        limit_freq = float(limit_freq) # se convierte el dato introducido en un número de punto flotante (float).
    except: # se ejecuta si hay algún error en la sección de código anterior.
        print("ERROR: limit frequency type detected is not " +
        "valid. Shutting down program.") # mensaje de error.
        quit() # se cierra el programa.
    print("")
    hz = hertzs(time_vector = max_time_vector) # se genera el vector de frecuencias a partir del vector de tiempo.
    limit_idx = np.sum(hz < limit_freq) # se obtiene el índice de la frecuencia introducida antes para el vector de frecuencias.
    arr = arr[:,:,0:limit_idx] # se recorta la matriz de las amplitudes de las frecuencias usando este índice.
    mean_matrix = np.zeros([no_channels,limit_idx]) # se crea la matriz vacía para las medias de las amplitudes.
    std_matrix = np.zeros([no_channels,limit_idx]) # se crea la matriz vacía para las desviaciones estándar.
elif Y_or_n in ["N","NO"]: # se ejecuta si se quiere crear las plantillas considerando la suma acumulada de las amplitudes.
    mean_matrix = np.zeros([no_channels,max_pnts]) # se crea la matriz vacía para las medias de las amplitudes.
    std_matrix = np.zeros([no_channels,max_pnts]) # se crea la matriz vacía para las desviaciones estándar.

for idx in channel_list: # bucle que itera para cada índice del vector de índices de los canales.
    index = int(idx-1) # se normaliza el índice.
    mean = np.mean(arr[index,:,:], axis = 0) # se calcula el dominio de frecuencia promedio por canal.
    mean_matrix[index,:] = mean # se inserta el vector que representa este promedio en la matriz de medias.
    std = np.std(arr[index,:,:], axis = 0) # se calcula la desviación estándar promedio por canal.
    std_matrix[index,:] = std # se inserta este vector en la matriz de desviaciones estándar.

if Y_or_n in ["N","NO"]: # se ejecuta si se quiere crear las plantillas considerando la suma acumulada de las amplitudes.
    if max_pnts%2 == 0: # se ejecuta si el número de puntos de la señal es par.
        mean_matrix = mean_matrix[:,0:int(max_pnts/2)] # se inserta el vector de amplitudes promedio en la matriz de medias.
    else: # se ejecuta si el número de puntos de la señal es impar.
        mean_matrix = mean_matrix[:,0:int(max_pnts/2)+1] # se inserta el vector de amplitudes promedio en la matriz de medias.

templ_dir = "templates" # nombre de la carpeta que contendrá las plantillas.
reset_dir(templ_dir) # reseteo de la carpeta de las plantillas.

print("Resetting template directory... Done.") # mensaje de información.

if Y_or_n in ["N","NO"]: # se ejecuta si se quiere crear las plantillas considerando la suma acumulada de las amplitudes.
    prop = input("Select the frequency amplitudes cumulative"+
    " sum proportion that is going to be considered (NOTE:"+
    " Given value must be a number between 0 and 1): ") # variable introducida igual a la proporción para la suma acumulada de los datos.
    print("")
    try: # se ejecutará el siguiente fragmento de código si no hay errores. 
        prop = float(prop) # transforma la variable introducida en un número decimal (float).
    except: # se ejecuta si hay algún error en la sección de código anterior.
        print("Input value not valid. Shutting down program.") # mensaje de error.
        quit() # se cierra el programa.
    if prop < 0 or prop > 1: # se ejecutará si la proporción introducida es menor que 0 o mayor que 1.
        print("Input value not valid. Shutting down program.") # mensaje de error.
        quit() # se cierra el programa.

row_idx = 0 # índice inicial de las filas de las matrices de medias y desviaciones estándar.

for row in mean_matrix: # bucle que itera sobre cada fila de la matriz de las medias de las frecuencias.
    if Y_or_n in ["N","NO"]: # se ejecuta si se quiere crear las plantillas considerando la suma acumulada de las amplitudes.
        one_p = np.sum(row) # suma total de todas las amplitudes de las frecuencias de una señal promedio.
        wanted_cumsum = one_p * prop # proporción de la suma calculada a partir de la proporción introducida.
        idx = np.sum(np.cumsum(row) < wanted_cumsum) + 1 # índice del valor a partir del que se alcanza la proporción de la suma acumulada.
        channel_template = np.zeros([2,idx]) # matriz vacía con la forma de la plantilla para la señal promedio de un canal.
        channel_template[0,:] = mean_matrix[row_idx,0:idx] # se insertan los valores de medias en la matriz de la plantilla.
        channel_template[1,:] = std_matrix[row_idx,0:idx] # se insertan los valores de desviaciones estándar en la matriz de la plantilla.
    elif Y_or_n in ["Y","YES"]: # se ejecuta si se quiere crear las plantillas usando los datos de las 'n' primeras frecuencias.
        channel_template = np.zeros([2,limit_idx]) # matriz vacía con la forma de la plantilla para la señal promedio de un canal.
        channel_template[0,:] = mean_matrix[row_idx,:] # se insertan los valores de medias en la matriz de la plantilla.
        channel_template[1,:] = std_matrix[row_idx,:] # se insertan los valores de desviaciones estándar en la matriz de la plantilla.
    templ_trans = np.transpose(channel_template) # se transpone la matriz de la plantilla, con las medias y desviaciones.
    templ_name = "templ_channel" + str(int(
                 channel_list[row_idx])) + ".txt" # se crea el nombre del archivo con la información de la plantilla para un canal.
    templ_path = templ_dir + "/" + templ_name # se indica la localización donde se ha de crear la plantilla.
    pd.DataFrame(templ_trans).to_csv(templ_path,
                                     sep = "\t",
                                     index = False,
                                     header = False) # se crea un archivo nuevo con la información de la plantilla de un canal.
    row_idx = row_idx + 1 # aumenta en uno el índice de las filas

print("Creating templates... Done.") # mensaje de información.

# Finalmente, se crea un archivo de texto que contiene el número de
# coeficientes de Fourier estandarizado para todas las señales,
# que se usó para que se pudiera computar la media de las amplitudes
# y la desviación estándar, frecuencia por frecuencia. Este mismo
# número de puntos se va a considerar cuando se computen los
# coeficientes de Fourier de una señal entrante que se quiera
# comparar con la señal promedio que represente la plantilla con
# el segundo script. Otro de los datos que contiene este archivo,
# es el número máximo de canales detectado por archivo. Este valor
# se pretende guardar para hacer una modificación futura en el
# programa de comparación de señales, para que sólo se vayan a analizar
# archivos de señales que contengan el mismo número de canales que
# tenían los archivos usados para hacer las plantillas, como una
# forma de control de seguridad del programa.

output_content = str(max_pnts) + "\n" + str(no_channels) # string que contiene número máximo de puntos de las señales y de canales.
max_output = open("no_cols_and_channels.txt", "w") # se crea un archivo de texto vacío. 
max_output.write(output_content) # se sobreescribe con el string con los números de puntos y de canales.
max_output.close() # se cierra el archivo.

print("Creating file containing maximum number of points" +
      " per signal and number of channels... Done.\n") # mensaje de información.