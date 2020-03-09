$(document).ready(function() {

    var jgasp = $.getJSON($(location).attr('href') + '/data', function (data) {
        $.each(data, function(row, cols) {
            $.each(cols, function(col) {
                var sample = data[row][col];
                if (sample == null) {
                    $("#" + row + ";" + col).html("H");
                }
            });
        });
    });
});