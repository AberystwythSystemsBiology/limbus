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

from app import db


class SampleToCustomAttributeTextValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_text_values"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String)
    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SampleToCustomAttributeNumericValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_numeric_values"

    id = db.Column(db.Integer, primary_key=True)

    value = db.Column(db.String)
    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))

    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    update_date = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        server_onupdate=db.func.now(),
        nullable=False,
    )


class SampleToCustomAttributeOptionValue(db.Model):
    __tablename__ = "sample_to_custom_attribute_option_values"
    id = db.Column(db.Integer, primary_key=True)

    custom_option_id = db.Column(
        db.Integer, db.ForeignKey("custom_attribute_options.id")
    )

    custom_attribute_id = db.Column(db.Integer, db.ForeignKey("custom_attributes.id"))
    sample_id = db.Column(db.Integer, db.ForeignKey("samples.id"))

    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    creation_date = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
