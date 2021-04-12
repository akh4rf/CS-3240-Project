function drawProfileChart() {
  google.charts.load("current", {packages:['corechart']});
  google.charts.setOnLoadCallback(drawChart);

  var date1 = new Date();
  var date2 = new Date();
  var date3 = new Date();
  var date4 = new Date();
  var date5 = new Date();
  var date6 = new Date();
  var date7 = new Date();
  date2.setDate(date1.getDate()-1);
  date3.setDate(date1.getDate()-2);
  date4.setDate(date1.getDate()-3);
  date5.setDate(date1.getDate()-4);
  date6.setDate(date1.getDate()-5);
  date7.setDate(date1.getDate()-6);

  var days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  function drawChart() {
    var data = google.visualization.arrayToDataTable([
      ['Date', 'Calories Burned', { role: 'style' } ],
      [days[date7.getDay()-1], 10, 'color: #76A7FA'],
      [days[date6.getDay()-1], 14, 'color: #76A7FA'],
      [days[date5.getDay()-1], 16, 'color: #76A7FA'],
      [days[date4.getDay()-1], 22, 'color: #76A7FA'],
      [days[date3.getDay()-1], 28, 'color: #76A7FA'],
      ['Yesterday', 35, 'color: #76A7FA'],
      ['Today', 42, 'color: #76A7FA'],
    ]);

    var view = new google.visualization.DataView(data);

    var options = {
      title: "Calories Burned by Day",
      width: 750,
      height: 400,
      bar: {groupWidth: "95%"},
      legend: { position: "none" },
      fontSize: 10
    };
    
    var chart = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
    chart.draw(view, options);
  }
}
