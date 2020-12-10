function make_doughnut(dom_id, data, labels) {
    new Chart(document.getElementById(dom_id), {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
                data: data,
                backgroundColor: dynamicColours(labels.length)
            }],

        },
        options: {
            legend: {
                display: true
            },
            title: {
                display: false
               }}}
        );
}

function make_pie(dom_id, data, labels) {
    if (data.length > 0) {
        new Chart(document.getElementById(dom_id), {
            type: 'pie',
            data: {
              labels: labels,
              datasets: [{
                    data: data,
                    backgroundColor: dynamicColours(labels.length)
                }],
    
            },
            options: {
                legend: {
                    display: true
                },
                title: {
                    display: false
                   }}}
            );
        }
     else {
        $(dom_id).parent().css({"color": "red", "border": "2px solid red"});
    }
}

function make_bar(dom_id, data, labels) {
    new Chart(document.getElementById(dom_id), {
        type: 'bar',
        data: {
          labels: labels,
          barThickness: "flex",
          datasets: [{
                data: data,
                backgroundColor: dynamicColours(labels.length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: false
               }}}
        );
}
