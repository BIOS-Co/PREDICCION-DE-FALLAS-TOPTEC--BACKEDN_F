### Librerias

from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
import uuid
from django.http import HttpResponse
import os
from django.forms.models import model_to_dict
from collections import defaultdict
import json
from django.template.loader import get_template
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.core.files import File
from rest_framework.utils.serializer_helpers import ReturnDict
import binascii

import threading
import zipfile
from django.core.files.base import ContentFile


import base64
import xml.etree.ElementTree as ET
from xml.etree import ElementTree
import tempfile
import shutil
import io

import json
from django.db import transaction
from rest_framework.generics import RetrieveAPIView, ListAPIView, DestroyAPIView, UpdateAPIView
from django.utils.dateparse import parse_date
from django.db.models import Max
from io import BytesIO
import pandas as pd
from django.http import HttpResponse
import pickle

## importar las funciones para la predicción del modelo
from .utils import * 
from .serializers import * 

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


## obtener los datos de la maquina y los procesos
class MachineList(ListAPIView):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

class ProcessList(ListAPIView):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer

## Predicción con los datos ingresados manualmente

class process_data_view(APIView):
    @transaction.atomic  ## para  evitar guardar los datos con errores

    def post(self, request):
        try:
            data = request.data
            print("data", data) 
            machine = data.get('machine')
            process = data.get('process')
            database = data.get('data')

            if not all([machine, process]):
                return Response({'error': 'Faltan parámetros necesarios.'}, status=400)

            reponse, inst = load_and_process_data(machine, process, database)

            if reponse == True:
                serializer = AnalysisResultSerializer(inst)
                return Response({'resultado': serializer.data}, status=200)
            else:
                transaction.set_rollback(True)
                return Response({'error': str(inst)}, status=500)

        except Exception as e:
            print({'error': str(e)})
            transaction.set_rollback(True)
            return Response({'error': str(e)}, status=500)
        
class process_data_excel_view(APIView):
    @transaction.atomic  ## para  evitar guardar los datos con errores

    def post(self, request):
        try:
            data = request.data
            print("data", data) 
            file = request.FILES.get('File')

            if not (file):
                return Response({'error': 'Faltan parámetros necesarios.'}, status=400)

            reponse, inst = load_and_process_data2(file)
            if reponse == True:
                #serializer = AnalysisResultSerializer(inst, many=True)
                return Response({'resultado': inst}, status=200)
            else:
                transaction.set_rollback(True)
                return Response({'error': str(inst)}, status=500)


        except Exception as e:
            transaction.set_rollback(True)
            print({'error': str(e)})
            return Response({'error': str(e)}, status=500)

## obtener el historial de predicciones

class DatPredictionView(APIView):
    def get(self, request, *args, **kwargs):
        # Leer parámetros de fecha de la solicitud

        dat_predictions = DatPrediction.objects.all()

        # Preparar lista para datos enriquecidos
        enriched_data = []

        # Iterar sobre los DatPrediction filtrados
        for prediction in dat_predictions:
            analysis_result = prediction.responsepredict
            # Calcular los valores False de los campos BooleanField de este AnalysisResult
            total_true = sum([
                getattr(analysis_result, field.name) == True
                for field in analysis_result._meta.fields
                if isinstance(field, models.BooleanField) and getattr(analysis_result, field.name) is not None
            ])
            
            # Serializar el objeto DatPrediction actual
            serializer = DatPredictionSerializer(prediction)
            # Añadir el total de falses al dato serializado
            prediction_data = serializer.data
            prediction_data['mala'] = total_true
            # Añadir a la lista de datos enriquecidos
            enriched_data.append(prediction_data)
        
        # Construir la respuesta con datos enriquecidos
        response_data = {
            'dat_predictions': enriched_data
        }

        return Response(response_data)
    
## Generación de excel con los datos de la prediccion
    


class GenerateExcelView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data  # Asumiendo que esto es una lista de diccionarios
        
        print("data", data)
        # Crear un DataFrame con los datos recibidos
        df = pd.DataFrame(data)

        # Definir la ruta completa del archivo Excel
        excel_file_path = os.path.join(BASE_DIR, 'temp', 'DatPrediction.xlsx')

        # Asegurarte de que la carpeta 'temp' existe
        os.makedirs(os.path.dirname(excel_file_path), exist_ok=True)

        # Guardar el DataFrame en un archivo Excel
        with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        # Leer el contenido del archivo para enviarlo al frontend
        with open(excel_file_path, 'rb') as excel_file:
            excel_data = excel_file.read()

        # Crear una respuesta HTTP con el contenido del archivo Excel
        response = HttpResponse(
            excel_data,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(excel_file_path)}"'

        return response

class LoadFeature(APIView):

    def get(self, request):
 
        path = os.path.join(BASE_DIR, 'feature_importance', 'feature_importance.pkl')  # Usa os.path.join para construir la ruta
        print("path", path)
        try:
            path = os.path.join(BASE_DIR, 'feature_importance', 'feature_importance.pkl')  # Usa os.path.join para construir la ruta
            print("path", path)
            with open(path, 'rb') as f:
                loaded_dict = pickle.load(f)
                print(loaded_dict)
                return Response({'resultado': loaded_dict})
        except Exception as e:
            print("El archivo no se encontró")
            return Response({'error': str(e)}, status=500)