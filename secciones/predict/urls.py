from django.urls import path
from .views import *



urlpatterns = [

   # Obtención de datos 
   path('machines/', MachineList.as_view(), name='machine-list'),
   path('processes/', ProcessList.as_view(), name='process-list'),

   # Predicción de datos manuales
   path('process-data/', process_data_view.as_view(), name='process-data'),
   path('process-data-excel/', process_data_excel_view.as_view(), name='process_data_excel_view'),

   # obtener el historial de predicciones
   path('dat-predictions/', DatPredictionView.as_view(), name='dat-predictions'),

   # para generar los excel:
   path('generate-excel/', GenerateExcelView.as_view(), name='generate-excel'),

   # cargar los pesos de cada dato de entrada
   path('load-feature/', LoadFeature.as_view(), name='load-feature'),

]