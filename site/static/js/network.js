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
  var courseTextsG;
  var reqsG;
  // arrowheads
  var markers;
  // mapping from number to course data object
  var num2course;
  // force layout
  var force;
  // results table
  var results;
  // search box
  var finder;
  // event handlers
  var zoom;
  var drag;

  function network(svgNode, query, data) {
    // init everything
    canvas = svgNode;
    zoom = d3.behavior.zoom()
      .scaleExtent([1, 1])
      .on('zoom', redraw);
    svg = d3.select(svgNode)
      .attr('pointer-events', 'all')
      .classed('network', true) // for move cursor
      .call(zoom);
    resize();
    options = {};
    resize();
    searchHistory = [];
    courses = [];
    reqs = [];
    displayedCourses = [];
    displayedReqs = [];
    // reqs before courses, so the course circle masks the line
    reqsG = svg.append('g').attr('id', 'reqs');
    coursesG = svg.append('g').attr('id', 'courses');
    courseTextsG = svg.append('g').attr('id', 'courseTexts');
    num2course = {};
    // set up arrowhead shape
    svg.append('defs').selectAll('marker')
      .data(['prereq'])
    .enter().append('marker')
      .attr('id', function(d) { return d; })
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 18)
      .attr('refY', 0)
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .attr('orient', 'auto')
    .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#888');
    // set up force
    force = cola.d3adaptor()
      .linkDistance(function(d) {
        if (d.type === 'x')
          return 20;
        return 70;
      })
      .size([width, height])
      .on('tick', ontick)
      //.handleDisconnected(false)
      .constraints({axis: 'y', left: 0, right: 0, gap: 0})
      //.symmetricDiffLinkLengths()
      //.avoidOverlaps(true);

    force.nodes(displayedCourses);
    force.links(displayedReqs);
    
    // set up tables
    results = d3.select('#results');

    // set up search
    finder = d3.select('#finder')
      .on('submit', onsearch);

    window.resize = network.resize;
    network.add(query, data);
    updateGraph();
  }

  // inserts course specific data into the popup modal
  function updateModal(course) {
    var modal = d3.select('#modal');

    // clear the schedule of old data
    modal.select('#modalSchedule').selectAll('div').remove();
    // fetch schedule data
    detailsLookup(course.number, function(data) {
      var instances = data.instances;
      // sort instances: fall->summer->spring, then descending years
      instances.sort(function(left, right) {
        var a = left.tag;
        var b = right.tag;
        var aYear = +a.substring(1);
        var bYear = +b.substring(1);
        if (aYear != bYear)
          return bYear - aYear; // show sessions in reverse order
        var semOrder = {'S': 1, 'M': 2, 'F': 3};
        return semOrder[b[0]] - semOrder[a[0]];
      });
      
      // insert schedule into modal; one ul per semester
      var semesters = modal.select('#modalSchedule').selectAll('div')
        .data(instances).enter().append('div');
      semesters.append('h4').append('small').text(function(d) { return d.session; });
      var semContainer = semesters.append('ul').classed('media-list', true).selectAll('li')
        .data(function(d) { return d.lectures; }).enter();
      // insert lectures per semester
      function populateMeetingInfo(parent) {
        var lectures = parent.append('li').classed('media', true);
        lectures.append('div').classed('pull-left', true)
          .append('h4').text(function(d) { return d.name; });
        // insert meetings per lecture
        var meetContainer = lectures.append('div').classed('media-body', true);
        var meetings = meetContainer.selectAll('div').data(function(d) { return d.meetings; }).enter().append('div');
        meetings.append('h4').classed('media-heading', true).text(function(d) {
          if (d.instructors.length > 0)
            return d.instructors.join('; ');
          return 'TBA';
        });
        meetings.append('p').html(function(d) {
          return d.days + ': ' +  d.begin + ' &mdash; ' + d.end + ' @ ' + d.room + ', ' + d.campus;
        });
        return meetContainer;
      }
      var meetContainer = populateMeetingInfo(semContainer);
      var recContainer = meetContainer.selectAll('ul')
        .data(function(d) { return d.recitations; }).enter()
        .append('ul').classed('media-list', true);
      var recitations = populateMeetingInfo(recContainer);
    });

    modal.select('#modalTitle').text(course.number + ' - ' + course.name + ' (' +  course.units + ' units' + ')');
    modal.select('#modalMeasure1') // quality
      .attr('class', '').text('--');
    modal.select('#modalMeasure2') // enjoyability
      .attr('class', '').text('--');
    modal.select('#modalMeasure3') // difficulty
      .attr('class', '').text('--');
    modal.select('#modalMeasure4') // workload
      .attr('class', '').text('--');

    // spring/fall split bar
    var totalAvailability = course.availability[0] + course.availability[1] + course.availability[2];
    modal.select('#modalSpringBar')
      .style('width', 100 * course.availability[0] / totalAvailability + '%');
    modal.select('#modalSummerBar')
      .style('width', 100 * course.availability[1] / totalAvailability + '%');
    modal.select('#modalFallBar')
      .style('width', 100 * course.availability[2] / totalAvailability + '%');

    // related courses
    modal.select('#modalPrereqs')
      .text(stringifyReqs(course.prerequisites));
    modal.select('#modalCoreqs')
      .text(stringifyReqs(course.corequisites));
    if (course.crosslisted.length > 0)
      modal.select('#modalXlisted')
        .text(course.crosslisted.join(', '));
    else
      modal.select('#modalXlisted')
        .text('None');

    // text
    if (course.description == 'None')
      modal.select('#modalDescription').text('No description');
    else
      modal.select('#modalDescription').html(course.description);
    modal.select('#modalNotes').html(course.notes || 'No notes');
  }


  // Updates the graph whenever the graph elements change.
  // assumes that options are set to the correct values, and
  // uses them to rebuild displayedCourses, displayedReqs, and the graph viz.
  function updateGraph() {
    // extract a list of all courses
    displayedCourses = [];
    displayedReqs = [];
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
    displayedCourses.forEach(function(d) {
      d.width = 60;
      d.height = 15;
    });

    // extract reqs
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
      var xlist = course.crosslisted
        .map(function(num) {
          return {source: num, target: course.number, type: 'x'}
        });
      displayedReqs.extend(prereq);
      displayedReqs.extend(coreq);
      displayedReqs.extend(xlist);
    }
    // remove duplicates
    displayedReqs = uniqBy(displayedReqs, function(req) {
      return req.source + ',' + req.target + ',' + req.type;
    });
    // remove edges whose endpoints don't exist or courses with themselves as prereqs
    // (I'm looking at you, 02654)
    displayedReqs = displayedReqs.filter(function(d) {
      return !!num2course[d.source] && !!num2course[d.target] && d.target != d.source;
    });
    // remap endpoint ids to node references
    displayedReqs.forEach(function(d) {
      d.sourceId = d.source;
      d.targetId = d.target;
      d.source = num2course[d.source];
      d.target = num2course[d.target];
    });

    // populate nodes and links
    var nodes = coursesG.selectAll('circle').data(displayedCourses, function(d) { return d.number; });
    nodes.enter().append('circle')
      .attr('r', 7.5)
      .style('fill', function(d) { return d3.hsl(Math.random() * 360, 0.5, 0.6).toString(); })
      .style('stroke', 'white')
      .style('stroke-width', 1.2)
      .call(force.drag)
      .on('mousedown', function() { d3.event.stopPropagation(); });
    var texts = courseTextsG.selectAll('text').data(displayedCourses, function(d) { return d.number; });
    texts.enter().append('text')
      .text(function(d) { return d.number; })
      .attr('dx', '.8em')
      .attr('dy', '.375em')
      .on('mousedown', function() { d3.event.stopPropagation(); })
      .on('mouseover', function(d1) {
        var me = d3.select(this);
        if (!me.classed('muted')) {
          me.text(d1.name).attr('font-weight', 'bold');
          courseTextsG.selectAll('text').classed('muted', function(d2) { return d1.number !== d2.number; });
        }
      })
      .on('mouseout', function(d) {
        var me = d3.select(this);
        if (!me.classed('muted')) {
          me.text(d.number).attr('font-weight', 'normal');
          courseTextsG.selectAll('text').classed('muted', false);
        }
      })
      .on('click', function(d) {
        updateModal(d);
        $('#modal').modal();
      });
    nodes.exit().remove();
    texts.exit().remove();

    var edges = reqsG.selectAll('g.link')
      .data(displayedReqs, function(d) { return d.sourceId + ',' + d.targetId + ',' + d.type; });
    var newEdges = edges.enter().append('g').classed('link', true);
    newEdges.append('line')
      .attr('stroke', '#666')
      .attr('stroke-width', 1.2)
      .attr('stroke-opacity', 0.8)
      .attr('stroke-dasharray', function(d) {
        if (d.type === 'c')
          return '3, 5';
        return null;
      })
      .attr('marker-end', function(d) {
        if (d.type === 'x')
          return null;
        return 'url(#prereq)';
      });
    edges.exit().remove();

    // populate tables
    var panels = results.selectAll('.panel')
      .data(searchHistory, function(d) { return d[0]; /* query */ });
    var newPanels = panels.enter().insert('div').attr('class', 'panel panel-primary');
    var newHeaders = newPanels.append('div')
      .attr('class', 'panel-heading');
    newHeaders.append('h3')
      .attr('class', 'pull-left panel-title')
      .text(function(d) { return d[0]; });
    newHeaders.append('button')
      .classed('close', true)
      .html('&times;')
      .on('click', function(d) {
        // remove from history
        for (var i = 0; i < searchHistory.length; i++) {
          if (searchHistory[i] === d) {
            searchHistory.splice(i, 1);
            break;
          }
        }
        replaceURL();
        updateGraph();
      });
    newHeaders.append('span')
      .attr('class', 'label label-primary')
      .text(function(d) {
        var len = d[1].courses.length;
        return len + (len == 1 ? ' course' : ' courses');
      });
    newHeaders.append('div').attr('class', 'clearfix');
    panels.exit().remove();

    var newTables = newPanels.append('table')
      .attr('class', 'table table-striped table-hover')
      .append('tbody');
    var newRows = newTables.selectAll('tr')
      .data(function(d) { return d[1].courses; /* course list */ })
      .enter()
      .append('tr');
    newRows.append('td').text(function(d) { return d.number; });
    newRows.append('td').append('a')
      .attr('href', '#')
      .text(function(d) { return d.name; })
      .attr('data-toggle', 'modal')
      .attr('data-target', '#modal')
      .on('click', function(d) {
        d3.event.preventDefault();
        updateModal(d);
      });
    newRows.append('td').text(function(d) { return d.units; })
      .style('text-align', 'center');
    force.nodes(displayedCourses);
    force.links(displayedReqs);

    force.start(10, 15, 20);
  }
  // adds data to the result stack and data cache.
  network.add = function(query, data) {
    if (!data || !query)
      return;
    // save data
    searchHistory.unshift([query, data]);
    // concat queries and set url
    replaceURL();
    // TODO: cache displayed data
  }

  function replaceURL() {
    var queries = uniqBy(searchHistory.map(function(h) { return h[0]; }), function(d) { return d; });
    var queries_str = queries.join(',');
    history.replaceState({}, '', '/courses/' + queries_str);
  }

  function ontick() {
    var circles = coursesG.selectAll('circle');
    circles.attr('cx', function(d) { return d.x; })
      .attr('cy', function(d) { return d.y; });
    var texts = courseTextsG.selectAll('text')
      .attr('x', function(d) { return d.x; })
      .attr('y', function(d) { return d.y; });

    var reqLineGs = reqsG.selectAll('g.link');

    var lines = reqLineGs.selectAll('line');
    
    lines
      .attr('x1', function(d) { return d.source.x; })
      .attr('y1', function(d) { return d.source.y; })
      .attr('x2', function(d) { return d.target.x; })
      .attr('y2', function(d) { return d.target.y; });
  }

  function onsearch() {
    d3.event.preventDefault();
    var searchNode = finder.select('#searchinput').node();
    var query = searchNode.value.trim();
    searchNode.value = '';

    // don't repeat the same query
    for (var i = 0; i < searchHistory.length; i++) {
      if (searchHistory[i][0] === query)
        return;
    }

    dataLookup(query, function(data) {
      network.add(query, data);
      updateGraph();
    });
  }

  function resize() {
    var rect = canvas.getBoundingClientRect();
    width = rect.width;
    height = rect.height;
  }

  // for zoom
  function redraw() {
    var transform = 'translate(' + d3.event.translate + ')';
    coursesG.attr('transform', transform);
    courseTextsG.attr('transform', transform);
    reqsG.attr('transform', transform);
  }

  network.onresize = function() {
    resize();
    force.size([width, height]).start();
  }

  return network;
}

function stringifyReqs(reqs, paren) {
  if (typeof paren === 'undefined')
    paren = false;
  if (typeof reqs === 'string')
    return reqs;

  if (reqs.length < 2)
    return 'None';

  var reqsClone = reqs.slice(0);
  var op = reqsClone.shift();

  if (paren) {
    var parenLeft = '(';
    var parenRight = ')';
  } else {
    var parenLeft = '';
    var parenRight = '';
  }
  return parenLeft + reqsClone.map(function(d) { return stringifyReqs(d, true); }).join(' ' + op + ' ') + parenRight;
}

function dataLookup(query, callback) {
  console.log("Requested");
  console.log(query);
  d3.json('/data')
    .header('Content-Type', 'application/json')
    .post(JSON.stringify(query), function(error, data) {
    console.log("Received");
    console.log(data);
    callback(data);
  });
}

function detailsLookup(query, callback) {
  console.log("Requested details");
  console.log(query);
  d3.json('/data/details')
    .header('Content-Type', 'application/json')
    .post(JSON.stringify(query), function(error, data) {
      console.log("Received");
      console.log(data);
      callback(data);
    });
}

var viz = Network();
// the path in the url after courses/
var query = decodeURIComponent(window.location.pathname.replace(/^\/\w+\/?/, ''));

dataLookup(query, function(data) {
  console.log("Initial query is " + query);
  viz(document.querySelector('#main svg'), query, data);
});
