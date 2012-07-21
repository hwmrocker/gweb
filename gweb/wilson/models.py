from django.db import models
from django.contrib.contenttypes import generic
from htags.models import TaggedObject
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.utils import translation
from django.contrib import messages
from django.conf import settings
from django.template.defaultfilters import slugify


#from forms import PictureForm, PictureDescriptionForm

# Create your models here.
class InternURL(models.Model):
    url = models.CharField(max_length=200, unique=True)
    page = models.ForeignKey('Page', null=True, blank=True)
    redirect_to = models.CharField(max_length=2000, null=True, blank=True)
    def __unicode__(self):
        return "%s" % (self.url)
    
class Page(TaggedObject):
    headline = models.CharField(max_length=200)
    short_name = models.CharField(max_length=20)
    content = models.TextField()
    i18n = models.CharField(max_length=12)
    translation_of = models.ForeignKey('self', null=True, blank=True)
    header = models.ForeignKey('Block', null=True, blank=True, related_name='page_hdr')
    footer = models.ForeignKey('Block', null=True, blank=True, related_name='page_ftr')
    additional_menus = models.ManyToManyField('MenuObject', null=True, blank=True, related_name='shown_on_page')
    #pictures = models.ManyToManyField('Pictures', through='PagePicBridge', null=True, blank=True)

    def __unicode__(self):
        return "%s (%i)" % (self.short_name , self.id)
    
    def get_translated_page(self, lang=None, request=None):
        def check_list(lang, querylist):
            """
                returns Page or None
            """
            possible_match = querylist.filter(i18n=lang)
            #TODO: settings -> if exclude_rude ...
            #TODO: create translation cloud and check them first
            try_one_more = True
            while True:
                if len(possible_match) == 0:
                    #TODO if not settings.exlcude_rude and exclude_rude ->
                    #recrusive
                    pass
                elif len(possible_match) == 1:
                    return possible_match[0]
                else:
                    for tag in possible_match.filter(is_representative=True):
                        if tag.i18n.startswith(lang):
                            return tag

                    if self in possible_match and self.i18n.startswith(lang):
                        return self
                    return possible_match[0]
                if not try_one_more:
                    break
                try_one_more = False
                possible_match = querylist.filter(i18n__startswith=lang)
        
        tmp_list = []
        trans_list = []    
        if self.translation_of:
            tmp_list.append(self.translation_of)
        if len(self.page_set.all()) > 0:
            tmp_list.extend(list(self.page_set.all()))
        while len(tmp_list) > 0:
            tr = tmp_list.pop()
            trans_list.append(tr)
            for pos in tr.page_set.all():
                if pos not in tmp_list and pos not in trans_list:
                    tmp_list.append(pos)
            if tr.translation_of and tr.translation_of not in tmp_list and tr.translation_of not in trans_list:
                tmp_list.append(tr.translation_of)
        querylist = Page.objects.filter(id__in=[t.id for t in trans_list])
        
        
        if lang == None:
            lang = translation.get_language()
        try_one_more = True
        while True:
            while True:
                match = check_list(lang, querylist)
                if match:
                    return match
                oldlang, lang = lang, lang.rsplit('-', 1)[0]
                if oldlang == lang or lang == '':
                    break
            if not try_one_more:
                break
            try_one_more = False
            lang = 'en' #TODO settings default lang
            messages.warning(request, "Sorry, this page isn't translated yet", fail_silently=True)
        return self
    
class Block(models.Model):
    name = models.CharField(max_length=100)
    content = models.TextField()

    def __unicode__(self):
        return "%s (%i)" % (self.name , self.id)

class MenuPlaceholder(models.Model):
    name = models.CharField(max_length=20, null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    position_v = models.SmallIntegerField()
    position_h = models.CharField(max_length=1,
                                  choices=(('r', _('right')),
                                           ('l', _('left')),
                                           (' ', _('None'))),
                                   default=' ')
    logo = models.CharField(max_length=20, null=True, blank=True)
    html_class = models.CharField(max_length=100, null=True, blank=True)
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self,*args, **kwargs)
        self._cache = {}
        
    def menu_object(self, force_lang=None):
        if force_lang != None:
            tmp = self.menuobject_set.filter(i18n__startswith=force_lang)
            if len(tmp) > 0:
                return tmp[0]
            else:
                return None
        try:
            return self._cache['description']
        except:
            lang = translation.get_language()
            tmp = self.menuobject_set.all()
            
            #TODO: include i18n support
            if len(tmp) == 1:
                self._cache['description'] = tmp[0]
                return tmp[0]
            elif len(tmp) >1:
                while True:
                    tmp2 = tmp.filter(i18n__startswith=lang)
                    if len(tmp2) >= 1:
                        self._cache['description'] = tmp2[0]
                        return tmp2[0]
                    #TODO remove hardcoded default language 'en'
                    if '-' in lang:
                        lang = lang.rsplit('-',1)[0]
                    elif not lang.startswith('en'):
                        lang = 'en'
                    else:
                        self._cache['description'] = None
                        return None
            else:
                self._cache['description'] = None
                return None
    
    def __unicode__(self):
        return "%s (%i)" % (self.name , self.id)
    
#TODO: split Menuobject into name, parent, position, logo and the i18n part
class MenuObject(models.Model):
    url = models.ForeignKey('InternURL', null=True, blank=True)
    html_class = models.CharField(max_length=100, null=True, blank=True)
    #parent = models.ForeignKey('self', null=True, blank=True)
    #position_v = models.SmallIntegerField()
    #position_h = models.CharField(max_length=1,
    #                              choices=(('r', _('right')),
    #                                       ('l', _('left')),
    #                                       (' ', _('None'))),
    #                               default=' ')
    extern_url = models.CharField(max_length=200, null=True, blank=True)
    title = models.CharField(max_length=20, null=True, blank=True)
    fontsize = models.SmallIntegerField(default=40)
    logo = models.CharField(max_length=20, null=True, blank=True)
    position_info = models.ForeignKey(MenuPlaceholder)
    i18n = models.CharField(max_length=12)

    def __unicode__(self):
        return "%s (%i)" % (self.title , self.id)
    
    def is_intern(self):
        if self.url:
            return True
        else:
            if self.extern_url:
                return False
            else:
                return True
#class MenuObjectI18NData(models.Model):
#    url = models.CharField(max_length=200, unique=True)
#
#    i18n = models.CharField(max_length=12)
#    translation_of = models.ForeignKey('MenuObject')

#==============================================================================#
#                                Page Elements
#==============================================================================#

class Person(TaggedObject):
    name = models.CharField(max_length=100)
    def __unicode__(self):
        return "%s (%i)" % (self.name , self.id)

#class PagePicBridge(models.Model):
#    page = models.ForeignKey('Page')
#    picture = models.ForeignKey('Picture')
#    label = models.CharField(max_length=20)

#class PageAlbumBridge(models.Model):
#    page = models.ForeignKey('Page')
#    album = models.ForeignKey('Album')
#    #label = models.CharField(max_length=20)
#    def label(self):
#        return unicode(self.album.label)

#class AlbumPicBridge(models.Model):
#    album = models.ForeignKey('Album', null=True, blank=True)
#    picture = models.ForeignKey('Picture')
#    #label = models.CharField(max_length=20)
    

class Album(models.Model):
    label = models.CharField(max_length=20)
    query = models.CharField(max_length=4000)
    sortby = models.CharField(max_length=100, default='id')
    reference_picture = models.ForeignKey('Picture', null=True, blank=True)
    def __init__(self, *args, **kwargs):
        models.Model.__init__(self,*args, **kwargs)
        self._cache = {}

    def queryurl(self):
        from urllib import quote
        return quote(self.query,"")
    def get_slice(self, idx):
        start=end=0
        if idx < 3:
            end = 7
        else:
            start = idx-3
            end = idx+4
        if end > len(self.pictures_list()):
            end = len(self.pictures_list())
            start = end - 7
            if start < 0:
                start = 0
        return self.pictures_id_list()[start:end]
    def num_pictures(self):
        try:
            return self._cache['num_pictures']
        except:
            self._cache['num_pictures'] = len(self.pictures_list())
            return self._cache['num_pictures']
    
    def pictures(self):
        try:
            return self._cache['pictures']
        except:
            from htags.models import Tag
            self._cache['pictures'] = Tag.complex_filter(str(self.query), Picture).distinct().order_by(self.sortby)
            return self._cache['pictures']
    def pictures_list(self):
        try:
            return self._cache['pictures_list']
        except:
            from htags.models import Tag
            self._cache['pictures_list'] = list(self.pictures())
            return self._cache['pictures_list']
    def pictures_id_list(self):
        from django.core.urlresolvers import reverse
        lang = translation.get_language()
        if self.id == 0:
            foo = "wilson:custom_album_picture"
            args = [{'picture_id':i,'query':self.queryurl(),'lang':lang } for i in range(self.num_pictures())]
        else:
            foo = "wilson:album_picture"
            args = [{'album_id':self.id,'picture_id':i,'lang':lang,'name':slugify(self.title())} for i in range(self.num_pictures())]
        urls=[reverse(foo,kwargs=args[i]) for i in range(self.num_pictures())]
        return zip(range(self.num_pictures()),self.pictures_list(),urls)    
    def representative(self):
        try:
            return self._cache['representative']
        except:
            pics = self.pictures_list()
            if self.reference_picture:
                self._cache['representative'] = self.reference_picture
            elif len(pics) > 0:
                self._cache['representative'] = pics[0]
            else:
                self._cache['representative'] = None  
            self._cache['representative'].albumid=pics.index(self._cache['representative'])
            return self._cache['representative']
    def description(self, force_lang=None):
        if force_lang != None:
            tmp = self.albumdescription_set.filter(i18n__startswith=force_lang)
            if len(tmp) > 0:
                return tmp[0]
            else:
                return None
        try:
            return self._cache['description']
        except:
            lang = translation.get_language()
            tmp = self.albumdescription_set.all()
            
            #TODO: include i18n support
            if len(tmp) == 1:
                self._cache['description'] = tmp[0]
                return tmp[0]
            elif len(tmp) >1:
                while True:
                    tmp2 = tmp.filter(i18n__startswith=lang)
                    if len(tmp2) >= 1:
                        self._cache['description'] = tmp2[0]
                        return tmp2[0]
                    #TODO remove hardcoded default language 'en'
                    if '-' in lang:
                        lang = lang.rsplit('-',1)[0]
                    elif not lang.startswith('en'):
                        lang = 'en'
                    else:
                        self._cache['description'] = None
                        return None
            else:
                self._cache['description'] = None
                return None
    def title(self):
        if self.id == 0:
            return _('Custom')
        try:
            return self._cache['title']
        except:
            if self.description():
                self._cache['title']=self.description().title
            else:
                self._cache['title']=self.label
            return self._cache['title']
    def __unicode__(self):
        return "%s (%i)"%(self.label,self.id)
class AlbumDescription(models.Model):
    title = models.CharField(max_length=200)
    short = models.CharField(max_length=50)
    i18n = models.CharField(max_length=12)
    picture = models.ForeignKey('Album')
    description = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return "%s (%i)" % (self.title , self.id)
    
class Picture(TaggedObject):
    image = models.ImageField(upload_to='photo/wilson')
    thumb = models.ImageField(upload_to='thumbs/wilson', default='thumbs/none.jpg')
    title = models.CharField(max_length=100, default='')
    #datetime = models.DateTimeField()
    rating = models.FloatField(default=0)#min_value= -1, max_value=10
    number_of_ratings = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, null=True, blank=True)
    #lincense = models.ForeingKey(...)
    #comments = models.ManyToManyField(...)

    def __init__(self, *args, **kwargs):
        TaggedObject.__init__(self,*args, **kwargs)
        self._cache = {}
        
    def title(self):
        try:
            return self._cache['title']
        except:
            if self.description():
                self._cache['title'] = self.description().title 
            else:
                self._cache['title'] = self.image.name.rsplit('/',1)[1].rsplit('.',1)[0]
        return self._cache['title']

    def __unicode__(self):
        return "%s (%i)" % (self.image.name , self.id)

    def description_forms(self):
        from forms import PictureDescriptionForm 
        descforms=[]
        for lang,foo in settings.LANGUAGES:
            desc=self.description(force_lang=lang)
            if desc == None:
                descf = PictureDescriptionForm(instance=PictureDescription(i18n=lang,picture=self), prefix=lang)
            else:
                descf = PictureDescriptionForm(instance=desc, prefix=lang)
            descforms.append((foo,descf))
        return descforms
    def picture_form(self):
        from forms import PictureForm
        return PictureForm(instance=self, prefix="pic_")
    def description(self, force_lang=None):
        if force_lang != None:
            tmp = self.picturedescription_set.filter(i18n__startswith=force_lang)
            if len(tmp) > 0:
                return tmp[0]
            else:
                return None
        try:
            return self._cache['description']
        except:
            lang = translation.get_language()
            tmp = self.picturedescription_set.all()
            
            #TODO: include i18n support
            if len(tmp) == 1:
                self._cache['description'] = tmp[0]
                return tmp[0]
            elif len(tmp) >1:
                while True:
                    tmp2 = tmp.filter(i18n__startswith=lang)
                    if len(tmp2) >= 1:
                        self._cache['description'] = tmp2[0]
                        return tmp2[0]
                    #TODO remove hardcoded default language 'en'
                    if '-' in lang:
                        lang = lang.rsplit('-',1)[0]
                    elif not lang.startswith('en'):
                        lang = 'en'
                    else:
                        self._cache['description'] = None
                        return None
            else:
                self._cache['description'] = None
                return None
    def type(self):
        return "wilson.models.Picture"

    def save(self, force_insert=False, force_update=False):
        super(Picture,self).save(force_insert, force_update) 
        if not ( self.thumb and self.thumb.name != 'thumbs/none.jpg'):
            self.thumb.name = 'thumbs/'+self.image.name.split('/',1)[1]
            super(Picture,self).save(force_insert, force_update) 
            self.shrink_self()
            self.create_thumb(pos='c', THUMB_SIZE=(75,75))
        #else:
            #super(Picture,self).save(force_insert, force_update) 
           
            
    def shrink_self(self,size=(640,640)):
        from PIL import Image
        im = Image.open(self.image.path)
        im.thumbnail(size, Image.ANTIALIAS)
        im.save(self.image.path)
         
    def create_thumb(self,pos='c', THUMB_SIZE=(75,75)):
        from PIL import Image
        if pos not in ['c', 't', 'b', 'l', 'r']:
            pos = 'c'
        img = Image.open(self.image.path)
        width, height = img.size
    
        if width > height:
            delta = width - height
            upper = 0
            lower = height
            if pos == 'l':
                left = 0
                right = height
            elif pos == 'r':
                left = delta
                right = width
            else: # pos == 'c':
                left = int(delta/2)
                right = height + left
        else:
            delta = height - width
            left = 0
            right = width
            if pos == 't':
                upper = 0
                lower = width
            elif pos == 'b':
                upper = delta
                lower = height
            else: #pos == 'c'
                upper = int(delta/2)
                lower = width + upper
    
        img = img.crop((left, upper, right, lower))
        img.thumbnail(THUMB_SIZE, Image.ANTIALIAS)
        #if not ( self.thumb and not self.thumb.name == 'thumbs/none.jpg' ):
        #    self.thumb.name = 'thumbs/'+self.image.name.split('/',1)[1]
            
        img.save(self.thumb.path)
            
class PictureDescription(models.Model):
    title = models.CharField(max_length=200)
    short = models.CharField(max_length=50)
    i18n = models.CharField(max_length=12)
    picture = models.ForeignKey('Picture')
    description = models.TextField(null=True, blank=True)
    def __unicode__(self):
        return "%s (%i)" % (self.title , self.id)

class InfoTable(models.Model):
    title = models.CharField(max_length=100)
    num_columns = models.PositiveSmallIntegerField()#min_value=1, max_value=4
    html_class = models.CharField(max_length=50)
    column_options = models.CharField(max_length=200)
    header1 = models.CharField(max_length=200)
    header2 = models.CharField(max_length=200)
    header3 = models.CharField(max_length=200)
    header4 = models.CharField(max_length=200)
    def __unicode__(self):
        return "%s (%i)" % (self.title , self.id)

class InfoTableRow(models.Model):
    table = models.ForeignKey('InfoTable')
    col1 = models.CharField(max_length=200)
    col2 = models.CharField(max_length=200)
    col3 = models.CharField(max_length=200)
    col4 = models.CharField(max_length=200)
    sortkey = models.SmallIntegerField(default= -1)
    # column
