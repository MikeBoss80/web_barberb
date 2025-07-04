from django.db import models

# Create your models here.
class States(models.Model):
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'
        ordering = ['name']

    def __str__(self):
        return self.name