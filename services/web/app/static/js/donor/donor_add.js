

function check_status() {
    if ($("#status").val() == "DE") {
        //$("#death_date").val();
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();
        $('#death_date').val('');
    }
}   

$(document).ready(function(){
    check_status();

    $("#status").change(function() {
        check_status();
      });

});
  