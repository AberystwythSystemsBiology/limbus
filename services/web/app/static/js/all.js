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
  return '<div class="row"><div class="col-5">'+ label + ':</div><div class="col-7">'+content+'</div></div>';
   
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


function fill_greeting(greeting) {
  $("#greeting").html(greeting["greeting"]);
  $("#greet_language").html(greeting["language"]);
}

$(document).ready(function(){
  $('.toast').toast('show');

  $('#history').DataTable( {} );



  $("#navbarDropdown").click(function() {
    var greeting = get_greeting()
    fill_greeting(greeting);
  });


$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})

});
