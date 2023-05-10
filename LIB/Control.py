import pandas as pd
from tkinter.filedialog import askopenfilename
from tkinter.messagebox import showinfo
import numpy as np
import os

# Leer Excel con las tablas de las escalas
Categorias = pd.read_excel('Categorias.xlsx')

# Preguntar por el Excel con los Archivos de 'Mis Comprobantes'
Archivos = askopenfilename(title="Seleccione el Excel con las ubicaciones Archivos de 'Mis Comprobantes'")

# Leer el Excel con los Archivos de 'Mis Comprobantes'
Archivos = pd.read_excel(Archivos) 

# transformar la primer columna en una lista
Archivos = Archivos.iloc[:,0].tolist()

# Crear un DataFrame vacio para guardar los datos consolidados
Consolidado = pd.DataFrame()

# Leer cada uno de los archivos de 'Mis Comprobantes' y concat en el DataFrame Consolidado
# Consolidar archivos y renombrar columnas
# consolidadar columnas
for f in Archivos:
    #Si el existe el archivo, leerlo
    if os.path.isfile(f):  
        data = pd.read_excel(f, header = None, skiprows=2 , )
        # si el datsaframe esta vacio, no hacer nada
        if len(data) > 0:

            # Crear la columna 'Archivo' con el ultimo elemento de 'f' separado por "/"
            data['Archivo'] = f.split("/")[-1]
            #data['Archivo'] = f.str.split("/")[-1]
            data['CUIT Cliente'] = data["Archivo"].str.split("-").str[3].str.strip().astype(np.int64)
            data['Fin CUIT'] = data["Archivo"].str.split("-").str[0].str.strip().astype(np.int64)
            Consolidado = pd.concat([Consolidado , data])
        
# Renombrar columnas
Consolidado.columns = [ 'Fecha' , 'Tipo' , 'Punto de Venta' , 'Número Desde' , 'Número Hasta' , 'Cód. Autorización' , 'Tipo Doc. Receptor' , 'Nro. Doc. Receptor/Emisor' , 'Denominación Receptor/Emisor' , 'Tipo Cambio' , 'Moneda' , 'Imp. Neto Gravado' , 'Imp. Neto No Gravado' , 'Imp. Op. Exentas' , 'IVA' , 'Imp. Total' , 'Archivo' , 'CUIT Cliente' , 'Fin CUIT']

#Eliminar las columas 'Imp. Neto Gravado' , 'Imp. Neto No Gravado' , 'Imp. Op. Exentas' , 'IVA'
Consolidado.drop(['Imp. Neto Gravado' , 'Imp. Neto No Gravado' , 'Imp. Op. Exentas' , 'IVA'], axis=1, inplace=True)

#Multiplicar Total tipo de cambio
Consolidado['Imp. Total'] *= Consolidado['Tipo Cambio']   

#Cambiar de signo si es una Nota de Crédito
Consolidado.loc[Consolidado["Tipo"].str.contains("Nota de Crédito"), ['Imp. Total']] *= -1

#Crear columna de 'MC' con los valores 'archivo' que van desde el caracter 5 al 8 en la Consolidado
Consolidado['MC'] = Consolidado['Archivo'].str.split("-").str[1].str.strip()

#Crear Tabla dinámica con los totales de las columnas  'Imp. Total' por 'Archivo'
TablaDinamica = pd.pivot_table(Consolidado, values=['Imp. Total'], index=['CUIT Cliente'], aggfunc={'Imp. Total': np.sum , 'Tipo': 'count'})


# Renombrar la columna 'Tipo' por 'Cantidad de Comprobantes' de la TablaDinamica1 , TablaDinamica2 y TablaDinamica3
TablaDinamica.rename(columns={'Tipo': 'Cantidad de Comprobantes'}, inplace=True)

# Exportar
Archivo_final = pd.ExcelWriter('Control de Monotributistas.xlsx', engine='openpyxl')
Consolidado.to_excel(Archivo_final, sheet_name="Consolidado" , index=False)

#Exportar Tabla Dinámica a la hoja 'TD'
TablaDinamica.to_excel(Archivo_final, sheet_name="TD" , index=True , merge_cells=False)

#Guardar el archivo
Archivo_final.save()

#Mostrar mensaje de finalización
showinfo(title="Finalizado", message="El archivo se ha generado correctamente")