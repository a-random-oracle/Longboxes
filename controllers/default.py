# -*- coding: utf-8 -*-


# Site routes
def index():
    redirect(URL('main', 'index'))
    return dict()
