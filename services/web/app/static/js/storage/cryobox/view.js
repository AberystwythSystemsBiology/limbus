
function something_there(html_id, sample) {
    var a = "<a href='"+ sample["url"]+ "'<div class='cryovial full'>LIMSMP-" + sample["id"] + "</div></a>";
    $(html_id).html(a);
}

$(document).ready(function() {

    $.getJSON($(location).attr('href') + '/data', function (data) {
        $.each(data, function(pos, sample) {
            var html_id =  "#_"+pos;
            something_there(html_id, sample);
        });
    });
});