function get_donor() {
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


function deactivate_nav() {
    $("#diagnosis-nav").removeClass("active");
    $("#basic-info-nav").removeClass("active");
    $("#samples-nav").removeClass("active");
}

function hide_all() {
    $("#basic-info-div").fadeOut(50);
    $("#diagnosis-div").fadeOut(50);
    $("#samples-div").fadeOut(50);
    
}

function fill_basic_information(donor_information) {
    console.log(donor_information)
}


$(document).ready(function () {

    var donor_information = get_donor();

    $("#edit-donor-btn").on("click", function() {
        window.location.href = donor_information["_links"]["edit"];
    });


    $("#assign-diagnosis-btn").on("click", function() {
        window.location.href = donor_information["_links"]["assign_diagnosis"];
    });

    $("#donor-id").html(donor_information["id"]);

    fill_basic_information(donor_information)

    $("#diagnosis-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#diagnosis-div").fadeIn(1000);
    });

    $("#basic-info-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info-div").fadeIn(1000);

    });

    $("#samples-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#samples-div").fadeIn(1000);

    })
});