from rest_framework import serializers
from .models import *

class MachineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Machine
        fields = '__all__'

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = '__all__'
       
class AnalysisResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalysisResult
        fields = '__all__'

class DatosModeloSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosModelo
        fields = '__all__'        

class DatPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatPrediction
        fields = '__all__'        


