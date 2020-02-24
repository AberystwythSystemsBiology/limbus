$(document).ready(function () {

    var options = [];

    $("#submitOption").click(function(e) {
        var option = $("#optionInput").val();
        if (option != "") {
            options.push(option);
            update_view();
            $("#exampleModal").modal("hide");
            $("#optionInput").val("");
        }
    });

    function update_view() {
        $("#optionsDisplay").empty();
        for (i in options) {
            $("#optionsDisplay").append(
                '<li class="list-group-item">' +
                options[i] + '</li>');s
        }
    }


    var successFunction = function (data) {
        // do something
        console.log(data);
        window.location = data;
    };


    $("#submitButton").click(function submit_options(e) {
        if (options.length > 0 ) {

            var data = {
                "options[]": options
            };

            $.ajax({
                type: "POST",
                url: $(location).attr('href'),
                data: data,
                dataType: "json",
                success: function(response){
                    successFunction(response);
                    }
            });


        }

        else {
            alert("We're going to need some options.")
        }
    });

});