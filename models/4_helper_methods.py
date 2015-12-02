# -*- coding: utf-8 -*-
# Y0072003

# Helper methods
def sign_in_and_out():
    if auth.is_logged_in():
        return LI(A(get_display_name(auth.user), SPAN(_class='caret'), _class='dropdown-toggle', _href='#', _role='button',
                    **{'_data-toggle': 'dropdown', '_aria-haspopup': 'true', '_aria-expanded': 'false'}),
                  UL(LI(A(T('View Boxes'), _href=URL('main', 'user', args=['view_boxes']))),
                     LI(A(T('View Comics'), _href=URL('main', 'user', args=['view_comics']))),
                     LI(_class='divider', _role='separator'),
                     LI(A(T('Sign Out'), _href=URL('main', 'user', args=['logout'], vars=dict(_next=URL('main', 'index'))))),
                     _class='dropdown-menu'),
                  _class='dropdown')
    else:
        return LI(A(T('Sign In'), _href=URL('main', 'user', args=['login'], vars=dict(_next=URL('main', 'user', args=['view_boxes'])))))


def construct_box_preview(box):
    owner = db(db.auth_user.id == box.user_id).select()[0]
    comics = get_comics(box)
    box_thumbnail = get_box_thumbnail(box)
    
    return DIV(A(box_thumbnail,
                 _href=URL('boxes', 'box', vars=dict(id=box.id))),
               DIV(A(box.name,
                     _href=URL('boxes', 'box', vars=dict(id=box.id))),
                   _class='box-name'),
               DIV(str(len(comics)) + ' comics',
                   _class='box-comic-count'),
               DIV(A(owner.display_name,
                     _href=URL('main', 'user', args=['view_boxes'], vars=dict(id=owner.id))),
                   _class='box-owner'),
               DIV(_class='clear-floats'),
               _class='box-preview')


def construct_comic_preview(comic, current_box):
    owner = db(db.auth_user.id == current_box.user_id).select()[0]
    
    return DIV(A(IMG(_src=URL('main', 'download', args=comic.image),
                     _class='comic-thumbnail'),
                 _href=URL('comics', 'comic', vars=dict(id=comic.id, box_id=current_box.id))),
               A(DIV(comic.title, _class='comic-title'),
                 _href=URL('comics', 'comic', vars=dict(id=comic.id, box_id=current_box.id))),
               DIV('Issue No. ' + str(comic.issue_no),
                   _class='comic-issue-no'),
               DIV(A(owner.display_name,
                     _href=URL('main', 'user', args=['view_boxes'], vars=dict(id=owner.id))),
                   _class='comic-owner'),
               DIV(_class='clear-floats'),
               _class='comic-preview')


def construct_user_preview(user):
    users_public_boxes = db((db.boxes.user_id == user.id)
                            & (db.boxes.visible == True)).select()
    user_thumbnail = get_user_thumbnail(user, users_public_boxes)
    box_count = len(users_public_boxes)
    box_term = 'boxes' if box_count > 1 else 'box'
    box_text = str(box_count) + ' ' + box_term if box_count > 0 else 'No boxes'
    
    return DIV(A(user_thumbnail,
                 _href=URL('main', 'user', args=['view_boxes'], vars=dict(id=user.id))),
               A(DIV(user.display_name, _class='user-display-name'),
                 _href=URL('main', 'user', args=['view_boxes'], vars=dict(id=user.id))),
               DIV(box_text,
                   _class='user-boxes'),
               DIV(_class='clear-floats'),
               _class='user-preview')


def new_box_icon():
    return DIV(A(IMG(_src=URL('static', 'images/add_box.png'),
                     _class='box-thumbnail'),
                 _href=URL('boxes', 'create')),
               DIV(_class='clear-floats'),
               _class='box-preview')


def new_comic_icon(box=None):
    if box == None:
        link = URL('comics', 'create')
    else:
        link = URL('comics', 'create', vars=dict(box_id=box.id))
    
    return DIV(A(IMG(_src=URL('static', 'images/add_comic.png'),
                     _class='comic-thumbnail'),
                 _href=link),
               DIV(_class='clear-floats'),
               _class='comic-preview')


def get_box_thumbnail(box):
    comics = get_comics(box)
    
    # Check that the box has at least one comic
    # If not, use the default box image
    if (len(comics) == 0):
        thumbnail = IMG(_src=URL('static', 'images/default_box.png'),
                        _class='box-thumbnail')
    else:
        thumbnail = IMG(_src=URL('main', 'download', args=comics[0].image),
                        _class='box-thumbnail')
    
    return DIV(thumbnail,
               IMG(_src=URL('static', 'images/box_indicator.png'),
                   _class='box-indicator'),
               _class='box-image')


def get_user_thumbnail(user, users_public_boxes=None):
    if users_public_boxes == None:
        users_public_boxes = db((db.boxes.user_id == user.id)
                                & (db.boxes.visible == True)).select()
    
    # Check that the user has at least one public box
    # If not, use the default user image
    if (len(users_public_boxes) == 0):
        thumbnail = IMG(_src=URL('static', 'images/default_user.png'),
                        _class='user-thumbnail')
    else:
        comics = get_comics(users_public_boxes[0])
        
        # Check that the box has at least one comic
        # If not, use the default box image
        if (len(comics) == 0):
            thumbnail = IMG(_src=URL('static', 'images/default_box.png'),
                            _class='box-thumbnail')
        else:
            thumbnail = IMG(_src=URL('main', 'download', args=comics[0].image),
                            _class='box-thumbnail')
    
    return DIV(thumbnail,
               IMG(_src=URL('static', 'images/user_indicator.png'),
                   _class='user-indicator'),
               _class='user-image')


def get_comics(box, select=db.comics.ALL):
    return db((db.comics.id == db.comic_box_map.comic_id)
              & (db.comic_box_map.box_id == box.id)).select(select)


def get_boxes(comic, select=db.boxes.ALL):
    return db((db.boxes.id == db.comic_box_map.box_id)
              & (db.comic_box_map.comic_id == comic.id)).select(select)


def get_visible_boxes(public_only=False, order=None):
    # Public boxes are always visible to everyone, so fetch them first
    if order:
        public_boxes = db(db.boxes.visible == True).select(db.boxes.ALL, orderby=order)
    else:
        public_boxes = db(db.boxes.visible == True).select(db.boxes.ALL)
    
    if public_only:
        visible_boxes = public_boxes
    else:
        # If a user is signed in, also show their private boxes
        if auth.user:
            if order:
                users_boxes = db(db.auth_user.id == auth.user.id).select(db.boxes.ALL, orderby=order)
            else:
                users_boxes = db(db.auth_user.id == auth.user.id).select(db.boxes.ALL)
            
            visible_boxes = public_boxes | users_boxes
    
    return visible_boxes


def is_box_visible(box):
    return box.visible or (auth.user and (auth.user.id == box.user_id))


def is_comic_visible(comic):
    # A comic is visible if:
    # - it is in a box owned by the current user, or
    # - it is in at least one public box
    
    boxes = get_boxes(comic)
    
    for box in boxes:
        if is_box_visible(box):
            return (True, box)
    
    return (False, None)
