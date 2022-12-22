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

function get_protocols() {
    var api_url = encodeURI(window.location + 'data');

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
         return json["content"];
    })();

    return json;
}

function fill_protocol_table(protocol) {


    $('#protocol-table').DataTable( {
        data: protocol,
       
        columns: [
            {
                mData: {},
                mRender: function (data, type, row) {
                    var href = window.location.href + "LIMBPRO-" + data["id"];
                    var attr_html = "";
                    attr_html +=  "<a href='" + href + "'>";
                    attr_html += '<i class="fab fa-buffer"></i>';
                    attr_html += 'LIMBPRO-' + data["id"];
                    attr_html += ': ' + data["name"];
                    attr_html += '</a>';
                    return attr_html;
                }
            },
            {

                mData: {},
                mRender: function (data, type, row) {
                    if (data["is_locked"]) {
                        return "<i class='fa fa-lock fa-1x'></i>"
                    }
                    else {
                        return "✅";
                    }

                }
            },
            { data: "type" },

              {// created_by
                mData: {},
                mRender: function (data, type, row) {
                    var author = "";
                    if (data["author"]!=null && data["author"]!=undefined) {
                        author = [data["author"]["first_name"], data["author"]["last_name"]].join(" ");
                    }
                    return author;
                }
            },
            { data: "created_on"},
            

            

           
        ]
    });



}

$(document).ready(function() {
    var protocol = get_protocols();
  
    fill_protocol_table(protocol);
   // fill_attributes_table(attributes);
   
});