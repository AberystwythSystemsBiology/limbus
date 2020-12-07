

function check_status() {
    if ($("#status").val() == "DE") {
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();
    }
}   

$(document).ready(function(){
    check_status();

    $("#status").change(function() {
        check_status();
      });

});
  