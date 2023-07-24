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

function get_consentforms() {
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

function fill_consetnform_table(consentforms) {

    $('#consent-table').DataTable({
        data: consentforms,
        pageLength: 25,
        columns: [
            {
                mData: {},
                mRender: function (data, type, row) {
                    var href = window.location.href + "LIMBPCF-" + data["id"];
                    var consent_html = "";
                    consent_html +=  "<a href='" + href + "'>";
                    consent_html += '<i class="fab fa-buffer"></i>';
                    consent_html += 'LIMBPCF-' + data["id"];
                    consent_html += data["name"];
                    consent_html += '</a>';
                    return consent_html;
                }
            },

            { data: "version"},

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
        ],


    });
}


$(document).ready(function() {
    var consentforms = get_consentforms();
    fill_consetnform_table(consentforms);


});