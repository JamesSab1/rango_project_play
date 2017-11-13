from django.shortcuts import render, redirect

from django.http import HttpResponse
#Import Category model
from rango.models import Category, Page, UserProfile

from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import login_required

from datetime import datetime
from rango.webhose_search import run_query, read_webhose_key

from django.contrib.auth.models import User


def index(request):
    #request.session.set_test_cookie()
    #get cats and return top 5 liked
    category_list = Category.objects.order_by('-likes')[:5]
    pages_list = Page.objects.order_by('-views')[:5]
    #construct a dict to pass to template engine as its context
    context_dict = {'categories' : category_list, 'pages' : pages_list}

    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']

    response = render(request, 'rango/index.html',context=context_dict)
    return response
    

def about(request):
    #if request.session.test_cookie_worked():
        #print("TEST COOKIE WORKED!")
        #request.session.delete_test_cookie()

    #site visit counter server side cookie
    context_dict = {}
    visitor_cookie_handler(request)
    context_dict['visits'] = request.session['visits']
    
    return render(request, 'rango/about.html', context_dict)

def show_category(request, category_name_slug):#1161 for notes, 4646 for refine
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:#the template will display no cat
        context_dict['category'] = None
        context_dict['pages'] = None

    context_dict['query'] = category.name

    result_list = []
    if request.method =='POST':
        query = request.POST['query'].strip()

        if query:
            result_list = run_query(query)
            context_dict['query'] = query
            context_dict['result_list'] = result_list

    return render(request, 'rango/category.html', context_dict)

def add_category(request):
    form = CategoryForm()
    #A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        #valid?
        if form.is_valid():
            #save to database
            form.save(commit=True)
            return index(request)
        else:
            #errors
            print(form.errors)
    return render(request, 'rango/add_category.html', {'form':form})

def add_page(request, category_name_slug):
    #pages are assoc to a category
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()
    if request.method == 'POST':
            form = PageForm(request.POST)
            if form.is_valid():
                if category:
                    page = form.save(commit=False)
                    page.category = category
                    page.views = 0
                    page.save()
                    return show_category(request, category_name_slug)
            else:
                print(form.errors)
    context_dict = {'form':form, 'category':category}
    return render(request, 'rango/add_page.html', context_dict)

def register(request):
    #change to True if registration succeeds
    registered = False
    #if HTTP POST we want to process the data
    if request.method == 'POST':
        #grab info
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        #if both are valis save user's form data
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            #hash password and update user object
            user.set_password(user.password)
            user.save()

            #delay saving, and link the two User model instances, giving access
            #to the added attributes of UserProfileForm
            profile = profile_form.save(commit=False)
            profile.user = user
            #submit a pic?
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            #save UserProfile model instance
            profile.save()
            #registration succeeded
            registered = True
        else:
            print(user_form.errors, profile_form.errors)

    #not a HTTP POST so we produce new forms
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    #render the template with given context
    return render(request, 'rango/register.html',
                  {'user_form':user_form, 'profile_form':profile_form,
                   'registered': registered})


def user_login(request):
    #HTTP POST?
    if request.method == 'POST':
        #use get() rather than keys because if it does not exist we return
        #None whereas request.POST[] would return KEyError exception
        username = request.POST.get('username')
        password = request.POST.get('password')

        #Django magic authenticate(), a User object is returned if valid
        user = authenticate(username=username, password=password)

        #if user then details correct o/w None
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            #inactive acc?
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            #bad login
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse("Invalid login details supplied.")

    #not HTTP POST, back to login
    else:
        #no context dict to pass so empty
        return render(request, 'rango/login.html', {})
    
                  
                
@login_required
def restricted(request):
    return render(request, 'rango/restricted.html', {})

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

            
#helper functions for server side site counter

def visitor_cookie_handler(request):
    #use COOKIES.get('key','default_value') to get number of visits
    visits = int(get_server_side_cookie(request, 'visits','1'))

    last_visit_cookie = get_server_side_cookie(request,'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')
    #if longer than a day since last visit
    if (datetime.now() - last_visit_time).seconds > 0:
        visits = visits + 1
        #update last visit cookie
        request.session['last_visit'] =  str(datetime.now())
        
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie
                           
    #visits cookie
    request.session['visits'] = visits
    
    
def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def search(request):
    result_list = []
    query = ''

    if request.method == 'POST':
        query = request.POST['query'].strip()
        if query:
            result_list = run_query(query)

    return render(request, 'rango/search.html', {'result_list' : result_list,
                                                 'query':query})

def track_url(request):
    page_id = None
    url = '/rango/'
    if request.method =='GET':
        if 'page_id' in request.GET:
            page_id = request.GET['page_id']

            try:
                page = Page.objects.get(id=page_id)
                page.views = page.views + 1
                page.save()
                url = page.url
            except:
                pass
    return redirect(url)


@login_required
def register_profile(request):
    form = UserProfileForm()

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile = form.save(commit=False)
            user_profile.user = request.user
            user_profile.save()

            return redirect('index')
        else:
            print(form.errors)
    context_dict = {'form':form}

    return render(request, 'rango/profile_registration.html', context_dict)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return redirect('index')
    
    userprofile = UserProfile.objects.get_or_create(user=user)[0]
    form = UserProfileForm({'website':userprofile.website, 'picture':userprofile.picture})

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=userprofile)
        if form.is_valid():
            form.save(commit=True)
            return redirect('profile', user.username)
        else:
            print(form.errors)

    return render(request, 'rango/profile.html', {'userprofile': userprofile,
                                                  'selecteduser':user,
                                                  'form':form})

@login_required
def list_profiles(request):
    userprofile_list = UserProfile.objects.all()

    return render(request, 'rango/list_profiles.html',
                  {'userprofile_list':userprofile_list})

@login_required
def like_category(request):
    cat_id = None
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        likes = 0
        if cat_id:
            cat = Category.objects.get(id=int(cat_id))
            if cat:
                likes = cat.likes + 1
                cat.likes = likes
                cat.save()
    return HttpResponse(likes)

def get_category_list(max_results=0, starts_with=''):
    cat_list = []
    if starts_with:
        cat_list = Category.objects.filter(name__istartswith=starts_with)

        if max_results > 0:
            if len(cat_list) > max_results:
                cat_list = cat_list[:max_results]
    return cat_list



def suggest_category(request):
    cat_list = []
    starts_with = ''

    if request.method == 'GET':
        starts_with = request.GET['suggestion']
    cat_list = get_category_list(8, starts_with)

    return render(request, 'rango/cats.html', {'cats' : cat_list})


@login_required
def auto_add_page(request):
    cat_id = None
    url = None
    title = None
    context_dict = {}
    if request.method == 'GET':
        cat_id = request.GET['category_id']
        url = request.GET['url']
        title = request.GET['title']
        if cat_id:
            category = Category.objects.get(id=int(cat_id))
            p = Page.objects.get_or_create(category=category, title=title, url=url)
            pages = Page.objects.filter(category=category).order_by('-views')
            # Adds our results list to the template context under name pages.
            context_dict['pages'] = pages

    return render(request, 'rango/page_list.html', context_dict)



    
    
            

    

