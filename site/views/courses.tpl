% rebase('base.tpl', title='Find courses', script='network.js')
<h3 class="page-header"><i class="fa fa-search"></i> Find courses</h3>
<form>
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

  <div id="searchbox">
    <div class="panel panel-primary">
      <div class="panel-heading">
        <input type="search" class="form-control" placeholder="Search classes, departments, or instructors">
      </div>
    </div>
  </div>
</form>


<div id="results">
</div>