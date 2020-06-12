
function something_there(html_id, sample) {
    var a = "<a href='"+ sample["url"]+ "'<div class='tube full'><img src='"+sample["barcode"]+"'></div></a>";
    
    
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