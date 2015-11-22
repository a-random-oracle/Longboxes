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
    DIV(INPUT(_name='box_name', _placeholder='Box name', _class='form-control'),
                    _class='form-group'),
    
    search = FORM(INPUT(_id='site-search', _name='search_term', _placeholder='Search by Name, Artist, Writer or Publisher', _class='form-control'),
                  INPUT(_name='Search', _type='submit', _value='Search', _class='btn btn-default'),
                  _class='form-inline')
    
    results = []
    
    if search.accepts(request, session):
        if search.vars.search_term != None:
            query_term = '%' + search.vars.search_term + '%'
            match_title = db(db.comics.title.like(query_term)).select()
            match_writer = db(db.comics.writers.like(query_term)).select()
            match_artist = db(db.comics.artists.like(query_term)).select()
            match_publisher = db(db.comics.publisher.like(query_term)).select()
            results = match_title | match_writer | match_artist | match_publisher
    elif search.errors:
        pass
    else:
        pass
    
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
    box = db(db.boxes.id == comic.box_id).select()[0]
    user_id = db(db.auth_user.id == db.boxes.user_id
                 and db.boxes.id == comic.box_id).select()[0].user_id
    owner = db(db.auth_user.id == user_id).select()[0]
    
    response.title = comic.title
    return dict(comic=comic, owner=owner)


def user():
    # Use custom handler for user/profile
    if request.args(0) == 'profile':
        user_id = request.vars['id'] if request.vars['id'] != None else 1
        user = db(db.auth_user.id == user_id).select()[0]
        
        response.view = 'default/profile.html'
        
        users_boxes = db(db.boxes.user_id == user_id).select(db.boxes.ALL, orderby=db.boxes.creation_date|~db.boxes.id)
        
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
            
            redirect(URL('box', vars=dict(id=box_id)))
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
        if box.removable:
            box_contents = db(db.comics.box_id == box_id).select()
            
            for comic in box_contents:
                comic.update_record(box_id=unfiled_box.id)
            
            db(db.boxes.id == box_id).delete()
        else:
            #TODO
            pass
            
        redirect(URL('user', args=['profile']))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, box_name=box.name, unfiled_box_link=unfiled_box_link)


@auth.requires_login()
def new_comic():
    box_id = request.vars['box'] if request.vars['box'] != None else 1
    
    form = FORM(DIV(INPUT(_name='comic_title', _placeholder='Comic title', _class='form-control'),
                    _class='form-group'),
                DIV(INPUT(_name='comic_issue_no', _placeholder='Issue no.', _class='form-control'),
                    _class='form-group'),
                DIV(UL(LI(INPUT(_name='comic_writers', _placeholder='Writers', _class='form-control')),
                       _class='w2p_list',
                       _style='list-style: none'),
                    _class='w2p_fw'),
                DIV(UL(LI(INPUT(_name='comic_artists', _placeholder='Artists', _class='form-control')),
                       _class='w2p_list',
                       _style='list-style: none'),
                    _class='w2p_fw'),
                DIV(INPUT(_name='comic_publisher', _placeholder='Publisher', _class='form-control'),
                    _class='form-group'),
                DIV(TEXTAREA(_name='comic_description', _placeholder='Description', _class='form-control'),
                    _class='form-group'),
                DIV(IMG(_id='comic-image-preview', _src='', _hidden=True),
                    INPUT(_id='comic-image-selector', _name='comic_image', _type='file', _class='upload',
                          requires=IS_IMAGE(extensions=('png', 'jpg'), maxsize=(300, 400))),
                    _class='form-group'),
                INPUT(_name='Add Comic', _type='submit', _value='Add Comic', _class='btn btn-default'),
                _role='form')
    
    if form.accepts(request, session):
        comic_id = db.comics.insert(box_id=box_id,
                                    title=form.vars.comic_title,
                                    issue_no=form.vars.comic_issue_no,
                                    writers=form.vars.comic_writers,
                                    artists=form.vars.comic_artists,
                                    publisher=form.vars.comic_publisher,
                                    description=form.vars.comic_description,
                                    image=form.vars.comic_image)
        
        redirect(URL('comic', vars=dict(id=comic_id)))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form)


@auth.requires_login()
def edit_comic():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    writers = []
    if len(comic.writers) == 0:
        writers += LI(INPUT(_name='comic_artists', _placeholder='Writers', _class='form-control'))
    else:
        for writer in comic.writers:
            writers += LI(INPUT(_name='comic_writers', _value=writer, _class='form-control'))
    
    artists = []
    if len(comic.artists) == 0:
        artists += LI(INPUT(_name='comic_artists', _placeholder='Artists', _class='form-control'))
    else:
        for artist in comic.artists:
            artists += LI(INPUT(_name='comic_artists', _value=artist, _class='form-control'))
    
    form = FORM(DIV(INPUT(_name='comic_title', _value=comic.title, _class='form-control'),
                    _class='form-group'),
                DIV(INPUT(_name='comic_issue_no', _value=comic.issue_no, _class='form-control'),
                    _class='form-group'),
                DIV(UL(writers,
                       _class='w2p_list',
                       _style='list-style: none'),
                    _class='w2p_fw'),
                DIV(UL(artists,
                       _class='w2p_list',
                       _style='list-style: none'),
                    _class='w2p_fw'),
                DIV(INPUT(_name='comic_publisher', _value=comic.publisher, _class='form-control'),
                    _class='form-group'),
                DIV(TEXTAREA(_name='comic_description', _value=comic.description, _class='form-control'),
                    _class='form-group'),
                DIV(INPUT(_name='Edit Image', _value='Edit Image', _class='btn btn-default',
                          _onclick='location.href="' + URL('#') + '"'),
                    _class='form-group'),
                INPUT(_name='Confirm', _type='submit', _value='Confirm', _class='btn btn-default'),
                _role='form')
    
    if form.accepts(request, session):
        comic.update_record(title=form.vars.comic_title,
                            issue_no=form.vars.comic_issue_no,
                            writers=form.vars.comic_writers,
                            artists=form.vars.comic_artists,
                            publisher=form.vars.comic_publisher,
                            description=form.vars.comic_description)
        
        redirect(URL('comic', vars=dict(id=comic.id)))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, comic_title=comic.title)


@auth.requires_login()
def remove_comic():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    form = FORM.confirm('Delete This Comic', dict(Cancel=URL(user, args=['profile'])))
    form.element('input', _type='submit')['_class'] = 'btn btn-danger'
    
    if form.accepted:
        db(db.comics.id == comic_id).delete()
            
        redirect(URL('box', vars=dict(id=comic.box_id)))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, comic_title=comic.title)


@cache.action()
def download():
    return response.download(request, db)
