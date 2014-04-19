% rebase('base.tpl', title='Find courses', script='network.js', modal='course_detail.tpl')
<h3 class="page-header"><i class="fa fa-search"></i> Find courses</h3>

  <!--
  <div class="pull-left">
    <i class="fa fa-gear"></i> Options
  </div>
  <div class="pull-right">
    <label>Color by</label>
    <div class="btn-group btn-group-xs">
      <button type="button" class="btn btn-default">Random</button>
      <button type="button" class="btn btn-default">Semester</button>
      <button type="button" class="btn btn-default">Rating</button>
      <button type="button" class="btn btn-default">Department</button>
      <button type="button" class="btn btn-default">Course Level</button>
    </div>
  </div>

  <div class="clearfix"></div>
  -->

<div id="searchbox">
  <div class="panel panel-primary">
    <div class="panel-heading">
      <form id="finder">
        <input type="search" class="form-control" placeholder="Search classes by course number, name, or department number" id="searchinput">
      </form>
    </div>
    <div>
      <div id="search_help" class="collapse panel-body">
        <ul>
          <li>98</li>
          <li>15213</li>
          <li>non-majors</li>
          <li>photography &amp; 79</li>
          <li>materials, quantum physics</li>
          <li>98, 15213, non-majors, photography &amp; 79, materials, quantum physics</li>
        </ul>
      </div>
      <button data-toggle="collapse" data-target="#search_help" class="btn btn-link btn-xs btn-block dropdown-toggle">
        <small>example searches <span class="caret"></span></small>
      </button>
    </div>
  </div>
</div>



<div id="results">
</div>
