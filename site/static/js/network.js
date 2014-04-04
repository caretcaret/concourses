// helper functions
// appends array b to array a
// thanks http://stackoverflow.com/questions/1374126/how-to-append-an-array-to-an-existing-javascript-array
Array.prototype.extend = function(other) {
  other.forEach(function(v) { this.push(v)}, this);
}

// remove duplicates from ary with key function
// thanks http://stackoverflow.com/questions/9229645/remove-duplicates-from-javascript-array
function uniqBy(ary, key) {
  var seen = {};
  return ary.filter(function(elem) {
    var k = key(elem);
    return (seen[k] === 1) ? 0 : seen[k] = 1;
  });
}

function flattenReqTree(tree) {
  var t = [];
  for (var i = 1; i < tree.length; i++) { // skip op node
    if (typeof(tree[i]) === 'string') // don't use instanceof, some strings can be objects
      t.push(tree[i]);
    else if (tree[i] instanceof Array)
      t.extend(flattenReqTree(tree[i]));
  }
  return t;
}

function Network() {
  // svg
  var canvas;
  var svg;
  var width;
  var height;
  // data
  // stack of search results
  var searchHistory;
  // set of all course data
  var courses;
  // set of all req edges
  var reqs;
  // list of all shown course data
  var displayedCourses;
  // list of all shown req edges
  var displayedReqs;
  // <g> elements to hold the circles and lines of viz as a whole
  var coursesG;
  var reqsG;
  // arrowheads
  var markers;
  // mapping from number to course data object
  var num2course;
  // force layout
  var force;

  function network(svgNode, query, data) {
    // init everything
    canvas = svgNode;
    svg = d3.select(svgNode);
    options = {};
    resize();
    searchHistory = [];
    courses = [];
    reqs = [];
    // reqs before courses, so the course circle masks the line
    reqsG = svg.append('g').attr('id', 'reqs');
    coursesG = svg.append('g').attr('id', 'courses');
    num2course = {};
    // set up arrowhead shape
    svg.append('defs').selectAll('marker')
      .data(['prereq'])
    .enter().append('marker')
      .attr('id', function(d) { return d; })
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 15)
      .attr('refY', -1.5)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
    .append('path')
      .attr('d', 'M0,-5L10,0L0,5');
    // set up force
    /*force = cola.d3adaptor()
      .linkDistance(60)
      .size([width, height])
      .on('tick', ontick)
      //.constraints({axis: 'y', left: 0, right: 1, gap: 25})
      //.symmetricDiffLinkLengths()
      //.avoidOverlaps(true);*/
    
    force = d3.layout.force()
      .size([width, height])
      .on('tick', ontick)
      .charge(-120)
      .linkDistance(100);
     

    window.resize = network.resize;
    network.add(query, data);
    updateGraph();
  }
  // Updates the graph whenever the graph elements change.
  // assumes that options are set to the correct values, and
  // uses them to rebuild displayedCourses, displayedReqs, and the graph viz.
  function updateGraph() {
    // extract a list of all courses
    displayedCourses = [];
    for (var i = 0; i < searchHistory.length; i++) {
      var history = searchHistory[i];
      var query = history[0];
      var data = history[1];
      if (data.courses)
        displayedCourses.extend(data.courses);
    }
    // remove duplicates
    displayedCourses = uniqBy(displayedCourses, function(course) {
      return course.number;
    });

    // extract reqs
    displayedReqs = [];
    num2course = {};
    for (var i = 0; i < displayedCourses.length; i++) {
      var course = displayedCourses[i];
      // add course to mapping
      num2course[course.number] = course;
      var prereq = flattenReqTree(course.prerequisites)
        .map(function(req) {
          return {source: req, target: course.number, type: 'p'}
        });
      var coreq = flattenReqTree(course.corequisites)
        .map(function(req) {
          return {source: req, target: course.number, type: 'c'}
        });
      displayedReqs.extend(prereq);
      displayedReqs.extend(coreq);
    }
    // remove duplicates
    displayedReqs = uniqBy(displayedReqs, function(req) {
      return req.source + ',' + req.target + ',' + req.type;
    });
    // remove edges whose endpoints don't exist
    displayedReqs = displayedReqs.filter(function(d) {
      return !!num2course[d.source] && !!num2course[d.target];
    });
    // remap endpoint ids to node references
    displayedReqs.forEach(function(d) {
      d.sourceId = d.source;
      d.targetId = d.target;
      d.source = num2course[d.source];
      d.target = num2course[d.target];
    });

    // populate nodes and links
    var nodes = coursesG.selectAll('g.node')
      .data(displayedCourses, function(d) { return d.number; });
    var newNodes = nodes.enter().append('g').classed('node', true);
    newNodes.append('circle')
      .attr('cx', function(d) { return Math.random() * width; })
      .attr('cy', function(d) { return Math.random() * height; })
      .attr('r', 7.5)
      .style('fill', function(d) { return d3.hsl(Math.random() * 360, 0.5, 0.5).toString(); })
      .style('stroke', 'white')
      .style('stroke-width', 1.2)
      .call(force.drag);
    newNodes.append('text')
      .text(function(d) { return d.number; })
      .call(force.drag);
    nodes.exit()
      .remove();

    var edges = reqsG.selectAll('g.link')
      .data(displayedReqs, function(d) { return d.sourceId + ',' + d.targetId + ',' + d.type; });
    var newEdges = edges.enter().append('g').classed('link', true);
    newEdges.append('line')
      .attr('stroke', '#888')
      .attr('stroke-width', 1.2)
      .attr('stroke-opacity', 0.8)
      .attr('stroke-dasharray', function(d) {
        if (d.type === 'p')
          return 'none';
        return '3, 5';
      })
      .attr('marker-end', function(d) { return 'url(#prereq)'; });
    edges.exit().remove();

    force.nodes(displayedCourses);
    force.links(displayedReqs);

    force.start(10,15,20);
    window.onresize = network.onresize;
  }
  // adds data to the result stack and data cache.
  network.add = function(query, data) {
    if (!data)
      return;
    // save data
    searchHistory.push([query, data]);
    // TODO: cache displayed data
  }

  function ontick() {
    var courseNodeGs = coursesG.selectAll('g.node');
    var circles = courseNodeGs.selectAll('circle');
    circles.attr('cx', function(d) { return d.x; })
      .attr('cy', function(d) { return d.y; });
    var texts = courseNodeGs.selectAll('text')
      .attr('x', function(d) { return d.x; })
      .attr('y', function(d) { return d.y; })
      .attr('dx', '.8em')
      .attr('dy', '.4em');

    var reqLineGs = reqsG.selectAll('g.link');

    var lines = reqLineGs.selectAll('line');
    
    lines
      .attr('x1', function(d) { return d.source.x; })
      .attr('y1', function(d) { return d.source.y; })
      .attr('x2', function(d) { return d.target.x; })
      .attr('y2', function(d) { return d.target.y; });
  }

  function resize() {
    var rect = canvas.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
  }

  network.onresize = function() {
    resize();
    force.size([width, height]).start();
  }

  return network;
}

function dataLookup(query, callback) {
  console.log("Requested");
  console.log(query);
  d3.json('/data', function(data) {
    console.log("Received");
    console.log(data);
    callback(data);
  })
    .header('Content-Type', 'application/json')
    .post(JSON.stringify(query));
}

var viz = Network();
// the path in the url after courses/
var query = window.location.pathname.replace(/^\/\w+\/?/, '');

dataLookup({department: query}, function(data) {
  console.log("Initial query is " + query);
  viz(document.querySelector('#main svg'), query, data);
});
