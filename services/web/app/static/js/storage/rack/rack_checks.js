

function check_rack() {
    var rackSelect = {"id":document.getElementById("racks").value};
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
            console.log(res)
        }
    });
    console.log(res['warning'])
    if (res['warning'] === "RST"){
        document.getElementById("rack-warning").innerHTML = "<b>Warning:</b> This will move the rack from its current shelf"
        document.getElementById("rack-warning").style.display = "block";
        document.getElementById("submit").style.display = "block"
        document.getElementById("rack-warning").className = "alert alert-warning"
    }
    else if(res['warning'] === "RCT"){
        document.getElementById("rack-warning").innerHTML = "<b>Warning:</b> Rack is currently in the cart"
        document.getElementById("submit").style.display = "none"
        document.getElementById("rack-warning").style.display = "block";
        // document.getElementById("rack-warning").style.backgroundColor = "red";
        document.getElementById("rack-warning").className = "alert alert-error"
    }
    else{
        document.getElementById("rack-warning").style.display = "none";
        document.getElementById("submit").style.display = "block"
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

    if (res['warning'] === "SRT"){
        document.getElementById("rack-warning").innerHTML = "<b>Warning:</b> This will move the sample from its current location"
        document.getElementById("rack-warning").style.display = "block";
        document.getElementById("submit").style.display = "block"
        document.getElementById("rack-warning").className = "alert alert-warning"
    }
    else if(res['warning'] === "SCT"){
        document.getElementById("rack-warning").innerHTML = "<b>Warning:</b> This sample is currently in the cart"
        document.getElementById("submit").style.display = "none"
        document.getElementById("rack-warning").style.display = "block";
        // document.getElementById("rack-warning").style.backgroundColor = "red";
        document.getElementById("rack-warning").className = "alert alert-error"
    }
    else{
        document.getElementById("rack-warning").style.display = "none";
        document.getElementById("submit").style.display = "block"
    }
}