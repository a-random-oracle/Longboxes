# -*- coding: utf-8 -*-


# Site routes
#def index():
#    redirect(URL('main', 'index'))
#    return dict()

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


@auth.requires_login()
def create():
    form = FORM(DIV(INPUT(_name='box_name', _placeholder='Box name', _class='form-control'),
                    _class='form-group'),
                DIV(LABEL(INPUT(_name='visibility', _type='checkbox'),
                          'Allow others to view this box'),
                    _class='checkbox'),
                INPUT(_name='Add Box', _type='submit', _value='Add Box', _class='btn btn-default'),
                _role='form')
    
    if form.accepts(request, session):
        if form.vars.box_name != None:
            box_id = db.boxes.insert(user_id=auth.user.id,
                                     name=form.vars.box_name,
                                     visible=form.vars.visibility == 'on')
            
            redirect(URL('boxes', 'box', vars=dict(id=box_id)))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form)


@auth.requires_login()
def edit():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    
    form = FORM(DIV(INPUT(_name='box_name', value=box.name, _class='form-control'),
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
            
            redirect(URL('boxes', 'box', vars=dict(id=box_id)))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, box_name=box.name)


@auth.requires_login()
def remove():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    unfiled_box = db(db.boxes.user_id == auth.user.id
                     and db.boxes.name == DEFAULT_BOX).select()[0]
    unfiled_box_link = URL('boxes', 'box', vars=dict(id=unfiled_box.id))
    
    form = FORM.confirm('Delete This Box', dict(Cancel=URL('main', 'user', args=['view_boxes'])))
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
            
        redirect(URL('main', 'user', args=['view_boxes']))
    elif form.errors:
        pass
    else:
        pass
    
    return dict(form=form, box_name=box.name, unfiled_box_link=unfiled_box_link)
