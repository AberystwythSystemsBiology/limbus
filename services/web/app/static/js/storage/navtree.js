
function sap2tree(sap) {
    var sites = sap["content"];




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
                'text': 'Sites',
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


    function selectSite(site) {
        var site_id = parseId(site.id);
        location.href=`/storage/sites/LIMBSIT-${site_id}`
    }

    function selectRoom(room) {
        var room_id = parseId(room.id);
        location.href=`/storage/rooms/LIMBROM-${room_id}`
    }

    function selectFridge(fridge) {
        var fridge_id = parseId(fridge.id);
        location.href=`/storage/lts/LIMBLTS-${fridge_id}`
    }

    function selectShelf(shelf) {
        var shelf_id = parseId(shelf.id);
        location.href=`/storage/shelves/LIMBSHF-${shelf_id}`
    }

    function selectBox(box) {
        var box_id = parseId(box.id);
        location.href=`/storage/cryobox/LIMBCRB-${box_id}`
    }

    function selectSample(sample) {
        var sample_id = parseId(sample.id);
        location.href=`../../../samples/LIMBSMP-${sample_id}`
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