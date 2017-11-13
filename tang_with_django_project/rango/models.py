from django.db import models
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User



class Category(models.Model):
    """The name of the Category"""
    name = models.CharField(max_length=128, unique=True)
    views = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):#see 1034 location - returns a string rep of the model
        return self.name
    

class Page(models.Model):
    """Page model"""
    category = models.ForeignKey(Category)
    title = models.CharField(max_length=128)
    url = models.URLField()
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    #links UserProfile to User model instance
    user = models.OneToOneField(User)

    #the attributes we want to add (on top of Django's given ones eg name)
    #both can be left blank
    website = models.URLField(blank=True)
    picture = models.ImageField(upload_to='profile_images', blank=True)

    #override __unicode__ method
    def __str__(self):
        return self.user.username


#check book should UserProfileFrom be here? Surely not
        
    
