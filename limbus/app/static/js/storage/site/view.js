

$(document).ready(function () {
    var valid;

    scheduled = $.ajax({
        type: "get",
        url: $(location).attr('href') + '/get',
        async: false,
        success: function (response) {
            valid = response;
        }
    });

});
