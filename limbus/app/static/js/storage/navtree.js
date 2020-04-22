function sap2tree(sap) {
    var sites = sap['sites'];
    for (var i = 0; i < sites.length; i++) {
        var site = sites[i];
        site['id'] = `site:${site["id"]}`
        site['text'] = site['name'];
        site['type'] = 'site';
        site['children'] = site['rooms'];
        for (var j = 0; j < site['rooms'].length; j++) {
            var room = site['rooms'][j];
            room['id'] = `room:${room["id"]}`
            room['text'] = `${room['building']}: ${room['number']}`;
            room['type'] = 'room';
            room['children'] = room['fridges'];
            for (var k = 0; k < room['fridges'].length; k++) {
                var fridge = room['fridges'][k];
                fridge['id'] = `fridge:${fridge["id"]}`
                fridge['text'] = `${fridge['manufacturer']}: ${fridge['serial']}`;
                fridge['type'] = 'fridge';
                fridge['children'] = fridge['shelves'];
                for (var l = 0; l < fridge['shelves'].length; l++) {
                    var shelf = fridge['shelves'][l];
                    shelf['id'] = `shelf:${shelf["id"]}`
                    shelf['text'] = shelf['name'];
                    shelf['type'] = 'shelf';
                    shelf['children'] = shelf['cryoboxes'].concat(shelf['samples']);
                    for (var m = 0; m < shelf['cryoboxes'].length; m++) {
                        var box = shelf['cryoboxes'][m];
                        box['id'] = `box:${box["id"]}`
                        box['text'] = `Box ${box['id']}`;
                        box['type'] = 'box';
                    }
                    for (var m = 0; m < shelf['samples'].length; m++) {
                        var sample = shelf['samples'][m];
                        sample['id'] = `sample:${sample["id"]}`
                        sample['text'] = `Sample ${sample['id']}`;
                        sample['type'] = 'sample';
                    }
                }
            }
        }
    }

    return {
        'types': {
            'site': { 'icon': 'fa fa-hospital' },
            'room': { 'icon': 'fa fa-warehouse' },
            'fridge': { 'icon': 'fa fa-temperature-low' },
            'shelf': { 'icon': 'fa fa-bars' },
            'box': { 'icon': 'fa fa-box' },
            'sample': { 'icon': 'fa fa-flask' }
        },
        'plugins' : ['types'],
        'core': {
            'data': sites
        }
    }
}
$(function() {
    $.get( "/storage/overview", function( data ) {
        $('#jstree').jstree(sap2tree(data));
        $('#jstree').on("changed.jstree", function(e, data) {
            console.log(data.node.type);
            switch (data.node.type) {
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