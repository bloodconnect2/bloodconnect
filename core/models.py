from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


BLOOD_GROUPS = [
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
]

BLOOD_COMPATIBILITY = {
    'A+':  ['A+', 'A-', 'O+', 'O-'],
    'A-':  ['A-', 'O-'],
    'B+':  ['B+', 'B-', 'O+', 'O-'],
    'B-':  ['B-', 'O-'],
    'AB+': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
    'AB-': ['A-', 'B-', 'AB-', 'O-'],
    'O+':  ['O+', 'O-'],
    'O-':  ['O-'],
}


class Donneur(models.Model):
    SEX_CHOICES = [('M', 'Homme'), ('F', 'Femme')]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donneur')
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    sexe = models.CharField(max_length=1, choices=SEX_CHOICES)
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)

    def get_delai_don(self):
        return 56 if self.sexe == 'M' else 84

    def get_prochain_don(self):
        dernier = self.dons.filter(valide=True).order_by('-date_don').first()
        if dernier:
            return dernier.date_don + timedelta(days=self.get_delai_don())
        return None

    def est_eligible(self):
        prochain = self.get_prochain_don()
        if prochain is None:
            return True
        return timezone.now().date() >= prochain

    def get_groupes_compatibles(self):
        return BLOOD_COMPATIBILITY.get(self.groupe_sanguin, [])

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.groupe_sanguin})"


class Hopital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='hopital')
    nom = models.CharField(max_length=200)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    numero_agrement = models.CharField(max_length=50, unique=True)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return self.nom


class DemandeUrgente(models.Model):
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('cloturee', 'Clôturée'),
        ('satisfaite', 'Satisfaite'),
    ]

    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='demandes')
    groupe_sanguin = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    quantite = models.PositiveIntegerField(help_text="Nombre de poches")
    delai = models.DateField(help_text="Date limite")
    description = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    date_creation = models.DateTimeField(auto_now_add=True)

    def est_active(self):
        return self.statut == 'active' and self.delai >= timezone.now().date()

    def __str__(self):
        return f"{self.groupe_sanguin} — {self.hopital.nom} ({self.statut})"


class Don(models.Model):
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE, related_name='dons')
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='dons_recus')
    date_don = models.DateField()
    notes = models.TextField(blank=True)
    valide = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date_don']

    def __str__(self):
        return f"Don de {self.donneur} le {self.date_don}"


class Campagne(models.Model):
    hopital = models.ForeignKey(Hopital, on_delete=models.CASCADE, related_name='campagnes')
    nom = models.CharField(max_length=200)
    date = models.DateField()
    lieu = models.CharField(max_length=200)
    groupes_cibles = models.JSONField(default=list, help_text="Liste de groupes sanguins ciblés")
    capacite_totale = models.PositiveIntegerField()

    def places_restantes(self):
        inscrits = self.inscriptions.count()
        return max(0, self.capacite_totale - inscrits)

    def __str__(self):
        return f"{self.nom} — {self.date}"


class Inscription(models.Model):
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name='inscriptions')
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE, related_name='inscriptions')
    creneau_horaire = models.TimeField()
    date_inscription = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('campagne', 'donneur')

    def __str__(self):
        return f"{self.donneur} → {self.campagne} à {self.creneau_horaire}"


class ReponseAppel(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]

    demande = models.ForeignKey(DemandeUrgente, on_delete=models.CASCADE, related_name='reponses')
    donneur = models.ForeignKey(Donneur, on_delete=models.CASCADE, related_name='reponses')
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')

    class Meta:
        unique_together = ('demande', 'donneur')

    def __str__(self):
        return f"{self.donneur} → {self.demande} ({self.statut})"