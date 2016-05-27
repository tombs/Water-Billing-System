var uncollected_data = uncollected;
console.log("uncollected_data " + uncollected_data);
console.log("type is " + uncollected_data.type);

d3.select("#uncollected-piechart");

//Width and height
			var w = 300;
			var h = 300;

var container1 = document.getElementById('collected-stackgraph-flot');
var container2 = document.getElementById('uncollected-piechart-flot');

var myticks = [];
var uncollected_flot = [];
for (i=0;i<uncollected.length;i++) {
	uncollected_flot.push([i,uncollected[i]["unc"]]);
	myticks.push([i,uncollected[i]["address4"]]);
};
var collected_flot = [];
for (i=0;i<collected.length;i++) {
	collected_flot.push([i,collected[i]["col"]]);
};

var stackdata = [
	{ data : [], label : 'Collected' },
    { data : [], label : 'Uncollected' },
    ];

for (i=0;i<flot_stack['collected'].length;i++){
	stackdata[0]['data'].push([i,flot_stack['collected'][i][1]/1000.0]);
	stackdata[1]['data'].push([i,flot_stack['uncollected'][i][1]/1000.0]);
};

console.log('stackdata ',stackdata);
graph1 = Flotr.draw(container1,stackdata, 
	{
    legend : {
      backgroundColor : '#D2E8FF', // Light blue 
    },
    bars : {
      show : true,
      stacked : true,
      horizontal : false,
      barWidth : 0.6,
      lineWidth : 1,
      shadowSize : 0
    },
    xaxis: {
    	ticks : myticks,
    },
    grid : {
      verticalLines : false,
      horizontalLines : true
    },
  });


var piedata = [];
for (i in flot_pie) {
	piedata.push({'data': [[0,flot_pie[i]['uncollected']/1000000.0]],
					'label': i});
};

graph2 = Flotr.draw(container2, piedata,
	{
    HtmlText : false,
    grid : {
      verticalLines : false,
      horizontalLines : false
    },
    xaxis : { showLabels : false },
    yaxis : { showLabels : false },
    pie : {
      show : true, 
      //explode : 6
    },
    mouse : { track : false },
    legend : {
      position : 'se',
      backgroundColor : '#D2E8FF'
    }
  });
	
$('.flotr-grid-label-x').css('-webkit-transform', 'rotateY(45deg)');
				