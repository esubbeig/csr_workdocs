from .models import *
import pandas as pd
import numpy as np
import logging
import traceback
import json

from .models import *

from django.forms.models import model_to_dict

csr_logger        = logging.getLogger('csr')
csr_except_logger = logging.getLogger('csr_except')

# audit log for user's edit project
def edit_project_log(previoust_state, current_state, reason, project, user, client_ip):

    try:

        action = 'Edit Project'

        rm_keys = ['id', 'active', 'delete', 'created_by', 'generated']

        # conveting to dictionary from model instalce
        pre_dict_obj = model_to_dict(previoust_state)
        cur_dict_obj = model_to_dict(current_state)

        # replacing id with the name
        pre_dict_obj['therapeutic_area'] = previoust_state.therapeutic_area.therapeutic_area
        cur_dict_obj['therapeutic_area'] = current_state.therapeutic_area.therapeutic_area
        pre_dict_obj['client'] = previoust_state.client.client_name
        cur_dict_obj['client'] = current_state.client.client_name

        # popping keys which are not required
        [pre_dict_obj.pop(key) for key in rm_keys]
        [cur_dict_obj.pop(key) for key in rm_keys]

        pre_dict_obj = str(pre_dict_obj).replace("{","").replace("}","").replace("'","")
        cur_dict_obj = str(cur_dict_obj).replace("{","").replace("}","").replace("'","")

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre_dict_obj,
                current_state  = cur_dict_obj,
                reason         = reason,
                ip             = client_ip
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

# audit log for admin assing projects
def assign_project_log(pre_assinged, post_assinged, reason, user, client_ip, project):

    try:

        action = 'Assign Project'

        pre_assinged = ','.join(map(str, list(pre_assinged)))
        post_assinged = ','.join(map(str, post_assinged))

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre_assinged,
                current_state  = post_assinged,
                reason         = reason,
                ip             = client_ip,
                project        = project,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
    
# audit log for add user
def adduser_audit(pre_assinged, post_assinged, user, reason, client_ip):

    try:

        action = 'Add User'

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre_assinged,
                current_state  = post_assinged,
                reason         = reason,
                ip             = client_ip,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
    
# audit log for add client
def addclient_audit(pre_assinged, post_assinged, user, reason, client_ip, client):

    try:

        action = 'Add Client'

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre_assinged,
                current_state  = post_assinged,
                reason         = reason,
                ip             = client_ip,
                client         = client,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

# audit log for create project
def createproj_audit(pre_assinged, post_assinged, user, reason, client_ip, project):

    try:

        action = 'Create Project'

        rm_keys = ['id', 'active', 'delete', 'created_by', 'generated']

        # conveting to dictionary from model instance
        cur_dict_obj = model_to_dict(post_assinged)

        # replacing id with the name
        cur_dict_obj['therapeutic_area'] = post_assinged.therapeutic_area.therapeutic_area
        cur_dict_obj['client'] = post_assinged.client.client_name

        # popping keys which are not required
        [cur_dict_obj.pop(key) for key in rm_keys]

        cur_dict_obj = str(cur_dict_obj).replace("{","").replace("}","").replace("'","")

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre_assinged,
                current_state  = cur_dict_obj,
                reason         = reason,
                ip             = client_ip,
                project        = project,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

# audit log for user's custom csr mapping
# def edit_custom_csr_mapping_log(custom_mapping, csr_headings_data, source_data, copy_headings_data, reason, user, project, client_ip):

#     try:

#         action = 'Edit Mapping'
        
#         new_custom_mapping = [{k: v for k, v in d.items() if k != 'id' and k != 'project_id' and k != 'created_by_id'} for d in custom_mapping]
            
#         pre_mapped_dataframe = pd.DataFrame(new_custom_mapping, columns=['csr_heading', 'source_file', 'copy_headings'])

#         pre_mapped_dataframe = pre_mapped_dataframe.replace(r'^\s*$', np.nan, regex=True)
#         pre_mapped_dataframe = pre_mapped_dataframe.dropna()

#         pre_mapped_dataframe_dict = pre_mapped_dataframe.to_dict(orient='records')
#         pre_mapped_dataframe_dict = str(pre_mapped_dataframe_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")
        
#         data = {
#             'csr_heading' : csr_headings_data,
#             'source_file' : source_data,
#             'copy_headings' : copy_headings_data
#         }

#         dataframe = pd.DataFrame(data, columns=['csr_heading', 'source_file', 'copy_headings'])
#         dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
#         dataframe = dataframe.dropna()

#         dataframe_dict = dataframe.to_dict(orient='records')
#         dataframe_dict = str(dataframe_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")

#         audit_model = LogsAudit(

#                 user           = user,
#                 project        = project,
#                 action         = action,
#                 previous_state = pre_mapped_dataframe_dict,
#                 current_state  = dataframe_dict,
#                 ip             = client_ip,
#                 reason         = reason
#             )
#         audit_model.save()

#     except Exception as e:
#         csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def edit_custom_csr_mapping_log(changed_sections_only, tempe, reason, user, project, client_ip):

    try:

        action = 'Edit Mapping'

        df1 = pd.DataFrame(changed_sections_only)
        df2 = pd.DataFrame(tempe)

        try:
            df1 = df1.drop(columns=['parent_id'])
            df2 = df2.drop(columns=['parent_id'])
        except:
            pass

        df1_dict = df1.to_dict(orient='records')
        df2_dict = df2.to_dict(orient='records')
        
        pre_mapped_dataframe_dict = str(df1_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")
        dataframe_dict = str(df2_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre_mapped_dataframe_dict,
                current_state  = dataframe_dict,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# audit log for admin's global csr mapping
# def edit_global_csr_mapping_log(pre_mapped_headings, csr_headings_data, source_data, copy_headings_data, reason, user, client_ip, client):


#       try:

#           action = 'Edit Mapping'
            
#           new_pre_mapped_headings = [{k: v for k, v in d.items() if k != 'id'} for d in pre_mapped_headings]

#           pre_mapped_dataframe = pd.DataFrame(new_pre_mapped_headings, columns=['csr_heading', 'source_file', 'copy_headings'])

#           pre_mapped_dataframe = pre_mapped_dataframe.replace(r'^\s*$', np.nan, regex=True)
#           pre_mapped_dataframe = pre_mapped_dataframe.dropna()

#           pre_mapped_dataframe_dict = pre_mapped_dataframe.to_dict(orient='records')
#           pre_mapped_dataframe_dict = str(pre_mapped_dataframe_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")

#           data = {
#               'csr_heading' : csr_headings_data,
#               'source_file' : source_data,
#               'copy_headings' : copy_headings_data
#           }

#           dataframe = pd.DataFrame(data, columns=['csr_heading', 'source_file', 'copy_headings'])
#           dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
#           dataframe = dataframe.dropna()

#           dataframe_dict = dataframe.to_dict(orient='records')
#           dataframe_dict = str(dataframe_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")

#           audit_model = LogsAudit(

#                   user           = user,
#                   action         = action,
#                   previous_state = pre_mapped_dataframe_dict,
#                   current_state  = dataframe_dict,
#                   ip             = client_ip,
#                   reason         = reason,
#                   client         = client,
#               )
#           audit_model.save()

#       except Exception as e:
#           csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def edit_global_csr_mapping_log(changed_sections_only, tempe, reason, user, client_ip, client):

    try:
        action = 'Edit Mapping'

        df1 = pd.DataFrame(changed_sections_only)
        df2 = pd.DataFrame(tempe)

        try:
            df1 = df1.drop(columns=['parent_id'])
            df2 = df2.drop(columns=['parent_id'])
        except:
            pass

        df1_dict = df1.to_dict(orient='records')
        df2_dict = df2.to_dict(orient='records')
        
        pre_mapped_dataframe_dict = str(df1_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")
        dataframe_dict = str(df2_dict).replace("{","").replace("}","").replace("[","").replace("]","").replace("'","")

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre_mapped_dataframe_dict,
                current_state  = dataframe_dict,
                ip             = client_ip,
                reason         = reason,
                client         = client,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def upload_csr_admin_audit(pre, post, user, reason, client_ip, client):

    try:
        action = 'Upload Global CSR'

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason,
                client         = client,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_protocol_admin_audit(pre, post, user, reason, client_ip, client):

    try:
        action = 'Upload Global Protocol'

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason,
                client         = client,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_sar_admin_audit(pre, post, user, reason, client_ip, client):

    try:
        action = 'Upload Global SAR'

        audit_model = LogsAudit(

                user           = user,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason,
                client         = client,
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_csr_user_audit(pre, post, user, reason, client_ip, project):

    try:
        action = 'Upload CSR'

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_protocol_user_audit(pre, post, user, reason, client_ip, project):

    try:
        action = 'Upload Protocol'

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_sar_user_audit(pre, post, user, reason, client_ip, project):

    try:
        action = 'Upload SAR'

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_another_user_audit(source, pre, post, user, reason, client_ip, project):

    try:
        action = 'Upload ' + source

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def upload_finaldoc_user_audit(pre, post, user, reason, client_ip, project):

    try:
        action = 'Upload Final CSR'

        audit_model = LogsAudit(

                user           = user,
                project        = project,
                action         = action,
                previous_state = pre,
                current_state  = post,
                ip             = client_ip,
                reason         = reason
            )
        audit_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))