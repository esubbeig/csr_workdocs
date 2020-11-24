// record activity log on client change in upload csr
$(document).on('change', '#client_sel', function(){

  var url = $(this).val();

  var cli_id = url.substring(url.lastIndexOf("/")+1);

  $.ajax({

    type : "GET",
    url : "/cli_cng/" + cli_id,
    success: function(){
      location.href=url;
    }

  });

});

// record activity log for upload csr
$(document).on('click', '#header_global_csr_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_csr_up/",
    success: function(){
      return true;
    }

  });

});

// record activity log for upload csr
$(document).on('click', '#header_projects_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_proj/",
    success: function(){
      return true;
    }

  });

});

// record activity log for activity log
$(document).on('click', '#header_activity_log_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_actlog/",
    success: function(){
      return true;
    }

  });

});

// record activity log for audit log
$(document).on('click', '#header_audit_log_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_audlog/",
    success: function(){
      return true;
    }

  });

});

// record activity log for email log
$(document).on('click', '#header_email_log_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_emaillog/",
    success: function(){
      return true;
    }

  });

});

// record activity log for users link
$(document).on('click', '#header_users_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_users/",
    success: function(){
      return true;
    }

  });

});

// record activity log for client link
$(document).on('click', '#header_clients_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_clients/",
    success: function(){
      return true;
    }

  });

});

// record activity log for protocol search link
$(document).on('click', '#header_protsearch_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_prtsrch/",
    success: function(){
      return true;
    }

  });

});

// record activity log for protocol search link
$(document).on('click', '#header_globcsrmap_link', function(){

  $.ajax({

    type : "GET",
    url : "/click_glbcsrmap/",
    success: function(){
      return true;
    }

  });

});

// record activity log on client change in upload csr
$(document).on('click', '#proj_dash', function(){

  var url = $(this).attr('href');

  var proj_id = url.substring(url.lastIndexOf("/")+1);

  $.ajax({

    type : "GET",
    url : "/click_prjdash/" + proj_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on global csr template download
$(document).on('click', '#down_csr_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_glbcsr/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on global protocol download
$(document).on('click', '#down_protocol_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_glbprotocol/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on global sar download
$(document).on('click', '#down_sar_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_glbsar/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on custom csr template download
$(document).on('click', '#down_customcsr_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_custcsr/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on protocol download
$(document).on('click', '#down_customprotocol_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_custprotocol/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on sar download
$(document).on('click', '#down_customsar_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_custsar/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on another document download
$(document).on('click', '#down_anotherdoc_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_antdoc/" + doc_id,
    success: function(){
      return true;
    }

  });

});

// record activity log on report download
$(document).on('click', '#down_report_link', function(){

  doc_id = $(this).attr('data-url');

  $.ajax({

    type : "GET",
    url : "/down_report/" + doc_id,
    success: function(){
      return true;
    }

  });

});
