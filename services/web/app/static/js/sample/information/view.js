function get_img_url() {
    var base_url = window.location;
    return base_url + "/barcode/uuid"
}

$(document).ready(function() {
    var img_url = get_img_url();
    $("#barcode").hide();
    $("#barcode").attr("src", img_url);
    $("#loading-barcode").hide();
    $("#barcode").show();


    $('#subsampleTable').DataTable( {
        dom: 'Pfrtip'
    });

    $("#subsampleTable_filter").hide();

    $(".dtsp-panesContainer").hide();

    $("#showFilter").click(function(e) {
        if ($(".dtsp-panesContainer").is(":visible")) {
            $(".dtsp-panesContainer").hide();
            $("#showFilterText").text("Show Filters")
        }

        else {
            $("#showFilterText").text("Hide Filters")
            $(".dtsp-panesContainer").show();
        }

    });

});