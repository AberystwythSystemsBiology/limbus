

function check_status() {
    if ($("#status").val() == "DE") {
        $('#death_date').val('');
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();

        var now = new Date();

        var day = ("0" + now.getDate()).slice(-2);
        var month = ("0" + (now.getMonth() + 1)).slice(-2);

        var today = now.getFullYear()+"-"+(month)+"-"+(day) ;
        
        $('#death_date').val(today);
    }
}   

$(document).ready(function(){
    check_status();

    $("#status").change(function() {
        check_status();
      });

});
  