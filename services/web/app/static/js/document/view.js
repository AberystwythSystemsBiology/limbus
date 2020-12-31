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

function deactivate_nav() {
    $("#document-info-nav").removeClass("active");
    $("#history-nav").removeClass("active");
}

function hide_all() {
    var tim = 50;
    $("#basic-info-div").fadeOut(50);
    $("#history-div").fadeOut(50);
}

$(document).ready(function() {
    $("#document-info-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info-div").fadeIn(100);

        console.log("Hello")
    });

    $("#history-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#history-div").fadeIn(100);
    });
});