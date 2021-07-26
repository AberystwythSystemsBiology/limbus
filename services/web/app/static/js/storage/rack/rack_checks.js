

function check_rack() {
    var rackSelect = {"id":document.getElementById("racks").value};
    // console.log(rackSelect['id'])
    if (rackSelect['id']===""){
        document.getElementById("rack-warning").style.display = "none";
        return;
    }
    var res;
    var api_url = window.location.origin + "/storage/rack/query/rack";
    $.post({
        'async': false,
        'global': false,
        'url': api_url,
        'contentType': 'application/json',
        'data': JSON.stringify(rackSelect),
        'success': function (data) {
            res = data;
            // console.log(res)
        }
    });

    if (res['in_ets'] === true){
        document.getElementById("rack-warning").style.display = "block";
    }
    else{
        document.getElementById("rack-warning").style.display = "none";
    }
}

function check_sample(){
    var rackSelect = {"id":document.getElementById("samples").value};
    console.log(rackSelect['id'])
    if (rackSelect['id']===""){
        document.getElementById("rack-warning").style.display = "none";
        return;
    }


    var res;
    var api_url = window.location.origin + "/storage/rack/query/sample";
    $.post({
        'async': false,
        'global': false,
        'url': api_url,
        'contentType': 'application/json',
        'data': JSON.stringify(rackSelect),
        'success': function (data) {
            res = data;
            // console.log(res)
        }
    });

    if (res['in_ets'] === true){
        document.getElementById("rack-warning").style.display = "block";
    }
    else{
        document.getElementById("rack-warning").style.display = "none";
    }
}