function sap2tree(data) {

    var content = data["content"];

    var proc_class = content;
    proc_class["text"] = `LIMBDIAG-${proc_class['id']}: ${proc_class['name']}`;
    proc_class["type"] = "class";
    proc_class["children"] = proc_class["volumes"];
    proc_class["id"] = "a"


    for (var a = 0; a < proc_class["children"].length; a++) {
        var volume = proc_class["children"][a];
        volume["text"] = `${volume['code']}: ${volume['name']}`;
        volume["type"] = "volume"
        volume["id"] = volume["_links"]["self"];

        volume["children"] = volume["subvolumes"]


        for (var b = 0; b < volume["children"].length; b++) {
            var subvolume = volume["children"][b];
            subvolume["text"] = `${subvolume['code']}: ${subvolume['name']}`;
            subvolume["type"] = "subvolume"
            subvolume["children"] = [];

        }

    }


    return {
        'types': {
            'class': { 'icon': 'fa fa-stethoscope' },
            'volume': { 'icon': 'fa fa-book' },
            'subvolume': { 'icon': 'fa fa-book-open' },
            'procedure': { 'icon': 'fa fa-user-md' }
        },
        'plugins' : ['types', 'wholerow', 'search'] ,
        'core': {
            'data': {
                'text': proc_class["text"],
                'type': 'class',
                'children': proc_class["children"]
            }
        }
    }
}

function collapse_sidebar() {
        $('#sidebar').toggleClass('active');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-left');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-right');
        $('#sidebar-collapse button').toggleClass('btn-light');
        $('#sidebar-collapse button').toggleClass('btn-primary');
}

function get_endpoing_data(api_url) {

    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'dataType': "json",
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();

    return json["content"];
}



function generate_volume_view(endpont_url) {
    var volume = get_endpoing_data(endpont_url);
    $("#primary-heading").html(`${volume['code']}: ${volume['name']}`);
}

function generate_subvolume_view(endpont_url) {
    var subvolume = get_endpoing_data(endpont_url);
    $("#primary-heading").html(`${subvolume['code']}: ${subvolume['name']}`);

}

$(function() {

    $('#sidebar-collapse').on('click', function () {
        collapse_sidebar();
    });


    function selectElement(element) {

        if (element["type"] == "volume") {
            generate_volume_view(element["id"]);
        }

        else if (element["type"] == "subvolume") {
            generate_subvolume_view(element["id"]);

        }

    }

    
    $.get( location.href + "/tree", function( data ) {
        $('#jstree').jstree(sap2tree(data));
        
        $('#jstree').on("changed.jstree", function(e, data) {
            // Don't process event if not triggered by user (e.g. page state reload)
            if(!data.event) { return; }

            switch (data.node.type) {
                case 'class':
                    location.href = location.href;
                    break;
                default:
                    selectElement(data.node);
                    break;
            }
        });
        
    });
});


