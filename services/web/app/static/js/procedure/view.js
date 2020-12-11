function sap2tree(data) {

    var content = data["content"];

    var proc_class = content;
    proc_class["text"] = `LIMBDIAG-${proc_class['id']}: ${proc_class['name']}`;
    proc_class["type"] = "class";
    proc_class["children"] = proc_class["volumes"];
    proc_class["id"] = proc_class["_links"]["self"];


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
            subvolume["id"] = subvolume["_links"]["self"];
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
                'children': proc_class["children"],
                'id': proc_class["id"]
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

function wipe_all() {
    $("#secondary-heading").html("");
    $("#primary-heading").html("");
    $("#created-on").html("");
    $("#author").html("");
    $("#jumbotron-btn-toolbar").html("");
    $("#information").html("");
    $("#additional-content").html("");

}


function generate_class_view(endpoint_url) {
    var pclass = get_endpoing_data(endpoint_url);

    var title = `LIMBDIAG-${pclass['id']}: ${pclass['name']}`

    $(document).prop('title', title);

    $("#secondary-heading").html("<a href='"+ pclass["_links"]["procedures_index"]+"'><i class='fa fa-stethoscope'></i> Diagnostic Procedure</a>")
    $("#primary-heading").html(title);

    $("#created-on").html(pclass["creation_date"]);
    $("#author").html(render_author(pclass["author"]));

    var btn_html = render_jumbotron_btn(pclass["_links"]["new_volume"], "fa fa-plus", "New Volume");
    $("#jumbotron-btn-toolbar").html(btn_html);

    html = render_content("Description", pclass["description"])
    html += render_content("Version", pclass["version"])



    $("#information").html(html);

}

function generate_volume_view(endpont_url) {
    var volume = get_endpoing_data(endpont_url);

    $("#secondary-heading").html(`<i class="fa fa-stethoscope"></i> LIMBDIAG-${volume['pclass']['id']}: ${volume['pclass']['name']}`);
    $("#primary-heading").html(`Volume ${volume['code']}: ${volume['name']}`);
    $("#created-on").html(volume["creation_date"]);
    $("#author").html(render_author(volume["author"]));

    var html = "<h2>Subvolumes</h2><table class='table table-striped'>";
  

    for (i in volume["subvolumes"]) {
        var subvolume = volume["subvolumes"][i];
        html += render_content(subvolume["code"], subvolume["name"]);
    }

    

    html += "</table>"

    $("#additional-content").html(html);


    var btn_html = render_jumbotron_btn(volume["_links"]["new_subvolume"], "fa fa-plus", "New Subvolume");
    $("#jumbotron-btn-toolbar").html(btn_html);

}

function generate_subvolume_view(endpont_url) {
    var subvolume = get_endpoing_data(endpont_url);
    $("#secondary-heading").html(`<i class='fa fa-book'></i> Volume ${subvolume['volume']['code']}: ${subvolume['volume']['name']}`);
    $("#primary-heading").html(`${subvolume['code']}: ${subvolume['name']}`);
    $("#created-on").html(subvolume["creation_date"]);
    $("#author").html(render_author(subvolume["author"]));

    var html = "<h2>Procedures</h2><table class='table table-striped'>";

    for (i in subvolume["procedures"]) {
        var procedure = subvolume["procedures"][i];
        html += render_content(procedure["code"], procedure["procedure"]);
    }

    html += "</table>"

    $("#additional-content").html(html);

    console.log(subvolume)


    var btn_html = render_jumbotron_btn(subvolume["_links"]["new_procedure"], "fa fa-plus", "New Procedure");
    $("#jumbotron-btn-toolbar").html(btn_html);

}

$(function() {

    $('#sidebar-collapse').on('click', function () {
        collapse_sidebar();
    });


    function selectElement(element) {

        wipe_all();

        if (element["type"] == "class" ) {
            generate_class_view(element["id"]);
        }

        else if (element["type"] == "volume") {
            generate_volume_view(element["id"]);
        }

        else if (element["type"] == "subvolume") {
            generate_subvolume_view(element["id"]);

        }

    }

    
    $.get( location.href + "/tree", function( data ) {
        $('#jstree').jstree(sap2tree(data));
        
        $('#jstree').on("changed.jstree", function(e, data) {
            if(!data.event) { return; }

            switch (data.node.type) {
                default:
                    selectElement(data.node);
                    break;
            }
        });
        
    });
});


