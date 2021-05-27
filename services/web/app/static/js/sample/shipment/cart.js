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

function get_cart() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    var api_url = split_url.join("/") + "/data"
    
    console.log(api_url)

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

function fill_cart_table(cart) {
    $('#cart-table').DataTable( {
        data: cart,
        dom: 'Bfrtip',
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["sample"]["colour"])
                    col_data += "<a href='"+data["sample"]["_links"]["self"]+ "'>";
                    col_data += '<i class="fas fa-vial"></i> '
                    col_data += data["sample"]["uuid"];
                    col_data += "</a>";
                    if (data["sample"]["source"] != "New") {

                    col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                    col_data += '<a href="'+data["sample"]["parent"]["_links"]["self"]+'" target="_blank">'
                    col_data += '<i class="fas fa-vial"></i> ';
                    col_data += data["sample"]["parent"]["uuid"],
                    col_data += "</a></small>";
                }

                    return col_data
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                   return data["sample"]["base_type"]


                }
            },            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample"]["sample_type_information"];


                    if (data["sample"]["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    }
                    else if (data["sample"]["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    }


                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var percentage = data["sample"]["remaining_quantity"] / data["sample"]["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="'+percentage+' Available">';
                    col_data += data["sample"]["remaining_quantity"]+"/"+data["sample"]["quantity"]+get_metric(data["sample"]["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
        },
        {
            "mData": {},
            "mRender": function(data, type, row) {
                return data["sample"]["status"]

            },
        },
      {
        "mData": {},
        "mRender": function (data, type, row) {
            return data["created_on"]

        
        }
    },
    {
        "mData": {},
        "mRender": function (data, type, row) {
            return "Sadge"
        }
    }
    



        ],

    });
}

$(document).ready(function() {
    var cart = get_cart();
    fill_cart_table(cart);
});