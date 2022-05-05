/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

function add_warning(question) {
    $(question).addClass("list-group-item-warning")
    $(question).find(".question-warning").css("visibility", 'visible');
    var modal_question = $(`#${$(question).attr('id')}-m`)
    var fa = $(`#${$(question).attr('id')}-m`).find(".fa")

    fa.removeClass("fa-check-circle")
    fa.removeClass("text-success")
    fa.addClass("fa-exclamation-circle")
    fa.addClass("text-white")

    $(modal_question).addClass("bg-danger")
    $(modal_question).addClass("text-white")
}

function remove_warning(question) {
    $(question).removeClass("list-group-item-warning")
    $(question).find(".question-warning").css("visibility", 'hidden');
    var modal_question = $(`#${$(question).attr('id')}-m`)
    var fa = $(`#${$(question).attr('id')}-m`).find(".fa")

    fa.removeClass("fa-exclamation-circle")
    fa.removeClass("text-white")
    fa.addClass("fa-check-circle")
    fa.addClass("text-success")

    $(modal_question).removeClass("bg-danger")
    $(modal_question).removeClass("text-white")
}

function style_item(item) {
    var question = $(item).parents(".list-group-item")
    if (item.checked) {
        remove_warning(question)
    } else {
        add_warning(question)
    }
}

$(document).ready(function() {
    $("#questionnaire-list").find(".form-check-input")
                            .change(function(e) {
        style_item(this);
    });

    $("#questionnaire-list").find(".form-check-input")
                            .each( (i, item) => {style_item(item)});
});
