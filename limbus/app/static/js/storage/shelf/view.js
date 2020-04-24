function updateCryoChoices(cryo_ids) {
    $('#cryobox-modal-body').empty();
    for(var i=0; i < cryo_ids.length; i++) {
        var cryo_container = document.createElement('div');
        $(cryo_container).addClass('card')
        var cryo_radio = document.createElement('input');
        $(cryo_radio).addClass('form-check-input')
                    .attr('type', 'radio')
                    .attr('value', cryo_ids[i].id)
                    .attr('name', 'cryo-choices')
                    .attr('id', `cryoChoice${i}`);
        var label = document.createElement('label');
        $(label).addClass('form-check-label')
                .attr('for', `cryoChoice${i}`)
                .text(`Cryobox ${cryo_ids[i].serial}`);
        $(cryo_container).append(cryo_radio);
        $(cryo_container).append(label);
        $('#cryobox-modal-body').append(cryo_container);
    }
}

$('#assign-cryobox-modal').on('show.bs.modal', function(e) {
    $.get('/storage/cryobox/unassigned', function(data) {
        $('#cryobox-error-alert').addClass('hidden');
        updateCryoChoices(data);
    })
});

$('#assign-cryobox-button').on('click', function(e) {
    console.log("Pressed");
    var box_id = $('#assign-cryobox-modal .form-check-input').filter(':checked')
                                                             .attr('value');
    var page_part = window.location.pathname.split('/').pop()
    var shelf_id = page_part.match(/LIMBSHF-([0-9]+)/)[1];
    $.ajax({
        type: "POST",
        url: `/storage/cryobox/assign/LIMCRB-${box_id}`,
        // The key needs to match your method's input parameter (case-sensitive).
        data: JSON.stringify({ 'id': shelf_id }),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(data){
            console.log({'success': data});
            $('#assign-cryobox-modal').modal('hide');
            $('#assign-cryobox-button').attr('disabled', 'true');
            location.reload(true);
        },
        error: function(errMsg) {
            console.log({'error': errMsg});
            $('#assign-cryobox-button').removeAttr('disabled');
            $('#cryobox-error-message').text('Could not assign box');
            $('#cryobox-error-alert').removeClass('hidden');
        }
    });
});