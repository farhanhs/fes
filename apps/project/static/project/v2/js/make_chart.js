function show_make_chart_dialog(){
    var year = $('#year').val();
    $('#chart_year').val(year);
    $('#make_chart_dialog').modal('show');
}

function make_chart(){
    var year = $('#chart_year').val();
    var year_text = $('#chart_year option:selected').text()
    var type = $(this).attr('type');
    $('#loading').show();
    var data = {
        csrfmiddlewaretoken: CSRFMIDDLEWARETOKEN,
        year: year,
        type: type
    }
    $.ajax({
        url: '/project/get_chart_data/',
        type: 'POST',
        data: data,
        dataType: 'json',
        success: function (json, text, xhr) {
            if (type=='start_date'){
                $('#div_canvas').html('<canvas class="chart_canvas" id="canvas_start_date"></canvas>');
                $('.chart_canvas').closest('div').css('width', '1200px');
                var color = Chart.helpers.color;
                var barChartData = {
                    labels: ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月", "未設定"],
                    datasets: [{
                        label: '件數',
                        backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.blue,
                        borderWidth: 1,
                        data: json['data']
                    }]
                };
                var config = {
                    type: 'bar',
                    data: barChartData,
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '開工月份件數統計表(年度：' + year_text + ')',
                            fontSize: 18
                        },
                        animation: {
                          "duration": 1,
                          "onComplete": function() {
                            var chartInstance = this.chart,
                              ctx = chartInstance.ctx;

                            ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';

                            this.data.datasets.forEach(function(dataset, i) {
                              var meta = chartInstance.controller.getDatasetMeta(i);
                              meta.data.forEach(function(bar, index) {
                                var data = dataset.data[index];
                                ctx.fillText(data, bar._model.x, bar._model.y - 5);
                              });
                            });
                          }
                        }
                    }
                };
                var ctx = document.getElementById("canvas_start_date").getContext("2d");
                Chart.pluginService.register({
                    beforeDraw: function (chart, easing) {
                        var ctx = chart.chart.ctx;
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, 1200, 1200);
                        ctx.restore();
                    }
                });
                window.myBar = new Chart(ctx, config);
                $("#save-image-btn").unbind('click');
                $("#save-image-btn").click(function() {
                    $("#canvas_start_date").get(0).toBlob(function(blob) {
                        var today = moment().format('YYYY-MM-DD');
                        saveAs(blob, today + '-開工月份件數統計表(年度：' + year_text + ').png');
                    });
                });
                $('#canvas_start_date').show();
            } else if (type=='project_status'){
                $('#div_canvas').html('<canvas class="chart_canvas" id="canvas_project_status"></canvas>');
                $('.chart_canvas').closest('div').css('width', '800px');
                var n = json['data']['nums'].reduce(function(a, b) { return a + b; }, 0);;
                var config = {
                    type: 'pie',
                    data: {
                        datasets: [{
                            data: json['data']['nums'],
                            backgroundColor: [
                                window.chartColors.green,
                                window.chartColors.blue,
                                window.chartColors.orange,
                                window.chartColors.red,
                                'gray',
                            ],
                            label: json['data']['titles']
                        }],
                        labels: json['data']['titles'],
                    },
                    options: {
                        responsive: true,
                        title: {
                            display: true,
                            text: '工程狀態統計統計表(年度：' + year_text + ')',
                            fontSize: 18
                        },
                        pieceLabel: {
                            // mode 'label', 'value' or 'percentage', default is 'percentage'
                            mode: 'value',
                            fontSize: 16,
                            fontColor: '#000',
                            fontStyle: 'bold',
                            arc: true,
                            position: 'outside',
                            format: function (value) {
                              return value+'件：' + Math.round(value*10000/n)/100 + '%';
                            }
                        }
                    }
                };
                var ctx = document.getElementById("canvas_project_status").getContext("2d");
                Chart.pluginService.register({
                    beforeDraw: function (chart, easing) {
                        var ctx = chart.chart.ctx;
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, 1200, 1200);
                        ctx.restore();
                    }
                });
                window.myPie = new Chart(ctx, config);
                $("#save-image-btn").unbind('click');
                $("#save-image-btn").click(function() {
                    $("#canvas_project_status").get(0).toBlob(function(blob) {
                        var today = moment().format('YYYY-MM-DD');
                        saveAs(blob, today + '-工程狀態統計統計表(年度：' + year_text + ').png');
                    });
                });
                $('#canvas_project_status').show();
            } else if (type=='project_num'){
                $('#div_canvas').html('<canvas class="chart_canvas" id="canvas_project_num"></canvas>');
                $('.chart_canvas').closest('div').css('width', '1200px');
                var color = Chart.helpers.color;
                var barChartData = {
                    labels: json['data']['units'],
                    datasets: [{
                        label: '件數',
                        backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.blue,
                        borderWidth: 1,
                        data: json['data']['nums']
                    }]
                };
                var config = {
                    type: 'bar',
                    data: barChartData,
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '各單位工程件數統計表(年度：' + year_text + ')',
                            fontSize: 18
                        },
                        scales: {
                            xAxes: [{
                                ticks: {
                                    autoSkip: false,
                                }
                            }]
                        },
                        animation: {
                          "duration": 1,
                          "onComplete": function() {
                            var chartInstance = this.chart,
                              ctx = chartInstance.ctx;

                            ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';

                            this.data.datasets.forEach(function(dataset, i) {
                              var meta = chartInstance.controller.getDatasetMeta(i);
                              meta.data.forEach(function(bar, index) {
                                var data = dataset.data[index];
                                ctx.fillText(data, bar._model.x, bar._model.y - 5);
                              });
                            });
                          }
                        }
                    }
                };
                var ctx = document.getElementById("canvas_project_num").getContext("2d");
                Chart.pluginService.register({
                    beforeDraw: function (chart, easing) {
                        var ctx = chart.chart.ctx;
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, 1200, 1200);
                        ctx.restore();
                    }
                });
                window.myBar = new Chart(ctx, config);

                $("#save-image-btn").unbind('click');
                $("#save-image-btn").click(function() {
                    $("#canvas_project_num").get(0).toBlob(function(blob) {
                        var today = moment().format('YYYY-MM-DD');
                        saveAs(blob, today + '-各單位工程件數統計表(年度：' + year_text + ').png');
                    });
                });
                $('#canvas_project_num').show();
            } else if (type=='project_photo'){
                $('#div_canvas').html('<canvas class="chart_canvas" id="canvas_project_photo"></canvas>');
                $('.chart_canvas').closest('div').css('width', '1200px');
                var color = Chart.helpers.color;
                console.log(json);
                var barChartData = {
                    labels: json['data']['title'],
                    datasets: [{
                        label: '件數',
                        backgroundColor: color(window.chartColors.blue).alpha(0.5).rgbString(),
                        borderColor: window.chartColors.blue,
                        borderWidth: 1,
                        data: json['data']['num']
                    }]
                };
                var config = {
                    type: 'bar',
                    data: barChartData,
                    options: {
                        responsive: true,
                        legend: {
                            position: 'top',
                        },
                        title: {
                            display: true,
                            text: '工程相片數量件數統計表(年度：' + year_text + ')',
                            fontSize: 18
                        },
                        animation: {
                          "duration": 1,
                          "onComplete": function() {
                            var chartInstance = this.chart,
                              ctx = chartInstance.ctx;

                            ctx.font = Chart.helpers.fontString(Chart.defaults.global.defaultFontSize, Chart.defaults.global.defaultFontStyle, Chart.defaults.global.defaultFontFamily);
                            ctx.textAlign = 'center';
                            ctx.textBaseline = 'bottom';

                            this.data.datasets.forEach(function(dataset, i) {
                              var meta = chartInstance.controller.getDatasetMeta(i);
                              meta.data.forEach(function(bar, index) {
                                var data = dataset.data[index];
                                ctx.fillText(data, bar._model.x, bar._model.y - 5);
                              });
                            });
                          }
                        }
                    }
                };
                var ctx = document.getElementById("canvas_project_photo").getContext("2d");
                Chart.pluginService.register({
                    beforeDraw: function (chart, easing) {
                        var ctx = chart.chart.ctx;
                        ctx.fillStyle = 'white';
                        ctx.fillRect(0, 0, 1200, 1200);
                        ctx.restore();
                    }
                });
                window.myBar = new Chart(ctx, config);
                $("#save-image-btn").unbind('click');
                $("#save-image-btn").click(function() {
                    $("#canvas_project_photo").get(0).toBlob(function(blob) {
                        var today = moment().format('YYYY-MM-DD');
                        saveAs(blob, today + '-工程相片數量件數統計表(年度：' + year_text + ').png');
                    });
                });
                $('#canvas_project_photo').show();
            }
            
            $('#loading').hide();
            $('#div_s_curve').show();
            $('#div_s_curve_background').show();
        },
        error: function () {
        },
    })
}






$(document).ready(function(){
    $('#show_make_chart_dialog').click(show_make_chart_dialog);
    $('.make_chart').click(make_chart);
});
