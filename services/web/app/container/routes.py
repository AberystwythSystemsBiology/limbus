# Copyright (C) 2021  Keiron O'Shea <keo7@aber.ac.uk>
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

from ..container import container
from flask import render_template
from flask_login import current_user, login_required
from .forms import NewContainerForm, NewFixationType


@container.route("/")
@login_required
def index():
    return render_template("container/index.html")

@container.route("/new/container", methods=["GET", "POST"])
@login_required
def new_container():
    form = NewContainerForm()

    if form.validate_on_submit():
        pass

    return render_template("container/new/container.html", form=form)

@container.route("/new/fixation")
@login_required
def new_fixation_type():
    form = NewFixationType()

    return render_template("container/new/fixation.html", form=form)