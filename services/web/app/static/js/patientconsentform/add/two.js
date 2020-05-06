$(document).ready(function () {
    var options = [];

    $("#remove_question").click(function (e) {
        alert("Hello World")
    });

    function update_view() {
        $("#questionsToSubmit").empty();


        for (o in options) {
            var q_num = parseInt(parseInt(o)+parseInt(1));
            $("#questionsToSubmit").append(
                '<div class="list-group-item list-group-item-action">\n' +
                '            <div class="d-flex w-100 justify-content-between">\n' +
                '              <h5 class="mb-1">Question '+ q_num +'</h5>\n' +
                '            </div>\n' +
                '            <p class="mb-1">'+options[o]+'</p>\n' +
                '          </div>'
            );
        }
    }

    update_view();

    $("#submitOption").click(function (e) {
        options.push($("#questionInput").val());
        update_view();
        $("#exampleModal").modal("hide");
        $("#questionInput").val("");
    });

    $("#submitButton").click(function (e) {
        if (options.length > 0) {
            var data = {
            "questions[]": options
        }

        $.ajax({
            type: "POST",
            url: $(location).attr('href'),
            data: data,
            dataType: "json",
            success: function(response) {
                window.location = response["redirect"];
            }
        });
        }

        else (
            alert("No questions have been entered?")
        )

    });
});


