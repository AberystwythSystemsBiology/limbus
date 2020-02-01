$(document).ready(function() {
    $('#attributeTable').DataTable( {
        dom: 'Pfrtip'
    });

    $("#attributeTable_filter").hide();

    $(".dtsp-panesContainer").hide();

    $("#showFilter").click(function(e) {
        if ($(".dtsp-panesContainer").is(":visible")) {
            $(".dtsp-panesContainer").hide();
            $("#showFilter").text("Show Element")
        }

        else {
            $("#showFilter").text("Hide Element")
            $(".dtsp-panesContainer").show();
        }

    });

});