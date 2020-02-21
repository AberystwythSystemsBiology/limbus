$(document).ready(function() {
    $('#attributeTable').DataTable( {
        dom: 'Pfrtip'
    });

    $("#attributeTable_filter").hide();

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