% rebase('base.tpl', title='Find courses', script='network.js')
<h3 class="page-header"><i class="fa fa-search"></i> Find courses</h3>
<form>
  <input type="search" class="form-control" placeholder="Search department and course names or numbers">
  
  <div class="pull-left">
    <label>Press enter to add courses.</label>
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
</form>
