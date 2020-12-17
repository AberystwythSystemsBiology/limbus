

function check_status() {
    if ($("#status").val() == "DE") {
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();
    }
}   


function calculate_age() {
    var month = $("#month").val();
    var year = $("#year").val();

    var dob = new Date(year, month);
    var today = new Date();

    var age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000))

    $("#years").html(age);
}

$(document).ready(function(){
    check_status();

    calculate_age();

    $("#month").change(function() {
        calculate_age();
    });

    $("#year").change(function() {
        calculate_age();
    });

    $("#status").change(function() {
        check_status();
      });

});
  