

$(document).ready(function () {

    function hide_text_options() {
        $("input[name=max_length]").hide();
        $("label[for=max_length]").hide();
    }

    function show_text_options() {
        $("input[name=max_length]").show();
        $("label[for=max_length]").show();
    }


    hide_text_options()

    $("select").on("change", function() {
        if (this.value == "TEXT") {
            show_text_options()
        }

        else if (this.value == "NUMERIC") {
            hide_text_options()
        }

        else if (this.value == "OPTION") {
            hide_text_options()
        }
    });
});