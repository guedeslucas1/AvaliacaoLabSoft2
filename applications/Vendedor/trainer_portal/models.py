from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class TimeSlot(models.Model):
  professional_id = models.ForeignKey(User, on_delete=models.CASCADE)
  time            = models.DateTimeField(default=datetime.now)

  def __str__(self):
    return self.time.strftime("%Y-%m-%d %H:%M:%S")

class LugarEstadio(models.Model):
    linha = models.CharField(max_length=20)  # Agora pode ser uma string qualquer
    coluna = models.CharField(max_length=20)  # Agora pode ser uma string qualquer
    disponivel = models.BooleanField(default=True)

    def __str__(self):
        return f'Lugar: {self.linha}{self.coluna}, Disponível: {self.disponivel}'
