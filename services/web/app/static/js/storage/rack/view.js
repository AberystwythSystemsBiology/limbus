function get_rack_information() {
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


function render_subtitle(rack_information) {
    $("#createdOn").html(rack_information["created_on"]);
    $("#createdBy").html(rack_information["author"]["first_name"] + " " + rack_information["author"]["last_name"] );

}

$(document).ready(function() {
    var rack_information = get_rack_information();
    render_subtitle(rack_information);
});