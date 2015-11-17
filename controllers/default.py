# -*- coding: utf-8 -*-

import operator


# Helper methods
def construct_box_preview(box):
    user_id = db(db.auth_user.id == db.boxes.user_id and
                 db.boxes.id == box.id).select()[0].user_id
    owner = db(db.auth_user.id == user_id).select()[0]
    comics = db(db.comics.box_id == box.id).select(db.comics.ALL, orderby=~db.comics.id)
    
    if (len(comics) == 0):
        box_image = IMG(_src=URL('static', 'images/default_comic.png'),
                        _class='box-thumbnail')
    else:
        box_image = IMG(_src=URL('download', args=comics[0].image),
                        _class='box-thumbnail')
    
    return DIV(A(box_image,
                 _href=URL('box', vars=dict(id=box.id))),
               A(DIV(box.name,
                     _class='box-name'),
                 _href=URL('box', vars=dict(id=box.id))),
               DIV(display_name(owner),
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
               DIV(display_name(owner),
                   _class='comic-owner'),
               DIV(_class='clear-floats'),
               _class='comic-preview')


def display_name(user):
    return str(user.first_name + ' ' + user.last_name)









# Site routes

def index():
    # Get the five largest boxes
    comic_counts = []
    
    for box in db().select(db.boxes.ALL):
        comic_counts.append((box, db(db.comics.box_id == box.id).count()))
    
    largest_boxes = sorted(comic_counts, key=operator.itemgetter(1), reverse=True)
    
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
    
    
    response.title = DEFAULT_TITLE
    return dict(largest_boxes_html=largest_boxes_html, newest_boxes_html=newest_boxes_html)


def search():
    search = FORM(INPUT(_name='search_term', _placeholder="Search by Name, Artist, Writer or Publisher"),
                  INPUT(_name='Search', _type='submit', _value='Search'))
    
    results = []
    
    if search.vars != None and search.vars.search_term != None:
        query_term = '%' + search.vars.search_term + '%'
        match_title = db(db.comics.title.like(query_term)).select()
        match_writer = db(db.comics.writers.like(query_term)).select()
        match_artist = db(db.comics.artists.like(query_term)).select()
        match_publisher = db(db.comics.publisher.like(query_term)).select()
        results = match_title | match_writer | match_artist | match_publisher
    
    results_html = []
    if len(results) > 0:
        for comic in results:
            results_html.append(construct_comic_preview(comic))
    
    return dict(search=search, results_html=results_html)


def box():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    user_id = db(db.auth_user.id == db.boxes.user_id and
                 db.boxes.id == box_id).select()[0].user_id
    owner = db(db.auth_user.id == user_id).select()[0]
    comics = db(db.comics.box_id == box.id).select()
    
    comics_html = []
    for comic in comics:
        comics_html.append(construct_comic_preview(comic))
    
    response.title = box.name
    return dict(box=box, owner=owner, comics_html=comics_html)


def comic():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    response.title = comic.title
    return dict(comic=comic)


def user():
    # Use custom handler for user/profile
    if request.args(0) == 'profile':
        response.view = 'default/profile.html'
        
        users_boxes = db(db.boxes.user_id == auth.user.id).select(db.boxes.ALL, orderby=db.boxes.creation_date)
        
        users_boxes_html = []
        for box in users_boxes:
            users_boxes_html.append(construct_box_preview(box))
        
        return dict(users_boxes_html=users_boxes_html)
    
    
    login_form = auth()
    
    return dict(login_form=login_form)


@cache.action()
def download():
    return response.download(request, db)
