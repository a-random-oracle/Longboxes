# -*- coding: utf-8 -*-

import operator


def index():
    # Get the five largest boxes
    comic_counts = []
    
    for box in db().select(db.boxes.ALL):
        comic_counts.append((box, box.id, db(db.comics.box_id == box.id).count()))
    
    # Double sort is necessary here as otherwise when two boxes have the same number
    # of comics their order is not well defined (and can switch on page reloads)
    largest_boxes = sorted(comic_counts, key=operator.itemgetter(2), reverse=True)
    largest_boxes = sorted(largest_boxes, key=operator.itemgetter(1))
    
    largest_boxes = [box[0] for box in largest_boxes]
    
    if len(largest_boxes) >= NUM_LARGEST_BOXES_TO_DISPLAY:
        largest_boxes = largest_boxes[:NUM_LARGEST_BOXES_TO_DISPLAY]
    
    largest_boxes_html = []
    for box in largest_boxes:
        largest_boxes_html.append(construct_box_preview(box))
    
    
    # Get the five newest boxes
    newest_boxes = db().select(db.boxes.ALL, orderby=db.boxes.creation_date|db.boxes.id)
    
    if len(newest_boxes) >= NUM_NEWEST_BOXES_TO_DISPLAY:
        newest_boxes = newest_boxes[:NUM_NEWEST_BOXES_TO_DISPLAY]
    
    newest_boxes_html = []
    for box in newest_boxes:
        newest_boxes_html.append(construct_box_preview(box))
    
    
    response.title = ""
    return dict(largest_boxes_html=largest_boxes_html, newest_boxes_html=newest_boxes_html)


def box():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    user_id = db(db.users.id == db.boxes.user_id and
                 db.boxes.id == box_id).select()[0].user_id
    owner = db(db.users.id == user_id).select()[0]
    comics = db(db.comics.box_id == box.id)
    
    response.title = box.name
    return dict(box=box, owner=owner, comics=comics)


def comic():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    response.title = comic.title
    return dict(comic=comic)


def comic_preview():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    comic_html = construct_comic_preview(comic)

    response.title = comic.title
    return dict(comic_html=comic_html)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    return response.download(request, db)
