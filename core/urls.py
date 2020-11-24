from django.urls import path, include
from django.contrib import admin
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('add_user/', views.add_user, name='add_user'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name='logout'),    
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
	path('activate_user/<usr_id>', views.activate_user, name='activate_user'),
	path('deactivate_user/<usr_id>', views.deactivate_user, name='deactivate_user'),
    path('set_password/', views.set_password, name='set_password'),
    path('reset_password/', views.reset_password, name='reset_password'),

    path('add_client/', views.add_client, name='add_client'),
	path('global_csr_upload/<cli_id>', views.global_csr_upload, name='global_csr_upload'),
    path('upload_csr_admin/<cli_id>', views.upload_csr_admin, name='upload_csr_admin'),
    path('upload_protocol_admin/<cli_id>', views.upload_protocol_admin, name='upload_protocol_admin'),
    path('upload_sar_admin/<cli_id>', views.upload_sar_admin, name='upload_sar_admin'),
    path('csr_mapping/<cli_id>', views.csr_mapping, name='csr_mapping'),
    path('confirm_csr_mapping_admin/<cli_id>', views.confirm_csr_mapping_admin, name='confirm_csr_mapping_admin'),
    path('display_global_csr_mapping/<cli_id>', views.display_global_csr_mapping, name='display_global_csr_mapping'),
    path('clear_configurations__admin/<cli_id>', views.clear_configurations__admin, name='clear_configurations__admin'),
	    
    path('users/', views.get_all_users_details, name='get_all_users_details'),
    path('get_all_active_users_details/', views.get_all_active_users_details, name='get_all_active_users_details'),
    path('get_all_act_inact_users_details/', views.get_all_act_inact_users_details, name='get_all_act_inact_users_details'),
    path('clients/', views.get_all_client_details, name='get_all_client_details'),
    path('get_all_active_client_details/', views.get_all_active_client_details, name='get_all_active_client_details'),
    path('get_all_act_inact_client_details/', views.get_all_act_inact_client_details, name='get_all_act_inact_client_details'),
    path('activate_client/<cli_id>', views.activate_client, name='activate_client'),
    path('deactivate_client/<cli_id>', views.deactivate_client, name='deactivate_client'),

    path('create_project/<usr_id>', views.create_project, name='create_project'),
    path('edit_user_project/<usr_id>/<proj_id>', views.edit_user_project, name='edit_user_project'),
    path('assign_project/<prj_id>', views.assign_project_new, name='assign_project'),
    path('project_dashboard/<usr_id>/<proj_id>', views.project_dashboard, name='project_dashboard'),

    path('csr_upload/<usr_id>/<pro_id>', views.csr_upload, name='csr_upload'),
    path('protocol_file_upload/<usr_id>/<pro_id>', views.protocol_file_upload, name='protocol_file_upload'),
    path('sar_file_upload/<usr_id>/<pro_id>', views.sar_file_upload, name='sar_file_upload'),
    path('edit_csr_mapping/<usr_id>/<proj_id>/', views.edit_csr_mapping, name='edit_csr_mapping'),
    path('confirm_csr_mapping_user/<usr_id>/<proj_id>', views.confirm_csr_mapping_user, name='confirm_csr_mapping_user'),
    path('generate_csr/<usr_id>/<proj_id>', views.generate_csr, name='generate_csr'),
    path('add_another_document__usr/<usr_id>/<proj_id>', views.add_another_document__usr, name='add_another_document__usr'),
    path('another_file_upload/<usr_id>/<pro_id>', views.another_file_upload, name='another_file_upload'),
    path('clear_configurations__usr/<usr_id>/<proj_id>', views.clear_configurations__usr, name='clear_configurations__usr'),
    path('finalcsr_file_upload/<usr_id>/<pro_id>', views.finalcsr_file_upload, name='finalcsr_file_upload'),

    path('protocol/<usr_id>', views.protocol, name='protocol'),
    path('protocol_ad/', views.protocol_ad, name='protocol_ad'),

    path('download/<path>', views.download, name='download'),
    
    path('activity_log/', views.activity_log, name='activity_log'),
    path('audit_log/', views.audit_log, name='audit_log'),
    path('mail_logs/', views.mail_logs, name='mail_logs'),
    path('display_logging/', views.display_logging, name='display_logging'),
        
    path('email_configuration/', views.email_configuration, name='email_configuration'),
    path('resend_email/<mail_id>', views.resend_email, name='resend_email'),

    path('filter_project_names_info/', views.filter_project_names_info, name='filter_project_names_info'),
    path('get_client_info/', views.get_client_info, name='get_client_info'),
    path('get_therapeutic_area_info/', views.get_therapeutic_area_info, name='get_therapeutic_area_info'),
    
    path('filter_protocol_user_date/', views.filter_protocol_user_date, name='filter_protocol_user_date'),
    path('filter_protocol_user_filterobj/', views.filter_protocol_user_filterobj, name='filter_protocol_user_filterobj'),
    path('filter_protocol_user_filterdateobj/', views.filter_protocol_user_filterdateobj, name='filter_protocol_user_filterdateobj'),

    path('filter_protocol_admin_date/', views.filter_protocol_admin_date, name='filter_protocol_admin_date'),
    path('filter_protocol_admin_filterobj/', views.filter_protocol_admin_filterobj, name='filter_protocol_admin_filterobj'),
    path('filter_protocol_admin_filterdateobj/', views.filter_protocol_admin_filterdateobj, name='filter_protocol_admin_filterdateobj'),

    path('share_workDocs/<report_id>', views.share_workDocs, name='share_workDocs'),

    path('shared_doc_by/<usr_id>/<proj_id>', views.shared_doc_by, name='shared_doc_by'),

    path('shared_doc_with/<usr_id>/<proj_id>', views.shared_doc_with, name='shared_doc_with'),

    path('download_workdocs_doc/<document_id>', views.download_workdocs_doc, name='download_workdocs_doc'),

    path('add_report_comments/<report_id>', views.add_report_comments, name='add_report_comments'),
    path('view_report_comments/<report_id>', views.view_report_comments, name='view_report_comments'),

    path('get_notifications/', views.get_notifications, name='get_notifications'),

    path('get_notifications_count/', views.get_notifications_count, name='get_notifications_count'),

    path('cli_cng/<cli_id>', views.to_record_actlog_on_client_change, name='cli_cng'),
    path('click_csr_up/', views.to_record_actlog_on_click_up_csr, name='click_csr_up'),
    path('click_proj/', views.to_record_actlog_on_click_projects, name='click_proj'),
    path('click_actlog/', views.to_record_actlog_on_click_activitylog, name='click_actlog'),
    path('click_audlog/', views.to_record_actlog_on_click_auditlog, name='click_audlog'),
    path('click_emaillog/', views.to_record_actlog_on_click_emaillog, name='click_emaillog'),
    path('click_users/', views.to_record_actlog_on_click_users, name='click_users'),
    path('click_clients/', views.to_record_actlog_on_click_clients, name='click_clients'),
    path('click_prtsrch/', views.to_record_actlog_on_click_protsrch, name='click_prtsrch'),
    path('click_glbcsrmap/', views.to_record_actlog_on_click_gblcsrmapp, name='click_glbcsrmap'),
    path('click_prjdash/<proj_id>', views.to_record_actlog_on_prj_dashboard, name='click_prjdash'),

    path('down_glbcsr/<doc_id>', views.to_record_actlog_gbl_csr_download, name='down_glbcsr'),
    path('down_glbprotocol/<doc_id>', views.to_record_actlog_gbl_protocol_download, name='down_glbprotocol'),
    path('down_glbsar/<doc_id>', views.to_record_actlog_gbl_sar_download, name='down_glbsar'),
    path('down_custcsr/<doc_id>', views.to_record_actlog_cust_csr_download, name='down_custcsr'),
    path('down_custprotocol/<doc_id>', views.to_record_actlog_cust_protocol_download, name='down_custprotocol'),
    path('down_custsar/<doc_id>', views.to_record_actlog_cust_sar_download, name='down_custsar'),
    path('down_antdoc/<doc_id>', views.to_record_actlog_another_doc_download, name='down_antdoc'),
    path('down_report/<doc_id>', views.to_record_actlog_report_download, name='down_report'),

    path('filter_acvt_log/', views.filter_acvt_log, name='filter_acvt_log'),
    path('filter_audt_log/', views.filter_audt_log, name='filter_audt_log'),

    path('acvt_usr_cng/<usr_name>', views.to_record_actlog_actv_user_change, name='acvt_usr_cng'),
    path('audt_usr_cng/<usr_name>', views.to_record_actlog_audt_user_change, name='audt_usr_cng'),
    path('glbmap_cli_cng/<cli_name>', views.to_record_actlog_glbmap_client_change, name='glbmap_cli_cng'),
]


