# -*- coding: utf-8 -*-

import operator


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
    newest_boxes = db().select(db.boxes.ALL, orderby=db.boxes.creation_date|~db.boxes.id)
    
    if len(newest_boxes) >= NUM_NEWEST_BOXES_TO_DISPLAY:
        newest_boxes = newest_boxes[:NUM_NEWEST_BOXES_TO_DISPLAY]
    
    newest_boxes_html = []
    for box in newest_boxes:
        newest_boxes_html.append(construct_box_preview(box))
    
    
    response.title = DEFAULT_TITLE
    return dict(largest_boxes_html=largest_boxes_html, newest_boxes_html=newest_boxes_html)


def search():
    search = FORM(INPUT(_name='search_term', _placeholder='Search by Name, Artist, Writer or Publisher'),
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
    user_id = db(db.auth_user.id == db.boxes.user_id
                 and db.boxes.id == box_id).select()[0].user_id
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
    if auth.is_logged_in() and request.args(0) == 'profile':
        response.view = 'default/profile.html'
        
        users_boxes = db(db.boxes.user_id == auth.user.id).select(db.boxes.ALL,
                                                                  orderby=db.boxes.creation_date|~db.boxes.id)
        
        users_boxes_html = []
        for box in users_boxes:
            users_boxes_html.append(construct_box_preview(box))
        
        return dict(users_boxes_html=users_boxes_html)
    
    
    login_form = auth()
    
    return dict(login_form=login_form)


@auth.requires_login()
def new_box():
    form = FORM(DIV(INPUT(_name='box_name', _placeholder='Box name', _class='form-control'),
                    _class='form-group'),
                DIV(LABEL(INPUT(_name='visibility', _type='checkbox'),
                          'Allow others to view this box'),
                    _class='checkbox'),
                INPUT(_name='Add Box', _type='submit', _value='Add Box', _class='btn btn-default'),
                _role='form')
    
    if form.accepts(request, session):
        if form.vars.box_name != None:
            new_box_name = form.vars.box_name
            is_public = form.vars.visibility == 'on'
            db.boxes.insert(user_id=auth.user.id, name=new_box_name, visible=is_public)
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form)


@auth.requires_login()
def edit_box():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    
    form = FORM(DIV(INPUT(_name='box_name', _placeholder=box.name, _class='form-control'),
                    _class='form-group'),
                DIV(LABEL(INPUT(_name='visibility', _type='checkbox', value=box.visible),
                          'Allow others to view this box'),
                    _class='checkbox'),
                INPUT(_name='Confirm', _type='submit', _value='Confirm', _class='btn btn-default'),
                _role='form')
    
    if form.accepts(request, session):
        if form.vars.box_name != None:
            new_box_name = form.vars.box_name
            is_public = form.vars.visibility == 'on'
            box.update_record(name=new_box_name, visible=is_public)
            
            redirect(URL('user', args=['profile']))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, box_name=box.name)


@auth.requires_login()
def remove_box():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    unfiled_box = db(db.boxes.user_id == auth.user.id
                     and db.boxes.name == DEFAULT_BOX).select()[0]
    unfiled_box_link = URL('boxes', vars=dict(id=unfiled_box.id))
    
    form = FORM.confirm('Delete This Box', dict(Cancel=URL(user, args=['profile'])))
    form.element('input', _type='submit')['_class'] = 'btn btn-danger'
    
    if form.accepted:
        box_contents = db(db.comics.box_id == box_id).select()
        
        for comic in box_contents:
            comic.update_record(box_id=unfiled_box.id)
        
        db(db.boxes.id == box_id).delete()
        
        redirect(URL('user', args=['profile']))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, box_name=box.name, unfiled_box_link=unfiled_box_link)


@cache.action()
def download():
    return response.download(request, db)
