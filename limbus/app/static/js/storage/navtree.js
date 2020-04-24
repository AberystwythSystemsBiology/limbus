function sap2tree(sap) {
    var sites = sap['sites'];
    for (var i = 0; i < sites.length; i++) {
        var site = sites[i];
        site['text'] = site['name'];
        site['type'] = 'site';
        site['children'] = site['rooms'];
        site['id'] = `site:${site["id"]}`
        for (var j = 0; j < site['rooms'].length; j++) {
            var room = site['rooms'][j];
            room['text'] = `${room['building']}: ${room['number']}`;
            room['type'] = 'room';
            room['children'] = room['fridges'];
            room['id'] = `room:${room["id"]}`
            for (var k = 0; k < room['fridges'].length; k++) {
                var fridge = room['fridges'][k];
                fridge['text'] = `${fridge['manufacturer']}: ${fridge['serial']}`;
                fridge['type'] = 'fridge';
                fridge['children'] = fridge['shelves'];
                fridge['id'] = `fridge:${fridge["id"]}`
                for (var l = 0; l < fridge['shelves'].length; l++) {
                    var shelf = fridge['shelves'][l];
                    shelf['text'] = shelf['name'];
                    shelf['type'] = 'shelf';
                    shelf['children'] = shelf['cryoboxes'].concat(shelf['samples']);
                    shelf['id'] = `shelf:${shelf["id"]}`
                    for (var m = 0; m < shelf['cryoboxes'].length; m++) {
                        var box = shelf['cryoboxes'][m];
                        box['text'] = `Box ${box["id"]}`;
                        box['type'] = 'box';
                        box['id'] = `box:${box["id"]}`
                    }
                    for (var m = 0; m < shelf['samples'].length; m++) {
                        var sample = shelf['samples'][m];
                        sample['text'] = `Sample ${sample['id']}`;
                        sample['type'] = 'sample';
                        sample['id'] = `sample:${sample["id"]}`
                    }
                }
            }
        }
    }

    return {
        'types': {
            'home': { 'icon': 'fa fa-home' },
            'site': { 'icon': 'fa fa-hospital' },
            'room': { 'icon': 'fa fa-warehouse' },
            'fridge': { 'icon': 'fa fa-temperature-low' },
            'shelf': { 'icon': 'fa fa-bars' },
            'box': { 'icon': 'fa fa-box' },
            'sample': { 'icon': 'fa fa-flask' }
        },
        'state': { 'key': 'storage' },
        'plugins' : ['types', 'state'],
        'core': {
            'data': {
                'text': 'Manage',
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

    $('#add-site-button').on('click', function() {
        location.href='/storage/sites/new'
    });

    function selectSite(site) {
        var site_id = parseId(site.id);
        location.href=`/storage/sites/view/LIMBSIT-${site_id}`
    }

    function selectRoom(room) {
        var room_id = parseId(room.id);
        location.href=`/storage/rooms/view/LIMBROM-${room_id}`
    }

    function selectFridge(fridge) {
        var fridge_id = parseId(fridge.id);
        location.href=`/storage/lts/view/LIMBLTS-${fridge_id}`
    }

    function selectShelf(shelf) {
        var shelf_id = parseId(shelf.id);
        location.href=`/storage/shelves/view/LIMBSHF-${shelf_id}`
    }

    function selectBox(box) {
        var box_id = parseId(box.id);
        location.href=`/storage/cryobox/view/LIMBCRB-${box_id}`
    }

    function selectSample(sample) {
        var sample_id = parseId(sample.id);
        location.href=`/storage/samples/view/LIMBSAM-${sample_id}`
    }

    function parseId(id_field) {
        return id_field.split(':').slice(1).join(':');
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
                case 'site':
                    selectSite(data.node);
                    break;
                case 'room':
                    selectRoom(data.node);
                    break;
                case 'fridge':
                    selectFridge(data.node);
                    break;
                case 'shelf':
                    selectShelf(data.node);
                    break;
                case 'box':
                    selectBox(data.node);
                    break;
                case 'sample':
                    selectSample(data.node);
                    break;
            }
        });
    });
});