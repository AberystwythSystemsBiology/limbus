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

function get_panel_info() {
    var api_url = encodeURI(window.location+'/data');

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



function fill_document_statistics(document_statistics) {
    make_bar("document-type", document_statistics["document_type"]["data"], document_statistics["document_type"]["labels"], "");
}

function fill_attribute_statistics(attribute_statistics) {
    make_bar("attribute-type", attribute_statistics["attribute_type"]["data"], attribute_statistics["attribute_type"]["labels"], "");

}

function fill_sample_statistics(sample_statistics) {
    make_doughnut("sample-status", sample_statistics["sample_status"]["data"], sample_statistics["sample_status"]["labels"], "");
    make_bar("sample-source", sample_statistics["sample_source"]["data"], sample_statistics["sample_source"]["labels"], "");
    make_pie("sample-biohazard", sample_statistics["sample_biohazard"]["data"], sample_statistics["sample_biohazard"]["labels"], "");
    make_doughnut("sample-type", sample_statistics["sample_type"]["data"], sample_statistics["sample_type"]["labels"], "");


}

function fill_protocol_statistics(protocol_statistics) {
    make_pie("protocol-type", protocol_statistics["protocol_type"]["data"], protocol_statistics["protocol_type"]["labels"], "");

}

function fill_donor_statistics(donor_statistics) {
    make_doughnut("donor-status", donor_statistics["donor_status"]["data"], donor_statistics["donor_status"]["labels"], "Donor Status");
    make_pie("donor-sex", donor_statistics["donor_sex"]["data"], donor_statistics["donor_sex"]["labels"], "Donor Sex");
    make_bar("donor-race", donor_statistics["donor_race"]["data"], donor_statistics["donor_race"]["labels"], "Donor Race");

}

function fill_basic_statistics(basic_statistics) {
    $("#donor-count").html(basic_statistics["donor_count"]);
    $("#sample-count").html(basic_statistics["sample_count"]);
    $("#user-count").html(basic_statistics["user_count"]);
    $("#site-count").html(basic_statistics["site_count"]);
}

function fill_panel() {
    var panel_info = get_panel_info();
    $("#biobank-name").html(panel_info["name"]);
    fill_basic_statistics(panel_info["basic_statistics"]);
    fill_sample_statistics(panel_info["sample_statistics"]);
    fill_donor_statistics(panel_info["donor_statistics"]);
    fill_document_statistics(panel_info["document_statistics"]);
    fill_attribute_statistics(panel_info["attribute_statistics"]);
    fill_protocol_statistics(panel_info["protocol_statistics"]);

}

$(document).ready(function() {
    $("body").css({"backgroundColor":"#eeeeee"});
    fill_panel();
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});