# -*- coding: utf-8 -*-


# Site routes
def index():
    redirect(URL('main', 'index'))
    return dict()


def comic():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    first_box = db(db.boxes.id == comic.boxes[0]).select()[0]
    owner = db(db.auth_user.id == first_box.user_id).select()[0]
    
    response.title = comic.title
    return dict(comic=comic, owner=owner, box_id=box_id)


@auth.requires_login()
def create():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
    
    form = FORM(DIV(INPUT(_id='first-field', _name='comic_title', _placeholder='Comic title', _class='form-control'),
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
        
        redirect(URL('comics', 'comic', vars=dict(id=comic_id, box_id=box_id)))
    elif form.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Creation'
    return dict(form=form)


@auth.requires_login()
def edit():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
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
    
    edit_comic = FORM(DIV(INPUT(_id='first-field', _name='comic_title', _value=comic.title, _class='form-control'),
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
                      DIV(TEXTAREA(_name='comic_description', value=comic.description, _class='form-control'),
                          _class='form-group'),
                      DIV(IMG(_id='comic-image-preview', _src='', _hidden=True),
                          INPUT(_id='comic-image-selector', _name='comic_image', _type='file', _class='upload',
                                requires=IS_EMPTY_OR(IS_IMAGE(extensions=('png', 'jpeg'), maxsize=(300, 400)))),
                          _class='form-group'),
                      INPUT(_name='Confirm', _type='submit', _value='Confirm', _class='btn btn-default'),
                      _role='form')
    
    if edit_comic.accepts(request, session):
        if edit_comic.vars.comic_image != None and edit_comic.vars.comic_image != '':
            new_image = edit_comic.vars.comic_image
        else:
            new_image = comic.image
        
        comic.update_record(title=edit_comic.vars.comic_title,
                            issue_no=edit_comic.vars.comic_issue_no,
                            writers=edit_comic.vars.comic_writers,
                            artists=edit_comic.vars.comic_artists,
                            publisher=edit_comic.vars.comic_publisher,
                            description=edit_comic.vars.comic_description,
                            image=new_image)
        
        redirect(URL('comics', 'comic', vars=dict(id=comic.id, box_id=box_id)))
    elif edit_comic.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Editing'
    return dict(edit_comic=edit_comic, comic_title=comic.title)


@auth.requires_login()
def remove():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    if len(comic.boxes) == 1:
        redirect(URL('comics', 'remove_entirely', vars=dict(id=comic.id, box_id=box_id)))
    
    remove_from_box = FORM(INPUT(_name='remove_from_box', _type='submit',
                                 _value='Remove Comic From This Box',
                                 _class='btn btn-default btn-block'),
                           _role='form')
    
    remove_entirely = FORM(INPUT(_name='remove_entirely', _type='submit',
                                 _value='Remove Comic Entirely',
                                 _class='btn btn-default btn-block'),
                           _role='form')
    
    if remove_from_box.process(formname='remove_from_box').accepted:
        comic.boxes.remove(long(box_id))
        comic.update_record(boxes=comic.boxes)
        
        redirect(URL('main', 'user', args=['view_boxes']))
    elif remove_from_box.errors:
        pass
    else:
        pass
    
    if remove_entirely.process(formname='remove_entirely').accepted:
        redirect(URL('comics', 'remove_entirely', vars=dict(id=comic.id, box_id=box_id)))
    elif remove_entirely.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Removal'
    return dict(remove_from_box=remove_from_box, remove_entirely=remove_entirely, comic_title=comic.title)


def remove_entirely():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    
    delete_comic = FORM(INPUT(_name='delete_comic', _type='submit', _value='Delete This Comic',
                              _class='btn btn-danger btn-block'),
                        _role='form')
    
    cancel = FORM(INPUT(_name='cancel', _type='submit', _value='Cancel',
                        _class='btn btn-default btn-block'),
                  _role='form')
    
    if delete_comic.process(formname='delete_comic').accepted:
        db(db.comics.id == comic_id).delete()
        
        redirect(URL('main', 'user', args=['view_boxes']))
    elif delete_comic.errors:
        pass
    else:
        pass
    
    if cancel.process(formname='cancel').accepted:
        redirect(URL('boxes', 'box', vars=dict(id=box_id)))
    elif cancel.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Deletion'
    return dict(delete_comic=delete_comic, cancel=cancel, comic_title=comic.title)


@auth.requires_login()
def copy():
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    first_box = db(db.boxes.id == comic.boxes[0]).select()[0]
    owner = db(db.auth_user.id == first_box.user_id).select()[0]
    users_boxes = db(db.boxes.user_id == auth.user.id).select()
    
    box_options = []
    for box in users_boxes:
        if box.id not in comic.boxes:
            box_options.append(OPTION(box.name, _value=box.id))
        
    copy_comic = FORM(DIV(LABEL('Select a box to copy the comic to:'),
                          SELECT(box_options, _id='first-field', _name='selected_box', _class='form-control'),
                          _class='form-group'),
                      INPUT(_name='copy_comic', _type='submit', _value='Copy Comic',
                            _class='btn btn-default'),
                      _role='form')
    
    if copy_comic.accepts(request, session):
        if auth.user.id == owner.id:
            # Copy the comic
            comic.boxes.append(copy_comic.vars.selected_box)
            comic.update_record(boxes=comic.boxes)
        else:
            # Clone the comic
            db.comics.insert(box_id=copy_comic.vars.selected_box,
                             title=comic.title,
                             issue_no=comic.issue_no,
                             writers=comic.writers,
                             artists=comic.artists,
                             publisher=comic.publisher,
                             description=comic.description,
                             image=comic.image)
        
        redirect(URL('boxes', 'box', vars=dict(id=copy_comic.vars.selected_box)))
    elif copy_comic.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Copying'
    return dict(copy_comic=copy_comic, comic_title=comic.title)


@auth.requires_login()
def move():
    box_id = request.vars['box_id'] if request.vars['box_id'] != None else 1
    comic_id = request.vars['id'] if request.vars['id'] != None else 1
    comic = db(db.comics.id == comic_id).select()[0]
    users_boxes = db(db.boxes.user_id == auth.user.id).select()
    
    box_options = []
    for box in users_boxes:
        if box.id not in comic.boxes:
            box_options.append(OPTION(box.name, _value=box.id))
        
    move_comic = FORM(DIV(LABEL('Select a box to move the comic to:'),
                          SELECT(box_options, _id='first-field', _name='selected_box', _class='form-control'),
                          _class='form-group'),
                      INPUT(_name='move_comic', _type='submit', _value='Move Comic', _class='btn btn-default'),
                      _role='form')
    
    if move_comic.accepts(request, session):
        comic.boxes.remove(long(box_id))
        comic.boxes.append(move_comic.vars.selected_box)
        comic.update_record(boxes=comic.boxes)
        
        redirect(URL('boxes', 'box', vars=dict(id=move_comic.vars.selected_box)))
    elif move_comic.errors:
        pass
    else:
        pass
    
    response.title = 'Comic Moving'
    return dict(move_comic=move_comic, comic_title=comic.title)
