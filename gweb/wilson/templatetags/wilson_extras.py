from django import template
from django.utils.html import conditional_escape as esc
from django.template import Context, loader

from gweb.wilson.models import Picture, Page, Album

from django.shortcuts import render_to_response, get_object_or_404

register = template.Library()

@register.filter
def table(value):
    pass

def bylen(s1,s2):
    return len(s1)-len(s2)

@register.filter()
def pic(value, LANGUAGE_CODE='en'):
    """
        possible strings:
        for pictures:
             P[<id>]
             P[<id>][<config>]
             P[<id>][<config>](<caption>)
             
            <id> is the Picture id
            <config> could be,
                thumb   => will return a thumbnail of the picture
                big     => will will produce a big picture (with optional caption) 
                text    => will create a link to a picture (caption will be requiered and use as link text)
            <caption>
                valid HTML
        for albums:
             A[<label>]
             A[<label>][<config>]
             A[<label>][<config>](caption)
            
            <label> is the label of a Album
            <config> could be,
                thumb    => create a small preview of 
                    num=<num> define how many thumbs should be used
                    if a <caption> is set, this text will be printed beneath the thumbs
                text     => create a text link to the album
            <caption>
                valid HTML
                (eg. with combination of thumb, <> could be used to indicate which word should be used as a link.)
                    e.g.   "for more pictures visit the <album page>."
                           "for more pictures visit the <a href="..">album page</a>.
             
    """
    import re
    sa = re.compile(r'([AP]\[.*\](\(.*\))?)')
    replace_list =[]
    label_idx = 1
    for possibility,tmp in sa.findall(value):
        if possibility.startswith('P'):
            pic = re.compile(r"""(?P<all>         #
                    P                             # the inicial sign, that indicates a Picture
                    \[                            # a [
                        ((?P<id>[\d]+)             # the id
                        |(?P<ids>[\d]+,[\d]+))
                    \]                            # ]
                   (\[                            # the optional config
                        (?P<config>[\w\d=, -]+)   #
                    \])?                          #
                   (                              #
                       (<                         #
                           (?P<captiona>[^>]*)    # either a caption in () or in <>
                        >)                        #
                        |                         #
                        (\(                       #
                            (?P<captionb>[^\)]*)  #
                        \))                       #
                    )?)""",re.X)
            match = pic.match(possibility)
            
            if match:
                gd = match.groupdict('')
                gd['caption'] = gd['captiona'] or gd['captionb']
                additional_class = None
                if gd['id'] != '':
                    pic = Picture.objects.get(id=int(gd['id']))
                else:
                    pic = Picture.objects.filter(id__in=map(int,gd['ids'].split(',')))
                if 'label' in gd['config']:
                    tmp=re.findall(r'[\s,\[]label=([\d\w_-]+)',gd['config'])
                    try:
                        label = tmp[0]
                    except:
                        pass
                else:
                    label = str(gd['id']) + '_' + str(label_idx)
                    label_idx += 1
                
                if 'thumb' in gd['config']:
                    #we have a thumbpicture
                    t = loader.get_template('wilson/pic/thumb_pic.html')
                    text = gd['caption']
                elif 'text' in gd['config']:
                    text = gd.get('caption',pic.title())
                    t = loader.get_template('wilson/pic/link_pic.html')
                else: #if 'big' in gd['config'] or gd['config'] == '':
                    #we have big picture
                    if gd['id'] != '':
                        t = loader.get_template('wilson/pic/big_pic.html')
                    else:
                        t = loader.get_template('wilson/pic/2_pic.html')
                    text = gd['caption']
                    if 'class=' in gd['config']:
                        tmp=re.findall(r'[\s,\[]?class=([\w\s]+)',gd['config'])
                        try:
                            additional_class = tmp[0]
                        except:
                            additional_class = None
                c = Context({
                    'label': label,
                    'pic' : pic,
                    #'title' : title,
                    'text' : text,
                    'additional_class':additional_class,
                    'LANGUAGE_CODE':LANGUAGE_CODE,
                })
                rep = t.render(c)[:-1] # remove the last \n
                #ret = ret.format(label=label, imgurl=imgurl, thumburl=thumburl, imgtitle=esc(title), imgalt=esc(imgalt), text=text[1:-1])
                #value = value.replace(gd['all'], rep)
                replace_list.append((gd['all'], rep))
            else:
                pass
        elif possibility.startswith('A'):
            alb = re.compile(r"""(?P<all>          #
                    A                             # the inicial sign, that indicates an Album
                    \[                            # a [
                        (?P<label>[\w]+)          # the id
                    \]                            # ]
                   (\[                            # the optional config
                        (?P<config>[\w\d=, -]+)   #
                    \])?                          #
                   (                              #
                       (<                         #
                           (?P<captiona>[^>]*)    # either a caption in () or in <>
                        >)                        #
                        |                         #
                        (\(                       #
                            (?P<captionb>[^\)]*)  #
                        \))                       #
                    )?)""",re.X)
            match = alb.match(possibility)
            
            if match:
                gd = match.groupdict('')
                gd['caption'] = gd['captiona'] or gd['captionb']
                alternate_text = additional_class = None
                # this is a reference to a album 
                tmp = Album.objects.filter(label=gd['label'])
                if len(tmp) > 0:
                    album = tmp[0]
                else:
                    continue
            
                if 'text' in gd['config']:
                    num = 0
                elif 'whut' in gd['config']:
                    pass
                else: #if 'thumb' in gd['config']:
                    num = 5 
                    if 'full' in gd['config']:
                        num = album.num_pictures()
                    elif 'num=' in gd['config']:
                        tmp=re.findall(r'[\s,\[]num=([\d]+)',gd['config'])
                        try:
                            num = int(tmp[0])
                        except:
                            num = 5
                   
                        
                    if gd['caption'] != '':
                        alternate_text = gd['caption'].split('|')
                    
                t = loader.get_template('wilson/pic/thumb_album.html')
                c = Context({
                    'album': album,
                    #'label' : label,
                    'num' : num,
                    'LANGUAGE_CODE':LANGUAGE_CODE,
                    'alternate_text':alternate_text,
                    'LANGUAGE_CODE':LANGUAGE_CODE,
                })
                rep = t.render(c)[:-1] # remove the last \n
                #value = value.replace(gd['all'], rep)
                replace_list.append((gd['all'], rep))
    # Now replace everything, (longest value first)
    from operator import itemgetter
    replace_list.sort(cmp=bylen,reverse=True,key=itemgetter(0))
    for old, new in replace_list:
        value = value.replace(old,new)
    return value
#pic.is_save = False
