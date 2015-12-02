# -*- coding: utf-8 -*-
# Y0072003

import operator


# Site routes
def index():
    # Get the five largest boxes
    comic_counts = []
    
    for box in get_visible_boxes(public_only=True):
        comic_counts.append((box, len(get_comics(box))))
    
    largest_boxes = sorted(comic_counts, key=operator.itemgetter(1), reverse=True)
    
    largest_boxes = [box[0] for box in largest_boxes]
    
    if len(largest_boxes) >= NUM_LARGEST_BOXES_TO_DISPLAY:
        largest_boxes = largest_boxes[:NUM_LARGEST_BOXES_TO_DISPLAY]
    
    largest_boxes_html = []
    for box in largest_boxes:
        largest_boxes_html.append(construct_box_preview(box))
    
    
    # Get the five newest boxes
    newest_boxes = get_visible_boxes(public_only=True, order=~db.boxes.creation_date|~db.boxes.id)
    
    if len(newest_boxes) >= NUM_NEWEST_BOXES_TO_DISPLAY:
        newest_boxes = newest_boxes[:NUM_NEWEST_BOXES_TO_DISPLAY]
    
    newest_boxes_html = []
    for box in newest_boxes:
        newest_boxes_html.append(construct_box_preview(box))
    
    
    response.title = DEFAULT_TITLE
    return dict(largest_boxes_html=largest_boxes_html, newest_boxes_html=newest_boxes_html)


def search():
    search = FORM(INPUT(_id='site-search', _name='search_term',
                        _placeholder='Search by Name, Artist, Writer or Publisher',
                        _class='form-control', requires=IS_NOT_EMPTY(error_message='Please enter a search term')),
                  INPUT(_name='search', _type='submit', _value='Search', _class='btn btn-default'),
                  _class='form-inline')
    
    results = []
    
    search_complete = False
    search_term_error = None
    if search.accepts(request, session):
        if search.vars.search_term != None:
            query_term = '%' + search.vars.search_term + '%'
            match_title = db(db.comics.title.like(query_term)).select()
            match_writer = db(db.comics.writers.like(query_term)).select()
            match_artist = db(db.comics.artists.like(query_term)).select()
            match_publisher = db(db.comics.publisher.like(query_term)).select()
            results = match_title | match_writer | match_artist | match_publisher
            
            public_results = []
            for result in results:
                visible, box = is_comic_visible(result)
                if visible:
                    public_results.append((result, box))
        
        search_complete = True
    elif search.errors:
        if search.errors.search_term:
            search_term_error = search.errors.search_term
            search.errors.clear()
    else:
        pass
    
    results_html = []
    if len(results) > 0:
        for comic, box in public_results:
            results_html.append(construct_comic_preview(comic, box))
    
    response.title = 'Search Comics'
    return dict(search=search, results_html=results_html, search_complete=search_complete, search_term_error=search_term_error)


def search_users():
    filter = FORM(INPUT(_id='user-filter', _name='filter_term', _placeholder='Filter users by name',
                        _class='form-control'),
                  INPUT(_name='apply_filter', _type='submit', _value='Apply Filter', _class='btn btn-default'),
                  _class='form-inline')
    
    results = db().select(db.auth_user.ALL)
    
    filter_complete = False
    if filter.accepts(request, session):
        if filter.vars.filter_term != None:
            filter_complete = True
            
            # As virtual fields (i.e. auth_user.display_name) run at the application level
            # rather than the database level, they cannot be used in database queries
            # Consequently this search must be done manually
            
            filtered_results = []
            for result in results:
                if filter.vars.filter_term in result.display_name:
                    filtered_results.append(result)
            
            results = filtered_results
    elif filter.errors:
        pass
    else:
        pass
    
    results_html = []
    if len(results) > 0:
        for user in results:
            results_html.append(construct_user_preview(user))
    
    response.title = 'Search Users'
    return dict(filter=filter, results_html=results_html, filter_complete=filter_complete)


def user():
    # Use custom handler for user/view_boxes
    if request.args(0) == 'view_boxes':
        response.view = 'main/view_boxes.html'
        
        auth_user_id = auth.user.id if auth.user else 1
        user_id = request.vars['id'] if request.vars['id'] != None else auth_user_id
        user = db(db.auth_user.id == user_id).select()[0]
        users_boxes = db(db.boxes.user_id == user_id).select(db.boxes.ALL, orderby=db.boxes.creation_date|~db.boxes.id)
        
        users_boxes_html = []
        for box in users_boxes:
            if is_box_visible(box):
                users_boxes_html.append(construct_box_preview(box))
        
        response.title = user.display_name + '\'s Boxes'
        return dict(users_boxes_html=users_boxes_html, user=user)
    # Use custom handler for user/view_comics
    elif request.args(0) == 'view_comics':
        response.view = 'main/view_comics.html'
        
        auth_user_id = auth.user.id if auth.user else 1
        user_id = request.vars['id'] if request.vars['id'] != None else auth_user_id
        user = db(db.auth_user.id == user_id).select()[0]
        users_boxes = db(db.boxes.user_id == user_id).select(db.boxes.ALL, orderby=db.boxes.creation_date|~db.boxes.id)
        
        users_boxes_html = []
        for box in users_boxes:
            if is_box_visible(box):
                box_comics_html = []
                
                for comic in get_comics(box):
                    box_comics_html.append(construct_comic_preview(comic, box))
                   
                users_boxes_html.append((box, box_comics_html))
        
        options = DIV(DIV(_class='col-sm-3 col-md-4'),
                      DIV(new_comic_icon(), _class='col-sm-6 col-md-4'),
                      DIV(_class='col-sm-3 col-md-4'),
                      _class='col-md-12')
        
        response.title = user.display_name + '\'s Comics'
        return dict(users_boxes_html=users_boxes_html, user=user, options=options)
    
    response.title = 'Sign In'
    return dict(login=auth())


@cache.action()
def download():
    return response.download(request, db)
