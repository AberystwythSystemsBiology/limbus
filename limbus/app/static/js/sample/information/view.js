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

});