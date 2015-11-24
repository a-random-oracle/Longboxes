# -*- coding: utf-8 -*-


# Site routes
def index():
    redirect(URL('main', 'index'))
    return dict()


def box():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    comics = db(db.comics.boxes.contains(box.id)).select()
    owner = db(db.auth_user.id == box.user_id).select()[0]
    
    comics_html = []
    for comic in comics:
        comics_html.append(construct_comic_preview(comic, box))
    
    response.title = box.name
    return dict(box=box, owner=owner, comics_html=comics_html)


@auth.requires_login()
def create():
    new_box = FORM(DIV(INPUT(_name='box_name', _placeholder='Box name', _class='form-control'),
                       _class='form-group'),
                   DIV(LABEL(INPUT(_name='visibility', _type='checkbox'),
                             'Allow others to view this box'),
                       _class='checkbox'),
                   INPUT(_name='new_box', _type='submit', _value='Add Box', _class='btn btn-default'),
                   _role='form')
    
    if new_box.accepts(request, session):
        if new_box.vars.box_name != None:
            box_id = db.boxes.insert(user_id=auth.user.id,
                                     name=new_box.vars.box_name,
                                     visible=new_box.vars.visibility == 'on')
            
            redirect(URL('boxes', 'box', vars=dict(id=box_id)))
    elif new_box.errors:
        pass
    else:
        pass
    
    response.title = 'Box Creation'
    return dict(new_box=new_box)


@auth.requires_login()
def edit():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    
    edit_box = FORM(DIV(INPUT(_name='box_name', value=box.name, _class='form-control'),
                        _class='form-group'),
                    DIV(LABEL(INPUT(_name='visibility', _type='checkbox', value=box.visible),
                              'Allow others to view this box'),
                        _class='checkbox'),
                    INPUT(_name='edit_box', _type='submit', _value='Confirm', _class='btn btn-default'),
                    _role='form')
    
    if edit_box.accepts(request, session):
        if edit_box.vars.box_name != None:
            box.update_record(name=edit_box.vars.box_name,
                              visible=edit_box.vars.visibility == 'on')
            
            redirect(URL('boxes', 'box', vars=dict(id=box_id)))
    elif edit_box.errors:
        pass
    else:
        pass
    
    response.title = 'Box Editing'
    return dict(edit_box=edit_box, box_name=box.name)


@auth.requires_login()
def remove():
    box_id = request.vars['id'] if request.vars['id'] != None else 1
    box = db(db.boxes.id == box_id).select()[0]
    
    unfiled_box = db(db.boxes.user_id == auth.user.id
                     and db.boxes.name == DEFAULT_BOX).select()[0]
    unfiled_box_link = URL('boxes', 'box', vars=dict(id=unfiled_box.id))
    
    delete_box = FORM(INPUT(_name='delete_box', _type='submit', _value='Delete This Box',
                            _class='btn btn-danger btn-block'),
                      _role='form')
    
    cancel = FORM(INPUT(_name='cancel', _type='submit', _value='Cancel',
                        _class='btn btn-default btn-block'),
                  _role='form')
    
    if delete_box.process(formname='delete_box').accepted:
        if box.removable:
            box_contents = db(db.comics.boxes.contains(box.id)).select()
            
            # Move comics out to other boxes
            # If a comic is in another box already, just remove it from this box
            # If a comic is in no other boxes, move it to the unfiled box
            for comic in box_contents:
                if len(comic.boxes) == 1:
                    comic.update_record(boxes=[unfiled_box.id])
                else:  
                    comic.boxes.remove(long(box.id))
                    comic.update_record(boxes=comic.boxes)
            
            db(db.boxes.id == box.id).delete()
        else:
            pass
            
        redirect(URL('main', 'user', args=['view_boxes']))
    elif delete_box.errors:
        pass
    else:
        pass
    
    if cancel.process(formname='cancel').accepted:
        redirect(URL('boxes', 'box', vars=dict(id=box.id)))
    elif cancel.errors:
        pass
    else:
        pass
    
    response.title = 'Box Deletion'
    return dict(delete_box=delete_box, cancel=cancel, box_name=box.name, unfiled_box_link=unfiled_box_link)
