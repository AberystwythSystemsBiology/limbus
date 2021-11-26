function fill_sample_pos(api_url, rack_id=null, sampletostore, commit) {
    var json = (function () {
        var json = null;
        $.ajax({
            'async': true, //false,
            'global': false,
            'url': api_url, //"{{ url_for('storage.rack_automatic_entry_validation', _external=True) }}",
            'type': 'POST',
            'dataType': "json",
            // 'data': JSON.stringify({'rack_id': rack_id,
            //     'samples':(sampletostore), 'commit': commit
            // }),
            'data': JSON.stringify(sampletostore),
            'contentType': 'application/json; charset=utf-8',
            'success': function (data) {
                json = data
            },
            'failure': function (data) {
                json = data;
            }

        });
        return json;
    })();

    return json;

}

$(document).ready(function () {

    //$("#create-from-file-btn").click(function() {
    if (sampletostore==undefined) {
        var sampletostore = JSON.parse(sessionStorage.getItem("sampletostore"));
        console.log("sampletostore", sampletostore);
        var api_url = window.location.href + "/validation";
        fill_sample_pos(api_url, rack_id = null, sampletostore = sampletostore, commit = true);
    }

});