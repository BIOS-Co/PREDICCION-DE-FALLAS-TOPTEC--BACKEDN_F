
from django.utils import timezone
from datetime import datetime
from datetime import date
from django.db import models

## Modelo para el almacenamiento de los datos

class Machine(models.Model):
    name = models.CharField(db_column="name", blank=False, null=False, max_length=50)
    description = models.CharField(db_column="description", null=False, blank=True, max_length=500, default="")

class Process(models.Model):
    name = models.CharField(db_column="name", blank=False, null=False, max_length=50)
    description = models.CharField(db_column="description", null=False, blank=True, max_length=500, default="")

class DatosModelo(models.Model):
    PP_Hidro_Cemento_Kg = models.FloatField()
    PP_Hidro_Carbonato_Kg = models.FloatField()
    PP_Hidro_Silice_Kg = models.FloatField()
    PP_Hidro_Celulosa_Kg = models.FloatField()
    PP_Hidro_Hidroxido_Kg = models.FloatField()
    PP_Hidro_SolReales_porcentage = models.FloatField()
    PP_Hidro_CelulosaS_porcentage = models.FloatField()
    PP_Refi_EE_AMP = models.FloatField()
    PP_Refi_CelulosaH_porcentage = models.FloatField()
    PP_Refi_CelulosaS_porcentage = models.FloatField()
    PP_Refi_CelulosaSR_SR_grados = models.FloatField()
    PP_Maq_FlujoFloc_L_min = models.FloatField()
    PP_Maq_Resi_ml = models.FloatField()
    PP_Maq_Vueltas_N = models.IntegerField()
    PP_Maq_Vel_m_min = models.FloatField()
    PP_Maq_FormatoP_PSI = models.FloatField()
    PP_Maq_FlujoFlocForm_L_Placa = models.FloatField()
    PP_Maq_VacíoCP_PulgadasHg = models.FloatField()
    PP_Maq_VacioSF_PulgadasHg = models.FloatField()
    PP_Maq_Recir_porcentage = models.FloatField()
    PP_Maq_Fieltro_Dias = models.IntegerField()
    PP_PF_Humedad_porcentage = models.FloatField()
    PP_PF_Espesor_mm = models.FloatField()
    PP_PF_Dens_g_cm3 = models.FloatField()
    PP_Maq_FlocCanalS_porcentage = models.FloatField()
    PP_Maq_FlocTkS_porcentage = models.FloatField()
    PP_Maq_FlocFormS_porcentage = models.FloatField()
    PP_MaqTCE_Densidad_g_cm3 = models.FloatField()
    PP_Maq_TCES_porcentage = models.FloatField()
    PP_Maq_CilinS_porcentage = models.FloatField()
    PP_Maq_Cono1S_porcentage = models.FloatField()
    PP_Maq_MolinoS_porcentage = models.FloatField()
    PP_Maq_P1H_porcentage = models.FloatField()
    PP_Maq_P3H_porcentage = models.FloatField()

    def __str__(self):
        return f'DatosModelo {self.id}'

class AnalysisResult(models.Model):
    # Define los campos aquí
    Separador = models.BooleanField(null=True, blank=True)
    Tallon = models.BooleanField(null=True, blank=True)
    Nudo = models.BooleanField(null=True, blank=True)
    Fisura = models.BooleanField(null=True, blank=True)
    Delaminada = models.BooleanField(null=True, blank=True)
    Desborde =models.BooleanField(null=True, blank=True)
    Ondulación = models.BooleanField(null=True, blank=True)
    Burbuja = models.BooleanField(null=True, blank=True)
    Despunte = models.BooleanField(null=True, blank=True)
    Basura = models.BooleanField(null=True, blank=True)
    Daño_Estiba = models.BooleanField(null=True, blank=True)
    Manipulación = models.BooleanField(null=True, blank=True)
    Mancha = models.BooleanField(null=True, blank=True)
    Material = models.BooleanField(null=True, blank=True)
    Rajada = models.BooleanField(null=True, blank=True)
    Desmoldeo = models.BooleanField(null=True, blank=True)
    Desmoldeadora = models.BooleanField(null=True, blank=True)
    Mal_Corte = models.BooleanField(null=True, blank=True)
    Descolgada = models.BooleanField(null=True, blank=True)
    Mal_Ondulada = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"AnalysisResult {self.id}"
    
class DatPrediction(models.Model):
    Lote = models.CharField('Lote', max_length=100, blank=False, null=True)
    registration = models.DateField('registration', blank=True, null=False, default=date.today)
    registration_date = models.DateField('registration_date', blank=True, null=False, default=date.today)
    code_product = models.CharField('code_product', max_length=100, blank=False, null=True)
    type_product = models.CharField('type_product', max_length=100, blank=False, null=True)
    measure = models.IntegerField('measure',  blank=False, null=True)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, null=False, blank=False)
    process = models.ForeignKey(Process, on_delete=models.CASCADE, null=False, blank=False)    
    responsepredict = models.ForeignKey(AnalysisResult, on_delete=models.CASCADE, null=False, blank=False)
    data_input = models.ForeignKey(DatosModelo, on_delete=models.CASCADE, null=False, blank=False)
