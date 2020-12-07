function get_panel_information() {
    var api_url = encodeURI(window.location+'/endpoint');
    
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


function render_counts(basic_statistics) {
    $("#site_count").html(basic_statistics["site_count"]);
    $("#room_count").html(basic_statistics["site_count"]);
    $("#building_count").html(basic_statistics["building_count"]);
    $("#cold_storage_count").html(basic_statistics["cold_storage_count"]);


}

function render_cold_storage_statistics(cold_storage_statistics) {
    make_pie("cold_storage_type", cold_storage_statistics["cold_storage_type"]["data"], cold_storage_statistics["cold_storage_type"]["labels"])
    make_pie("cold_storage_temp", cold_storage_statistics["cold_storage_temp"]["data"], cold_storage_statistics["cold_storage_temp"]["labels"])


}

$(document).ready(function() {
    $("body").css({"backgroundColor":"#eeeeee"});

    var panel_information = get_panel_information();
    render_counts(panel_information["basic_statistics"]);
    render_cold_storage_statistics(panel_information["cold_storage_statistics"]);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();
});