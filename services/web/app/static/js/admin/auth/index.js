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

function get_users() {
    var api_url = encodeURI(window.location + '/data');

    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'dataType': "json",
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();

    return json["content"];
}

function fill_accounts_table(accounts) {
    $('#accounts-table').DataTable({
        data: accounts,
        pageLength: 5,
        columns: [
            { 
                mData: {},
                mRender: function (data, type, row) {

                    var href = window.location.href + data["id"];

                    var email_html = "<a href='" + href + "'>"
                    email_html += "<i class='fa fa-user'></i> "
                    email_html += data["email"]
                    email_html += "</a>"
                    return email_html
                }
            },
            { data: "account_type" },
            {  
                mData: {},
                mRender: function (data, type, row) {
                    if (data["is_locked"]) {
                        return "✅"
                    }
                    else {
                        return "❌"
                    }
                
            }
        },
            { data: "created_on"},
        ],  


    });
}


$(document).ready(function () {
    fill_accounts_table(get_users());
});