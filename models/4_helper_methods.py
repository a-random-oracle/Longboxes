# -*- coding: utf-8 -*-

# Helper methods
def construct_box_preview(box):
    user_id = db(db.auth_user.id == db.boxes.user_id and
                 db.boxes.id == box.id).select()[0].user_id
    owner = db(db.auth_user.id == user_id).select()[0]
    comics = db(db.comics.box_id == box.id).select(db.comics.ALL, orderby=~db.comics.id)
    
    if (len(comics) == 0):
        box_image = IMG(_src=URL('static', 'images/default_box.png'),
                        _class='box-thumbnail')
    else:
        box_image = IMG(_src=URL('download', args=comics[0].image),
                        _class='box-thumbnail')
    
    return DIV(A(box_image,
                 _href=URL('box', vars=dict(id=box.id))),
               A(DIV(box.name,
                     _class='box-name'),
                 _href=URL('box', vars=dict(id=box.id))),
               DIV(owner.display_name,
                   _class='box-owner'),
               DIV(str(len(comics)) + ' comics',
                   _class='box-comic-count'),
               DIV(_class='clear-floats'),
               _class='box-preview')


def construct_comic_preview(comic):
    box_id = db(db.boxes.id == db.comics.box_id and
                db.comics.id == comic.id).select()[0].box_id
    user_id = db(db.auth_user.id == db.boxes.user_id and
                 db.boxes.id == box_id).select()[0].user_id
    owner = db(db.auth_user.id == user_id).select()[0]
    
    return DIV(A(IMG(_src=URL('download', args=comic.image),
                     _class='comic-thumbnail'),
                 _href=URL('comic', vars=dict(id=comic.id))),
               A(DIV(comic.title, _class='comic-title'),
                 _href=URL('comic', vars=dict(id=comic.id))),
               DIV('Issue No. ' + str(comic.issue_no),
                   _class='comic-issue-no'),
               DIV(owner.display_name,
                   _class='comic-owner'),
               DIV(_class='clear-floats'),
               _class='comic-preview')


def new_box_icon():
    return DIV(A(IMG(_src=URL('static', 'images/add_box.png'),
                     _class='box-thumbnail'),
                 _href=URL('new_box')),
               DIV(_class='clear-floats'),
               _class='box-preview')


def new_comic_icon():
    return DIV(A(IMG(_src=URL('static', 'images/add_comic.png'),
                     _class='comic-thumbnail'),
                 _href=URL('new_comic')),
               DIV(_class='clear-floats'),
               _class='comic-preview')
