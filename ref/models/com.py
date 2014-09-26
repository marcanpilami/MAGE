# coding: utf-8
""" Models related to end-user communication """

## Django imports
from django.db import models

class Link(models.Model):
    url = models.URLField(verbose_name="URL cible")
    legend = models.CharField(max_length=100, verbose_name='légende du lien')
    color = models.CharField(max_length=7, verbose_name='couleur', help_text='couleur au format #RRGGBB hexadécimal. Ex: #FF00CC')

    class Meta:
        verbose_name = 'lien page accueil'
        verbose_name_plural = 'liens page accueil'
