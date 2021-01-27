//thegraph = document.getElementById("5cce2308-2fad-4ce0-822e-b782d421da0b");
thegraph = document.getElementsByClassName("plotly-graph-div js-plotly-plot")[0]
thegraph.on('plotly_selected', function(eventData){
console.log(eventData.range['x'])
}
);
