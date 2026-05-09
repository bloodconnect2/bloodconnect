from django.contrib import admin
from core.models import Donneur, Hopital, DemandeUrgente, Don, Campagne, Inscription, ReponseAppel


@admin.register(Donneur)
class DonneurAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ville', 'groupe_sanguin', 'sexe', 'actif')
    list_filter = ('groupe_sanguin', 'sexe', 'actif', 'ville')
    search_fields = ('user__first_name', 'user__last_name', 'user__email')


@admin.register(Hopital)
class HopitalAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'numero_agrement', 'valide')
    list_filter = ('valide', 'ville')
    search_fields = ('nom', 'numero_agrement')
    actions = ['valider_hopitaux']

    def valider_hopitaux(self, request, queryset):
        updated = queryset.update(valide=True)
        self.message_user(request, f"{updated} hôpital(aux) validé(s).")
    valider_hopitaux.short_description = "Valider les hôpitaux sélectionnés"


@admin.register(DemandeUrgente)
class DemandeUrgenteAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hopital', 'quantite', 'delai', 'statut', 'date_creation')
    list_filter = ('statut', 'groupe_sanguin')
    search_fields = ('hopital__nom',)


@admin.register(Don)
class DonAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hopital', 'date_don', 'valide')
    list_filter = ('valide', 'date_don')
    search_fields = ('donneur__user__first_name', 'donneur__user__last_name')


@admin.register(Campagne)
class CampagneAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'hopital', 'lieu', 'capacite_totale')
    list_filter = ('date',)
    search_fields = ('nom', 'hopital__nom')


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'creneau_horaire', 'present', 'date_inscription')
    list_filter = ('present',)


@admin.register(ReponseAppel)
class ReponseAppelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'statut', 'date_reponse')
    list_filter = ('statut',)
