from django.db import models
from django.contrib.auth.models import User, AbstractUser
from django.conf import settings
from django.core.validators import FileExtensionValidator
from .field_mixin import CaseInsensitiveFieldMixin

class CICharField(CaseInsensitiveFieldMixin, models.CharField):
	pass


class User(AbstractUser):
	
	is_reviewer = models.BooleanField(default=False, blank=False)
	phone 		= models.CharField(max_length=10, default=None, null=True, blank=True)
	delete 	    = models.BooleanField(default=False)
	created_by  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='core_user_created_by', default=None, null=True, blank=True)


class TherapeuticArea(models.Model):
	therapeutic_area = models.CharField(max_length=512)

	class Meta:
		db_table = 'ikp_therapeutic_area'


class ClientInfo(models.Model):
	client_name = models.CharField(max_length=100, unique=True, error_messages={'unique':"Client is already existed."})
	active		= models.BooleanField(default=True)
	delete 		= models.BooleanField(default=False)
	created_by	= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
	created_on 	= models.DateTimeField(auto_now_add=True, blank=True, null=True)
	updated_on 	= models.DateTimeField(auto_now=True, blank=True, null=True)
	project_count = models.IntegerField(default=0)

	@property
	def is_delete(self):
		"Is the client is deleted?"
		return self.delete

	@property
	def is_active(self):
		"Is the client is active?"
		return self.active

	class Meta:
		db_table = 'clientinfo'



class ProjectInfo(models.Model):
	project_name	= models.CharField(max_length=512)
	protocol_id 	= models.CharField(max_length=32,unique=True, error_messages={'unique':"This protocol id already existed."})
	therapeutic_area= models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE)
	phase			= models.CharField(max_length=16)
	client			= models.ForeignKey(ClientInfo, on_delete=models.CASCADE)
	active			= models.BooleanField(default=True)
	delete 			= models.BooleanField(default=False)
	created_on 		= models.DateTimeField(auto_now_add=True)
	created_by		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	updated_on 		= models.DateTimeField(auto_now=True)
	generated 		= models.BooleanField(default=False)

	@property
	def is_delete(self):
		"Is the project is deleted?"
		return self.delete

	@property
	def is_active(self):
		"Is the project is active?"
		return self.active

	@property
	def is_generated(self):
		"Is the csr generated?"
		return self.generated


	class Meta:
		db_table = 'projectinfo'



class ProjectsXUsers(models.Model):
	project 	= models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	user 		= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	active		= models.BooleanField(default=True)
	created_on 	= models.DateTimeField(auto_now_add=True)
	created_by	= models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='projectxusers_created_by', null=True, blank=True)

	@property
	def is_active(self):
		"Is the project is active?"
		return self.active

	class Meta:
		db_table = 'projectsXusers'


# Contains count of project for each user
class UserProjectCount(models.Model):
	user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	project_count = models.IntegerField(default=0)

	class Meta:
		db_table = 'usersXprojectCount'



class ActivityLogEvents(models.Model):
	event 	= models.CharField(max_length=150)
	message = models.CharField(max_length=1024)

	class Meta:
		db_table = 'activity_log_events'

	def __str__(self):
		return self.event


class LogsActivity(models.Model):
	event  = models.ForeignKey(ActivityLogEvents, on_delete=models.CASCADE, blank=True)
	message   = models.CharField(max_length=1024)
	user 	  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	created_on= models.DateTimeField(auto_now=True)
	sessionid = models.CharField(max_length=256)
	ip 		  = models.CharField(max_length=100, blank=True, null=True)

	class Meta:
		db_table = 'logs_activity'


class LogsEmails(models.Model):
	event		   = models.CharField(max_length=64)
	to_email 	   = models.CharField(max_length=128)
	from_email	   = models.CharField(max_length=1024)
	subject 	   = models.CharField(max_length=512)
	message_body   = models.CharField(max_length=1024)
	created_on 	   = models.DateTimeField(auto_now_add=True)
	created_by	   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
	email_sent 	   = models.BooleanField(default=False)
	email_response = models.CharField(max_length=2048, blank=True, null=True)

	class Meta:
		db_table = 'logs_emails'


class GlobalMappingTable(models.Model):
	csr_heading   = models.CharField(max_length=1024)
	source_file   = models.CharField(max_length=1024, null=True)
	copy_headings = models.CharField(max_length=2048, null=True)
	parent_id 	  = models.CharField(max_length=1024, default=0)
	client		  = models.ForeignKey(ClientInfo, on_delete=models.CASCADE)

	class Meta:
		db_table = 'global_mapping_table'	



class CSRTemplate(models.Model):
	therapeutic_area 	  = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	csr_template_location = models.FileField(upload_to='admin/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	# version_no			  = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  = models.CharField(max_length=10, blank=True, null=True)
	comments			  = models.CharField(max_length=512, null=True, blank=True)
	delete 				  = models.BooleanField(default=False)
	created_on 			  = models.DateTimeField(auto_now_add=True)
	created_by			  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	client				  = models.ForeignKey(ClientInfo, on_delete=models.CASCADE)

	class Meta:
		db_table = 'ikp_csrtemplate'

	@property
	def is_delete(self):
		"Is the csr_template is deleted?"
		return self.delete



class ProtocolAdmin(models.Model):
	therapeutic_area 	  = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	protocol_template_location = models.FileField(upload_to='admin/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	version_no			  = models.CharField(max_length=10, blank=True, null=True)
	comments			  = models.CharField(max_length=512, null=True, blank=True)
	delete 				  = models.BooleanField(default=False)
	created_on 			  = models.DateTimeField(auto_now_add=True)
	created_by			  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	client				  = models.ForeignKey(ClientInfo, on_delete=models.CASCADE)

	class Meta:
		db_table = 'ikp_protocol_admin'

	@property
	def is_delete(self):
		"Is the protocol is deleted?"
		return self.delete


class SARAdmin(models.Model):
	therapeutic_area 	  = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	sar_template_location = models.FileField(upload_to='admin/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	version_no			  = models.CharField(max_length=10, blank=True, null=True)
	comments			  = models.CharField(max_length=512, null=True, blank=True)
	delete 				  = models.BooleanField(default=False)
	created_on 			  = models.DateTimeField(auto_now_add=True)
	created_by			  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	client				  = models.ForeignKey(ClientInfo, on_delete=models.CASCADE)

	class Meta:
		db_table = 'ikp_sar_admin'

	@property
	def is_delete(self):
		"Is the sar is deleted?"
		return self.delete



class CSRTemplateUser(models.Model):
	therapeutic_area 	  = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	csr_template_location = models.FileField(upload_to='users/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	project 			  = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	# version_no			  = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  = models.CharField(max_length=10, blank=True, null=True)
	comments			  = models.CharField(max_length=512, null=True, blank=True)
	delete 				  = models.BooleanField(default=False)
	created_on 			  = models.DateTimeField(auto_now_add=True)
	created_by			  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

	class Meta:
		db_table = 'ikp_csrtemplateuser'

	@property
	def is_delete(self):
		"Is the csr_template_user is deleted?"
		return self.delete



class ProtocolFileUpload(models.Model):
	therapeutic_area 	  	   = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	protocol_document_location = models.FileField(upload_to='users/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	# version_no			  	   = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  	   = models.CharField(max_length=10, blank=True, null=True)
	project 				   = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	uploaded_on 			   = models.DateTimeField(auto_now_add=True)
	created_by			  	   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	delete 				  	   = models.BooleanField(default=False)
	comments			  	   = models.CharField(max_length=512, null=True, blank=True)

	class Meta:
		db_table = 'protocol_file_upload'

	@property
	def is_delete(self):
		"Is the protocol is deleted?"
		return self.delete


		
class SarFileUpload(models.Model):
	therapeutic_area 	  	   = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	sar_document_location 	   = models.FileField(upload_to='users/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	# version_no			  	   = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  	   = models.CharField(max_length=10, blank=True, null=True)
	project 				   = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	uploaded_on 			   = models.DateTimeField(auto_now_add=True)
	created_by			  	   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	delete 				  	   = models.BooleanField(default=False)
	comments			  	   = models.CharField(max_length=512, null=True, blank=True)

	class Meta:
		db_table = 'sar_file_upload'

	@property
	def is_delete(self):
		"Is the sar is deleted?"
		return self.delete


class AnotherFileUploadUser(models.Model):
	therapeutic_area 	  	   = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	another_document_location  = models.FileField(upload_to='users/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	# version_no			  	   = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  	   = models.CharField(max_length=10, blank=True, null=True)
	project 				   = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	uploaded_on 			   = models.DateTimeField(auto_now_add=True)
	created_by			  	   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	delete 				  	   = models.BooleanField(default=False)
	comments			  	   = models.CharField(max_length=512, null=True, blank=True)

	class Meta:
		db_table = 'another_file_upload_user'

	@property
	def is_delete(self):
		"Is the another document is deleted?"
		return self.delete


class AnotherFileUploadUserInfo(models.Model):
	therapeutic_area = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	source_name		 = models.CharField(max_length=100)
	project 		 = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	created_by		 = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	created_on 		 = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'another_file_upload_user_info'



class Generated_Reports(models.Model):
	therapeutic_area 	  = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	project 			  = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	generated_report_path = models.CharField(max_length=200)
	# version_no			  = models.DecimalField(max_digits=5, decimal_places=1, blank=True, null=True)
	version_no			  = models.CharField(max_length=10, blank=True, null=True)
	created_by 			  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
	created_on 			  = models.DateTimeField(auto_now_add=True)
	delete 				  = models.BooleanField(default=False)

	class Meta:
		db_table = 'generated_reports'

	@property
	def is_delete(self):
		"Is the generated_report is deleted?"
		return self.delete


class CustomMappingTable(models.Model):
	csr_heading   = models.CharField(max_length=1024)
	source_file   = models.CharField(max_length=1024, null=True)
	copy_headings = models.CharField(max_length=2048, null=True)
	parent_id 	  = models.CharField(max_length=1024, default=0)
	project 	  = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	created_by	  = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)

	class Meta:
		db_table = 'custom_mapping_table'



class AuditLogsForMappingUser(models.Model):
	user 		   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	project 	   = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	action 		   = models.CharField(max_length=100, blank=True, null=True)
	previous_state = models.TextField(blank=True)
	current_state  = models.TextField(blank=True)
	reason 		   = models.CharField(max_length=2048, null=True)
	ip 			   = models.CharField(max_length=100)
	timestamp 	   = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'auditlogs_for_mapping_user'


class AuditLogsForMappingAdmin(models.Model):
	user 		   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	action 		   = models.CharField(max_length=100, blank=True, null=True)
	project_or_client = models.CharField(max_length=100, blank=True, null=True, default=None)
	previous_state = models.TextField(blank=True)
	current_state  = models.TextField(blank=True)
	reason 		   = models.CharField(max_length=2048, null=True)
	ip 			   = models.CharField(max_length=100)
	timestamp 	   = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'auditlogs_for_mapping_admin'


class EmailConfiguration(models.Model):
	email_host 			= models.CharField(max_length=1024)
	email_host_user 	= models.CharField(max_length=255)
	email_host_password = models.CharField(max_length=255, blank=True, null=True)
	email_port 			= models.PositiveSmallIntegerField(default=587)
	email_default_mail  = models.CharField(max_length=255, blank=True, null=True)
	email_use_tls 		= models.BooleanField(default=True)
	email_fail_silently = models.BooleanField(default=True)
	created_by 			= models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	created_on 			= models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'email_configuration'


class Library(models.Model):
	standard_csr_heading = models.CharField(max_length=1024)
	protocol_headings 	 = models.TextField(null=True, blank=True)
	sar_headings 		 = models.TextField(null=True, blank=True)
	
	class Meta:
		db_table = 'library'




class FinalCSRFileUpload(models.Model):
	therapeutic_area 	  	   = models.ForeignKey(TherapeuticArea, on_delete=models.CASCADE, blank=True, null=True)
	finalcsr_document_location = models.FileField(upload_to='finalcsr/', default=None, validators=[FileExtensionValidator(allowed_extensions=['docx'])])
	version_no			  	   = models.CharField(max_length=10, blank=True, null=True)
	project 				   = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE)
	uploaded_on 			   = models.DateTimeField(auto_now_add=True)
	created_by			  	   = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	delete 				  	   = models.BooleanField(default=False)
	comments			  	   = models.CharField(max_length=512, null=True, blank=True)

	class Meta:
		db_table = 'final_csr_file_upload'

	@property
	def is_delete(self):
		"Is the final csr is deleted?"
		return self.delete


class SharedDocumentData(models.Model):
	folder_id 	  = models.CharField(max_length=500)
	folder_name   = models.CharField(max_length=500)
	document_id   = models.CharField(max_length=500)
	document_name = models.CharField(max_length=500)
	report  	  = models.ForeignKey(Generated_Reports, default=None, on_delete=models.CASCADE)
	shared_by 	  = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	shared_on 	  = models.DateTimeField(auto_now=True)
	shared_with   = models.TextField(default=None, null=True, blank=True)
	active 		  = models.BooleanField(default=True)
	delete 		  = models.BooleanField(default=False)

	class Meta:
		db_table = 'shared_document_data'

	@property
	def is_active(self):
		"Is the shared doc active?"
		return self.active

	@property
	def is_delete(self):
		"Is the shared doc deleted?"
		return self.delete


class ReportComments(models.Model):
	report 		 = models.ForeignKey(Generated_Reports, default=None, on_delete=models.CASCADE)
	comments 	 = models.TextField(default=None, null=True, blank=True)
	commented_by = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	commented_on = models.DateTimeField(auto_now_add=True)
	updated_on 	 = models.DateTimeField(auto_now=True)
	active 		 = models.BooleanField(default=True)
	delete 		 = models.BooleanField(default=False)

	class Meta:
		db_table = 'reportcomments'

	@property
	def is_active(self):
		"Is the comment is active?"
		return self.active

	@property
	def is_delete(self):
		"Is the comment is deleted?"
		return self.delete


class ReviewersWorkdocs(models.Model):
	wdocs_usr_id = models.CharField(max_length=500)
	csr_usr_id	 = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE)
	created_by 	 = models.ForeignKey(settings.AUTH_USER_MODEL, default=None, on_delete=models.CASCADE, related_name='reviewers_workdocs_created_by')
	created_on 	 = models.DateTimeField(auto_now_add=True)
	delete 		 = models.BooleanField(default=False)
	active 		 = models.BooleanField(default=True)

	class Meta:
		db_table = 'reviewers_workdocs'

	@property
	def is_active(self):
		"Is the user is active?"
		return self.active

	@property
	def is_delete(self):
		"Is the user is deleted?"
		return self.delete


class CredInfo(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	key_pass = models.TextField(default=None, blank=True, null=True)
	updated_on 	 = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'credinfo'



class Notifications(models.Model):
	senderId = models.IntegerField()
	receiverId = models.IntegerField()
	messageDateTime = models.DateTimeField(auto_now_add=True)
	message = models.CharField(max_length=3000)
	read = models.BooleanField(default=False, blank=True, null=True)
	event_type = models.CharField(max_length=500, blank=True, null=True)
	projectId = models.IntegerField(default=None)

	class Meta:
		db_table = 'notifications'
