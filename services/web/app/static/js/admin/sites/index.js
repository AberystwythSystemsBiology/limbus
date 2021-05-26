/*
Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>

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


function get_sites() {
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


function fill_sites_table(sites) {
    $('#sites-table').DataTable({
        data: sites,
        pageLength: 5,
        columns: [
            { 
                mData: {},
                mRender: function (data, type, row) {
                    console.log();
                    var site = "<a href='" + data["_links"]["view_site"] + "'>"
                    site += "<i class='fa fa-home'></i> "
                    site += "LIMBSIT-" + data["id"] + ": ";
                    site += data["name"]
                    site += "</a>"
                    return site
                }
            },
            {
                mData: {},
                mRender: function (data, type, row) {
                    var address = data["address"]["street_address_one"] + ", ";
                    address += data["address"]["city"] + ", ";
                    address += data["address"]["county"] + ", ";
                    address += data["address"]["post_code"]
                    return address
                }
            },            
            { data: "created_on"},
        ],  


    });

}


$(document).ready(function () {
    fill_sites_table(get_sites());
});