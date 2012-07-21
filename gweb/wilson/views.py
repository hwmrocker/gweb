# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, Http404, HttpResponseNotAllowed
from models import MenuPlaceholder, InternURL, Picture, PictureDescription, Album
from htags.models import Tag
from htags.forms.tag_forms import SimpleTagAddForm
from django.contrib.auth.decorators import permission_required
from django.utils import translation
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.template.defaultfilters import slugify

# Create your views here.
def wilson(request):
    return render_to_response('wilson/wilson.html', {}, context_instance=
RequestContext(request))

def index(request):
    return redirect_to_translation(request, 'startseite')

def photo_index(request):
    return render_to_response('wilson/photo_index.html', {'albums':Album.objects.all(),}, context_instance=
RequestContext(request))

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def edit_picture(request, photo_id):
    from forms import PictureForm, PictureDescriptionForm
    photo = get_object_or_404(Picture, pk=photo_id)
    if request.method == "POST":
        pform = PictureForm(request.POST,instance=photo, prefix="pic_")
        if pform.is_valid():
            pform.save()
        descforms=[]
        for lang,foo in settings.LANGUAGES:
            desc=photo.description(force_lang=lang)
            if desc == None:
                descf = PictureDescriptionForm(request.POST,instance=PictureDescription(i18n=lang,picture=photo), prefix=lang)
            else:
                descf = PictureDescriptionForm(request.POST,instance=desc, prefix=lang)
            if descf.is_valid():
                descf.save()
            else:
                pass
                #tmp_desc = descf.save(commit=False)
                #if (tmp_desc.title == "" and tmp_desc.short == "" and tmp_desc.description == ""):
                #    descf = PictureDescriptionForm(instance=desc, auto_id="id_"+lang+"_%s")
            descforms.append((foo,descf))
        return HttpResponseRedirect(request.POST['next'])

def photo(request, photo_id, lang='en'):
    photo = get_object_or_404(Picture, pk=photo_id)
    if request.GET.get('redirect','') != '':
        return HttpResponseRedirect(reverse('wilson:photo',kwargs={'lang':translation.get_language(),'photo_id':photo_id}))
    
    try:
        next = Picture.objects.filter(id__gt=photo_id).order_by('id')[0]
        next = reverse('wilson:photo',kwargs={"photo_id":next.id, 'lang':lang})
    except:
        next = ''
    try:    
        prev = Picture.objects.filter(id__lt=photo_id).order_by('-id')[0]
        prev = reverse('wilson:photo',kwargs={"photo_id":prev.id, 'lang':lang})
    except:
        prev = ""

    tags = photo.get_tags().keys()

    if len(tags) > 0:
        tag_list = tags[0].get_all_ancestors(additional_tags=tags[1:])
    else:
        tag_list = []
    
    return render_to_response('wilson/photo.html', {'obj': photo,
            'next':next, 'prev':prev, 'tag_list': tag_list, #'tags':tags, 
            'menu':{'left':list(MenuPlaceholder.objects.filter(parent=None, position_h='l').order_by('position_v')),
                    'right':list(MenuPlaceholder.objects.filter(parent=None, position_h='r').order_by('position_v'))},
            }, context_instance=
RequestContext(request))

def redirect_to_translation(request,page_url):
    int_url = get_object_or_404(InternURL, url=page_url)
    return HttpResponseRedirect('/'+int_url.page.get_translated_page(request=request).internurl_set.all()[0].url)

def get_page(request, page_url):
    if page_url == "":
        return index(request)

    int_url = get_object_or_404(InternURL, url=page_url)
    if int_url.redirect_to != '' and int_url.redirect_to != None:
        return HttpResponseRedirect(int_url.redirect_to)
    
    if (int_url.page.i18n in translation.get_language() or translation.get_language() in int_url.page.i18n):
        page = int_url.page
    else:
        redirect = request.GET.get('redirect','')
        if redirect != '':
            return redirect_to_translation(request, int_url.url)
        else:
            page = int_url.page
    #print page_url
    #left_menu_items = MenuObject.objects.filter(parent=null, position_h='l')
    return render_to_response('wilson/wilson.html', {'page':page,
    'menu':{'left':list(MenuPlaceholder.objects.filter(parent=None, position_h='l').order_by('position_v')),
            'right':list(MenuPlaceholder.objects.filter(parent=None, position_h='r').order_by('position_v'))}},
            context_instance=RequestContext(request))


def photo_index(request, lang='en'):
    if request.GET.get('redirect','') != '':
        return HttpResponseRedirect(reverse('wilson:photo_index',kwargs={'lang':translation.get_language()}))

    albums = Album.objects.all()
    return render_to_response('wilson/album_index.html', {'albums':albums,
    'menu':{'left':list(MenuPlaceholder.objects.filter(parent=None, position_h='l').order_by('position_v')),
            'right':list(MenuPlaceholder.objects.filter(parent=None, position_h='r').order_by('position_v'))}},
            context_instance=RequestContext(request))
    
def album(request, album_id, lang='en',name=''):
    if album_id == '0':
        query = request.GET.get('query',' ')
        album=Album(query=query)
        album.id=0

    else:
        album = get_object_or_404(Album, id=album_id)
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    
    if request.GET.get('redirect','') != '':
        if album_id == '0' and page == 1:
            goto = reverse('wilson:custom_album',kwargs={'lang':translation.get_language(),'query':query})
        elif album_id =='0' and page > 1:
            goto=reverse('wilson:custom_album',kwargs={'lang':translation.get_language(),'page':page,'query':query})
        elif page == 1:
            goto=reverse('wilson:album',kwargs={'lang':translation.get_language(),'album_id':album_id,'name':slugify(album.title())})
        else:
            goto=reverse('wilson:album_page',kwargs={'lang':translation.get_language(),'album_id':album_id,'name':slugify(album.title()),'page':page})
        return HttpResponseRedirect(goto)

    paginator = Paginator(album.pictures_id_list(), 35,7)

    # If page request (9999) is out of range, deliver last page of results.
    try:
        album_pics = paginator.page(page)
    except (EmptyPage, InvalidPage):
        album_pics = paginator.page(paginator.num_pages)
    album_pics.page_range = paginator.page_range
    return render_to_response('wilson/album.html', {'album':album,'album_pics':album_pics,
    'menu':{'left':list(MenuPlaceholder.objects.filter(parent=None, position_h='l').order_by('position_v')),
            'right':list(MenuPlaceholder.objects.filter(parent=None, position_h='r').order_by('position_v'))}},
            context_instance=RequestContext(request))

def album_picture(request, album_id, picture_id, lang='en',name='', redirect=False, picture_title=''):
    if album_id == '0':
        query = request.GET.get('query',' ')
        album=Album(query=query)
        album.id=0
    else:
        album = get_object_or_404(Album, id=album_id)
    picture_id = int(picture_id)
    picture = album.pictures_list()[picture_id]
    album.slice = album.get_slice(picture_id)
    
    if redirect or request.GET.get('redirect','') != '':
        if album_id == '0':
            return HttpResponseRedirect(reverse('wilson:custom_album_picture',kwargs={'lang':lang,'query':album.queryurl(), 'picture_title':slugify(picture.title()), 'picture_id':picture_id}))
        else:
            return HttpResponseRedirect(reverse('wilson:album_picture',kwargs={'lang':lang,'name':slugify(album.title()), 'album_id':album_id, 'picture_title':slugify(picture.title()), 'picture_id':picture_id}))
    prev = next = None
    if album.id != 0:
        if 0 < picture_id:
            prev = reverse('wilson:album_picture',kwargs={'album_id':album_id,'picture_id':picture_id-1, 'lang':lang, 'name':slugify(album.title())})
        if picture_id < len(album.pictures_list())-1:
            next = reverse('wilson:album_picture',kwargs={'album_id':album_id,'picture_id':picture_id+1, 'lang':lang, 'name':slugify(album.title())})
    else:
        if 0 < picture_id:
            prev = reverse('wilson:custom_album_picture',kwargs={'picture_id':picture_id-1,'query':album.queryurl(), 'lang':lang})
        if picture_id < len(album.pictures_list())-1:
            next = reverse('wilson:custom_album_picture',kwargs={'picture_id':picture_id+1,'query':album.queryurl(), 'lang':lang})
    album_page = ((picture_id)//35)+1
    if album.id == 0:
        album_url = reverse('wilson:custom_album_page',kwargs={'page':album_page,'query':album.queryurl(), 'lang':lang})
    else:
        album_url = reverse('wilson:album_page',kwargs={'name':slugify(album.title()),'album_id':album_id,'page':album_page, 'lang':lang})
    return render_to_response('wilson/album_picture.html', {'album':album, 'obj':picture, 'prev':prev,'next':next,
    'album_url':album_url,
    'menu':{'left':list(MenuPlaceholder.objects.filter(parent=None, position_h='l').order_by('position_v')),
            'right':list(MenuPlaceholder.objects.filter(parent=None, position_h='r').order_by('position_v'))}},
            context_instance=RequestContext(request))

def ie(request):
    return render_to_response('wilson/ie.html', context_instance=RequestContext(request))
def logout_redirect(request):
    from django.contrib.auth import logout
    redirect_to = request.META.get('HTTP_REFERER','/home') 
    logout(request)
    return HttpResponseRedirect(redirect_to)

def ajax_get_tag_id(request):
    if request.method == 'POST':
        ids = request.POST.get('ids','').split(',')
        from htags.models import Tag
        tmp = []
        for id in ids:
            try:
                tag = Tag.objects.get(id=id).text
            except:
                tag = 'id='+str(id)
            tmp.append(str(id)+':'+tag)
        return HttpResponse('|'.join(tmp))
    return HttpResponseNotAllowed(['POST'])

def ajax_get_tag_info(request):
    def clean(st):
        """
        fall 1: <> or foo | <> and foo  ==> foo
        fall 2: foo or <> | foo and <>  ==> foo
        fall 3: foo or <> or bar        ==> foo or bar
        fall 4: foo and <> or bar       ==> foo or bar
        fall 5: foo or <> and bar       ==> foo or bar
        
        """
        import re
        pos = st.find('<>')
        begin=old_begin = st.find('(',0,pos)
        while begin > 0:
            old_begin = begin
            begin = st.find('(',begin+1,pos)
        
        begin = old_begin+1
        end = st.find(')',pos)
        end = len(st) if end == -1 else end
        tmp_st = st[begin:end]
        def rp(mo):
            return mo.group(1).replace(mo.group(2),'')
        tmp_st = re.sub(r'((<>[\s]+and)[\s\w\d=_]+)',rp,tmp_st)
        tmp_st = re.sub(r'([\s\w\d=_]+(and[\s]+<>))',rp,tmp_st)
        tmp_st = re.sub(r'((<>[\s]+or)[\s\w\d=_]+)',rp,tmp_st)
        tmp_st = re.sub(r'([\s\w\d=_]+(or[\s]+<>))',rp,tmp_st)
        tmp_st = tmp_st.replace('<>','')
        tmp_st = re.sub(r'[\s]{2,}',' ',tmp_st)
        return st[:old_begin+1]+tmp_st+st[end:]
        
    if request.method == 'POST':
        id = request.POST.get('id','')
        query = request.POST.get('query','mist')
        from htags.models import Tag
        #try:
        tag=Tag.objects.get(id=id)
        parent_list = []
        child_list =[]
        tmp_list = [o.id for o in Tag.complex_filter(query.replace('<>','id='+str(id)),Picture)]
        tmp_list.sort()
        rm = [i.id for i in Tag.complex_filter(clean(query),Picture)]
        rm.sort()
        for parent in tag.get_all_parents():
            tmpquery = query.replace('<>','id='+str(parent.id))
            tmp = [i.id for i in Tag.complex_filter(tmpquery,Picture)]
            tmp.sort()
            tmpquery = query.replace('<>','')
            if tmp == tmp_list or tmp == rm:
                continue
            pic_count = len(tmp)
            if pic_count > 0:
                parent_list.append((parent,pic_count))
        for child in tag.get_all_children():
            tmpquery = query.replace('<>','id='+str(child.id))
            tmp = [i.id for i in Tag.complex_filter(tmpquery,Picture)]
            tmp.sort()
            if tmp == tmp_list or tmp == rm:
                continue
            pic_count = len(tmp)
            if pic_count > 0:
                child_list.append((child,pic_count))
        
        
        return render_to_response('wilson/replace_snippet.html',{'tag':tag,'query':query,'parents':parent_list,'children':child_list,'current_count':len(tmp_list), 'del':{'count':len(rm),'query':clean(query)}},
        context_instance=RequestContext(request))
        #except TypeError as t:
        #    raise t
        #except Exception as e:
        #    info = str(e) if settings.DEBUG else ''
        #    return HttpResponse('<p>interner Fehler</p><p>'+info+'</p>')
    return HttpResponseNotAllowed(['POST'])
def ajax_get_tag_infos(request):
    if request.method == 'POST':
        ids = request.POST.get('ids','').split(',')
        from htags.models import Tag
        data = {}
        for id in ids:
            try:
                tag = Tag.objects.get(id=id)
                children = tag.get_all_children()
                parents = tag.get_all_parents()
                data[tag.id] = {}
                data[tag.id]['name']=tag.text
                data[tag.id]['children']={}
                for child in children:
                    data[tag.id]['children'][child.id]=child.text
                data[tag.id]['parents']={}
                for parent in parents:
                    data[tag.id]['parents'][parent.id]=parent.text
                
            except:
                pass
        import simplejson
        return HttpResponse(simplejson.dumps(data),mimetype='application/json')
    return HttpResponseNotAllowed(['POST'])

@permission_required('htags.can_attach_tag')
def attach_tags(request):
    def get_type(type_str):
        """ find the lookup class for the named channel.  this is used internally """
        lookup_label = type_str.rsplit('.',1)
        lookup_module = __import__( lookup_label[0],{},{},[''])
        lookup_class = getattr(lookup_module,lookup_label[1] )
        return lookup_class()
    
    if request.method == 'POST': # If the form has been submitted...
        form = SimpleTagAddForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            ret = ""
            object_id = form.cleaned_data['object_id']
            type = get_type(form.cleaned_data['object_type'])
            object = get_object_or_404(type, pk=object_id)
            for tag in form.cleaned_data['tag_list'].split(','):
                tag = tag.strip()
                try:
                    if tag.startswith("id="):
                        tag = tag[3:]
                        tago = Tag.objects.get(id=int(tag))
                    elif tag.startswith("new="):
                        tag = tag[4:]
                        count = Tag.objects.filter(text__iexact=tag).count()
                        if count == 1:
                            tago = Tag.objects.filter(text__iexact=tag)[0]
                        elif count > 1:
                            count = Tag.objects.filter(text=tag).count()
                            if count == 1:
                                tago = Tag.objects.filter(text=tag)[0]
                            elif count > 1:
                                ret += 'WW:' + tag + '|'
                                continue
                        else:
                            tago = Tag()
                            tago.text = tag
                            tago.save()

                    else:
                        tago = Tag.objects.get(text=tag)
                    object.add_tags(tago)
                    ret += "OK:" + str(tago.id) + ":" + tago.text + "|"
                    #else:
                    #    ret += "EE:" + tag + "|"
                except:
                    #TODO message to user
                    ret += "EE:" + tag + "|"
                    continue

#            return "OK"
            return HttpResponse(ret)
            #return HttpResponseRedirect(reverse('truemen.slogans.views.slogan',
            #                                    args=(slogan_id,))) # Redirect after POST
        else:
            #return HttpResponseRedirect('/')
            pass
    else:
        #return HttpResponseRedirect('/')
        form = SimpleTagAddForm() # An unbound form

    return render_to_response('slogans/add_tag.html', {
        'form': form,
    }, context_instance=RequestContext(request))

@permission_required('htags.can_detach_tag')    
def detach_tags(request):
    def get_type(type_str):
        """ find the lookup class for the named channel.  this is used internally """
        lookup_label = type_str.rsplit('.',1)
        lookup_module = __import__( lookup_label[0],{},{},[''])
        lookup_class = getattr(lookup_module,lookup_label[1] )
        return lookup_class()
    if request.method == 'POST': # If the form has been submitted...
        form = SimpleTagAddForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            ret = ""
            object_id = form.cleaned_data['object_id']
            type = get_type(form.cleaned_data['object_type'])
            object = get_object_or_404(type, pk=object_id)
            for tag in form.cleaned_data['tag_list'].split(','):
                tag = tag.strip()
                try:
                    if tag.startswith("id="):
                        tago = Tag.objects.get(id=int(tag[3:]))
                    else:
                        tago = Tag.objects.get(text=tag)

                    object.remove_tags(tago)
                    ret += "OK:" + str(tago.id) + ":" + tago.text + "|"
                except Exception as e:
                    #TODO message to user
                    if tag.startswith("id="):
                        tag = tag[3:]
                    ret += "EE:" + tag + "|"
                    continue

#            return "OK"
            return HttpResponse(ret)
        else:
            #return HttpResponseRedirect('/')
            pass
    else:
        #return HttpResponseRedirect('/')
        form = SimpleTagAddForm() # An unbound form

    return render_to_response('slogans/add_tag.html', {
        'form': form,
    }, context_instance=RequestContext(request))
