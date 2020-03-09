function nothing_there(html_id) {
    $(html_id).css("background-color", "red");
}

function something_there(html_id) {
    $(html_id).html("Hello World");
}

$(document).ready(function() {

    $.getJSON($(location).attr('href') + '/data', function (data) {
        $.each(data, function(pos, sample) {
            var html_id =  "#_"+pos;
            something_there(html_id);
        });
    });
});