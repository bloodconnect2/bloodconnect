from django.contrib import admin
from core.models import Donneur, Hopital, DemandeUrgente, Don, Campagne, Inscription, ReponseAppel

admin.site.register(Donneur)
admin.site.register(Hopital)
admin.site.register(DemandeUrgente)
admin.site.register(Don)
admin.site.register(Campagne)
admin.site.register(Inscription)
admin.site.register(ReponseAppel)