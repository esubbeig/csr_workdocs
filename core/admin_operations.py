from django.contrib.auth.models import User
from datetime import datetime
from .models import *
import os
import pandas as pd
import numpy as np
import logging
import traceback
import re
from docx import Document
from .admin_csr_mapping import get_all_headings
from django.conf import settings
from django.db.models import Count

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

csr_logger = logging.getLogger('csr')
csr_except_logger = logging.getLogger('csr_except')


def get_library_suggesions(csr_headings, protocol_headings, sar_headings):

	Library_suggestion_dicT = {}
	matched_csr_headings = []
	
	# fetching the mapping from library
	try:
		library_mapping = list(Library.objects.all().values())
	except Library.DoesNotExist:
		library_mapping = None

	# removing prefix numbers of csr/protocol/sar headings
	csr_headings = list(map(lambda x: re.sub("^\d+(?:\.\d*)*", '', x).strip(), csr_headings))
	protocol_headings = list(map(lambda x: re.sub("^\d+(?:\.\d*)*", '', x).strip(), protocol_headings))
	sar_headings = list(map(lambda x: x.strip(), sar_headings))

	if library_mapping:

		library_dataframe = pd.DataFrame(library_mapping, columns=['standard_csr_heading', 'protocol_headings', 'sar_headings'])

		library_empty_records = library_dataframe[ (library_dataframe['protocol_headings'] == '') & (library_dataframe['sar_headings'] == '') ].index

		library_dataframe.drop(library_empty_records, inplace=True)
		
		library_dataframe = library_dataframe[library_dataframe['standard_csr_heading'].isin(csr_headings)]
		
		csr_heading = []
		source_file  = []
		copy_headings = []

		for index, row in library_dataframe.iterrows():

			if row['protocol_headings'] != '':
				temp_prot = list(filter(None, row['protocol_headings'].split(',')))
				for i in protocol_headings:
					if i in temp_prot:
						csr_heading.append(row['standard_csr_heading'])
						source_file.append('Protocol')
						copy_headings.append(i)
						break

			else:
				if row['sar_headings'] != '':
					temp_sar = list(filter(None, row['sar_headings'].split(',')))
					for i in sar_headings:
						if i in temp_sar:
							csr_heading.append(row['standard_csr_heading'])
							source_file.append('SAR')
							copy_headings.append(i)
							break

		dict = {'csr_heading' : csr_heading, 'source_file' : source_file, 'copy_headings' : copy_headings}
		Library_suggestion_dicT = pd.DataFrame(dict)
		Library_suggestion_dicT = Library_suggestion_dicT.to_dict(orient='records')
		matched_csr_headings = csr_heading

	return Library_suggestion_dicT, matched_csr_headings



def update_project_count_based_on_client_status():

	try:

		Act_ProjUser_Cnt = list(ProjectsXUsers.objects.filter(project__client__active=True).values('user').annotate(the_count=Count('user')))

		UsrProj_Cnt = UserProjectCount.objects.all()

		df = pd.DataFrame(Act_ProjUser_Cnt)

		for i in UsrProj_Cnt:

			r = df.loc[df.isin([i.user.id]).any(axis=1)]

			if not r.empty:
				obj = UserProjectCount.objects.get(user__id=i.user.id)
				obj.project_count = r.iloc[0]['the_count']
				obj.save()
			else:
				i.project_count=0
				i.save()
				

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
		


def get_all_users():

	try:

		users = User.objects.all()
		return users

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_all_clients():

	try:

		clients = ClientInfo.objects.all()
		return clients

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_all_projects():

	try:

		projects = ProjectInfo.objects.all()
		return projects

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_all_users_active():

	try:

		users = User.objects.filter(is_active=True)
		return users

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_all_users_active_toshare(current_user, project):

	try:

		# users = User.objects.filter(is_active=True, is_superuser=False).exclude(pk=current_user.id)
		projectXusers = ProjectsXUsers.objects.filter(project=project, active=True, user__is_superuser=False).exclude(user__id=current_user.id)
		return projectXusers

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_all_project_list():

	try:

		projects = ProjectInfo.objects.all()
		return projects

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#to record activity log
def record_user_activity_log(event, actor, **kwargs):

	try:
		activity_log_event = ActivityLogEvents.objects.get(event=event)
		raw_message = activity_log_event.message

		if event == 'Login':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Logout':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Change Password':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Add User':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Add User':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('dif_user'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Activate User':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('dif_user'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Deactivate User':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('dif_user'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Global CSR Upload':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Projects':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Project Dashboard':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Activity Log':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Change Password':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Audit Log':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Global CSR Mapping':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Email Configuration':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Add Email Configuration':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Email Log':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Add Report Comments':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('report_name')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Add Report Comments':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('report_name')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'View Report Comments':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('report_name')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Click Create Project Btn':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Create Project':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Click Assign Project Btn':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Assign Project':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name')).replace('@', kwargs.get('list_users'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav CSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Dispaly Global CSR Mapping':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'CSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Edit Project':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Edit Project':
			temp_message = raw_message.replace('#', kwargs.get('proj_name')) + ' by ' + str(actor)
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Protocol Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Protocol Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav SAR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'SAR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Upload Protocol':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Upload Protocol':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Upload SAR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Upload SAR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Custom CSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Custom CSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Generate CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Generate CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Edit Custom CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Edit Custom CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'CSR Mapping':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Change client in UPLOAD CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Change Client Global Mapping':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Resend Email':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('email')).replace('$', kwargs.get('log_event'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Clear Configurations':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Configurations Clear':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Another Document':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name')).replace('@', kwargs.get('source_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Another Doc Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name')).replace('@', kwargs.get('source_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Another Doc Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name')).replace('@', kwargs.get('source_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Clients':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Users':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Protocol Search':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Add Client':
			temp_message = str(actor) + ' ' + raw_message
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Add Client':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Activate Client':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Deactivate Client':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('client'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav FinalCSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'FinalCSR Upload':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Nav Share Document':
			temp_message = str(actor) + ' ' + raw_message.replace('@', kwargs.get('proj_name')).replace('#', kwargs.get('report_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Share Document':
			temp_message = str(actor) + ' ' + raw_message.replace('@', kwargs.get('proj_name')).replace('#', kwargs.get('report_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Global CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Global Protocol':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Global SAR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('client_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Custom CSR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Protocol':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download SAR':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Another Document':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('proj_name')).replace('*', kwargs.get('source_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Download Report':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('version')).replace('@', kwargs.get('proj_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Change Users Acvt':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('usr_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()

		elif event == 'Change Users Audt':
			temp_message = str(actor) + ' ' + raw_message.replace('#', kwargs.get('usr_name'))
			log_model 	 = LogsActivity(
				event 	 = activity_log_event,
				message  = temp_message,
				user 	 = actor,
				sessionid= kwargs.get('session_id'),
				ip 		 = kwargs.get('client_ip')
				)
			log_model.save()


	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



def filtered_pre_mapped_admin_data(req_client):

	try:

		pre_mapped_headings = list(GlobalMappingTable.objects.filter(client=req_client).order_by('id').values())

		dataframe = pd.DataFrame(pre_mapped_headings, columns=['csr_heading', 'source_file', 'copy_headings', 'parent_id'])
		
		# dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
		# dataframe = dataframe.dropna()
		
		Dframe = dataframe.to_dict(orient='records')

		return Dframe

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def cleaned_pre_mapped_data(pre_mapped_headings):

	try:

		dataframe = pd.DataFrame(pre_mapped_headings)
		
		dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
		dataframe = dataframe.dropna()
		
		Dframe = dataframe.to_dict(orient='records')

		return Dframe

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



def csr_updated_admin_form_data(csr_headings_data, source_data, copy_headings_data, parent_ids, pre_mapped_headings):

	try:

		data = {
			'csr_heading' : csr_headings_data,
			'source_file' : source_data,
			'copy_headings' : copy_headings_data,
			'parent_id' : parent_ids
		}

		dataframe = pd.DataFrame(data, columns=['csr_heading', 'source_file', 'copy_headings', 'parent_id'])
		# dataframe = dataframe.drop(dataframe[(dataframe['parent_id'] != '0') & ((dataframe['source_file'] == '') | (dataframe['copy_headings'] == ''))].index)
		# dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
		# dataframe = dataframe.dropna()

		CDframe = pd.DataFrame(pre_mapped_headings)

		Only_updated = pd.concat([dataframe, CDframe]).drop_duplicates(keep=False)

		Dframe = Only_updated.to_dict(orient='records')

		return Dframe
		
	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def cleaned_csr_updated_form_data(csr_head, src_file, src_head, parent_ids):

	try:

		data = {
			'csr_heading' : csr_head,
			'source_file' : src_file,
			'copy_headings' : src_head,
			'parent_id' : parent_ids
		}

		dataframe = pd.DataFrame(data, columns=['csr_heading', 'source_file', 'copy_headings', 'parent_id'])
		dataframe = dataframe.drop(dataframe[(dataframe['parent_id'] != '0') & ((dataframe['source_file'] == '') | (dataframe['copy_headings'] == ''))].index)
		dataframe = dataframe.replace(r'^\s*$', np.nan, regex=True)
		dataframe = dataframe.dropna()		

		Dframe = dataframe.to_dict(orient='records')

		return Dframe
		
	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to fetch only changed records
def changed_records_only_admin(req_client, updated_mapping_form_data):

	try:

		pre_mapped_headings = list(GlobalMappingTable.objects.filter(client=req_client).order_by('id').values())

		pre_mapped_dataframe = pd.DataFrame(pre_mapped_headings, columns=['csr_heading', 'source_file', 'copy_headings', 'parent_id'])

		updated_mapped_dataframe = pd.DataFrame(updated_mapping_form_data)

		csrHead_list = updated_mapped_dataframe['csr_heading'].tolist()

		dFrame = pre_mapped_dataframe[pre_mapped_dataframe.csr_heading.isin(csrHead_list)]

		Dframe = dFrame.to_dict(orient='records')

		return Dframe

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def updated_only_sections(changed_sections_only,updated_mapping_form_data):
	try:
		changed_sections_only = pd.DataFrame(changed_sections_only)
		updated_mapped_dataframe = pd.DataFrame(updated_mapping_form_data)

		# df = updated_mapped_dataframe - changed_sections_only

		# df = updated_mapped_dataframe[updated_mapped_dataframe.isin(changed_sections_only)]

		df = updated_mapped_dataframe[updated_mapped_dataframe.index.isin(changed_sections_only.index)].dropna()
		Dframe = df.to_dict(orient='records')

		return Dframe

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

def global_mapping_table_structure(mapping_table, req_client):

	try:

		dicT = {}

		for i in mapping_table:
			if i.parent_id == '0':
				ch_cont = GlobalMappingTable.objects.filter(csr_heading = i.csr_heading, parent_id=i.csr_heading, client=req_client).count()
				dicT[i.csr_heading] = ch_cont

		return dicT

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def check_file_content(document):
	
	try:

		# calling procedure from admin_csr_mapping
		headings = get_all_headings(document)
		wrg__frmt = ''
		for i in headings:
			if re.match("^\d+(?:\.\d*)*(?![\w-])", i):
				wrg__frmt += i
				break

		return wrg__frmt

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# def del_file_on_clear__config_admin(req_client):

# 	try:

# 		media_path = settings.MEDIA_ROOT

# 		admin_media_path = media_path + '\\admin'

# 		for root, dirs, files in os.walk(admin_media_path):
# 			for file in files:
				
# 				if os.path.exists(os.path.join(root, file)):
					
# 					try:
# 						os.remove(os.path.join(root, file))
# 					except:
# 						pass


# 	except Exception as e:
# 		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# To delete the admin files from filesystem on clear_config
def del_files__admin(template_list):

	try:
		media_path = settings.MEDIA_ROOT

		if template_list:
			for each in template_list:
				temp_path = media_path + '\\' + each
				try:
					os.remove(temp_path)
				except:
					pass
		else:
			pass

	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def del_file_on_clear__config_admin(req_client):

	try:
	
		csr_templates_list 	  = list(CSRTemplate.objects.filter(client=req_client).values_list('csr_template_location', flat=True))
		protocol_list 	  	  = list(ProtocolAdmin.objects.filter(client=req_client).values_list('protocol_template_location', flat=True))
		sar_list 		      = list(SARAdmin.objects.filter(client=req_client).values_list('sar_template_location', flat=True))
		

		del_files__admin(csr_templates_list)
		del_files__admin(protocol_list)
		del_files__admin(sar_list)
		
		
	except Exception as e:
		csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))