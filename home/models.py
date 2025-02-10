from django.db import models

class GlobalSettings(models.Model):
    TYPE_CHOICES = [
        ('text', 'Texte'),
        ('image', 'Image'),
    ]

    key = models.CharField(max_length=255, unique=True)
    value_text = models.TextField(blank=True, null=True)  # Pour les textes
    value_image = models.ImageField(upload_to='settings/', blank=True, null=True)  # Pour les images
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='text')

    def __str__(self):
        return self.key

    @staticmethod
    def get(key, default=None):
        try:
            setting = GlobalSettings.objects.get(key=key)
            if setting.type == 'image':
                return setting.value_image.url if setting.value_image else default
            return setting.value_text if setting.value_text else default
        except GlobalSettings.DoesNotExist:
            return default
