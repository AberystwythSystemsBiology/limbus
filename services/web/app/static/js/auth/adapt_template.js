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

function adapt_templates(user_roles) {
    // --  Checking user roles for adaptive menu display
    //var user_roles = '{{ current_user.roles }}';
    var user_roles = user_roles.split(",");
    if (typeof user_roles === "string") {
        user_roles = [user_roles];
    }
    //console.log("user roles: ",  user_roles);
    const links = $('a,  button, div').filter('[data-role]');
    links.get().forEach( link => {
        if (!user_roles.includes("admin")) {
            if (!user_roles.includes(link.dataset.role)) {
                link.style.display = 'none';
        }}
    });
}

$(document).ready(function(){
    var user_roles = $('#user_roles').text();
    adapt_templates(user_roles);
});