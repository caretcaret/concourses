<!-- Modal -->
<div class="modal fade" id="modal" tabindex="-1" role="dialog">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal">&times;</button>
        <h4 class="modal-title" id="modalTitle"></h4>
      </div>
      <div class="modal-body" id="modalBody">
        <div class="well">
          <div class="row">
            <div class="col-sm-3">
              <div class="thumbnail">
                <h1 class="text-center">
                  <span id="modalMeasure1" class="text-success"></span> <small>%ile</small>
                </h1>
                <h4 class="text-center">Quality</h4>
              </div>
            </div>
            <div class="col-sm-3">
              <div class="thumbnail">
                <h1 class="text-center">
                  <span id="modalMeasure2" class="text-success"></span> <small>%ile</small>
                </h1>
                <h4 class="text-center">Enjoyability</h4>
              </div>
            </div>
            <div class="col-sm-3">
              <div class="thumbnail">
                <h1 class="text-center">
                  <span id="modalMeasure3" class="text-warning"></span> <small>%ile</small>
                </h1>
                <h4 class="text-center">Difficulty</h4>
              </div>
            </div>
            <div class="col-sm-3">
              <div class="thumbnail">
                <h1 class="text-center">
                  <span id="modalMeasure4" class="text-danger"></span> <small>hr/wk</small>
                </h1>
                <h4 class="text-center">Workload</h4>
              </div>
            </div>
          </div>
          <!--
          <div class="progress">
            <div class="progress-bar progress-bar-success" style="width: 90%" id="modalSpringBar">Spring</div>
            <div class="progress-bar progress-bar-info" style="width: 0%" id="modalSummerBar">Summer</div>
            <div class="progress-bar progress-bar-warning" style="width: 10%" id="modalFallBar">Fall</div>
          </div>
          -->
          <dl class="dl-horizontal">
            <dt>Prerequisites</dt>
            <dd id="modalPrereqs"></dd>
            <dt>Corequisites</dt>
            <dd class="muted" id="modalCoreqs"></dd>
            <dt>Crosslisted</dt>
            <dd id="modalXlisted"></dd>
          </dl>
        </div>

        <h4>Details</h4>
        <p id="modalDescription">
        <!--<a href="#"><span class="badge badge-default">#typetheory</span></a><a href="#"><span class="badge badge-default">#sml</span></a><a href="#"><span class="badge badge-default">#logic</span></a></p>-->
        <h4>Notes</h4>
        <p id="modalNotes"></p>
        <!--
        <h4>Schedule</h4>
        <p>Insert here</p>
        -->
      </div>
    </div>
  </div>
</div>