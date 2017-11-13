import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'tang_with_django_project.settings')#import project settings
                      

import django
django.setup()#call project settings
from rango.models import Category, Page

def populate():
    """First lists of dicts for pages we want to add in each cat, then
a dict of dicts for cats - to iterate through each data structure and
add to the models"""
    python_pages = [
        {"title": "Official Python Tutorial",
         "url":"http://docs.python.org/2/tutorial/"},
        {"title":"How To Think Like A Computer Scientist",
         
         "url":"http://www.greenteapress.com/thinkpython/"},
        {"title":"Learn Python in 10 Minutes",
         "url":"http://www.korokithakis.net/tutorials/python/"}]

    django_pages = [{"title":"Official Django Tutorial",
                     "url":"https://docs.djangoproject.com/en/1.9/intro/tutorial01/"},
                    {"title":"Django Rocks", "url":"http://www.djangorocks.com/"},
                    {"title":"How to Tango with Django","url":"http://www.tangowithdjango.com/"}]

    
    other_pages = [
        {"title":"Bottle",
        "url":"http://bottlepy.org/dos/dev/"},
        {"title":"Flask",
         "url":"http://flask.pocoo.org"}]

    cats = {"Python": {"pages": python_pages, "views":128, "likes":64},
            "Django": {"pages": django_pages, "views":64, "likes":32},
            "Other Frameworks": {"pages": other_pages, "views":32, "likes":16},}
    #see 1235 for eplanation of code


    for cat, cat_data in cats.items():
        c = add_cat(cat, cat_data["views"], cat_data["likes"])#this is where the error is-needs views and likes parameter
        for p in cat_data["pages"]:
            add_page(c, p["title"], p["url"], p["views"])

    for c in Category.objects.all():
        for p in Page.objects.filter(category=c):
            print("- {0} - {1}".format(str(c), str(p)))


def add_page(cat, title, url, views=0):
    p = Page.objects.get_or_create(category=cat, title=title)[0]#see 1349 - return object reference of the tuple if created is True
    p.url=url
    p.views=views
    p.save()
    return p

def add_cat(name, views=0, likes=0):
    c=Category.objects.get_or_create(name=name, views=views, likes=likes)[0]
    c.views=views
    c.likes=likes
    c.save()
    return c

#first time we call anything:

if __name__ == '__main__':#see notes 1319
    print("Starting Rango population script...")
    populate()
