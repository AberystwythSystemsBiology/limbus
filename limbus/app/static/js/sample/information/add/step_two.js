$(document).ready(function() {
    $('#selectAttribute').DataTable( {
        dom: 'Pfrtip'
    });

    $("#sampleTable_filter").hide();

    $(".dtsp-panesContainer").hide();

    $("#showFilter").click(function(e) {
        if ($(".dtsp-panesContainer").is(":visible")) {
            $(".dtsp-panesContainer").hide();
            $("#showFilter").text("Show Filters")
        }

        else {
            $("#showFilter").text("Hide Filters")
            $(".dtsp-panesContainer").show();
        }

    });

});