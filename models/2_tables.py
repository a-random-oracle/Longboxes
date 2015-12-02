# -*- coding: utf-8 -*-
# Y0072003

# Define database tables

## auth_user
get_display_name = lambda user: user.first_name + ' ' + user.last_name
get_display_name_func = lambda row: get_display_name(row.auth_user)
db.auth_user.display_name = Field.Virtual('display_name', get_display_name_func)

## Boxes
db.define_table('boxes',
    Field('user_id', type='reference auth_user'),
    Field('name', type='string'),
    Field('creation_date', type='date', default=request.now),
    Field('visible', type='boolean'),
    Field('removable', type='boolean', default=True)
)
 
## Comics
db.define_table('comics',
    Field('title', type='string'),
    Field('issue_no', type='integer'),
    Field('writers', type='list:string'),
    Field('artists', type='list:string'),
    Field('publisher', type='string'),
    Field('description', type='string'),
    Field('image', type='upload')
)

## Comic-Box Map
db.define_table('comic_box_map',
    Field('comic_id', type='reference comics'),
    Field('box_id', type='reference boxes'),
)
