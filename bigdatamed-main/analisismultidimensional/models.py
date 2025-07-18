from django.db import models


# Create your models here.

class ModeloEjemplo (models.Model):
    #Dimensiones. Son columnas de la tabla
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()

    def __str__(self):
        return self.nombre
    

    #Medidas
    

