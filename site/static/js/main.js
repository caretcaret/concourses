function Network() {
	var canvas;
	var width;
	var height;
	var allData = [];
	var curLinksData = [];
	var curNodesData = [];
	var linkedByIndex = {};
	/* nodes and links <g> (group) elements */
	var nodesG;
	var linksG;
	/* the <circle> and <line> elements */
	var node;
	var link;
	var force = d3.layout.force();

	/* initialize the network */
	function network(svg_node, data) {
		canvas = svg_node;
		curLinksData = data.links;
		curNodesData = data.nodes;
		console.log(curNodesData.length);
		nodesG = d3.select(svg_node).append('g').attr('id', 'nodes');
		linksG = d3.select(svg_node).append('g').attr('id', 'links');


		network.onresize();
		window.onresize = network.onresize;
		update();
		force.on('tick', ontick)
			.charge(-1)
			.linkDistance(1);
	}
	/* the updates to take when resume d3 force */
	function update() {
		force.nodes(curNodesData);
		updateNodes();
		force.start();
	}
	function updateNodes() {
		node = nodesG.selectAll('circle.node')
			.data(curNodesData, function(d) {
				return d.number;
			});
		node.enter().append('circle')
			.attr('class', 'node')
			.attr('cx', function(d) {
				return width * Math.random();
			})
			.attr('cy', function(d) {
				return height * Math.random();
			})
			.attr('r', 1)
			.style('fill', function (d) {
				// temporary color
				return d3.hsl(0, 0.5, 0.5).toString();
			});
	}
	function ontick() {
		node.attr('cx', function(d) { return d.x; })
			.attr('cy', function(d) { return d.y; });
	}
	/* resize handler */
	network.onresize = function() {
		var rect = canvas.getBoundingClientRect();
		width = rect.width;
		height = rect.height;
		force.size([width, height]).start();
	};

	return network;
}

var viz = Network();

d3.json("/static/data/graph.json", function(data) {
	viz(document.querySelector('#main svg'), data);
});