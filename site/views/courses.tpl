% rebase('base.tpl', title='Find courses', script='network.js', modal='course_detail.tpl')
<h3 class="page-header"><i class="fa fa-search"></i> Find courses</h3>
<form id="finder">
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
        <input type="search" class="form-control" placeholder="Search classes by number or name" id="searchinput">
      </div>
    </div>
  </div>
</form>


<div id="results">
</div>

<!-- Button trigger modal -->
<button class="btn btn-primary" data-toggle="modal" data-target="#modal">
  Launch demo modal
</button>
