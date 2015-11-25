# -*- coding: utf-8 -*-

# Helper methods
def construct_box_preview(box):
    owner = db(db.auth_user.id == box.user_id).select()[0]
    comics = db(db.comics.boxes.contains(box.id)).select(db.comics.ALL, orderby=~db.comics.id)
    
    if (len(comics) == 0):
        box_image = IMG(_src=URL('static', 'images/default_box.png'),
                        _class='box-thumbnail')
    else:
        box_image = IMG(_src=URL('main', 'download', args=comics[0].image),
                        _class='box-thumbnail')
    
    if auth.user and auth.user.id == owner.id:
        if box.visible:
            visibility = ' (Public)'
        else:
            visibility = ' (Private)'
    else:
        visibility = ''
    
    return DIV(A(box_image,
                 _href=URL('boxes', 'box', vars=dict(id=box.id))),
               DIV(A(box.name,
                     _href=URL('boxes', 'box', vars=dict(id=box.id))),
                   visibility,
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
    box_count = db((db.boxes.user_id == user.id)
                   & (db.boxes.visible == True)).count()
    box_term = 'boxes' if box_count > 1 else 'box'
    box_text = str(box_count) + ' ' + box_term if box_count > 0 else 'No boxes'
    
    return DIV(A(DIV(user.display_name, _class='user-display-name'),
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


def new_comic_icon(box):
    return DIV(A(IMG(_src=URL('static', 'images/add_comic.png'),
                     _class='comic-thumbnail'),
                 _href=URL('comics', 'create', vars=dict(box_id=box.id))),
               DIV(_class='clear-floats'),
               _class='comic-preview')


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
    
    boxes = db(db.boxes.id.belongs(comic.boxes)).select()
    
    for box in boxes:
        if is_box_visible(box):
            return (True, box)
    
    return (False, None)
