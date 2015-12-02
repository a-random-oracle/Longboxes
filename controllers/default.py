# -*- coding: utf-8 -*-
# Y0072003


# Site routes
def index():
    redirect(URL('main', 'index'))
    return dict()
