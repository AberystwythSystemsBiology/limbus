/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

function chart_placeholder(dom_id, data_length) {
    if (data_length < 1) {
        $("#" + dom_id + "-div").html("Not enough data provided.");
        return false
    }
    return true
}

function make_timeseries(dom_id, data, labels) {
    if (chart_placeholder(dom_id, data.length)) {

        var ctx = document.getElementById(dom_id);

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: "Samples Added",
                    data: data,
                    backgroundColor: 'rgba(0,102,255,0.6)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: false
                },
                title: {
                    display: false
                },
                scales: {
                  x: {
                    type: 'time',
                    time: {
                        unit: 'day'
                    },
                    title: {
                        display: false,
                    },
                  },
                    y: {
                        ticks: {
                            min: 0,
                            max: Math.ceil(Math.max(...data)),
                            stepSize: Math.ceil(Math.max(...data)/10)
                        },
                    }

                },
                
            }
        });

        
    }
}

function make_doughnut(dom_id, data, labels) {
    if (chart_placeholder(dom_id, data.length)) {
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
                }
            }
        }
        );
    }

}

function make_pie(dom_id, data, labels) {
    if (chart_placeholder(dom_id, data.length)) {
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
                }
            }
        }
        );
    }
}



function make_bar(dom_id, data, labels) {
    if (chart_placeholder(dom_id, data.length)) {


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
                },
                scales: {
                    y: {
                        display: true,
                        ticks: {
                            beginAtZero: true,
                            userCallback: function (label, index, labels) {
                                // when the floored value is the same as the value we have a whole number
                                if (Math.floor(label) === label) {
                                    return label;
                                }

                            },
                            max: Math.floor(Math.max(...data) * 1.3),
                            stepValue: 1,
                        }
                    }

                }
            }
        }
        );
    }
}
