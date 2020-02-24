$(document).ready(function () {
    var options = [];

    function update_view() {
        $("#whereItIs").empty();

        for (o in options) {
            $("#whereItIs").append(
                '<p>' + options[o] + '</p>'
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
            "options[]": options
        }

        $.ajax({
            type: "POST",
            url: $(location).attr('href'),
            data: data,
            dataType: "json",
            success: function(response) {
                console.log(response);
            }
        });
        }

        else (
            alert("No questions have been entered?")
        )

    });
});


