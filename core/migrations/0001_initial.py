# Generated by Django 2.2.6 on 2020-11-18 12:49

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0011_update_proxy_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('is_reviewer', models.BooleanField(default=False)),
                ('phone', models.CharField(blank=True, default=None, max_length=10, null=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='core_user_created_by', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLogEvents',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=150)),
                ('message', models.CharField(max_length=1024)),
            ],
            options={
                'db_table': 'activity_log_events',
            },
        ),
        migrations.CreateModel(
            name='ClientInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_name', models.CharField(error_messages={'unique': 'Client is already existed.'}, max_length=100, unique=True)),
                ('active', models.BooleanField(default=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True, null=True)),
                ('project_count', models.IntegerField(default=0)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'clientinfo',
            },
        ),
        migrations.CreateModel(
            name='Generated_Reports',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('generated_report_path', models.CharField(max_length=200)),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'generated_reports',
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('standard_csr_heading', models.CharField(max_length=1024)),
                ('protocol_headings', models.TextField(blank=True, null=True)),
                ('sar_headings', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'library',
            },
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('senderId', models.IntegerField()),
                ('receiverId', models.IntegerField()),
                ('messageDateTime', models.DateTimeField(auto_now_add=True)),
                ('message', models.CharField(max_length=3000)),
                ('read', models.BooleanField(blank=True, default=False, null=True)),
                ('event_type', models.CharField(blank=True, max_length=500, null=True)),
                ('projectId', models.IntegerField(default=None)),
            ],
            options={
                'db_table': 'notifications',
            },
        ),
        migrations.CreateModel(
            name='ProjectInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=512)),
                ('protocol_id', models.CharField(error_messages={'unique': 'This protocol id already existed.'}, max_length=32, unique=True)),
                ('phase', models.CharField(max_length=16)),
                ('active', models.BooleanField(default=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('generated', models.BooleanField(default=False)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projectinfo',
            },
        ),
        migrations.CreateModel(
            name='TherapeuticArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('therapeutic_area', models.CharField(max_length=512)),
            ],
            options={
                'db_table': 'ikp_therapeutic_area',
            },
        ),
        migrations.CreateModel(
            name='UserProjectCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'usersXprojectCount',
            },
        ),
        migrations.CreateModel(
            name='SharedDocumentData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('folder_id', models.CharField(max_length=500)),
                ('folder_name', models.CharField(max_length=500)),
                ('document_id', models.CharField(max_length=500)),
                ('document_name', models.CharField(max_length=500)),
                ('shared_on', models.DateTimeField(auto_now=True)),
                ('shared_with', models.TextField(blank=True, default=None, null=True)),
                ('active', models.BooleanField(default=True)),
                ('delete', models.BooleanField(default=False)),
                ('report', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.Generated_Reports')),
                ('shared_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'shared_document_data',
            },
        ),
        migrations.CreateModel(
            name='SarFileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sar_document_location', models.FileField(default=None, upload_to='users/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'sar_file_upload',
            },
        ),
        migrations.CreateModel(
            name='SARAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sar_template_location', models.FileField(default=None, upload_to='admin/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'ikp_sar_admin',
            },
        ),
        migrations.CreateModel(
            name='ReviewersWorkdocs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('wdocs_usr_id', models.CharField(max_length=500)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('active', models.BooleanField(default=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='reviewers_workdocs_created_by', to=settings.AUTH_USER_MODEL)),
                ('csr_usr_id', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'reviewers_workdocs',
            },
        ),
        migrations.CreateModel(
            name='ReportComments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comments', models.TextField(blank=True, default=None, null=True)),
                ('commented_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('delete', models.BooleanField(default=False)),
                ('commented_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('report', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='core.Generated_Reports')),
            ],
            options={
                'db_table': 'reportcomments',
            },
        ),
        migrations.CreateModel(
            name='ProtocolFileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol_document_location', models.FileField(default=None, upload_to='users/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'protocol_file_upload',
            },
        ),
        migrations.CreateModel(
            name='ProtocolAdmin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('protocol_template_location', models.FileField(default=None, upload_to='admin/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'ikp_protocol_admin',
            },
        ),
        migrations.CreateModel(
            name='ProjectsXUsers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='projectxusers_created_by', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'projectsXusers',
            },
        ),
        migrations.AddField(
            model_name='projectinfo',
            name='therapeutic_area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea'),
        ),
        migrations.CreateModel(
            name='LogsEmails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(max_length=64)),
                ('to_email', models.CharField(max_length=128)),
                ('from_email', models.CharField(max_length=1024)),
                ('subject', models.CharField(max_length=512)),
                ('message_body', models.CharField(max_length=1024)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('email_sent', models.BooleanField(default=False)),
                ('email_response', models.CharField(blank=True, max_length=2048, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'logs_emails',
            },
        ),
        migrations.CreateModel(
            name='LogsAudit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(blank=True, max_length=100, null=True)),
                ('previous_state', models.TextField(blank=True)),
                ('current_state', models.TextField(blank=True)),
                ('reason', models.CharField(max_length=2048, null=True)),
                ('ip', models.CharField(max_length=100)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('user', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'auditlogs',
            },
        ),
        migrations.CreateModel(
            name='LogsActivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=1024)),
                ('created_on', models.DateTimeField(auto_now=True)),
                ('sessionid', models.CharField(max_length=256)),
                ('ip', models.CharField(blank=True, max_length=100, null=True)),
                ('event', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='core.ActivityLogEvents')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'logs_activity',
            },
        ),
        migrations.CreateModel(
            name='GlobalMappingTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csr_heading', models.CharField(max_length=1024)),
                ('source_file', models.CharField(max_length=1024, null=True)),
                ('copy_headings', models.CharField(max_length=2048, null=True)),
                ('parent_id', models.CharField(default=0, max_length=1024)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
            ],
            options={
                'db_table': 'global_mapping_table',
            },
        ),
        migrations.AddField(
            model_name='generated_reports',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo'),
        ),
        migrations.AddField(
            model_name='generated_reports',
            name='therapeutic_area',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea'),
        ),
        migrations.CreateModel(
            name='FinalCSRFileUpload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('finalcsr_document_location', models.FileField(default=None, upload_to='finalcsr/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'final_csr_file_upload',
            },
        ),
        migrations.CreateModel(
            name='EmailConfiguration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email_host', models.CharField(max_length=1024)),
                ('email_host_user', models.CharField(max_length=255)),
                ('email_host_password', models.CharField(blank=True, max_length=255, null=True)),
                ('email_port', models.PositiveSmallIntegerField(default=587)),
                ('email_default_mail', models.CharField(blank=True, max_length=255, null=True)),
                ('email_use_tls', models.BooleanField(default=True)),
                ('email_fail_silently', models.BooleanField(default=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'email_configuration',
            },
        ),
        migrations.CreateModel(
            name='CustomMappingTable',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csr_heading', models.CharField(max_length=1024)),
                ('source_file', models.CharField(max_length=1024, null=True)),
                ('copy_headings', models.CharField(max_length=2048, null=True)),
                ('parent_id', models.CharField(default=0, max_length=1024)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
            ],
            options={
                'db_table': 'custom_mapping_table',
            },
        ),
        migrations.CreateModel(
            name='CSRTemplateUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csr_template_location', models.FileField(default=None, upload_to='users/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'ikp_csrtemplateuser',
            },
        ),
        migrations.CreateModel(
            name='CSRTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csr_template_location', models.FileField(default=None, upload_to='admin/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('delete', models.BooleanField(default=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ClientInfo')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'ikp_csrtemplate',
            },
        ),
        migrations.CreateModel(
            name='CredInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key_pass', models.TextField(blank=True, default=None, null=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'credinfo',
            },
        ),
        migrations.CreateModel(
            name='AnotherFileUploadUserInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_name', models.CharField(max_length=100)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'another_file_upload_user_info',
            },
        ),
        migrations.CreateModel(
            name='AnotherFileUploadUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('another_document_location', models.FileField(default=None, upload_to='users/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['docx'])])),
                ('version_no', models.CharField(blank=True, max_length=10, null=True)),
                ('uploaded_on', models.DateTimeField(auto_now_add=True)),
                ('delete', models.BooleanField(default=False)),
                ('comments', models.CharField(blank=True, max_length=512, null=True)),
                ('created_by', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.ProjectInfo')),
                ('therapeutic_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TherapeuticArea')),
            ],
            options={
                'db_table': 'another_file_upload_user',
            },
        ),
    ]
