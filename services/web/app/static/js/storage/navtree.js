
function sap2tree(sap) {
    var sites = sap["content"];


    for (var i = 0; i < sites.length; i++) {
        var site = sites[i];
        site["text"] = `LIMBSIT-${site['id']}: ${site['name']}`; 
        site["type"] = "site";
        site["children"] = site["buildings"];
        site["id"] = site["_links"]["self"]

        for (var j = 0; j < site["buildings"].length; j++) {
            var building = site["buildings"][j];
            building["text"] =`${building['name']}`;
            building["type"] = "building";
            building["children"] = building["rooms"];
            building["id"] = building["_links"]["self"]

            for (var k = 0; k < building["rooms"].length; k++) {
                var room = building["rooms"][k];
                room["text"] = `${room['name']}`;
                room["type"] = "room";
                room["id"] = room["_links"]["self"]
                room["children"] = room["storage"];

                for (var l = 0; l < room["storage"].length; l++) {
                    var storage = room["storage"][l];
                    storage["text"] = `${storage["manufacturer"]} (${storage["temp"]})`;
                    storage["type"] = "fridge";
                    storage["id"] = storage["_links"]["self"]
                }
            }
            
        }

    }

    return {
        'types': {
            'home': { 'icon': 'fa fa-home' },
            'building': { 'icon': 'fa fa-home'},
            'site': { 'icon': 'fa fa-hospital' },
            'room': { 'icon': 'fa fa-door-closed' },
            'fridge': { 'icon': 'fa fa-temperature-low' },
            'shelf': { 'icon': 'fa fa-bars' },
            'box': { 'icon': 'fa fa-box' },
            'sample': { 'icon': 'fa fa-flask' }
        },
        'state': { 'key': 'storage' },
        'plugins' : ['types', 'state'],
        'core': {
            'data': {
                'text': 'Show Sites',
                'type': 'home',
                'children': sites
            }
        }
    }
}
$(function() {

    $('#sidebar-collapse').on('click', function () {
        $('#sidebar').toggleClass('active');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-left');
        $('#sidebar-collapse-icon').toggleClass('fa-chevron-right');
        $('#sidebar-collapse button').toggleClass('btn-light');
        $('#sidebar-collapse button').toggleClass('btn-primary');
    });



    function selectElement(element) {
        location.href=element.id;
    }
    
    $.get( "/storage/overview", function( data ) {
        $('#jstree').jstree(sap2tree(data));
        $('#jstree').on("changed.jstree", function(e, data) {
            // Don't process event if not triggered by user (e.g. page state reload)
            if(!data.event) { return; }

            switch (data.node.type) {
                case 'home':
                    location.href = '/storage/';
                    break;
                default:
                    selectElement(data.node);
                    break;
            }
        });
    });
});