from django.db import models

class store(models.Model):
    
    def __str__(self):
        return self.store_name
    
    
    store_name = models.CharField(max_length=200)
    store_email = models.CharField(max_length=200)
    store_words = models.CharField(max_length=200)