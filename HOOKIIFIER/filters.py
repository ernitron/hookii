#!/usr/bin/python

import re


pattern_url = re.compile("https?:\/\/\S+")
pattern_youtube = re.compile("https?:\/\/(?:www\.)?(?:youtu\.be\/|youtube\.com\/(?:watch\?(?:.*&)?v=|(?:embed|v)\/))([^\?&\"\'>\s]+)")
pattern_vimeo = re.compile("https?:\/\/(?:[\w]+\.)*vimeo\.com(?:[\/\w:]*)?\/([0-9]+)[\S]*")
pattern_image = re.compile("(https?:\/\/\S+\.(?:png|jpg|gif|jpeg|JPG|JPEG|GIF|PNG)(?:\?\S+)?)")
pattern_disqus = re.compile("@(\w+):disqus")
pattern_email = re.compile("([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")


## helpers functions for url filter ##

def _embed_url_generic(url):
    string = "<a href='%s' target='_blank'>%s</a>" % (url, url)
    return string, True


def _embed_url_image(url):
    replacement_string = "<img src='\\1' width='420px' />"
    string, n = pattern_image.subn(replacement_string, url)
    return string, n > 0


def _embed_url_youtube(url):
    replacement_string = "<iframe width='560' height='315' src='https://www.youtube.com/embed/\\1' frameborder='0' allowfullscreen></iframe>"
    string, n = pattern_youtube.subn(replacement_string, url)
    return string, n > 0


def _embed_url_vimeo(url):
    replacement_string = "<iframe src='https://player.vimeo.com/video/\\1' width='500' height='281' frameborder='0' allowfullscreen></iframe>"
    string, n = pattern_vimeo.subn(replacement_string, url)
    return string, n > 0


def _urlrepl(matchobj):
    url = matchobj.group(0)
    funcs = [
        _embed_url_youtube,
        _embed_url_vimeo,
        _embed_url_image,
        _embed_url_generic
    ]
    for f in funcs:
        embed, matched = f(url)
        if matched:
            return embed
    return url


## filters ##

def url(string):
    return pattern_url.sub(_urlrepl, string)


def disqus_user(string):
    return pattern_disqus.sub("<a href='https://disqus.com/by/\\1' target='_blank'>\\1</a>", string)


def email_antispam(string):
    return pattern_email.sub("\\1 (at) \\2", string)
