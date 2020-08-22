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


$(document).ready(function(){
  $('.toast').toast('show');

  $('#history').DataTable( {
});

});
