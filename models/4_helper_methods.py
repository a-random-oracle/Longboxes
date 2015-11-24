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
    
    return DIV(A(box_image,
                 _href=URL('boxes', 'box', vars=dict(id=box.id))),
               A(DIV(box.name,
                     _class='box-name'),
                 _href=URL('boxes', 'box', vars=dict(id=box.id))),
               DIV(str(len(comics)) + ' comics',
                   _class='box-comic-count'),
               DIV(A(owner.display_name,
                     _href=URL('user', args=['view_boxes'], vars=dict(id=owner.id))),
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
                     _href=URL('user', args=['view_boxes'], vars=dict(id=owner.id))),
                   _class='comic-owner'),
               DIV(_class='clear-floats'),
               _class='comic-preview')


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
