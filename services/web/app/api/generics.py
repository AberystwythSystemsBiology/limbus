# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

def generic_new(db, model, new_schema, view_schema, values, tokenuser):
    if not values:
        return no_values_response()

    try:
        result = new_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    new = model(**building_result)
    new.author_id = tokenuser.id
    
    try:
        db.session.add(new)
        db.session.commit()
        db.session.flush()
        return success_with_content_response(view_schema.dump(new))
    except Exception as err:
        return transaction_error_response(err)


def generic_lock(db, model, id, view_schema, tokenuser):
    existing = Model.query.filter_by(id=id).first()

    if not existing:
        return not_found()

    existing.is_locked = not existing.is_locked
    existing.editor_id = tokenuser.id

    db.session.add(existing)
    db.session.commit()
    db.session.flush()

    return success_with_content_response(view_schema.dump(existing))

def generic_edit(db, model, id, new_schema, view_schema, values, token_user):

    if not values:
        return no_values_response()

    existing = model.query.filter_by(id=id).first()

    if not existing:
        return not_found()


    try:
        result = new_schema.load(values)
    except ValidationError as err:
        return validation_error_response(err)

    for attr, value in values.items():
        setattr(existing, attr, value)

    existing.editor_id = tokenuser.id

    try:
        db.session.add(existing)
        db.session.commit()
        db.session.flush()

        return success_with_content_response(view_schema.dump(existing))
    except Exception as err:
        return transaction_error_response(err)