 window.onload = function(){
    var selItem = sessionStorage.getItem("SelItem");

    // alert(selItem)
    // $('#client_sel').val(selItem);
  }

$(document).ready(function(){

  var days = 7;
  var date = new Date();
  var end_date = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  var start_date = new Date(date.getTime() - (days * 24 * 60 * 60 * 1000));

  setTimeout(location.reload.bind(location), 900000);

  // To select From/To in protocols search user
  $(function(){
    $('#from_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
    });
    $('#to_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
    });
    $('#from_date').datepicker('setDate', start_date);
    $('#to_date').datepicker('setDate', end_date);
  });
  // To select From/To in protocols search admin
  $(function(){
    $('#ad_from_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
    });
    $('#ad_to_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
    });
    $('#ad_from_date').datepicker('setDate', start_date);
    $('#ad_to_date').datepicker('setDate', end_date);
  });
  // To select From/To in activity log user
  $(function(){
    $('#acvt_from_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
      'defaultViewDate' : 'today',
    });
    $('#acvt_to_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
    });
    $('#acvt_from_date').datepicker('setDate', start_date);
    $('#acvt_to_date').datepicker('setDate', end_date);
  });
  // To select From/To in audit log user
  $(function(){
    $('#audt_from_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
      'defaultViewDate' : 'today',
    });
    $('#audt_to_date').datepicker({
      'format':'dd/mm/yyyy',
      'autoclose':true,
      'endDate': 'today',
      'todayHighlight' : true,
      'defaultViewDate' : 'today',
    });
    $('#audt_from_date').datepicker('setDate', start_date);
    $('#audt_to_date').datepicker('setDate', end_date);
  });
  // To handle onchange event in search protocol filterby
  $(document).on('change', '#filter_by', function(){
    var selected_val = $(this).val();
    $('#filter_element_label').css('color','black');

    if(selected_val == ''){

      $('#filter_element_label').text('Choose');
      $('select[name=filter_element]').empty();
      $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------')
        );

    }else if(selected_val == 'project'){

      $('#filter_element_label').text('Project');
      $.ajax({
        url : '/filter_project_names_info',
        success : function(data){
          $('select[name=filter_element]').empty();
          $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
          $.each(data, function(index, obj){
            $('select[name=filter_element]').append(
              $('<option></option>').val(obj.project__id).html(obj.project__project_name)
              );
          });
        }
      });

    }else if(selected_val == 'protocol_id'){

      $('#filter_element_label').text('Protocol ID');
      $.ajax({
        url : '/filter_project_names_info',
        success : function(data){
          $('select[name=filter_element]').empty();
          $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
          $.each(data, function(index, obj){
            $('select[name=filter_element]').append(
              $('<option></option>').val(obj.project__id).html(obj.project__protocol_id)
              );
          });
        }
      });

    }else if(selected_val == 'client'){

      $('#filter_element_label').text('Client');
      $.ajax({
        url : '/get_client_info',
        success : function(data){
          $('select[name=filter_element]').empty();
          $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
          $.each(data, function(index, obj){
            $('select[name=filter_element]').append(
              $('<option></option>').val(obj.id).html(obj.client_name)
              );
          });
        }
      });

    }else if(selected_val == 'therapeutic_area'){

      $('#filter_element_label').text('Therapeutic Area');
      $.ajax({
        url : '/get_therapeutic_area_info',
        success : function(data){
          $('select[name=filter_element]').empty();
          $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
          $.each(data, function(index, obj){
            $('select[name=filter_element]').append(
              $('<option></option>').val(obj.id).html(obj.therapeutic_area)
              );
          });
        }
      });

    }else if(selected_val == 'phase'){

      $('#filter_element_label').text('Phase');
      $('select[name=filter_element]').empty();
      $('select[name=filter_element]').append(
        $('<option></option>').val('').html('---------'),
        $('<option></option>').val('1').html('1'),
        $('<option></option>').val('2').html('2'),
        $('<option></option>').val('3').html('3'),
        $('<option></option>').val('4').html('4'),
        $('<option></option>').val('Observational').html('Observational')
        );

    }

  });

  // To handle onchange event in search protocol filterby admin
  $(document).on('change', '#ad_filter_by', function(){
    var selected_val = $(this).val();

    $('#ad_filter_element_label').css('color','black');

    if(selected_val == ''){

      $('#ad_filter_element_label').text('Choose');
      $('select[name=ad_filter_element]').empty();
      $('select[name=ad_filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
    }else if(selected_val == 'client'){

      $('#ad_filter_element_label').text('Client');
      $.ajax({
        url : '/get_client_info',
        success : function(data){
          $('select[name=ad_filter_element]').empty();
          $('select[name=ad_filter_element]').append(
        $('<option></option>').val('').html('---------')
        );
          $.each(data, function(index, obj){
            $('select[name=ad_filter_element]').append(
              $('<option></option>').val(obj.id).html(obj.client_name)
              );
          });
        }
      });

    }

  });

  $(document).on('change', '#filter_element', function(){
    $('#filter_element_label').css('color','black');

  });

  $(document).on('change', '#ad_filter_element', function(){
    $('#ad_filter_element_label').css('color','black');

  });

  // to handle/filter the elements when user clicked on filter button
  $('#filter_btn').on('click', function(){

    var filter_by = $('#filter_by').val();
    var filter_element = $('#filter_element').val();
    var from_date = $('#from_date').val();
    var to_date = $('#to_date').val();

    if (filter_by != '' && filter_element == ''){
      $('#filter_element_label').css('color','red');
    }else{
      $('#filter_element_label').css('color','black');
    }

    if (from_date != '' && to_date == ''){
      $('#to_date_label').css('color','red');
    }else{
      $('#to_date_label').css('color','black');
    }

    if (from_date == '' && to_date != ''){
      $('#from_date_label').css('color','red');
    }else{
      $('#from_date_label').css('color','black');
    }

    if (from_date == '' && to_date == '' && filter_by == '' && filter_element == ''){
      $('#from_date_label').css('color','red');
      $('#to_date_label').css('color','red');
    }


    if (from_date != '' && to_date != '' && filter_by == '' && filter_element == ''){

      var date_obj = [from_date, to_date]
      
      $.ajax({
        url : '/filter_protocol_user_date/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(date_obj),
        success : function(data){
          $('#user_protocol_partial').html(data.html_form);

          $('#protocol_tbl').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });
        }

      });

    }else if(filter_by != '' && filter_element != '' && from_date == '' && to_date == ''){

      var filter_obj = [filter_by, filter_element]

      $.ajax({
        url : '/filter_protocol_user_filterobj/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filter_obj),
        success : function(data){
          $('#user_protocol_partial').html(data.html_form);

          $('#protocol_tbl').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });

        }
      });

    }else if(filter_by != '' && filter_element != '' && from_date != '' && to_date != ''){
      
      var filterdate_obj = [from_date, to_date, filter_by, filter_element]

      $.ajax({
        url : '/filter_protocol_user_filterdateobj/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filterdate_obj),
        success : function(data){
          $('#user_protocol_partial').html(data.html_form);

          $('#protocol_tbl').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });

        }
      });

    }

  });

  // to handle/filter the elements when user clicked on filter button admin
  $('#ad_filter_btn').on('click', function(){

    var filter_by = $('#ad_filter_by').val();
    var filter_element = $('#ad_filter_element').val();
    var from_date = $('#ad_from_date').val();
    var to_date = $('#ad_to_date').val();

    if (filter_by != '' && filter_element == ''){
      $('#ad_filter_element_label').css('color','red');
    }else{
      $('#ad_filter_element_label').css('color','black');
    }

    if (from_date != '' && to_date == ''){
      $('#ad_to_date_label').css('color','red');
    }else{
      $('#ad_to_date_label').css('color','black');
    }

    if (from_date == '' && to_date != ''){
      $('#ad_from_date_label').css('color','red');
    }else{
      $('#ad_from_date_label').css('color','black');
    }

    if (from_date == '' && to_date == '' && filter_by == '' && filter_element == ''){
      $('#ad_from_date_label').css('color','red');
      $('#ad_to_date_label').css('color','red');
    }

    if (from_date != '' && to_date != '' && filter_by == '' && filter_element == ''){

      var date_obj = [from_date, to_date]
      
      $.ajax({
        url : '/filter_protocol_admin_date/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(date_obj),
        success : function(data){
          $('#admin_protocol_partial').html(data.html_form);
            $('#ad_protocol_tbl').DataTable({

              searching : true,
              "ordering": true,
              columnDefs: [{
                orderable: false,
                targets: "no-sort"
              }]

            });
        }

      });

    }else if(filter_by != '' && filter_element != '' && from_date == '' && to_date == ''){

      var filter_obj = [filter_by, filter_element]

      $.ajax({
        url : '/filter_protocol_admin_filterobj/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filter_obj),
        success : function(data){
          $('#admin_protocol_partial').html(data.html_form);

            $('#ad_protocol_tbl').DataTable({

              searching : true,
              "ordering": true,
              columnDefs: [{
                orderable: false,
                targets: "no-sort"
              }]

            });
        }
      });

    }else if(filter_by != '' && filter_element != '' && from_date != '' && to_date != ''){
      
      var filterdate_obj = [from_date, to_date, filter_by, filter_element]

      $.ajax({
        url : '/filter_protocol_admin_filterdateobj/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filterdate_obj),
        success : function(data){
          $('#admin_protocol_partial').html(data.html_form);

            $('#ad_protocol_tbl').DataTable({

              searching : true,
              "ordering": true,
              columnDefs: [{
                orderable: false,
                targets: "no-sort"
              }]

            });
        }
      });

    }

  });


  $.fn.dataTable.moment('DD/MM/YYYY HH:mm');


  // $("input[type='checkbox']").change(function() {
    $(document).on('change', '.user_inactive', function(){
    if(this.checked) {
        $.ajax({

        url   : '/get_all_active_users_details',
        type  : "get",
        dataType : "json",
       
        success   : function(data){

          $('.admin_users_div').html(data.html_form);

          $('#admin_users').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });
        
        }
    });      
    }
    else{

      $.ajax({

        url   : '/get_all_act_inact_users_details',
        type  : "get",
        dataType : "json",
       
        success   : function(data){

          $('.admin_users_div').html(data.html_form);

          $('#admin_users').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });
        
        }
    });    
    }
  });

  $(document).on('change', '.client_inactive', function(){
    if(this.checked) {
        $.ajax({

        url   : '/get_all_active_client_details',
        type  : "get",
        dataType : "json",
       
        success   : function(data){

          $('.admin_clients_div').html(data.html_form);

          $('#admin_clients').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });
        
        }
    });      
    }
    else{

      $.ajax({

        url   : '/get_all_act_inact_client_details',
        type  : "get",
        dataType : "json",
       
        success   : function(data){

          $('.admin_clients_div').html(data.html_form);

          $('#admin_clients').DataTable({

            searching : true,
            "ordering": true,
            columnDefs: [{
              orderable: false,
              targets: "no-sort"
            }]

          });
        
        }
    });    
    }
  });

  $(document).on('shown.bs.modal', '#create_project_modal', function () {
  $('.chosen', this).chosen('destroy').chosen();
  });

  $(document).on('shown.bs.modal', '#modal-update-project', function () {
  $('.chosen', this).chosen('destroy').chosen();
  });
  

  $('#audit_logs').DataTable({

    searching : false,
    "ordering": false,
    "pageLength": 25,
    "order" : [[ 4, "desc" ]],
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });
  $('#activity_log').DataTable({

    searching : false,
    "ordering": false,
    "pageLength": 25,
    "order" : [[ 4, "desc" ]],
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });
  $('#email_logs').DataTable({

    searching : true,
    "ordering": true,
    "order" : [[ 4, "desc" ]],
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });
  $('#admin_users').DataTable({

    searching : true,
    "ordering": true,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });

  $('#admin_clients').DataTable({

    searching : true,
    "ordering": true,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });

  $('#admin_projects_tbl').DataTable({

    searching : true,
    "ordering": true,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });

  $('#user_projects_tbl').DataTable({

    searching : true,
    "ordering": true,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });
  $('#protocol_tbl').DataTable({

    searching : true,
    "ordering": true,
    "pageLength": 25,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });

  $('#ad_protocol_tbl').DataTable({

    searching : true,
    "ordering": true,
    "pageLength": 25,
    columnDefs: [{
      orderable: false,
      targets: "no-sort"
    }]

  });

  // to handle popping messages
  $('#error-message').delay(6000).fadeOut();

  // to get the file name in upload field
  $(document).on('change', 'input[type=file]', function(event){

    $('#dispaly_f_name').html(event.target.files[0].name);

  });

  $(document).on('click', '#disabled_upload_csr_header', function(){
      // alert("Please add a client to upload CSR.");
      $('#pop_upload_csr_modal').modal({show : true, backdrop : 'static', keyboard : false});
  });

  $(document).on('click', '#disabled-edit-custome-csr-btn', function(){
      alert("You need to upload Custom CSR to edit mapping!");
  });

  $(document).on('click', '#disabled-map-csr-admin-btn', function(){
      alert("Please upload CSR, Protocol & SAR.");
  });

  $(document).on('click', '#user_create_form_disabled', function(){
      alert("Sorry! Email Configurations Not Set!");
  });

   $(document).on('click', '#disabled-clr-config-admin-btn', function(){
      alert("No Configurations found!");
  });



  // $(document).on('click', '#enabled-map-csr-admin-btn', function(){

  //   $('#ajax_loader').show();

  //     $.ajax({

  //       url : $(this).attr('data-href'),
  //       type : "get",
        
  //       success : function(data){

  //         $('.container').html(data.html_form)
          
  //       }

  //     });

      
  // });
  

  // loads signup form into the user create modal
  $('#user_create_form').click(function(){

    // $('#ajax_loader').show();

    $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#create_user_modal').modal({show : true, backdrop : 'static', keyboard : false});

        },
        success   : function(data){

          $('#create_user_modal .modal-content').html(data.html_form);
          // $('#ajax_loader').hide();
        }
    });      
  });

  $('#create_user_modal').on('submit', '.create_user_form', function(){

      var form = $(this);
      // $('#spin_loader').show();
      $('#ajax_loader').show();
      
      $.ajax({

          url : form.attr('data-url'),
          data : form.serialize(),
          type : form.attr('method'),
          dataType : 'json',       
          success : function(data){

              // $('#spin_loader').hide();
              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  if(data.mail_status){
                    
                    $('#create_user_modal').modal('hide');
                    location.reload();
                  }else{

                    $('#create_user_modal').modal('hide');
                    location.reload();
                  }
                  

              }else{
                 $('#create_user_modal .modal-content').html(data.html_form);
              }
          }
          
      });
      return false;
  });

  // to handle create project form
  $('#project_create_form').click(function(){

    // $('#ajax_loader').show();

    $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#create_project_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#create_project_modal .modal-content').html(data.html_form);
          // $('#ajax_loader').hide();
        }
    });      
  });

  $('#create_project_modal').on('submit', '.create_project_form', function(){

      var form = $(this);

      $('#ajax_loader').show();

      $.ajax({

          url : form.attr('data-url'),
          data : form.serialize(),
          type : form.attr('method'),
          dataType : 'json',
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#create_project_modal').modal('hide');
                  location.reload();

              }else{
                 $('#create_project_modal .modal-content').html(data.html_form);
                 $("select[name=therapeutic_area]").chosen('destroy').chosen();
              }
          }
      });
      return false;
  });

  var assign_project_form_original_data = '';

  // to handle project assigning
  $(document).on('click', '.project_assigning', function(){

    // var ik = $(this).attr('data-target');

    // $('#ajax_loader').show();
    
    $.ajax({

        url : $(this).attr("data-href"),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $("#assign_project_modal").modal({show : true, backdrop : 'static', keyboard : false});
        },

        success   : function(data){

          $('#assign_project_modal .modal-content').html(data.html_form);
          assign_project_form_original_data = $('.assign_project_form').serialize();
          // $('#ajax_loader').hide();
        }
    });      
  });

  var check_user_form_change_func = function(){
    var sel_val = $('input[name="check_user"]:checked').map(function() {return this.value;}).get().join(',')

    if ($(".assign_project_form").serialize() != assign_project_form_original_data && sel_val != '') {
       $('.assign_project_form .assin_pro_submit').removeAttr("disabled");
    }else{
      $('.assign_project_form .assin_pro_submit').prop("disabled", true);
    }
  };

  $(document).on('click', 'input[name="check_user"]', function(e){
    check_user_form_change_func();
    
  });

  $(document).on('click', '#assign_resetbtn', function(e){
    $(".assign_project_form")[0].reset();
    check_user_form_change_func();
  });


  $(document).on('submit', '.assign_project_form', function(){

      var form = $(this);

      var sel_val = $('input[name="check_user"]:checked').map(function() {return this.value;}).get().join(',')

      if (sel_val != ''){

        $('#ajax_loader').show();

        $.ajax({

            url : form.attr('data-url'),
            data : form.serialize(),
            type : form.attr('method'),
            dataType : 'json',
            success : function(data){

                $('#ajax_loader').hide();

                if(data.form_is_valid){

                    $('.assign_project_modal').modal('hide');
                    location.reload();

                }else{

                   $('.assign_project_modal .modal-content').html(data.html_form);
                   $('.assign_project_modal .assin_at_least').show();

                }
            }
        });}
      else{
        $('.assin_at_least').show();
      }
      return false;
  });

  var update_project_form_original_data = '';

  // to handle edit project
  $('#id_user_projects').on('click', '.update-project', function(){

        var btn = $(this);

        // $('#ajax_loader').show();

        $.ajax({

            url : btn.attr('data-url'),
            type : 'get',
            dataType : 'json',
            beforeSend : function() {
              $('#modal-update-project').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success : function(data) {
              $('#modal-update-project .modal-content').html(data.html_form);
              update_project_form_original_data = $('.edit_project_form').serialize();
              // $('#ajax_loader').hide();
            }


        });
  });

  var edit_project_form_func = function(){

    if ($(".edit_project_form").serialize() != update_project_form_original_data) {
         $('#update_project_subtn').removeAttr("disabled");
      }else{
        $('#update_project_subtn').prop("disabled", true);
      }
  }

  $('#modal-update-project').on('keyup change', '.edit_project_form', function(){
    edit_project_form_func()
  });

  $(document).on('click', '#edit_project_resetbtn', function(e){
    $(".edit_project_form")[0].reset() 
    edit_project_form_func();
  });

  $('#modal-update-project').on('submit', '.edit_project_form', function() {

    var form = $(this);

    $('#ajax_loader').show();

    $.ajax({
      url : form.attr('data-url'),
      data : form.serialize(),
      type : form.attr('method'),
      dataType : 'json',
      success : function(data){

          $('#ajax_loader').hide();

          if(data.form_is_valid) {
              // alert('Project has been Updated');
              $('#modal-update-project').modal('hide');
              location.reload();
          }
          else {
            $('#modal-update-project .modal-content').html(data.html_form);
            $("select[name=therapeutic_area]").chosen('destroy').chosen();
          }
      }
    });
    return false;
  });

    // to handle share document
  $('.share-doc').on('click', function(){

    $.ajax({

        url : $(this).attr('data-url'),
        type : 'get',
        dataType : 'json',
        beforeSend : function() {
          $('#share_doc_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success : function(data) {
          $('#share_doc_modal .modal-content').html(data.html_form);
        }


    });
  });

  $('.share_doc_modal').on('submit', '.share_doc_form', function(){

      var form = $(this);

      $('#ajax_loader').show();

      $.ajax({

          url : form.attr('data-url'),
          data : form.serialize(),
          type : form.attr('method'),
          dataType : 'json',
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('.share_doc_modal').modal('hide');
                  location.reload();

              }else{

                 $('.share_doc_modal .modal-content').html(data.html_form);

              }
          }
      });
      return false;
  });

  // to handle change password
  $('#change_password_link').click(function(){

    // $('#ajax_loader').show();
    $('.submenu').hide();
    
    $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#change_password_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#change_password_modal .modal-content').html(data.html_form);

          // $('#ajax_loader').hide();
        }
    });      
  });

  $('#change_password_modal').on('submit', '.change_password_form', function(){

      var form = $(this);
      // $('#spin_loader').show();

      $.ajax({

          url : form.attr('data-url'),
          data : form.serialize(),
          type : form.attr('method'),
          dataType : 'json',
          success : function(data){

              // $('#spin_loader').hide();

              if(data.form_is_valid){

                  $('#change_password_modal').modal('hide');
                  location.reload();

              }else{
                 $('#change_password_modal .modal-content').html(data.html_form);
                 if(data.old_pass){
                  $('#error_reason').html("New password should not match with old password.");
                 }
                 
              }
          }
      });
      return false;
  });

  // To handle csr admin upload
  $('#upload_csr_admin_form').click(function(){

    var is_Exist = $('#csr_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new Template will erase already mapped Configurations! Click on OK to continue.")
      if (r == true){
      
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_csr_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_csr_admin_modal .modal-content').html(data.html_form);
          
            }
        });
        }else{
          return false;
        }

    }else{

      $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_csr_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_csr_admin_modal .modal-content').html(data.html_form);
          
            }
        });

    }

      
  });


  $('#upload_csr_admin_modal').on('submit', '.admin_upload_csr_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#upload_csr_admin_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_csr_admin_modal .modal-content').html(data.html_form);
                 if (data.file_data_format != ''){
                    $('#upload_csr_admin_modal .modal-content #error_format').html('Document contains wrong formating at section "'+data.file_data_format+'"');
                 }
              }
          }
      });
      return false;
  });
  // To handle admin protocol upload
  $('#upload_protocol_admin_form').click(function(){

    var is_Exist = $('#protocol_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new Protocol will effect already mapped Configurations! Click on OK to continue.")
      if (r == true){
    
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_protocol_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_protocol_admin_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_protocol_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_protocol_admin_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
    }   
  });

  $('#upload_protocol_admin_modal').on('submit', '.admin_upload_protocol_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#upload_protocol_admin_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_protocol_admin_modal .modal-content').html(data.html_form);
                 if (data.file_data_format != ''){
                    $('#upload_protocol_admin_modal .modal-content #error_format').html('Document contains wrong formating at section "'+data.file_data_format+'"');
                 }
              }
          }
      });
      return false;
  });

  // To handle admin sar upload
  $('#upload_sar_admin_form').click(function(){

    // $('#ajax_loader').show();
    var is_Exist = $('#sar_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new SAR will effect already mapped Configurations! Click on OK to continue.")
      if (r == true){
    
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_sar_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_sar_admin_modal .modal-content').html(data.html_form);

              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#upload_sar_admin_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#upload_sar_admin_modal .modal-content').html(data.html_form);

          // $('#ajax_loader').hide();
        }
    });
    }     
  });

  $('#upload_sar_admin_modal').on('submit', '.admin_upload_sar_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#upload_sar_admin_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_sar_admin_modal .modal-content').html(data.html_form);
              }
          }
      });
      return false;
  });

  // to change the copy headings by changing source in admin csr mapping
  $(document).on('change', '.source_file_select',  function(){

      var a = $(this).attr('data-target');
      var v = $(this).val();
      var protocol_headings_list = JSON.parse($('#protocol_headings_list').val());   
      var sar_headings_list      = JSON.parse($('#sar_headings_list').val());

      var opt_html = '<option value="">---------</option>';
      
      if(v == 'Protocol')
      {

        $.each(protocol_headings_list, function(key,value){

          opt_html += "<option value='"+ value +"'>"+ value +"</option>";

        });

        $(a).html(opt_html);

      }
      else if(v == 'SAR')
      {
      
        $.each(sar_headings_list, function(key,value){

          opt_html += "<option value='"+ value +"'>"+ value +"</option>";

        });

        $(a).html(opt_html);

      }
      else
      {
        $(a).html('<option value="">-----</option>');
      }
  });

  // to add record in admin csr mapping
  $(document).on('click', '.add_record', function(){

    var no_of_records = $('#records_length').val();

    var proto_head = parseInt($('#protocol_headings_length').val());

    var sar_head = parseInt($('#sar_headings_length').val());

    // alert(no_of_records);

    var no_of_records_update = parseInt(no_of_records) + 1;

    var a = $(this).attr('data-target');

    var b = $(a).find('.csr_heading').val();

    // var c = $(a).find('.parent_id').val();

    var src = $(a).find('.source_file_select').val();

    var src_hd = $(a).find('.source_file_headings').val();

    if(src != '' && src_hd != ''){

        $('#ajax_loader').show();

        html = '';

        html += '<tr class="no-brd" id="record-'+ no_of_records_update +'">';

        html += '<td><input type="hidden" class="child_parent_id" name="child_parent_id[]" value="' + b + '"><input class="form-control csr_heading" hidden type="text" readonly value="'+ b +'" id="csr-heading-'+ no_of_records_update +'" name="csr_headings[]"></td>'

        html += '<td><select class="form-control source_file_select" required data-target="#copy-heading-'+ no_of_records_update +'" name="source[]" id="source-'+ no_of_records_update +'"><option value="">Source</option>';

        if(proto_head > 0 && sar_head > 0){

          html += '<option value="Protocol">Protocol</option><option value="SAR">SAR</option>';

        }else{

          if(proto_head > 0){

            html += '<option value="Protocol">Protocol</option>';

          }else if(sar_head > 0){

            html += '<option value="SAR">SAR</option>';
          }
        }

        html += '</select></td>';

        html += '<td><select class="form-control source_file_headings" required id="copy-heading-'+ no_of_records_update +'" name="copy_headings[]"><option value="">------</option></select></td>';

        html += '<td><input type="button" class="remove_record" value="" ></td></tr>';

        $(html).insertAfter($(this).closest('tr'));

        $('#records_length').val(no_of_records_update);

        $('#ajax_loader').hide();

    }
    else{
      alert('Please Map '+ b +' to add more ...');
    }

  });

  // to add record in admin csr mapping if already pre mapped
  $(document).on('click', '.add_record_prem', function(){
       
    var no_of_records = $('#records_length').val();

    var proto_head = parseInt($('#protocol_headings_length').val());

    var sar_head = parseInt($('#sar_headings_length').val());

    var no_of_records_update = parseInt(no_of_records) + 1;

    var a = $(this).attr('data-target');

    var b = $(a).find('.csr_heading').val();

    var c = $(a).find('.parent_id').val();

    var src = $(a).find('.source_file_select').val();

    var src_hd = $(a).find('.source_file_headings').val();

    if(src != '' && src_hd != ''){

      $('#ajax_loader').show();

          html = '';

          html += '<tr class="no-brd" id="record-'+ no_of_records_update +'">';

          html += '<td><input type="hidden" class="child_parent_id" name="child_parent_id[]" value="' + c + '"><input class="form-control csr_heading" hidden type="text" readonly value="'+ b +'" id="csr-heading-'+ no_of_records_update +'" name="csr_headings[]"></td>';

          html += '<td><select class="form-control source_file_select" required data-target="#copy-heading-'+ no_of_records_update +'" name="source[]" id="source-'+ no_of_records_update +'"><option value="">Source</option>';

          if(proto_head > 0 && sar_head > 0){

            html += '<option value="Protocol">Protocol</option><option value="SAR">SAR</option>';
      
          }else{

            if(proto_head > 0){

              html += '<option value="Protocol">Protocol</option>';

            }else if(sar_head > 0){

              html += '<option value="SAR">SAR</option>';
            }
          }

          html += '</select></td>';

          html += '<td><select class="form-control source_file_headings" required id="copy-heading-'+ no_of_records_update +'" name="copy_headings[]"><option value="">------</option></select></td>';

          html += '<td><input type="button" class="remove_record" value="" ></td></tr>';

          $(html).insertAfter(a);

          $('#records_length').val(no_of_records_update);

          $('#ajax_loader').hide();
    }
    else{
      alert('Please Map '+ b +' to add more ...');
    }

  });

  // to remove record in admin csr mapping
  $(document).on('click', '.remove_record', function(){

    var no_of_records = $('#records_length').val();

    // alert(no_of_records);

    var no_of_records_update = parseInt(no_of_records) - 1;

    $(this).closest('tr').remove();

    $('#records_length').val(no_of_records_update);

  });

   // To handle csr user upload
  $('#upload_csr_form').click(function(){

    var is_Exist = $('#custom_csr_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new Template will erase already mapped Configurations! Click on OK to continue.")
      if (r == true){
    
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_csr_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_csr_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#upload_csr_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#upload_csr_modal .modal-content').html(data.html_form);
          // $('#ajax_loader').hide();
        }
    });
    }     
  });

  $('#upload_csr_modal').on('submit', '.upload_csr_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  // alert('File uploaded succesfully');
                  $('#upload_csr_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_csr_modal .modal-content').html(data.html_form);
                 if (data.file_data_format != ''){
                    $('#upload_csr_modal .modal-content #error_format').html('Document contains wrong formating at section "'+data.file_data_format+'"');
                 }
              }
          }
      });
      return false;
  });

  // To handle user protocol upload
  $('#upload_protocol_form').click(function(){
    
    var is_Exist = $('#usr_protocol_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new Protocol will effect already mapped Configurations! Click on OK to continue.")
      if (r == true){

        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_protocol_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_protocol_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#upload_protocol_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#upload_protocol_modal .modal-content').html(data.html_form);
        }
    });
    }   
  });

  $('#upload_protocol_modal').on('submit', '.upload_protocol_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  // alert('File uploaded succesfully');
                  $('#upload_protocol_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_protocol_modal .modal-content').html(data.html_form);
                 if (data.file_data_format != ''){
                    $('#upload_protocol_modal .modal-content #error_format').html('Document contains wrong formating at section "'+data.file_data_format+'"');
                 }
              }
          }
      });
      return false;
  });

  // To handle user sar upload
  $('#upload_sar_form').click(function(){

    var is_Exist = $('#usr_sar_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new SAR will effect already mapped Configurations! Click on OK to continue.")
      if (r == true){
    
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_sar_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_sar_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#upload_sar_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#upload_sar_modal .modal-content').html(data.html_form);
          // $('#ajax_loader').hide();
        }
    });
    }    
  });

  $('#upload_sar_modal').on('submit', '.upload_sar_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache : false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  // alert('File uploaded succesfully');
                  $('#upload_sar_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_sar_modal .modal-content').html(data.html_form);
              }
          }
      });
      return false;
  });

  // To handle user another document upload
  $('#upload_another_doc_usr_form').click(function(){

    var is_Exist = $('#usr_another_doc_exist_or_not').val();

    if(is_Exist == '1'){

      var r = confirm("Uploading new document will effect already mapped Configurations! Click on OK to continue.")
      if (r == true){
    
        $.ajax({

            url   : $(this).attr('data-href'),
            type  : "get",
            dataType : "json",
            beforeSend : function(){

              $('#upload_another_doc_usr_modal').modal({show : true, backdrop : 'static', keyboard : false});
            },
            success   : function(data){

              $('#upload_another_doc_usr_modal .modal-content').html(data.html_form);
              // $('#ajax_loader').hide();
            }
        });
      }else{
        return false;
      }
    }else{
      $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){

          $('#upload_another_doc_usr_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#upload_another_doc_usr_modal .modal-content').html(data.html_form);
          // $('#ajax_loader').hide();
        }
    });
    }    
  });

  $('#upload_another_doc_usr_modal').on('submit', '.upload_another_doc_usr_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache : false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  // alert('File uploaded succesfully');
                  $('#upload_another_doc_usr_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_another_doc_usr_modal .modal-content').html(data.html_form);
                 if (data.file_data_format != ''){
                    $('#upload_another_doc_usr_modal .modal-content #error_format').html('Document contains wrong formating at section "'+data.file_data_format+'"');
                 }
              }
          }
      });
      return false;
  });

  // To handle user protocol upload
  $('#upload_finalcsr_form').click(function(){
    
    $.ajax({

      url   : $(this).attr('data-href'),
      type  : "get",
      dataType : "json",
      beforeSend : function(){

        $('#upload_finalcsr_modal').modal({show : true, backdrop : 'static', keyboard : false});
      },
      success   : function(data){

        $('#upload_finalcsr_modal .modal-content').html(data.html_form);
      }
    });
  });

  $('#upload_finalcsr_modal').on('submit', '.upload_finalcsr_form', function(){

      $('#ajax_loader').show();

      var form = $(this);
      var formData = new FormData(this);

      $.ajax({

          url : form.attr('data-url'),
          data : formData,
          type : form.attr('method'),
          cache: false,
          processData: false,
          contentType: false,
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#upload_finalcsr_modal').modal('hide');
                  location.reload();

              }else{
                 $('#upload_finalcsr_modal .modal-content').html(data.html_form);
                 
              }
          }
      });
      return false;
  });

  // to change the copy headings by changing source in user csr mapping
  $(document).on('change', '.source_file_select_usr',  function(){
      
      
      var proj_id = $('#project_id').val();

      var another_source_name = $('#another_source_name').val();
              
      var a = $(this).attr('data-target');
      var v = $(this).val();

      var protocol_headings_list = JSON.parse($('#usr_protocol_headings_list').val());   
      var sar_headings_list      = JSON.parse($('#usr_sar_headings_list').val());
      var another_doc_headings_list = JSON.parse($('#usr_another_doc_headings_list').val());

      var opt_html = '<option value="">---------</option>';
      
      if(v == 'Protocol')
      {
        
        $.each(protocol_headings_list, function(key,value){

          opt_html += "<option value='"+ value +"'>"+ value +"</option>";

        });

        $(a).html(opt_html);

      }
      else if(v == 'SAR')
      {
        
        $.each(sar_headings_list, function(key,value){

          opt_html += "<option value='"+ value +"'>"+ value +"</option>";

        });

        $(a).html(opt_html);
        
      }
      else if(v == another_source_name)
      {
        
        $.each(another_doc_headings_list, function(key,value){

          opt_html += "<option value='"+ value +"'>"+ value +"</option>";

        });

        $(a).html(opt_html);
        
      }
      else
      {
        $(a).html('<option value="">-----</option>');
      }
  });

  // to add record in user csr mapping
  $(document).on('click', '.add_record_user', function(){

    var no_of_records = $('#records_length').val();

    var proto_head = parseInt($('#protocol_headings_length').val());

    var sar_head = parseInt($('#sar_headings_length').val());

    var another_doc_head = parseInt($('#another_doc_headings_length').val());

    var another_source_name = $('#another_source_name').val();

    var no_of_records_update = parseInt(no_of_records) + 1;

    var a = $(this).attr('data-target');

    var b = $(a).find('.csr_heading_usr').val();

    var src = $(a).find('.source_file_select_usr').val();

    var src_hd = $(a).find('.source_file_headings_usr').val();

    if(src != '' && src_hd != ''){

        $('#ajax_loader').show();

        html = '';

        html += '<tr class="no-brd" id="record-'+ no_of_records_update +'">';

        html += '<td><input type="hidden" class="child_parent_id" name="child_parent_id[]" value="' + b + '"><input class="form-control csr_heading_usr" hidden type="text" readonly value="'+ b +'" id="csr-heading-usr-'+ no_of_records_update +'" name="csr_headings[]"></td>'

        html += '<td><select class="form-control source_file_select_usr" data-target="#copy-heading-usr-'+ no_of_records_update +'" name="source[]" id="source-usr-'+ no_of_records_update +'"><option value="">Source</option>';

        if(proto_head > 0 && sar_head > 0 && another_doc_head == 0){

          html += '<option value="Protocol">Protocol</option><option value="SAR">SAR</option>';

        }
       else if(proto_head > 0 && sar_head > 0 && another_doc_head > 0){

          html += "<option value='Protocol'>Protocol</option><option value='SAR'>SAR</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

        }
        else if(proto_head == 0 && sar_head > 0 && another_doc_head > 0){

          html += "<option value='SAR'>SAR</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

        }
        else if(proto_head > 0 && sar_head == 0 && another_doc_head > 0){

          html += "<option value='Protocol'>Protocol</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

        }
        else{

          if(proto_head > 0){

            html += '<option value="Protocol">Protocol</option>';

          }
          else if(sar_head > 0){

            html += '<option value="SAR">SAR</option>';
          }
          else if(another_doc_head > 0){

            html += "<option value='"+another_source_name+"'>"+another_source_name+"</option>";
          }
        }

        html += '</select></td>';

        html += '<td><select class="form-control source_file_headings_usr" id="copy-heading-usr-'+ no_of_records_update +'" name="copy_headings[]"><option value="">------</option></select></td>';

        html += '<td><input type="button" class="remove_record_user" value="" ></td></tr>';

        $(html).insertAfter($(this).closest('tr'));

        $('#records_length').val(no_of_records_update);

        $('#ajax_loader').hide();
    }
    else{
      alert('Please Map '+ b +' to add more ...');
    }

  });

  // to add record in user csr mapping if already pre mapped
  $(document).on('click', '.add_record_usr_prem', function(){

    var proj_id = $('#project_id').val();

    var proto_head = parseInt($('#protocol_headings_length').val());

    var sar_head = parseInt($('#sar_headings_length').val());

    var another_doc_head = parseInt($('#another_doc_headings_length').val());

    var another_source_name = $('#another_source_name').val();
       
    var no_of_records = $('#records_length').val();

    var no_of_records_update = parseInt(no_of_records) + 1;

    var a = $(this).attr('data-target');

    var b = $(a).find('.csr_heading_usr').val();

    var c = $(a).find('.parent_id').val();

    var src = $(a).find('.source_file_select_usr').val();

    var src_hd = $(a).find('.source_file_headings_usr').val();

    if(src != '' && src_hd != ''){

        $('#ajax_loader').show();

            html = '';

            html += '<tr class="no-brd" id="record-'+ no_of_records_update +'">';

            html += '<td><input type="hidden" class="child_parent_id" name="child_parent_id[]" value="' + c + '"><input class="form-control csr_heading_usr" hidden type="text" readonly value="'+ b +'" id="csr-heading-usr-'+ no_of_records_update +'" name="csr_headings[]"></td>';

            html += '<td><select class="form-control source_file_select_usr" data-target="#copy-heading-usr-'+ no_of_records_update +'" name="source[]" id="source-'+ no_of_records_update +'"><option value="">Source</option>';

            if(proto_head > 0 && sar_head > 0 && another_doc_head == 0){

              html += '<option value="Protocol">Protocol</option><option value="SAR">SAR</option>';
        
            }
            else if(proto_head > 0 && sar_head > 0 && another_doc_head > 0){

              html += "<option value='Protocol'>Protocol</option><option value='SAR'>SAR</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

            }
            else if(proto_head == 0 && sar_head > 0 && another_doc_head > 0){

              html += "<option value='SAR'>SAR</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

            }
            else if(proto_head > 0 && sar_head == 0 && another_doc_head > 0){

              html += "<option value='Protocol'>Protocol</option><option value='"+another_source_name+"'>"+another_source_name+"</option>";

            }
            else{

              if(proto_head > 0){

                html += '<option value="Protocol">Protocol</option>';

              }
              else if(sar_head > 0){

                html += '<option value="SAR">SAR</option>';
              }
              else if(another_doc_head > 0){

                html += "<option value='"+another_source_name+"'>"+another_source_name+"</option>";
              }
            }

            html += '</select></td>';

            html += '<td><select class="form-control source_file_headings_usr" id="copy-heading-usr-'+ no_of_records_update +'" name="copy_headings[]"><option value="">------</option></select></td>';

            html += '<td><input type="button" class="remove_record_user" value="" ></td></tr>';

            $(html).insertAfter(a);

            $('#records_length').val(no_of_records_update);

            $('#ajax_loader').hide();
            
    }
    else{
      alert('Please Map '+ b +' to add more ...');
    }

  });

  // to remove record in user csr mapping
  $(document).on('click', '.remove_record_user', function(){

    var no_of_records = $('#records_length').val();

    var no_of_records_update = parseInt(no_of_records) - 1;

    $(this).closest('tr').remove();

    $('#records_length').val(no_of_records_update);

  });

  // To handle onchange event for activity log events in admin
  // $(document).on('change', '#activity_log_on_change', function(){

  //   var url = $(this).val();

  //   var usr_name = $('#activity_log_on_change').find(":selected").text();

  //   $.ajax({

  //   type : "GET",
  //   url : "/acvt_usr_cng/" + usr_name,
  //   success: function(){
  //     location.href=url;
  //   }

  //   });

  // });



  // To handle onchange event for audit log events in admin
  // $(document).on('change', '#audit_log_on_change', function(){

  //   var url = $(this).val();

  //   var usr_name = $('#audit_log_on_change').find(":selected").text();

  //   $.ajax({

  //   type : "GET",
  //   url : "/audt_usr_cng/" + usr_name,
  //   success: function(){
  //     location.href=url;
  //   }

  //   });

  // });

   // To handle onchange event for global csr mapping display
  $(document).on('change', '#gbl_map_client_sel', function(){

    var url = $(this).val();

    var cli_name = $('#gbl_map_client_sel').find(":selected").text();

    $.ajax({

    type : "GET",
    url : "/glbmap_cli_cng/" + cli_name,
    success: function(){
      location.href=url;
    }

    });

  });

  // to show the confirmatin and take reason input form the user in user csr mapping
  $(document).on('click', '#edit_mapping_user_btn', function(e){
    
    var url = $('#edit_mapping_user_form').attr('data-url');

    var csr_headings    = $(".csr_heading_usr").map(function(){return $(this).val();}).get();
    var source          = $(".source_file_select_usr").map(function(){return $(this).val();}).get();
    var source_headings = $(".source_file_headings_usr").map(function(){return $(this).val();}).get();
    var parent_ids      = $(".child_parent_id").map(function(){return $(this).val();}).get();
    
    var values = [csr_headings, source, source_headings, parent_ids];
    var jsonText = JSON.stringify(values);

    $.ajax({
    
            url      : url,
            type     : "post",
            data     : jsonText,
            dataType : "json",
            success  : function(data){

              $('#confirm_user_mapping_modal .modal-content').html(data.html_form);

              $('.confirm_map_user').on('click', function(){

                var k = $('#id_reason').val();
                
                if($.trim(k).length === 0)
                {

                    $('#error_reason').html("Reason can't be blank");

                }else{

                    $('#confirm_user_mapping_modal').modal('hide');
                    $('#edit_mapping_user_form').submit();
                }

              });
            }
          });
  });

  // to show the confirmatin and take reason input form the admin in admin csr mapping
  $(document).on('click', '#edit_mapping_admin_btn', function(e){

    var url = $('#admin-csr-mapping-form').attr('data-url');

    var csr_headings    = $(".csr_heading").map(function(){return $(this).val();}).get();
    var source          = $(".source_file_select").map(function(){return $(this).val();}).get();
    var source_headings = $(".source_file_headings").map(function(){return $(this).val();}).get();
    var parent_ids      = $(".child_parent_id").map(function(){return $(this).val();}).get();
    
    var values   = [csr_headings, source, source_headings, parent_ids];
    var jsonText = JSON.stringify(values);

    $.ajax({

      url      : url,
      type     : "post",
      data     : jsonText,
      dataType : "json",
      success  : function(data){

        $('#confirm_admin_mapping_modal .modal-content').html(data.html_form);
        $('.confirm_map_admin').on('click', function(){

          var k = $('#id_reason').val();
          
          if($.trim(k).length === 0)
          {

              $('#error_reason').html("Reason can't be blank");

          }else{

              $('#confirm_admin_mapping_modal').modal('hide');
              $('#admin-csr-mapping-form').submit();
          }
      });

      }

    });    

  });


  // to show the confirmatin and take the file & version in generate csr
  $(document).on('click', '#generate_csr_link', function(e){

    var url = $(this).attr('data-href');
    
    $('.confirm_generate_csr').on('click', function(){

      var filename = $('#id_output_file_name').val();
      var version  = $('input[name=version]:checked').val();

      var values   = [filename, version];
      var jsonText = JSON.stringify(values);
      
      if($.trim(filename).length === 0)
      {

          $('#error_output_file_name').html("Report name can't be blank");

      }else{

          $('#confirm_generate_csr_modal').modal('hide');
          $('#ajax_loader').show();

          $.ajax({
            url      : url,
            type     : "post",
            data     : jsonText,
            dataType : "json",
            success  : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                location.reload();
            }
            else{
              
              location.reload();
            }
            }
          });
      }
    });

  });

  // to handle email configuration
  $('#email_configuration_link').click(function(){

    $('#ajax_loader').show();
    
    $.ajax({

        url        : $(this).attr('data-href'),
        type       : "get",
        dataType   : "json",
        beforeSend : function(){

          $('.submenu').hide();
          $('#email_configuration_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#email_configuration_modal .modal-content').html(data.html_form);
          $('#ajax_loader').hide();
        }
    });      
  });

  $('#email_configuration_modal').on('submit', '.email_configuration_form', function(){

      $('#ajax_loader').show();

      var form = $(this);

      $.ajax({

          url      : form.attr('data-url'),
          data     : form.serialize(),
          type     : form.attr('method'),
          dataType : 'json',
          success  : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#email_configuration_modal').modal('hide');
                  location.reload();

              }else{
                 $('#email_configuration_modal .modal-content').html(data.html_form);
              }
          }
      });
      return false;
  });

  // to handle resent email
  $(document).on('click', '#resend_email_button', function(){

    $('#ajax_loader').show();
  
    $.ajax({

        url      : $(this).attr('data-href'),
        type     : "get",
        dataType : "json",
        success  : function(data){

          $('#ajax_loader').hide();

          if(data.resend_status){
              
              location.reload();
          }else{
              
          }
        }
    });      
  });


// to handle admin clear configurations
  $(document).on('click', '#admin_clear_conf_btn', function(e){

     $('#confirm_admin_clear_configurations').modal({show : true, backdrop : 'static', keyboard : false});

  });

  $(document).on('submit', '#confirm_admin_clear_configurations_form', function(e){

      // e.preventDefault();

      var text = $('#adm_clr_conf_text').val();
      
      if(text == 'clear configurations'){
        
        $.ajax({

          url: $(this).attr('data-href'),
          type : "get",
          success : function(data){
            
            // alert('All the Configurations have been deleted succesfully!');
            location.reload();
          }

        });

        return true;

      }else {

        $('#admin_error_confirm_clear_configurations').html('Please enter proper input!');
      }

      return false;

  });

// to handle user clear configurations
  $(document).on('click', '#user_clear_conf_btn', function(e){

     $('#confirm_user_clear_configurations').modal({show : true, backdrop : 'static', keyboard : false});

  });

  $(document).on('submit', '#confirm_user_clear_configurations_form', function(e){

      // e.preventDefault();

      var text = $('#user_clr_conf_text').val();
      
      if(text == 'clear configurations'){
        
        $.ajax({

          url: $(this).attr('data-href'),
          type : "get",
          success : function(data){
            
            // alert('All the Configurations have been deleted succesfully!');
            location.reload();
          }

        });

        return true;

      }else {

        $('#user_error_confirm_clear_configurations').html('Please enter proper input!');
      }

      return false;

  });


  // $(document).on('click', '#clear_configurations__admin', function(){

  //   var r = confirm('This will delete all the Configurations! Click on OK to continue.')
  //   if (r == true){
  //     $.ajax({

  //       url: $(this).attr('data-href'),
  //       type : "get",
  //       success : function(){
          
  //         alert('All the Configurations have been deleted succesfully!');
  //         location.reload();
  //       }

  //     });
  //   }else{
  //     return false;
  //   }

  // });

  //  $(document).on('click', '#clear_configurations__usr', function(){

  //   var r = confirm('This will delete all the Configurations! Click on OK to continue.')
  //   if (r == true){
  //     $.ajax({

  //       url: $(this).attr('data-href'),
  //       type : "get",
  //       success : function(){
          
  //         alert('All the Configurations have been deleted succesfully!');
  //         location.reload();
  //       }

  //     });
  //   }else{
  //     return false;
  //   }

  // });

  // To hangle shared by
  $(document).on('click', '.shared_by', function(){
    $.ajax({

      url : $(this).attr('data-url'),
      type : "get",
      dataType : "json",
      beforeSend : function(){

          $('#shared_docs_by_modal').modal({show : true, backdrop : 'static', keyboard : false});
      },
      success : function(data){

        $('#shared_docs_by_modal .modal-content').html(data.html_form);
      }

    });

  });

  // To hangle shared with
  $(document).on('click', '.shared_with', function(){
    $.ajax({

      url : $(this).attr('data-url'),
      type : "get",
      dataType : "json",
      beforeSend : function(){

          $('#shared_docs_with_modal').modal({show : true, backdrop : 'static', keyboard : false});
      },
      success : function(data){

        $('#shared_docs_with_modal .modal-content').html(data.html_form);
      }

    });

  });

  $(document).on('click', '.add_comments', function(){

    $.ajax({

      url : $(this).attr('data-url'),
      type : "get",
      dataType : "json",
      beforeSend : function(){

          $('#add_comments_modal').modal({show : true, backdrop : 'static', keyboard : false});
      },
      success : function(data){

        $('#add_comments_modal .modal-content').html(data.html_form);
      }

    });

  });


  $('.add_comments_modal').on('submit', '.add_comments_form', function(){

      var form = $(this);

      if($('#report_comments').val().trim().length > 0){

        $('#ajax_loader').show();

        $.ajax({

            url : form.attr('data-url'),
            data : form.serialize(),
            type : form.attr('method'),
            dataType : 'json',
            success : function(data){

                $('#ajax_loader').hide();

                if(data.form_is_valid){

                    $('.add_comments_modal').modal('hide');
                    location.reload();

                }else{

                   $('.add_comments_modal .modal-content').html(data.html_form);

                }
            }
        });

      }else{
        $('#report_comments_error').show();
      }

      
      return false;
  });

  // To view comments
  $(document).on('click', '.view_comments', function(){

    $.ajax({

      url : $(this).attr('data-url'),
      type : "get",
      dataType : "json",
      beforeSend : function(){

          $('#view_comments_modal').modal({show : true, backdrop : 'static', keyboard : false});
      },
      success : function(data){

        $('#view_comments_modal .modal-content').html(data.html_form);
      }

    });

  });


  $(document).on('click', '.add_another_document_btn__usr', function(){

      var url = $('#add_another_document_form__usr').attr('data-href')

      var source_name = $('#id_source_doc_name').val();

      var values = [source_name];
      var jsonText = JSON.stringify(values);

      if($.trim(source_name).length === 0){

        $('#error_source_doc_name').html("Source name can't be blank");

      }else{

        $('#add_another_document__usr_modal').modal('hide');

        $.ajax({

          url : url,
          type : "post",
          data : jsonText,
          dataType : "json",
          success : function(data){
            if(data.add_status){
              location.reload()
            }
          }

        });
      }

    });

  // to handle add client
  $(document).on('click', '#add_client_link', function(){
  // $('#add_client_link').click(function(){

    // $('#ajax_loader').show();
    
    $.ajax({

        url   : $(this).attr('data-href'),
        type  : "get",
        dataType : "json",
        beforeSend : function(){
          
          $('#add_client_modal').modal({show : true, backdrop : 'static', keyboard : false});
        },
        success   : function(data){

          $('#add_client_modal .modal-content').html(data.html_form);
          $('#ajax_loader').hide();
        }
    });      
  });

  $(document).on('submit', '#add_client_modal .add_client_form', function(){

      $('#ajax_loader').show();

      var form = $(this);

      $.ajax({

          url : form.attr('data-href'),
          data : form.serialize(),
          type : form.attr('method'),
          dataType : 'json',
          success : function(data){

              $('#ajax_loader').hide();

              if(data.form_is_valid){

                  $('#add_client_modal').modal('hide');
                  location.reload();

              }else{
                 $('#add_client_modal .modal-content').html(data.html_form);
              }
          }
      });
      return false;
  });

  // to handle filter in acivity log
  $(document).on('click', '#actv_log_flt_btn', function(){
    var request_user = $('#avt_log_user').val();
    var from_date = $('#acvt_from_date').val();
    var to_date = $('#acvt_to_date').val();

    if (from_date != '' && to_date == ''){
      $('#acvt_to_date_label').css('color','red');
    }else{
      $('#acvt_to_date_label').css('color','black');
    }

    if (from_date == '' && to_date != ''){
      $('#acvt_from_date_label').css('color','red');
    }else{
      $('#acvt_from_date_label').css('color','black');
    }

    if ((from_date != '' && to_date != '') || (from_date == '' && to_date == '')){

      var filt_obj = [request_user, from_date, to_date];

      $('#ajax_loader').show();

      $.ajax({
        url : '/filter_acvt_log/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filt_obj),
        success : function(data){
          $('#activity_log_data').html(data.html_form);
          $('#ajax_loader').hide();
            $('#activity_log_tbl').DataTable({

              searching : false,
              "ordering": false,
              "pageLength": 25,
              columnDefs: [{
                orderable: false,
                targets: "no-sort"
              }]

            });
        }

      });
    }

  });

  // to handle filter in audit log
  $(document).on('click', '#audt_log_flt_btn', function(){
    var req_id = $('#adt_log_user').val();
    var proj_id = $('#adt_log_project').val();
    var from_date = $('#audt_from_date').val();
    var to_date = $('#audt_to_date').val();

    if (from_date != '' && to_date == ''){
      $('#audt_to_date_label').css('color','red');
    }else{
      $('#audt_to_date_label').css('color','black');
    }

    if (from_date == '' && to_date != ''){
      $('#audt_from_date_label').css('color','red');
    }else{
      $('#audt_from_date_label').css('color','black');
    }

    if ((from_date != '' && to_date != '') || (from_date == '' && to_date == '')){

      var filt_obj = [req_id, proj_id, from_date, to_date];

      $('#ajax_loader').show();

      $.ajax({
        url : '/filter_audt_log/',
        type : 'POST',
        dataType : 'json',
        data : JSON.stringify(filt_obj),
        success : function(data){
          $('#ajax_loader').hide();
          $('#audit_log_data').html(data.html_form);
            $('#audit_logs_tbl').DataTable({

              searching : false,
              "ordering": false,
              "pageLength": 25,
              columnDefs: [{
                orderable: false,
                targets: "no-sort"
              }]

            });
        }

      });
    }

  });




});




jQuery(document).ready(function (e) {
    function t(t) {
        e(t).bind("click", function (t) {
            t.preventDefault();
            e(this).parent().fadeOut()
        })
    }
    e(".dropdown-toggle__").click(function () {
        var t = e(this).parents(".button-dropdown").children(".dropdown-menu").is(":hidden");
        e(".button-dropdown .dropdown-menu").hide();
        e(".button-dropdown .dropdown-toggle__").removeClass("active___");
        if (t) {
            e(this).parents(".button-dropdown").children(".dropdown-menu").toggle().parents(".button-dropdown").children(".dropdown-toggle__").addClass("active___")
        }
    });
    e(document).bind("click", function (t) {
        var n = e(t.target);
        if (!n.parents().hasClass("button-dropdown")) e(".button-dropdown .dropdown-menu").hide();
    });
    e(document).bind("click", function (t) {
        var n = e(t.target);
        if (!n.parents().hasClass("button-dropdown")) e(".button-dropdown .dropdown-toggle__").removeClass("active___");
    })
});