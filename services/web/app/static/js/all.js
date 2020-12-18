function get_metric(type) {
  if (type == "Fluid") {
      var metric = "mL";
  }
  else if (type == "Molecular") {
      var metric = "μg/mL";
  }
  else {
      var metric = "Cell(s)"
  }

  return metric
}

function render_author(author) {
  return author["first_name"] + " " + author["last_name"];
}


function render_jumbotron_btn(url, fa, content) {
  html = '<div class="btn-group mr-2" role="group" aria-label="First group">'
  html += '<a href="' + url + '">'
  html += '<button type="button" class="btn btn-outline-dark"><i class="' + fa + '"></i> '
  html += content
  html += '</button></a></div>'
  return html
}

function calculate_age(month, year) {

  var dob = new Date(year, month);
  var today = new Date();

  var age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000))

  return age
}

function render_colour(colour) {
  if (colour == "Blue") {
      var colour_class = "bg-primary";
  }
  else if (colour == "Red") {
      var colour_class = "bg-danger";
  }
  else if (colour == "Green") {
      var colour_class = "bg-success";
  }
  else if (colour == "Yellow") {
      var colour_class= "bg-warning";
  }

  var colour_html = '<span class="colour-circle '+colour_class+'"></span>';
  
  return colour_html;

}

function render_content(label, content) {
  if (content == undefined || content == "") {
      content = "Not Available."
  }
  return '<tr"><td width="30%" style="font-weight:bold">'+ label + ':</td><td>'+content+'</td></tr>';
   
}

function view_form_helper(id_ref) {
  console.log(view_form_helper);
  var element_id = $("#"+id_ref+" option:selected").val();
  console.log(element_id);
  var url = $("#"+id_ref+"_href").attr("href");
  var url_without_id = url.substr(0, url.lastIndexOf("-") + 1)
  $("#"+id_ref+"_href").attr("href", url_without_id + element_id);
}



function dynamicColours(length) {
  var colours = [];
  for (i =0; i < length; i++) {
      var r = Math.floor(Math.random() * 255);
      var g = Math.floor(Math.random() * 255);
      var b = Math.floor(Math.random() * 255);
      colours.push("rgba(" + r + "," + g + "," + b + ", 1)");
  }
  return colours;
  
}




function get_greeting() {
  var api_url = encodeURI(window.location.origin+'/api/misc/greeting');


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

  return json;
}

function uuid_search(query) {
  var api_url = window.location.origin + "/sample/query";

  var json = (function () {
    var json = null;
    $.post({
        'async': false,
        'global': false,
        'url': api_url,
        'contentType': 'application/json',
        'data': JSON.stringify(query),
        'success': function (data) {
            json = data;
        }
    });
    return json;
  })();

  return json["content"];
}


function fill_greeting(greeting) {
  $("#greeting").html(greeting["greeting"]);
  $("#greet_language").html(greeting["language"]);
}

$(document).ready(function(){
  $('.toast').toast('show');

  $('#history').DataTable( {} );


  $("#nav-sample-search").keypress(function(e) {
    if(e.which == 13) {
        jQuery(this).blur();
        var result = uuid_search({"uuid": this.value});
        if (result.length > 0) {
          window.location.href = result[0]["_links"]["self"]
        }
        else {
          $("#sample-uuid-search-not-found-placeholder").html(this.value);
          $("#uuid-search-modal-not-found").modal('show');
        }
    }
  });

  $("#navbarDropdown").click(function() {
    var greeting = get_greeting()
    fill_greeting(greeting);
  });


$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

});
