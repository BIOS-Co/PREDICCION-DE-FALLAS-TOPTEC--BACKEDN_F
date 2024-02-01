## funciones del modelo 

import numpy as np
import pandas as pd
import joblib
from django.utils.timezone import make_aware
import os
import io
from datetime import datetime
import pytz


from .models import *
from .serializers import *

## _________________ Funciones Generales ______________________

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_and_process_data(machine, process, data):



    models = {"AUT":{},"NT_M1":{},"NT_M2":{}}


    ## se carga el modelo respectivo y los escaladores:
    root_path = BASE_DIR + "/models"
    root_path2 = BASE_DIR + "\scalers"

    if(machine==1 and process==1):
        for file in os.listdir(root_path+'/best-aut-m1-2'):
            name = file.split('_')[0]
            if '.joblib' in file:
                models["AUT"][name] = joblib.load(f'{root_path}/best-aut-m1-2/{file}')
                #Se cargan los pesos de los escaladores
                models["SCALER_AUT_M1"] = joblib.load(root_path2+'\scaler-aut-m1\scaler.joblib')

    if(machine==1 and process==2):
        for file in os.listdir(root_path+'/best-nt-m1'):
            name = file.split('_')[0]
            if '.joblib' in file:
                models["NT_M1"][name] = joblib.load(f'{root_path}/best-nt-m1/{file}')
                models["SCALER_NT_M1"] = joblib.load(root_path2+'\scaler-nt-m1\scaler.joblib')

    if(machine==2 and process==2):
        for file in os.listdir(root_path+'/best-nt-m2'):
            name = file.split('_')[0] 
            if '.joblib' in file:
                models["NT_M2"][name] = joblib.load(f'{root_path}/best-nt-m2\{file}')
                models["SCALER_NT_M2"] = joblib.load(root_path2+'\scaler-nt-m2\scaler.joblib')



    #salidas
        
    vars_aut = ['Separador','Tallon','Nudo',
                'Fisura','Delaminada','Desborde',
                'Ondulación','Burbuja','Despunte',
                'Basura','Daño Estiba','Manipulación',
                'Mancha']
    
    vars_aut_database = ['Separador','Tallon','Nudo',
                'Fisura','Delaminada','Desborde',
                'Ondulación','Burbuja','Despunte',
                'Basura','Daño_Estiba','Manipulación',
                'Mancha']


    vars_nt_m1 = ['Nudo','Material','Delaminada',
                'Desborde','Rajada','Despunte',
                'Basura','Desmoldeo','Tallon',
                'Mancha']
    vars_nt_m2 = ['Desmoldeo','Mancha','Basura',
                        'Desmoldeadora','Tallon','Rajada',
                        'Mal Corte','Despunte','Descolgada',
                        'Mal Ondulada','Desborde','Nudo',
                        'Manipulación','Delaminada',]
    
    vars_nt_m2_database = ['Desmoldeo','Mancha','Basura',
                        'Desmoldeadora','Tallon','Rajada',
                        'Mal_Corte','Despunte','Descolgada',
                        'Mal_Ondulada','Desborde','Nudo',
                        'Manipulación','Delaminada',]

    df_aut_global = pd.DataFrame()
    df_aut_global_str = pd.DataFrame()

    df_nt_m1_global = pd.DataFrame()
    df_nt_m1_global_str = pd.DataFrame()

    df_nt_m2_global = pd.DataFrame()
    df_nt_m2_global_str = pd.DataFrame()

    FORMA = False 

    arr = np.array(data)

    arr = arr.reshape(1,-1)

    # @markdown ---

    # Codigo

    di_pred = {}
    di_pred_str = {}

    # Se determina que proceso se debe inferir
    print(process)
    print(machine)
    print(arr)
    if (process == 1) and (machine == 1):

        #Se escalan los datos
        arr = models["SCALER_AUT_M1"].transform(arr)

        #Se realiza la inferencia para cada una de las variables
        for v in vars_aut:
            pred = models["AUT"][v].predict(arr)
            di_pred[v] = pred
            di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

        df_aut = pd.DataFrame(di_pred)
        df_aut_str = pd.DataFrame(di_pred_str)

        # Se imprime el dataframe acumulado o la inferencia actual
        if FORMA is True:
            df_aut_global = df_aut_global.append(df_aut, ignore_index=True)
            df_aut_global_str = df_aut_global_str.append(df_aut_str, ignore_index=True)
            print(df_aut_global_str)
            #aux_response1 = df_aut_global_str

            #if df_aut_global.shape[0] > 1:
            #plot_history(df_aut_global)

        else:
            print(df_aut_str)
            aux_response1 = df_aut
            df_aut_global = pd.DataFrame()
            df_aut_global_str = pd.DataFrame()

            try:
                # Crea un diccionario para mapear los resultados y guardar las salidas
                resultados = {}
                # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                analysis_result_instance = None
                for defecto, defecto2 in zip(vars_aut, vars_aut_database):
                    # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                    valor = df_aut_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                    resultados[defecto2] = valor

                # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                for defecto, valor in resultados.items():
                    if valor == 'F':
                        resultados[defecto] = True
                    else:
                        resultados[defecto] = False

                # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                print("resultados", resultados)
                try:
                    data_serializer = AnalysisResultSerializer(data=resultados)
                    if data_serializer.is_valid():
                        analysis_result_instance = data_serializer.save()
                        print("analysis_result_instance", analysis_result_instance)
                        print("Resultado de análisis guardado con éxito.")
                except Exception as e:
                    print("Errores de validación:", data_serializer.errors)
                    print(f"Error al guardar el resultado del análisis: {e}")  


                ## Ahora guardamos los datos de entrada:
                # Crea una instancia de DatosModelo con los datos desempaquetados
                data_flat = data
                print("data_flat[0]", data_flat[0])

                datos_dict = {
                    'PP_Hidro_Cemento_Kg': data_flat[0],
                    'PP_Hidro_Carbonato_Kg': data_flat[1],
                    'PP_Hidro_Silice_Kg': data_flat[2],
                    'PP_Hidro_Celulosa_Kg': data_flat[3],
                    'PP_Hidro_Hidroxido_Kg': data_flat[4],
                    'PP_Hidro_SolReales_porcentage': data_flat[5],
                    'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                    'PP_Refi_EE_AMP': data_flat[7],
                    'PP_Refi_CelulosaH_porcentage': data_flat[8],
                    'PP_Refi_CelulosaS_porcentage': data_flat[9],
                    'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                    'PP_Maq_FlujoFloc_L_min': data_flat[11],
                    'PP_Maq_Resi_ml': data_flat[12],
                    'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                    'PP_Maq_Vel_m_min': data_flat[14],
                    'PP_Maq_FormatoP_PSI': data_flat[15],
                    'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                    'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                    'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                    'PP_Maq_Recir_porcentage': data_flat[19],
                    'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                    'PP_PF_Humedad_porcentage': data_flat[21],
                    'PP_PF_Espesor_mm': data_flat[22],
                    'PP_PF_Dens_g_cm3': data_flat[23],
                    'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                    'PP_Maq_FlocTkS_porcentage': data_flat[25],
                    'PP_Maq_FlocFormS_porcentage': data_flat[26],
                    'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                    'PP_Maq_TCES_porcentage': data_flat[28],
                    'PP_Maq_CilinS_porcentage': data_flat[29],
                    'PP_Maq_Cono1S_porcentage': data_flat[30],
                    'PP_Maq_MolinoS_porcentage': data_flat[31],
                    'PP_Maq_P1H_porcentage': data_flat[32],
                    'PP_Maq_P3H_porcentage': data_flat[33]
                }           

                # Guarda la instancia en la base de datos
                instance_DatosModelo_Set = None
                instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                if instance_DatosModelo.is_valid():
                    validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                    instance_DatosModelo_Set = instance_DatosModelo.save()
                    print("analysis_result_instance 2", instance_DatosModelo_Set)
                    print("Resultado de análisis guardado con éxito.")
                else:
                    print("no valido")

                # Asegúrate de que instance_DatosModelo_Set no es None
                if not instance_DatosModelo_Set:
                    print("La instancia de DatosModelo no se creó correctamente.")
                    return False, "La instancia de DatosModelo no es válida."

                # Verificación de la existencia de analysis_result_instance
                if not analysis_result_instance:
                    print("La instancia de AnalysisResult no se creó correctamente.")
                    return False, "La instancia de AnalysisResult no es válida."


                ## Ahora guardamos los datos en el modelo de prediccion
                machine_instance = Machine.objects.get(id=machine)
                process_instance = Process.objects.get(id=process)

                datos_modelo_predict = DatPrediction(
                    machine=machine_instance,
                    process=process_instance,
                    responsepredict=analysis_result_instance,
                    data_input=instance_DatosModelo_Set,
                )                           
                # Guarda la instancia en la base de datos
                datos_modelo_predict.save()

                return True, analysis_result_instance

            except Exception as e:                
                print(f"Error al guardar el resultado del análisis: {e}") 
                return False,  e            

    elif  (process == 2) and (machine == 1):

        arr = models["SCALER_NT_M1"].transform(arr)

        for v in vars_nt_m1:
            pred = models["NT_M1"][v].predict(arr)
            di_pred[v] = pred
            di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

        df_nt_m1 = pd.DataFrame(di_pred)
        df_nt_m1_str = pd.DataFrame(di_pred_str)

        if FORMA is True:
            df_nt_m1_global = df_nt_m1_global.append(df_nt_m1, ignore_index=True)
            df_nt_m1_global_str = df_nt_m1_global_str.append(df_nt_m1_str, ignore_index=True)
            print(df_nt_m1_global_str)

            # if df_nt_m1_global.shape[0] > 1:
            # plot_history(df_nt_m1_global)

        else:
            print(df_nt_m1_str)
            df_nt_m1_global = pd.DataFrame()
            df_nt_m1_global_str = pd.DataFrame()

            try:
                # Crea un diccionario para mapear los resultados y guardar las salidas
                resultados = {}
                # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                analysis_result_instance = None
                for defecto, defecto2 in zip(vars_nt_m1, vars_nt_m1):
                    # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                    valor = df_nt_m1_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                    resultados[defecto2] = valor

                # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                for defecto, valor in resultados.items():
                    if valor == 'F':
                        resultados[defecto] = True
                    else:
                        resultados[defecto] = False

                # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                print("resultados", resultados)
                try:
                    data_serializer = AnalysisResultSerializer(data=resultados)
                    if data_serializer.is_valid():
                        analysis_result_instance = data_serializer.save()
                        print("analysis_result_instance", analysis_result_instance)
                        print("Resultado de análisis guardado con éxito.")
                except Exception as e:
                    print("Errores de validación:", data_serializer.errors)
                    print(f"Error al guardar el resultado del análisis: {e}")  


                ## Ahora guardamos los datos de entrada:
                # Crea una instancia de DatosModelo con los datos desempaquetados
                data_flat = data
                print("data_flat[0]", data_flat[0])

                datos_dict = {
                    'PP_Hidro_Cemento_Kg': data_flat[0],
                    'PP_Hidro_Carbonato_Kg': data_flat[1],
                    'PP_Hidro_Silice_Kg': data_flat[2],
                    'PP_Hidro_Celulosa_Kg': data_flat[3],
                    'PP_Hidro_Hidroxido_Kg': data_flat[4],
                    'PP_Hidro_SolReales_porcentage': data_flat[5],
                    'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                    'PP_Refi_EE_AMP': data_flat[7],
                    'PP_Refi_CelulosaH_porcentage': data_flat[8],
                    'PP_Refi_CelulosaS_porcentage': data_flat[9],
                    'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                    'PP_Maq_FlujoFloc_L_min': data_flat[11],
                    'PP_Maq_Resi_ml': data_flat[12],
                    'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                    'PP_Maq_Vel_m_min': data_flat[14],
                    'PP_Maq_FormatoP_PSI': data_flat[15],
                    'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                    'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                    'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                    'PP_Maq_Recir_porcentage': data_flat[19],
                    'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                    'PP_PF_Humedad_porcentage': data_flat[21],
                    'PP_PF_Espesor_mm': data_flat[22],
                    'PP_PF_Dens_g_cm3': data_flat[23],
                    'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                    'PP_Maq_FlocTkS_porcentage': data_flat[25],
                    'PP_Maq_FlocFormS_porcentage': data_flat[26],
                    'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                    'PP_Maq_TCES_porcentage': data_flat[28],
                    'PP_Maq_CilinS_porcentage': data_flat[29],
                    'PP_Maq_Cono1S_porcentage': data_flat[30],
                    'PP_Maq_MolinoS_porcentage': data_flat[31],
                    'PP_Maq_P1H_porcentage': data_flat[32],
                    'PP_Maq_P3H_porcentage': data_flat[33]
                }           

                # Guarda la instancia en la base de datos
                instance_DatosModelo_Set = None
                instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                if instance_DatosModelo.is_valid():
                    validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                    instance_DatosModelo_Set = instance_DatosModelo.save()
                    print("analysis_result_instance 2", instance_DatosModelo_Set)
                    print("Resultado de análisis guardado con éxito.")
                else:
                    print("no valido")

                # Asegúrate de que instance_DatosModelo_Set no es None
                if not instance_DatosModelo_Set:
                    print("La instancia de DatosModelo no se creó correctamente.")
                    return False, "La instancia de DatosModelo no es válida."

                # Verificación de la existencia de analysis_result_instance
                if not analysis_result_instance:
                    print("La instancia de AnalysisResult no se creó correctamente.")
                    return False, "La instancia de AnalysisResult no es válida."


                ## Ahora guardamos los datos en el modelo de prediccion
                machine_instance = Machine.objects.get(id=machine)
                process_instance = Process.objects.get(id=process)

                datos_modelo_predict = DatPrediction(
                    machine=machine_instance,
                    process=process_instance,
                    responsepredict=analysis_result_instance,
                    data_input=instance_DatosModelo_Set,
                )                           
                # Guarda la instancia en la base de datos
                datos_modelo_predict.save()

                return True, analysis_result_instance

            except Exception as e:                
                print(f"Error al guardar el resultado del análisis: {e}") 
                return False,  e
                            
    elif (process == 2) and (machine == 2):

        arr = models["SCALER_NT_M2"].transform(arr)

        for v in vars_nt_m2:
            pred = models["NT_M2"][v].predict(arr)
            di_pred[v] = pred
            di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

        df_nt_m2 = pd.DataFrame(di_pred)
        df_nt_m2_str = pd.DataFrame(di_pred_str)

        if FORMA is True:
            df_nt_m2_global = df_nt_m2_global.append(df_nt_m2, ignore_index=True)
            df_nt_m2_global_str = df_nt_m2_global_str.append(df_nt_m2_str, ignore_index=True)
            print(df_nt_m2_global_str)

            # if df_nt_m2_global.shape[0] > 1:
            # plot_history(df_nt_m2_global)

        else:
            try:
                print(df_nt_m2_str)
                df_nt_m2_global= pd.DataFrame()
                df_nt_m2_global_str = pd.DataFrame()

                # Crea un diccionario para mapear los resultados y guardar las salidas
                resultados = {}
                # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                analysis_result_instance = None
                for defecto, defecto2 in zip(vars_nt_m2, vars_nt_m2_database):
                    # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                    valor = df_nt_m2_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                    resultados[defecto2] = valor

                # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                for defecto, valor in resultados.items():
                    if valor == 'F':
                        resultados[defecto] = True
                    else:
                        resultados[defecto] = False

                # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                print("resultados", resultados)
                try:
                    data_serializer = AnalysisResultSerializer(data=resultados)
                    if data_serializer.is_valid():
                        analysis_result_instance = data_serializer.save()
                        print("analysis_result_instance", analysis_result_instance)
                        print("Resultado de análisis guardado con éxito.")
                except Exception as e:
                    print("Errores de validación:", data_serializer.errors)
                    print(f"Error al guardar el resultado del análisis: {e}")  


                ## Ahora guardamos los datos de entrada:
                # Crea una instancia de DatosModelo con los datos desempaquetados
                data_flat = data
                print("data_flat[0]", data_flat[0])

                datos_dict = {
                    'PP_Hidro_Cemento_Kg': data_flat[0],
                    'PP_Hidro_Carbonato_Kg': data_flat[1],
                    'PP_Hidro_Silice_Kg': data_flat[2],
                    'PP_Hidro_Celulosa_Kg': data_flat[3],
                    'PP_Hidro_Hidroxido_Kg': data_flat[4],
                    'PP_Hidro_SolReales_porcentage': data_flat[5],
                    'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                    'PP_Refi_EE_AMP': data_flat[7],
                    'PP_Refi_CelulosaH_porcentage': data_flat[8],
                    'PP_Refi_CelulosaS_porcentage': data_flat[9],
                    'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                    'PP_Maq_FlujoFloc_L_min': data_flat[11],
                    'PP_Maq_Resi_ml': data_flat[12],
                    'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                    'PP_Maq_Vel_m_min': data_flat[14],
                    'PP_Maq_FormatoP_PSI': data_flat[15],
                    'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                    'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                    'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                    'PP_Maq_Recir_porcentage': data_flat[19],
                    'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                    'PP_PF_Humedad_porcentage': data_flat[21],
                    'PP_PF_Espesor_mm': data_flat[22],
                    'PP_PF_Dens_g_cm3': data_flat[23],
                    'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                    'PP_Maq_FlocTkS_porcentage': data_flat[25],
                    'PP_Maq_FlocFormS_porcentage': data_flat[26],
                    'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                    'PP_Maq_TCES_porcentage': data_flat[28],
                    'PP_Maq_CilinS_porcentage': data_flat[29],
                    'PP_Maq_Cono1S_porcentage': data_flat[30],
                    'PP_Maq_MolinoS_porcentage': data_flat[31],
                    'PP_Maq_P1H_porcentage': data_flat[32],
                    'PP_Maq_P3H_porcentage': data_flat[33]
                }           

                # Guarda la instancia en la base de datos
                instance_DatosModelo_Set = None
                instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                if instance_DatosModelo.is_valid():
                    validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                    instance_DatosModelo_Set = instance_DatosModelo.save()
                    print("analysis_result_instance 2", instance_DatosModelo_Set)
                    print("Resultado de análisis guardado con éxito.")
                else:
                    print("no valido")

                # Asegúrate de que instance_DatosModelo_Set no es None
                if not instance_DatosModelo_Set:
                    print("La instancia de DatosModelo no se creó correctamente.")
                    return False, "La instancia de DatosModelo no es válida."

                # Verificación de la existencia de analysis_result_instance
                if not analysis_result_instance:
                    print("La instancia de AnalysisResult no se creó correctamente.")
                    return False, "La instancia de AnalysisResult no es válida."


                ## Ahora guardamos los datos en el modelo de prediccion
                machine_instance = Machine.objects.get(id=machine)
                process_instance = Process.objects.get(id=process)

                datos_modelo_predict = DatPrediction(
                    machine=machine_instance,
                    process=process_instance,
                    responsepredict=analysis_result_instance,
                    data_input=instance_DatosModelo_Set,
                )                           
                # Guarda la instancia en la base de datos
                datos_modelo_predict.save()

                return True, analysis_result_instance

            except Exception as e:                
                print(f"Error al guardar el resultado del análisis: {e}") 
                return False,  e


    else:
        print("Las opciones ingresadas no son correctas")

 

## _____________________________________________ Cargar el excel y predecirlo _______________________________________________________________________

def load_and_process_data2(file):

    df = pd.read_excel(io.BytesIO(file.read())) ## cargaar los datos del excel

    resultados_por_lote = {}  # Diccionario para almacenar los resultados

    # Recorrer cada fila del DataFrame
    for index, row in df.iterrows():


        Lote = row['Lote']
        Fecha = row['Fecha']
        Hora = row['Hora']
        Cod_Producto = row['Cod_Producto']
        Tipo_Producto = row['Tipo_Producto']
        Medida = row['Medida']

        machine = row['Maq']
        process = row['Proceso']

        data = [
            row['PP_Hidro_Cemento_Kg'], row['PP_Hidro_Carbonato_Kg'], row['PP_Hidro_Silice_Kg'],
            row['PP_Hidro_Celulosa_Kg'], row['PP_Hidro_Hidroxido_Kg'], row['PP_Hidro_SolReales__%'],
            row['PP_Hidro_CelulosaS_%'], row['PP_Refi_EE_AMP'], row['PP_Refi_CelulosaH_%'],
            row['PP_Refi_CelulosaS_%'], row['PP_Refi_CelulosaSR_SR_%'], row['PP_Maq_FlujoFloc_L_min'],
            row['PP_Maq_Resi_ml'], row['PP_Maq_Vueltas_N'], row['PP_Maq_Vel_m_min'],
            row['PP_Maq_FormatoP_PSI'], row['PP_Maq_FlujoFlocForm_L_Placa'], row['PP_Maq_VacíoCP_PulgadasHg'],
            row['PP_Maq_VacioSF_PulgadasHg'], row['PP_Maq_Recir__%'], row['PP_Maq_Fieltro_Dias'],
            row['PP_PF_Humedad__%'], row['PP_PF_Espesor_mm'], row['PP_PF_Dens_g_cm3'],
            row['PP_Maq_FlocCanalS_%'], row['PP_Maq_FlocTkS_%'], row['PP_Maq_FlocFormS_%'],
            row['PP_MaqTCE_Densidad_g_cm3'], row['PP_Maq_TCES__%'], row['PP_Maq_CilinS__%'],
            row['PP_Maq_Cono1S__%'], row['PP_Maq_MolinoS__%'], row['PP_Maq_P1H_%'],
            row['PP_Maq_P3H_%']
        ]


        models = {"AUT":{},"NT_M1":{},"NT_M2":{}}


        ## se carga el modelo respectivo y los escaladores:
        root_path = BASE_DIR + "/models"
        root_path2 = BASE_DIR + "\scalers"

        if(machine==1 and process==1):
            for file in os.listdir(root_path+'/best-aut-m1-2'):
                name = file.split('_')[0]
                if '.joblib' in file:
                    models["AUT"][name] = joblib.load(f'{root_path}/best-aut-m1-2/{file}')
                    #Se cargan los pesos de los escaladores
                    models["SCALER_AUT_M1"] = joblib.load(root_path2+'\scaler-aut-m1\scaler.joblib')

        if(machine==1 and process==2):
            for file in os.listdir(root_path+'/best-nt-m1'):
                name = file.split('_')[0]
                if '.joblib' in file:
                    models["NT_M1"][name] = joblib.load(f'{root_path}/best-nt-m1/{file}')
                    models["SCALER_NT_M1"] = joblib.load(root_path2+'\scaler-nt-m1\scaler.joblib')

        if(machine==2 and process==2):
            for file in os.listdir(root_path+'/best-nt-m2'):
                name = file.split('_')[0] 
                if '.joblib' in file:
                    models["NT_M2"][name] = joblib.load(f'{root_path}/best-nt-m2\{file}')
                    models["SCALER_NT_M2"] = joblib.load(root_path2+'\scaler-nt-m2\scaler.joblib')



        #salidas
            
        vars_aut = ['Separador','Tallon','Nudo',
                    'Fisura','Delaminada','Desborde',
                    'Ondulación','Burbuja','Despunte',
                    'Basura','Daño Estiba','Manipulación',
                    'Mancha']
        
        vars_aut_database = ['Separador','Tallon','Nudo',
                    'Fisura','Delaminada','Desborde',
                    'Ondulación','Burbuja','Despunte',
                    'Basura','Daño_Estiba','Manipulación',
                    'Mancha']


        vars_nt_m1 = ['Nudo','Material','Delaminada',
                    'Desborde','Rajada','Despunte',
                    'Basura','Desmoldeo','Tallon',
                    'Mancha']
        vars_nt_m2 = ['Desmoldeo','Mancha','Basura',
                            'Desmoldeadora','Tallon','Rajada',
                            'Mal Corte','Despunte','Descolgada',
                            'Mal Ondulada','Desborde','Nudo',
                            'Manipulación','Delaminada',]
        
        vars_nt_m2_database = ['Desmoldeo','Mancha','Basura',
                            'Desmoldeadora','Tallon','Rajada',
                            'Mal_Corte','Despunte','Descolgada',
                            'Mal_Ondulada','Desborde','Nudo',
                            'Manipulación','Delaminada',]

        df_aut_global = pd.DataFrame()
        df_aut_global_str = pd.DataFrame()

        df_nt_m1_global = pd.DataFrame()
        df_nt_m1_global_str = pd.DataFrame()

        df_nt_m2_global = pd.DataFrame()
        df_nt_m2_global_str = pd.DataFrame()

        FORMA = False 

        arr = np.array(data)

        arr = arr.reshape(1,-1)

        # @markdown ---

        # Codigo

        di_pred = {}
        di_pred_str = {}

        # Se determina que proceso se debe inferir
        print(process)
        print(machine)
        print(arr)
        if (process == 1) and (machine == 1):

            #Se escalan los datos
            arr = models["SCALER_AUT_M1"].transform(arr)

            #Se realiza la inferencia para cada una de las variables
            for v in vars_aut:
                pred = models["AUT"][v].predict(arr)
                di_pred[v] = pred
                di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

            df_aut = pd.DataFrame(di_pred)
            df_aut_str = pd.DataFrame(di_pred_str)

            # Se imprime el dataframe acumulado o la inferencia actual
            if FORMA is True:
                df_aut_global = df_aut_global.append(df_aut, ignore_index=True)
                df_aut_global_str = df_aut_global_str.append(df_aut_str, ignore_index=True)
                print(df_aut_global_str)
                #aux_response1 = df_aut_global_str

                #if df_aut_global.shape[0] > 1:
                #plot_history(df_aut_global)

            else:
                print(df_aut_str)
                aux_response1 = df_aut
                df_aut_global = pd.DataFrame()
                df_aut_global_str = pd.DataFrame()

                try:
                    # Crea un diccionario para mapear los resultados y guardar las salidas
                    resultados = {}
                    # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                    analysis_result_instance = None
                    for defecto, defecto2 in zip(vars_aut, vars_aut_database):
                        # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                        valor = df_aut_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                        resultados[defecto2] = valor

                    # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                    for defecto, valor in resultados.items():
                        if valor == 'F':
                            resultados[defecto] = True
                        else:
                            resultados[defecto] = False

                    # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                    print("resultados", resultados)
                    try:
                        data_serializer = AnalysisResultSerializer(data=resultados)
                        if data_serializer.is_valid():
                            analysis_result_instance = data_serializer.save()
                            print("analysis_result_instance", analysis_result_instance)
                            print("Resultado de análisis guardado con éxito.")
                    except Exception as e:
                        print("Errores de validación:", data_serializer.errors)
                        print(f"Error al guardar el resultado del análisis: {e}")  


                    ## Ahora guardamos los datos de entrada:
                    # Crea una instancia de DatosModelo con los datos desempaquetados
                    data_flat = data
                    print("data_flat[0]", data_flat[0])

                    datos_dict = {
                        'PP_Hidro_Cemento_Kg': data_flat[0],
                        'PP_Hidro_Carbonato_Kg': data_flat[1],
                        'PP_Hidro_Silice_Kg': data_flat[2],
                        'PP_Hidro_Celulosa_Kg': data_flat[3],
                        'PP_Hidro_Hidroxido_Kg': data_flat[4],
                        'PP_Hidro_SolReales_porcentage': data_flat[5],
                        'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                        'PP_Refi_EE_AMP': data_flat[7],
                        'PP_Refi_CelulosaH_porcentage': data_flat[8],
                        'PP_Refi_CelulosaS_porcentage': data_flat[9],
                        'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                        'PP_Maq_FlujoFloc_L_min': data_flat[11],
                        'PP_Maq_Resi_ml': data_flat[12],
                        'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                        'PP_Maq_Vel_m_min': data_flat[14],
                        'PP_Maq_FormatoP_PSI': data_flat[15],
                        'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                        'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                        'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                        'PP_Maq_Recir_porcentage': data_flat[19],
                        'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                        'PP_PF_Humedad_porcentage': data_flat[21],
                        'PP_PF_Espesor_mm': data_flat[22],
                        'PP_PF_Dens_g_cm3': data_flat[23],
                        'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                        'PP_Maq_FlocTkS_porcentage': data_flat[25],
                        'PP_Maq_FlocFormS_porcentage': data_flat[26],
                        'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                        'PP_Maq_TCES_porcentage': data_flat[28],
                        'PP_Maq_CilinS_porcentage': data_flat[29],
                        'PP_Maq_Cono1S_porcentage': data_flat[30],
                        'PP_Maq_MolinoS_porcentage': data_flat[31],
                        'PP_Maq_P1H_porcentage': data_flat[32],
                        'PP_Maq_P3H_porcentage': data_flat[33]
                    }           

                    # Guarda la instancia en la base de datos
                    instance_DatosModelo_Set = None
                    instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                    if instance_DatosModelo.is_valid():
                        validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                        instance_DatosModelo_Set = instance_DatosModelo.save()
                        print("analysis_result_instance 2", instance_DatosModelo_Set)
                        print("Resultado de análisis guardado con éxito.")
                    else:
                        print("no valido")

                    # Asegúrate de que instance_DatosModelo_Set no es None
                    if not instance_DatosModelo_Set:
                        print("La instancia de DatosModelo no se creó correctamente.")
                        return False, "La instancia de DatosModelo no es válida."

                    # Verificación de la existencia de analysis_result_instance
                    if not analysis_result_instance:
                        print("La instancia de AnalysisResult no se creó correctamente.")
                        return False, "La instancia de AnalysisResult no es válida."


                    ## Ahora guardamos los datos en el modelo de prediccion
                    machine_instance = Machine.objects.get(id=machine)
                    process_instance = Process.objects.get(id=process)

                    # Intenta combinar y convertir las cadenas en un objeto datetime
                    try:
                        # Combina las dos cadenas en una sola, solo si ambas están presentes
                        if Fecha and Hora:
                            fecha_hora_str = f'{Fecha} {Hora}'
                            fecha_hora_obj = datetime.strptime(fecha_hora_str, '%d/%m/%Y %H:%M')

                            # Asigna la zona horaria de Colombia
                            zona_horaria_colombia = pytz.timezone('America/Bogota')
                            fecha_hora_colombia = zona_horaria_colombia.localize(fecha_hora_obj)
                            fecha_hora_aware = make_aware(fecha_hora_colombia)
                        else:
                            # Si no hay fecha o hora, puedes asignar un valor por defecto
                            # Por ejemplo, la fecha y hora actual
                            fecha_hora_aware = datetime.now()
                    except ValueError:
                        # Si hay un error en la conversión, también asignas un valor por defecto
                        fecha_hora_aware = datetime.now()                

                    datos_modelo_predict = DatPrediction(
                        machine=machine_instance,
                        process=process_instance,
                        responsepredict=analysis_result_instance,
                        data_input=instance_DatosModelo_Set,
                        Lote= Lote,
                        registration= fecha_hora_aware,
                        code_product= Cod_Producto,
                        type_product= Tipo_Producto,
                        measure= Medida,

                    )                           
                    # Guarda la instancia en la base de datos
                    datos_modelo_predict.save()

                    resultados_por_lote[Lote] = analysis_result_instance

                except Exception as e:                
                    print(f"Error al guardar el resultado del análisis: {e}") 
                    return False,  e            

        elif  (process == 2) and (machine == 1):

            arr = models["SCALER_NT_M1"].transform(arr)

            for v in vars_nt_m1:
                pred = models["NT_M1"][v].predict(arr)
                di_pred[v] = pred
                di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

            df_nt_m1 = pd.DataFrame(di_pred)
            df_nt_m1_str = pd.DataFrame(di_pred_str)

            if FORMA is True:
                df_nt_m1_global = df_nt_m1_global.append(df_nt_m1, ignore_index=True)
                df_nt_m1_global_str = df_nt_m1_global_str.append(df_nt_m1_str, ignore_index=True)
                print(df_nt_m1_global_str)

                # if df_nt_m1_global.shape[0] > 1:
                # plot_history(df_nt_m1_global)

            else:
                print(df_nt_m1_str)
                df_nt_m1_global = pd.DataFrame()
                df_nt_m1_global_str = pd.DataFrame()

                try:
                    # Crea un diccionario para mapear los resultados y guardar las salidas
                    resultados = {}
                    # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                    analysis_result_instance = None
                    for defecto, defecto2 in zip(vars_nt_m1, vars_nt_m1):
                        # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                        valor = df_nt_m1_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                        resultados[defecto2] = valor

                    # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                    for defecto, valor in resultados.items():
                        if valor == 'F':
                            resultados[defecto] = True
                        else:
                            resultados[defecto] = False

                    # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                    print("resultados", resultados)
                    try:
                        data_serializer = AnalysisResultSerializer(data=resultados)
                        if data_serializer.is_valid():
                            analysis_result_instance = data_serializer.save()
                            print("analysis_result_instance", analysis_result_instance)
                            print("Resultado de análisis guardado con éxito.")
                    except Exception as e:
                        print("Errores de validación:", data_serializer.errors)
                        print(f"Error al guardar el resultado del análisis: {e}")  


                    ## Ahora guardamos los datos de entrada:
                    # Crea una instancia de DatosModelo con los datos desempaquetados
                    data_flat = data
                    print("data_flat[0]", data_flat[0])

                    datos_dict = {
                        'PP_Hidro_Cemento_Kg': data_flat[0],
                        'PP_Hidro_Carbonato_Kg': data_flat[1],
                        'PP_Hidro_Silice_Kg': data_flat[2],
                        'PP_Hidro_Celulosa_Kg': data_flat[3],
                        'PP_Hidro_Hidroxido_Kg': data_flat[4],
                        'PP_Hidro_SolReales_porcentage': data_flat[5],
                        'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                        'PP_Refi_EE_AMP': data_flat[7],
                        'PP_Refi_CelulosaH_porcentage': data_flat[8],
                        'PP_Refi_CelulosaS_porcentage': data_flat[9],
                        'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                        'PP_Maq_FlujoFloc_L_min': data_flat[11],
                        'PP_Maq_Resi_ml': data_flat[12],
                        'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                        'PP_Maq_Vel_m_min': data_flat[14],
                        'PP_Maq_FormatoP_PSI': data_flat[15],
                        'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                        'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                        'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                        'PP_Maq_Recir_porcentage': data_flat[19],
                        'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                        'PP_PF_Humedad_porcentage': data_flat[21],
                        'PP_PF_Espesor_mm': data_flat[22],
                        'PP_PF_Dens_g_cm3': data_flat[23],
                        'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                        'PP_Maq_FlocTkS_porcentage': data_flat[25],
                        'PP_Maq_FlocFormS_porcentage': data_flat[26],
                        'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                        'PP_Maq_TCES_porcentage': data_flat[28],
                        'PP_Maq_CilinS_porcentage': data_flat[29],
                        'PP_Maq_Cono1S_porcentage': data_flat[30],
                        'PP_Maq_MolinoS_porcentage': data_flat[31],
                        'PP_Maq_P1H_porcentage': data_flat[32],
                        'PP_Maq_P3H_porcentage': data_flat[33]
                    }           

                    # Guarda la instancia en la base de datos
                    instance_DatosModelo_Set = None
                    instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                    if instance_DatosModelo.is_valid():
                        validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                        instance_DatosModelo_Set = instance_DatosModelo.save()
                        print("analysis_result_instance 2", instance_DatosModelo_Set)
                        print("Resultado de análisis guardado con éxito.")
                    else:
                        print("no valido")

                    # Asegúrate de que instance_DatosModelo_Set no es None
                    if not instance_DatosModelo_Set:
                        print("La instancia de DatosModelo no se creó correctamente.")
                        return False, "La instancia de DatosModelo no es válida."

                    # Verificación de la existencia de analysis_result_instance
                    if not analysis_result_instance:
                        print("La instancia de AnalysisResult no se creó correctamente.")
                        return False, "La instancia de AnalysisResult no es válida."


                    ## Ahora guardamos los datos en el modelo de prediccion
                    machine_instance = Machine.objects.get(id=machine)
                    process_instance = Process.objects.get(id=process)

                  # Intenta combinar y convertir las cadenas en un objeto datetime
                    try:
                        # Combina las dos cadenas en una sola, solo si ambas están presentes
                        if Fecha and Hora:
                            fecha_hora_str = f'{Fecha} {Hora}'
                            fecha_hora_obj = datetime.strptime(fecha_hora_str, '%d/%m/%Y %H:%M')

                            # Asigna la zona horaria de Colombia
                            zona_horaria_colombia = pytz.timezone('America/Bogota')
                            fecha_hora_colombia = zona_horaria_colombia.localize(fecha_hora_obj)
                            fecha_hora_aware = make_aware(fecha_hora_colombia)
                        else:
                            # Si no hay fecha o hora, puedes asignar un valor por defecto
                            # Por ejemplo, la fecha y hora actual
                            fecha_hora_aware = datetime.now()
                    except ValueError:
                        # Si hay un error en la conversión, también asignas un valor por defecto
                        fecha_hora_aware = datetime.now()                

                    datos_modelo_predict = DatPrediction(
                        machine=machine_instance,
                        process=process_instance,
                        responsepredict=analysis_result_instance,
                        data_input=instance_DatosModelo_Set,
                        Lote= Lote,
                        registration= fecha_hora_aware,
                        code_product= Cod_Producto,
                        type_product= Tipo_Producto,
                        measure= Medida,

                    )                              
                    # Guarda la instancia en la base de datos
                    datos_modelo_predict.save()

                    resultados_por_lote[Lote] = analysis_result_instance

                except Exception as e:                
                    print(f"Error al guardar el resultado del análisis: {e}") 
                    return False,  e
                                
        elif (process == 2) and (machine == 2):

            arr = models["SCALER_NT_M2"].transform(arr)

            for v in vars_nt_m2:
                pred = models["NT_M2"][v].predict(arr)
                di_pred[v] = pred
                di_pred_str[v] = ['F'] if pred[0] == 1 else ['NF']

            df_nt_m2 = pd.DataFrame(di_pred)
            df_nt_m2_str = pd.DataFrame(di_pred_str)

            if FORMA is True:
                df_nt_m2_global = df_nt_m2_global.append(df_nt_m2, ignore_index=True)
                df_nt_m2_global_str = df_nt_m2_global_str.append(df_nt_m2_str, ignore_index=True)
                print(df_nt_m2_global_str)

                # if df_nt_m2_global.shape[0] > 1:
                # plot_history(df_nt_m2_global)

            else:
                try:
                    print(df_nt_m2_str)
                    df_nt_m2_global= pd.DataFrame()
                    df_nt_m2_global_str = pd.DataFrame()

                    # Crea un diccionario para mapear los resultados y guardar las salidas
                    resultados = {}
                    # Inicializa analysis_result_instance como None para manejar el ámbito correctamente
                    analysis_result_instance = None
                    for defecto, defecto2 in zip(vars_nt_m2, vars_nt_m2_database):
                        # Extrae el valor individual de la Serie (asumiendo que solo hay una fila en tu DataFrame)
                        valor = df_nt_m2_str[defecto].iloc[0]  # .iloc[0] accede al primer (y único, en este caso) elemento de la Serie
                        resultados[defecto2] = valor

                    # Ahora necesitas convertir los valores 'F' y 'NF' a True/False o None antes de pasarlos al modelo
                    for defecto, valor in resultados.items():
                        if valor == 'F':
                            resultados[defecto] = True
                        else:
                            resultados[defecto] = False

                    # Ahora 'resultados' contiene valores escalares adecuados para tu modelo
                    print("resultados", resultados)
                    try:
                        data_serializer = AnalysisResultSerializer(data=resultados)
                        if data_serializer.is_valid():
                            analysis_result_instance = data_serializer.save()
                            print("analysis_result_instance", analysis_result_instance)
                            print("Resultado de análisis guardado con éxito.")
                    except Exception as e:
                        print("Errores de validación:", data_serializer.errors)
                        print(f"Error al guardar el resultado del análisis: {e}")  


                    ## Ahora guardamos los datos de entrada:
                    # Crea una instancia de DatosModelo con los datos desempaquetados
                    data_flat = data
                    print("data_flat[0]", data_flat[0])

                    datos_dict = {
                        'PP_Hidro_Cemento_Kg': data_flat[0],
                        'PP_Hidro_Carbonato_Kg': data_flat[1],
                        'PP_Hidro_Silice_Kg': data_flat[2],
                        'PP_Hidro_Celulosa_Kg': data_flat[3],
                        'PP_Hidro_Hidroxido_Kg': data_flat[4],
                        'PP_Hidro_SolReales_porcentage': data_flat[5],
                        'PP_Hidro_CelulosaS_porcentage': data_flat[6],
                        'PP_Refi_EE_AMP': data_flat[7],
                        'PP_Refi_CelulosaH_porcentage': data_flat[8],
                        'PP_Refi_CelulosaS_porcentage': data_flat[9],
                        'PP_Refi_CelulosaSR_SR_grados': data_flat[10],
                        'PP_Maq_FlujoFloc_L_min': data_flat[11],
                        'PP_Maq_Resi_ml': data_flat[12],
                        'PP_Maq_Vueltas_N': data_flat[13],  # Asegúrate de convertir a entero si es necesario
                        'PP_Maq_Vel_m_min': data_flat[14],
                        'PP_Maq_FormatoP_PSI': data_flat[15],
                        'PP_Maq_FlujoFlocForm_L_Placa': data_flat[16],
                        'PP_Maq_VacíoCP_PulgadasHg': data_flat[17],
                        'PP_Maq_VacioSF_PulgadasHg': data_flat[18],
                        'PP_Maq_Recir_porcentage': data_flat[19],
                        'PP_Maq_Fieltro_Dias': data_flat[20],  # Asegúrate de convertir a entero si es necesario
                        'PP_PF_Humedad_porcentage': data_flat[21],
                        'PP_PF_Espesor_mm': data_flat[22],
                        'PP_PF_Dens_g_cm3': data_flat[23],
                        'PP_Maq_FlocCanalS_porcentage': data_flat[24],
                        'PP_Maq_FlocTkS_porcentage': data_flat[25],
                        'PP_Maq_FlocFormS_porcentage': data_flat[26],
                        'PP_MaqTCE_Densidad_g_cm3': data_flat[27],
                        'PP_Maq_TCES_porcentage': data_flat[28],
                        'PP_Maq_CilinS_porcentage': data_flat[29],
                        'PP_Maq_Cono1S_porcentage': data_flat[30],
                        'PP_Maq_MolinoS_porcentage': data_flat[31],
                        'PP_Maq_P1H_porcentage': data_flat[32],
                        'PP_Maq_P3H_porcentage': data_flat[33]
                    }           

                    # Guarda la instancia en la base de datos
                    instance_DatosModelo_Set = None
                    instance_DatosModelo = DatosModeloSerializer(data=datos_dict)
                    if instance_DatosModelo.is_valid():
                        validated_data = instance_DatosModelo.validated_data  # Accede a los datos validados aquí
                        instance_DatosModelo_Set = instance_DatosModelo.save()
                        print("analysis_result_instance 2", instance_DatosModelo_Set)
                        print("Resultado de análisis guardado con éxito.")
                    else:
                        print("no valido")

                    # Asegúrate de que instance_DatosModelo_Set no es None
                    if not instance_DatosModelo_Set:
                        print("La instancia de DatosModelo no se creó correctamente.")
                        return False, "La instancia de DatosModelo no es válida."

                    # Verificación de la existencia de analysis_result_instance
                    if not analysis_result_instance:
                        print("La instancia de AnalysisResult no se creó correctamente.")
                        return False, "La instancia de AnalysisResult no es válida."


                    ## Ahora guardamos los datos en el modelo de prediccion
                    machine_instance = Machine.objects.get(id=machine)
                    process_instance = Process.objects.get(id=process)

                  # Intenta combinar y convertir las cadenas en un objeto datetime
                    try:
                        # Combina las dos cadenas en una sola, solo si ambas están presentes
                        print("Fecha", Fecha)
                        print("Hora", Hora)
                        if Fecha and Hora:
                        # Extrae la parte de la fecha del Timestamp, sin la hora.
                            fecha_obj = Fecha.to_pydatetime().date()
                            
                            # Hora ya es un objeto time, por lo que no necesitas convertirlo
                            hora_obj = Hora  # Asumiendo que Hora es de tipo datetime.time

                            # Combina la fecha y la hora en un objeto datetime
                            fecha_hora_aware = datetime.combine(fecha_obj, hora_obj)

                        else:
                            # Si no hay fecha o hora, puedes asignar un valor por defecto
                            # Por ejemplo, la fecha y hora actual
                            fecha_hora_aware = datetime.now()
                    except ValueError:
                        # Si hay un error en la conversión, también asignas un valor por defecto
                        fecha_hora_aware = datetime.now()                

                    datos_modelo_predict = DatPrediction(
                        machine=machine_instance,
                        process=process_instance,
                        responsepredict=analysis_result_instance,
                        data_input=instance_DatosModelo_Set,
                        Lote= Lote,
                        registration= fecha_hora_aware,
                        code_product= Cod_Producto,
                        type_product= Tipo_Producto,
                        measure= Medida,

                    )                            
                    # Guarda la instancia en la base de datos
                    datos_modelo_predict.save()
                    resultados_por_lote[Lote] = analysis_result_instance
                    
                
                except Exception as e:                
                    print(f"Error al guardar el resultado del análisis: {e}") 
                    return False,  e       

        else:
            print("Las opciones ingresadas no son correctas")

    # Convertir las instancias de modelos a un formato serializable
    resultados_serializables = {}
    for lote, instance in resultados_por_lote.items():
        # Usar el serializador para convertir la instancia a un formato serializable
        serializer = AnalysisResultSerializer(instance)
        resultados_serializables[lote] = serializer.data

    return True, resultados_serializables



