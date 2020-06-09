function check() {
    if($("#from_file").is(":checked")) {
        $("#data").show();
        $("#json_file").prop("required", true);

    }
    else {
        $("#data").hide();
        $("#json_file").prop("required", false);
    }      
}

$(document).ready(function(){
    check();

    $('#from_file').change(function() {
        check();
    });
});
  