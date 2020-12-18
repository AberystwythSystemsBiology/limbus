

function check_status() {
    if ($("#status").val() == "DE") {
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();
    }
}   




function assign_age() {
    var month = $("#month").val();
    var year = $("#year").val();
    $("#years").html(calculate_age(month, year));
}



$(document).ready(function(){
    check_status();

    assign_age();

    $("#month").change(function() {
        assign_age();
    });

    $("#year").change(function() {
        assign_age();
    });

    $("#status").change(function() {
        assign_age();
      });

});
  