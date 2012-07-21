# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('wilson',
    # Uncomment the next line to enable the admin:
    (r'^fotos/?$', 'views.photo_index', {'lang':'de'}, "photo_index"),
    (r'^fotos/album/benutzerdefiniert-0\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'de'} ,"custom_album"),
    (r'^fotos/album/benutzerdefiniert-0\?page=(?P<page>[\d]+)&query=(?P<query>[^&]*)$', 'views.album', {'lang':'de'} ,"custom_album_page"),
    (r'^fotos/album/benutzerdefiniert-0/(?P<picture_id>[\d]+)\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'de','redirect':True} ,"custom_album_picture"),
    (r'^fotos/album/benutzerdefiniert-0/(?P<picture_title>[\w\d-]*)-(?P<picture_id>[\d]+)\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'de'} ,"custom_album_picture"),

    (r'^fotos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/?$', 'views.album', {'lang':'de'} ,"album"),
    (r'^fotos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)\?page=(?P<page>[\d]+)$', 'views.album', {'lang':'de'} ,"album_page"),
    (r'^fotos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/(?P<picture_id>[\d]+)/?$', 'views.album_picture', {'lang':'de','redirect':True} ,"album_picture"),
    (r'^fotos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/(?P<picture_title>[\w\d-]*)-(?P<picture_id>[\d]+)/?$', 'views.album_picture', {'lang':'de'} ,"album_picture"),

    (r'^foto/(?P<photo_id>[\d]+)$', 'views.photo', {"lang":"de"} ,"photo"),

    
    (r'^photos/?$', 'views.photo_index', {'lang':'en'}, "photo_index"),
    (r'^photos/album/custom-0\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'en'} ,"custom_album"),
    (r'^photos/album/custom-0\?page=(?P<page>[\d]+)&query=(?P<query>[^&]*)$', 'views.album', {'lang':'en'} ,"custom_album_page"),
    (r'^photos/album/custom-0/(?P<picture_id>[\d]+)\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'en'} ,"custom_album_picture"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/?$', 'views.album', {'lang':'en'} ,"album"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)\?page=(?P<page>[\d]+)$', 'views.album', {'lang':'en'} ,"album_page"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/(?P<picture_id>[\d]+)/?$', 'views.album_picture', {'lang':'en'} ,"album_picture"),

    (r'^photo/(?P<photo_id>[\d]+)$', 'views.photo', {"lang":"en"} ,"photo"),

    
    (r'^photos/?$', 'views.photo_index', {'lang':'fr'}, "photo_index"),
    (r'^photos/album/personnalise-0\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'fr'} ,"custom_album"),
    (r'^photos/album/personnalise-0\?page=(?P<page>[\d]+)&query=(?P<query>[^&]*)$', 'views.album', {'lang':'fr'} ,"custom_album_page"),
    (r'^photos/album/personnalise-0/(?P<picture_id>[\d]+)\?query=(?P<query>[^&]*)$', 'views.album', {'lang':'fr'} ,"custom_album_picture"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/?$', 'views.album', {'lang':'fr'} ,"album"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)\?page=(?P<page>[\d]+)$', 'views.album', {'lang':'fr'} ,"album_page"),
    (r'^photos/album/(?P<name>[\w\d-]*)-(?P<album_id>[\d]+)/(?P<picture_id>[\d]+)/?$', 'views.album_picture', {'lang':'fr'} ,"album_picture"),
    
    (r'^photo/(?P<photo_id>[\d]+)$', 'views.photo', {"lang":"fr"} ,"photo"),
    
    #(r'^photo$', 'views.photo_index', {} ,"photo_index"),
    (r'^edit/photo/(?P<photo_id>[\d]+)$', 'views.edit_picture', {} ,"edit_picture"),
    
    (r'^warning','views.ie',{},"ie"),
    (r'^(?P<page_url>[\w\d/-]+)$', 'views.get_page', {} ,"get_page"),
    (r'^$', 'views.index', {} ,"index"),
    (r'^translate/(?P<page_url>[\w\d/-]*)$', 'views.redirect_to_translation'),

)
