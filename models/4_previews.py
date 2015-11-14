# -*- coding: utf-8 -*-

def construct_box_preview(box):
    user_id = db(db.users.id == db.boxes.user_id and
                 db.boxes.id == box.id).select()[0].user_id
    owner = db(db.users.id == user_id).select()[0]
    comic_count = db(db.comics.box_id == box.id).count()
    
    return DIV(A(DIV(box.name), _href=URL('box', vars=dict(id=box.id))),
               DIV(owner.display_name),
               DIV(str(comic_count) + ' comics'),
               DIV(_style='clear: both'),
               _class='box-preview',
               _style='float: left')


def construct_comic_preview(comic):
    box_id = db(db.boxes.id == db.comics.box_id and
                db.comics.id == comic.id).select()[0].box_id
    user_id = db(db.users.id == db.boxes.user_id and
                 db.boxes.id == box_id).select()[0].user_id
    owner = db(db.users.id == user_id).select()[0]
    
    return DIV(A(IMG(_src=URL('download', args=comic.image), _class='comic-thumbnail'), _href=URL('comic', vars=dict(id=comic.id))),
               A(DIV(comic.title, _class='comic-title'), _href=URL('comic', vars=dict(id=comic.id))),
               DIV('Issue No. ' + str(comic.issue_no), _class='comic-issue-no'),
               DIV(owner.display_name, _class='comic-owner'),
               DIV(_style='clear: both'),
               _class='comic-preview')