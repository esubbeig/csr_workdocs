import json
import os
import ntpath
import logging
import math
import decimal
import traceback
from operator import itemgetter
from datetime import datetime, timedelta
from threading import Thread

from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect, HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, SetPasswordForm
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from django.urls import reverse
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import EmailMessage, get_connection, EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.views import View

from .admin_operations import *
from .user_operations import *
from .models import *
from .forms import *
from .token_generator import *
from .generate_csr import *
from .edit_csr_mapping import *
from .admin_csr_mapping import *
from .audit import *
from .load_library import *
from .workdocs import *
from .data_encrypt import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_NAME = BASE_DIR.split('\\')[-1]

csr_logger = logging.getLogger('csr')
csr_except_logger = logging.getLogger('csr_except')


# To handle email sending
def EmailThread(event, email, to_email, from_email, email_subject, html_content, created_by):

    email_status = email.send()

    # recording Email logs
    e_log = LogsEmails(

            event = 'Assign Project',
            to_email = to_email,
            from_email = from_email,
            subject = email_subject,
            message_body = html_content,
            email_sent = email_status,
            created_by = created_by

        )
    e_log.save()
    
    return email_status


def release_note(request):
    return render(request, 'releasenote.html')

def handler404(request, exception):
    return render(request,'404.html', status=404)

def handler500(request):
    return render(request,'500.html', status=500)

def handler400(request, exception):
    return render(request,'400.html', status=400)

def handler403(request, exception):
    return render(request,'403.html', status=403)

def home(request):

    try:

        if request.user.is_authenticated:

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None
            
            if request.user.is_superuser:
                projects = ProjectInfo.objects.all()
                template = 'admin_projects.html'                
            else:
                projects = get_user_projects(request.user.id)
                template = 'user_projects.html'

            return render(request, template, {'projects' : projects, 'latest_client' : latest_client,})

        else:
            return redirect('login')

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def add_user(request):

    try:

        if request.is_ajax():

            data = {}
            # fetching smtp configurations
            try:
                config  = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None

            if request.method == 'POST':

                try:
                    form = SignUpForm(request.POST)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():
                    user = form.save(commit=False)
                    user.is_active = False
                    user.created_by = request.user
                    user.set_unusable_password()
                    user.save()

                    username = form.cleaned_data.get('username')

                    # Updating the ProjectXCount modal
                    temp_count = UserProjectCount(user=user)
                    temp_count.save()

                    
                    #to send confirmation mail                    
                    backend = EmailBackend(

                        host          = config.email_host,
                        username      = config.email_host_user,
                        password      = config.email_host_password,
                        port          = config.email_port,
                        use_tls       = True,
                        fail_silently = True

                    )
                    from_email = config.email_default_mail
                    current_site = get_current_site(request)
                    email_subject = 'Activate Your Account with CSR'
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    token = account_activation_token.make_token(user)
                    activation_link = "http://{0}/set_password/?uid={1}".format(current_site, uid)
                    # message = "Dear {0},\n {1}" .format(user.username, activation_link)
                    to_email = form.cleaned_data.get('email')
                    html_content = "<h3>Dear <b>"+ user.username +"</b>,</h3><br>A new account was created with CSR. To make use of your account, first you need to set the password. Please follow the below link.<br><br><a href='"+ activation_link + "'><button style='background-color: #4CAF50; border: none; color: white; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px;'>Activate</button></a><br><br><b>Thanks & Regards<br>CSR Automation</b>"
                    # html_content = "hello"
                    email = EmailMessage(subject=email_subject, body=html_content, from_email=from_email, to=[to_email], connection=backend)
                    email.content_subtype = 'html'
                    email_status = email.send()

                    # recording Email logs
                    e_log = LogsEmails(

                            event = 'Create User',
                            to_email = to_email,
                            from_email = from_email,
                            subject = email_subject,
                            message_body = html_content,
                            email_sent = email_status,
                            created_by = request.user

                        )
                    if email_status:
                        e_log.email_response = "Email sent scuccessfully"
                        data['mail_status'] = True
                        messages.success(request, "Confirmation mail send to the registered mail! Please activate")
                        # recording logging
                        csr_logger.info(username + " is successfully created by " + request.user.username + " & email sent.")

                    else:
                        e_log.email_response = "Not able to connect SMTP server"
                        data['mail_status'] = False
                        messages.error(request, "Problem with connecting SMTP server. Please check the Email Configurations!")
                        # recording logging
                        csr_except_logger.critical("Not able to connect SMTP server while creating " + username)

                    e_log.save()

                    #recording activity log
                    event = 'Add User'
                    record_user_activity_log(
                        event       = event,
                        actor       = request.user, 
                        dif_user    = username, 
                        session_id  = request.session.session_key,
                        client_ip = get_client_ip(request)
                        )

                    # recording audit log
                    pre = ''
                    post = username
                    reason = 'Added'
                    client_ip = request.META['REMOTE_ADDR']
                    adduser_audit(pre, post, request.user, reason, client_ip)


                    data['form_is_valid'] = True

                else:
                    data['form_is_valid'] = False

            else:
                form = SignUpForm()

                #recording activity log
                event = 'Nav Add User'
                record_user_activity_log(
                    event       = event,
                    actor       = request.user, 
                    session_id  = request.session.session_key,
                    client_ip = get_client_ip(request)
                    )

            context = {
                'form' : form,
                'config' : config,
            }
            data['html_form'] = render_to_string('registration/signup.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to set the password first time when user is created
def set_password(request):

    try:

        uidb64 = request.GET.get('uid')
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user is not None:

            if user.has_usable_password():

                return HttpResponse('Sorry, You have already set your password. Please contact Admin!')
            
            else:

                status = 0
                user.is_active = True
                user.save()
                login(request, user)
        
                if request.method == 'POST':

                    password = request.POST.get('new_password1')

                    try:
                        form = SetPasswordForm(request.user, request.POST)
                    except Exception as e:
                        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                    if form.is_valid():
                        user = form.save()
                        update_session_auth_hash(request, user)

                        # storing encrypted password in another table
                        encrypted_password = encrypt_message(password)
                        obj, created =  CredInfo.objects.get_or_create(user=request.user)
                        obj.key_pass = encrypted_password
                        obj.save()

                        logout(request)
                        return render(request, 'registration/set_password_success.html')
                        status = 1

                    else:
                        pass

                else:
                    form = SetPasswordForm(request.user)

                if status == 0:
                    user.is_active = False
                    user.save()

                return render(request, 'registration/activate_set_password.html', {'form' : form})

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to reset the password if user forgets the password
def reset_password(request):

    try:

        uidb64 = request.GET.get('uid')
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if user is not None:

            if user.is_active:

                login(request, user)
                
                if request.method == 'POST':

                    password = request.POST.get('new_password1')

                    try:
                        form = SetPasswordForm(request.user, request.POST)
                    except Exception as e:
                        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                    if form.is_valid():
                        user = form.save()
                        update_session_auth_hash(request, user)

                        # storing encrypted password in another table
                        encrypted_password = encrypt_message(password)
                        obj, created =  CredInfo.objects.get_or_create(user=request.user)
                        obj.key_pass = encrypted_password
                        obj.save()

                        logout(request)
                        return render(request, 'registration/reset_password_success.html')

                    else:
                        # messages.error(request, 'Passwords mismatched!')
                        pass

                else:
                    form = SetPasswordForm(request.user)

                return render(request, 'registration/reset_password.html', {'form' : form})

            else:
                return HttpResponse('Sorry, Your account has been disabled, please contact Admin!')

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle forgot password
def forgot_password(request):

    try:

        if request.method == 'POST':

            to_email = request.POST['email']

            try:
                user = User.objects.get(email=to_email)
            except User.DoesNotExist:
                user = None


            if user is not None:

                if user.is_active:

                    #to send forgot password mail
                    config  = EmailConfiguration.objects.last()
                    backend = EmailBackend(

                        host          = config.email_host,
                        username      = config.email_host_user,
                        password      = config.email_host_password,
                        port          = config.email_port,
                        use_tls       = True,
                        fail_silently = True
                    )
                    from_email            = config.email_default_mail
                    current_site          = get_current_site(request)
                    email_subject         = 'Reset your Account Password with CSR'
                    uid                   = urlsafe_base64_encode(force_bytes(user.pk))
                    password_reset_link   = "http://{0}/reset_password/?uid={1}".format(current_site, uid)
                    html_content          = "<h3>Dear <b>"+ user.username +"</b>,</h3><br>We got a request to reset your password with CSR. Please follow the below link.<br><br>"+ password_reset_link + "<br><br><b>Thanks & Regards<br>CSR Automation</b>"
                    email                 = EmailMessage(subject=email_subject, body=html_content, from_email=from_email, to=[to_email], connection=backend)
                    email.content_subtype = 'html'
                    email_status          = email.send()

                    # recording Email logs
                    e_log = LogsEmails(

                            event        = 'Forgot Password',
                            to_email     = to_email,
                            from_email   = from_email,
                            subject      = email_subject,
                            message_body = html_content,
                            email_sent   = email_status,
                            created_by   = User.objects.get(email=to_email)
                        )
                    if email_status:
                        e_log.email_response = "Email sent scuccessfully"

                    else:
                        e_log.email_response = "Not able to connect SMTP server"                    

                    e_log.save()

                    if email_status:
                        messages.success(request, 'A password reset link has been sent to your email')
                    else:
                        messages.error(request, 'Failed! to send reset password link. Please try after some time.')

                else:
                    messages.error(request, 'Sorry, Your account has been disabled. Please contact Admin!')

            else:
                messages.error(request, 'No user found with given email')
                

        return render(request, 'registration/forgot_password.html')

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# to handle login request
def login_request(request):

    try:

        if request.user.is_authenticated:

            return redirect('/')
        
        if request.method == 'POST':

            try:
                form = AuthenticationForm(request, request.POST)
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        messages.success(request, "You are logged in as " + username)

                        #recording user acivity log
                        event = 'Login'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            session_id  = request.session.session_key,
                            client_ip = get_client_ip(request)
                            )

                        return redirect('home')
                        
                    else:
                        messages.error(request, "Your account is disabled!")
                else:
                    messages.error(request, 'Invalid username or password')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            form = AuthenticationForm()

        return render(request, 'registration/login.html', {'form' : form})

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle login request
@login_required(login_url='/')
def logout_request(request):

    try:
        #recording user acivity log
        event = 'Logout'
        record_user_activity_log(
            event       = event, 
            actor       = request.user,
            session_id  = request.session.session_key,
            client_ip = get_client_ip(request)
            )

        logout(request)
        return redirect('home')

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle change password request
@login_required(login_url='/')
def change_password(request):

    try:

        if request.is_ajax():

            data = {}

            if request.method == 'POST':

                try:
                    form = PasswordChangeForm(request.user, request.POST)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():

                    updated_pass = request.POST.get('new_password1')

                    req_user = User.objects.get(pk=request.user.id)

                    if not req_user.check_password(updated_pass):

                        user = form.save()

                        update_session_auth_hash(request, user)

                        # storing passwords seperately in another table
                        encrypted_password = encrypt_message(updated_pass)

                        obj, created =  CredInfo.objects.get_or_create(user=request.user)
                        obj.key_pass = encrypted_password
                        obj.save()

                        #recording user acivity log
                        event = 'Change Password'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            session_id  = request.session.session_key,
                            client_ip = get_client_ip(request)
                            )

                        messages.success(request, "Password changed successfully")

                        data['form_is_valid'] = True

                    else:

                        data['form_is_valid'] = False
                        data['old_pass'] = True

                else:
                    data['form_is_valid'] = False
            else:
                form = PasswordChangeForm(request.user)

                # recording activity log
                event = 'Nav Change Password'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )
                
            context = {
                'form' : form
            }
            data['html_form'] = render_to_string('registration/change_password.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#to activate the users
@login_required(login_url='/')
def activate_user(request, usr_id):

    try:

        if request.user.is_superuser:

            usr = User.objects.get(pk=usr_id)

            if usr.has_usable_password():

                usr.is_active = True
                usr.save()
                messages.success(request, usr.username + ' has been activated successfully!')

                #recording user acivity log
                event = 'Activate User'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user, 
                    dif_user    = usr.username, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            else:
                messages.error(request, 'Sorry! '+ usr.username +' not set the password yet!')

            return redirect('get_all_users_details')

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#to deactivate the users
@login_required(login_url='/')
def deactivate_user(request, usr_id):

    try:

        if request.user.is_superuser:

            usr = User.objects.get(pk=usr_id)
            usr.is_active = False
            usr.save()
            messages.success(request, usr.username + ' has been deactivated successfully!')

            #recording user acivity log
            event = 'Deactivate User'
            record_user_activity_log(
                event       = event, 
                actor       = request.user, 
                dif_user    = usr.username, 
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

            return redirect('get_all_users_details')

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle admin csr template upload
@login_required(login_url='/')
def upload_csr_admin(request, cli_id):

    try:

        if request.is_ajax() and request.user.is_superuser:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            try:
                vn = CSRTemplate.objects.filter(client=cli_id).latest('id')
                pre = 'Version : ' + vn.version_no
            except CSRTemplate.DoesNotExist:
                pre = ''

            try:
                req_client = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            if request.method == 'POST':

                version          = request.POST['version']
                file_Name        = request.FILES['csr_template_location']

                try:
                    form = GlobalCsrUploadForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))            

                if form.is_valid():
                    
                    fr__mt = check_file_content(file_Name)

                    if fr__mt == '':

                        dd = form.save(commit=False)
                        dd.created_by = request.user
                        dd.client = req_client

                        try:
                            obj = CSRTemplate.objects.filter(client=req_client).latest('id').version_no
                        except CSRTemplate.DoesNotExist:
                            obj = None

                        if obj is not None:

                            if version == '0.1':
                                ver, rev = obj.split('.')
                                obj = ver + '.' + str(int(rev) + 1)

                                # obj = obj + decimal.Decimal(float(version))
                            else:
                                ver, rev = obj.split('.')
                                obj = str(int(ver)+1) + '.' + str(0)
                                # obj = obj + decimal.Decimal(float(version))
                                # obj = decimal.Decimal(float(math.floor(obj)))

                        else:
                            obj = version
                            # obj = decimal.Decimal(float(version))

                        dd.version_no = obj
                        dd.save()
                        # Deleting premapped data in GlobalMappingTable
                        try:
                            GlobalMappingTable.objects.filter(client=req_client).delete()
                        except Exception as e:
                            csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


                        messages.success(request, "Global CSR has been uploaded successfully!")

                        #recording user acivity log
                        event = 'CSR Upload'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            client      = req_client.client_name,
                            session_id  = request.session.session_key,
                            client_ip   = get_client_ip(request)
                            )

                        try:
                            vn = CSRTemplate.objects.filter(client=cli_id).latest('id')
                            post = 'Version : ' + vn.version_no
                            reason = vn.comments
                        except CSRTemplate.DoesNotExist:
                            post = ''
                            reason = ''

                        # recording audit log
                        client_ip = request.META['REMOTE_ADDR']
                        upload_csr_admin_audit(pre, post, request.user, reason, client_ip, req_client)

                        data['form_is_valid'] = True
                        data['file_data_format'] = ''

                    else:
                        data['form_is_valid'] = False
                        data['file_data_format'] = fr__mt

                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''
            else:
                form = GlobalCsrUploadForm()

                #recording user acivity log
                event = 'Nav CSR Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    client      = req_client.client_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'req_client' : req_client,
            }

            data['html_form'] = render_to_string('upload_global_csr_admin.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle admin protocol upload
@login_required(login_url='/')
def upload_protocol_admin(request, cli_id):

    try:

        if request.is_ajax() and request.user.is_superuser:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            try:
                vn = ProtocolAdmin.objects.filter(client=cli_id).latest('id')
                pre = 'Version : ' + vn.version_no
            except ProtocolAdmin.DoesNotExist:
                pre = ''

            try:
                req_client = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            if request.method == 'POST':

                version          = request.POST['version']
                file_Name        = request.FILES['protocol_template_location']

                try:
                    form = ProtocolUploadAdminForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():

                    fr__mt = check_file_content(file_Name)
                    
                    if fr__mt == '':

                        dd = form.save(commit=False)
                        dd.created_by = request.user
                        dd.client = req_client

                        try:
                            obj = ProtocolAdmin.objects.filter(client=req_client).latest('id').version_no
                        except ProtocolAdmin.DoesNotExist:
                            obj = None

                        if obj is not None:

                            if version == '0.1':
                                ver, rev = obj.split('.')
                                obj = ver + '.' + str(int(rev) + 1)

                                # obj = obj + decimal.Decimal(float(version))
                            else:
                                ver, rev = obj.split('.')
                                obj = str(int(ver)+1) + '.' + str(0)
                                # obj = obj + decimal.Decimal(float(version))
                                # obj = decimal.Decimal(float(math.floor(obj)))

                        else:
                            obj = version
                            # obj = decimal.Decimal(float(version))

                        dd.version_no = obj
                        dd.save()
                        messages.success(request, "Protocol has been uploaded successfully!")

                        event = 'Upload Protocol'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            client      = req_client.client_name,
                            session_id  = request.session.session_key,
                            client_ip   = get_client_ip(request)
                            )

                        try:
                            vn = ProtocolAdmin.objects.filter(client=cli_id).latest('id')
                            post = 'Version : ' + vn.version_no
                            reason = vn.comments
                        except ProtocolAdmin.DoesNotExist:
                            post = ''
                            reason = ''

                        # recording audit log
                        client_ip = request.META['REMOTE_ADDR']
                        upload_protocol_admin_audit(pre, post, request.user, reason, client_ip, req_client)

                        data['form_is_valid'] = True
                        data['file_data_format'] = ''

                    else:
                        data['form_is_valid'] = False
                        data['file_data_format'] = fr__mt

                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''
            else:
                form = ProtocolUploadAdminForm()

                # recording activity log
                event = 'Nav Upload Protocol'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    client      = req_client.client_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'req_client' : req_client,
            }

            data['html_form'] = render_to_string('upload_protocol_admin.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle admin sar upload
@login_required(login_url='/')
def upload_sar_admin(request, cli_id):

    try:

        if request.is_ajax() and request.user.is_superuser:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            try:
                vn = SARAdmin.objects.filter(client=cli_id).latest('id')
                pre = 'Version : ' + vn.version_no
            except SARAdmin.DoesNotExist:
                pre = ''

            try:
                req_client = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            if request.method == 'POST':

                version          = request.POST['version']

                try:
                    form = SARUploadAdminForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():
                    
                    dd = form.save(commit=False)
                    dd.created_by = request.user
                    dd.client = req_client

                    try:
                        obj = SARAdmin.objects.filter(client=req_client).latest('id').version_no
                    except SARAdmin.DoesNotExist:
                        obj = None

                    if obj is not None:

                        if version == '0.1':
                            ver, rev = obj.split('.')
                            obj = ver + '.' + str(int(rev) + 1)

                            # obj = obj + decimal.Decimal(float(version))
                        else:
                            ver, rev = obj.split('.')
                            obj = str(int(ver)+1) + '.' + str(0)
                            # obj = obj + decimal.Decimal(float(version))
                            # obj = decimal.Decimal(float(math.floor(obj)))

                    else:
                        obj = version
                        # obj = decimal.Decimal(float(version))

                    dd.version_no = obj
                    dd.save()
                    messages.success(request, "SAR has been uploaded successfully!")

                    # recording activity log
                    event = 'Upload SAR'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        client      = req_client.client_name,
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    try:
                        vn = SARAdmin.objects.filter(client=cli_id).latest('id')
                        post = 'Version : ' + vn.version_no
                        reason = vn.comments
                    except SARAdmin.DoesNotExist:
                        post = ''
                        reason = ''

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    upload_sar_admin_audit(pre, post, request.user, reason, client_ip, req_client)

                    data['form_is_valid'] = True
                else:
                    data['form_is_valid'] = False
            else:
                form = SARUploadAdminForm()

                # recording activity log
                event = 'Nav Upload SAR'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    client      = req_client.client_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'req_client' : req_client,
            }

            data['html_form'] = render_to_string('upload_sar_admin.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# this handle globaL csr upload functionality
@login_required(login_url='/')
def global_csr_upload(request, cli_id):

    try:

        try:
            req_client = ClientInfo.objects.get(pk=cli_id)
        except ClientInfo.DoesNotExist:
            req_client = None

        if request.user.is_superuser and req_client.is_active:

            therapeutic_area_list = TherapeuticArea.objects.all()
            client_list = ClientInfo.objects.filter(active=True)

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            try:
                csr_doc_latest = CSRTemplate.objects.filter(client=req_client).latest('id')
            except CSRTemplate.DoesNotExist:
                csr_doc_latest = None
            try:
                csr_doc_list = CSRTemplate.objects.filter(client=req_client).order_by('-created_on')[1:]
            except CSRTemplate.DoesNotExist:
                csr_doc_list = None

            try:
                protocol_doc_latest = ProtocolAdmin.objects.filter(client=req_client).latest('id')
            except ProtocolAdmin.DoesNotExist:
                protocol_doc_latest = None
            try:
                protocol_doc_list = ProtocolAdmin.objects.filter(client=req_client).order_by('-created_on')[1:]
            except ProtocolAdmin.DoesNotExist:
                protocol_doc_list = None

            try:
                sar_doc_latest = SARAdmin.objects.filter(client=req_client).latest('id')
            except SARAdmin.DoesNotExist:
                sar_doc_latest = None
            try:
                sar_doc_list = SARAdmin.objects.filter(client=req_client).order_by('-created_on')[1:]
            except SARAdmin.DoesNotExist:
                sar_doc_list = None
                
            context = {
                'csr_doc_latest'      : csr_doc_latest,
                'csr_doc_list'        : csr_doc_list,
                'protocol_doc_latest' : protocol_doc_latest,
                'protocol_doc_list'   : protocol_doc_list,
                'sar_doc_latest'      : sar_doc_latest,
                'sar_doc_list'        : sar_doc_list,
                'client_list'         : client_list,
                'latest_client'       : latest_client,
                'req_client'          : req_client,
            }

            return render(request, 'global_csr_upload.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



#this handle the csr upload operation in each project of user
@login_required(login_url='/')
def csr_upload(request, usr_id, pro_id):

    try:

        proj = ProjectInfo.objects.get(pk=pro_id)

        is_belongs = ProjectsXUsers.objects.get(project=proj, user=request.user)

        try:
            vn = CSRTemplateUser.objects.filter(project=pro_id).latest('id')
            pre = 'Version : ' + vn.version_no
        except CSRTemplateUser.DoesNotExist:
            pre = ''

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            if request.method == 'POST':

                version          = request.POST['version']
                file_Name        = request.FILES['csr_template_location']

                try:
                    form = CsrUploadForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
                
                if form.is_valid():

                    fr__mt = check_file_content(file_Name)

                    if fr__mt == '':

                        dd = form.save(commit=False)
                        dd.project = proj
                        dd.created_by = request.user

                        try:
                            obj = CSRTemplateUser.objects.filter(project=pro_id).latest('id').version_no
                        except CSRTemplateUser.DoesNotExist:
                            obj = None

                        if obj is not None:

                            if version == '0.1':
                                ver, rev = obj.split('.')
                                obj = ver + '.' + str(int(rev) + 1)

                                # obj = obj + decimal.Decimal(float(version))
                            else:
                                ver, rev = obj.split('.')
                                obj = str(int(ver)+1) + '.' + str(0)
                                # obj = obj + decimal.Decimal(float(version))
                                # obj = decimal.Decimal(float(math.floor(obj)))

                        else:
                            obj = version
                            # obj = decimal.Decimal(float(version))

                        dd.version_no = obj
                        dd.save()

                        # Deleting premapped data in GlobalMappingTable
                        try:
                            CustomMappingTable.objects.filter(project=pro_id).delete()
                        except Exception as e:
                            csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                        # Logging activity log
                        event = 'Custom CSR Upload'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            proj_name   = proj.project_name, 
                            session_id  = request.session.session_key,
                            client_ip   = get_client_ip(request)
                            )

                        try:
                            vn = CSRTemplateUser.objects.filter(project=pro_id).latest('id')
                            post = 'Version : ' + vn.version_no
                            reason = vn.comments
                        except CSRTemplateUser.DoesNotExist:
                            post = ''
                            reason = ''

                        # recording audit log
                        client_ip = request.META['REMOTE_ADDR']
                        upload_csr_user_audit(pre, post, request.user, reason, client_ip, proj)

                        messages.success(request, "Custom CSR has been uploaded successfully!")
                        data['form_is_valid'] = True
                        data['file_data_format'] = ''

                    else:
                        data['form_is_valid'] = False
                        data['file_data_format'] = fr__mt


                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''

            else:
                form = CsrUploadForm()

                # Logging activity log
                event = 'Nav Custom CSR Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = proj.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'proj' : proj
            }
            data['html_form'] = render_to_string('csr_upload.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this handle the protocol upload operation in each project of user
@login_required(login_url='/')
def protocol_file_upload(request, usr_id, pro_id):

    try:

        proj = ProjectInfo.objects.get(pk=pro_id)

        is_belongs = ProjectsXUsers.objects.get(project=proj, user=request.user)

        try:
            vn = ProtocolFileUpload.objects.filter(project=pro_id).latest('id')
            pre = 'Version : ' + vn.version_no
        except ProtocolFileUpload.DoesNotExist:
            pre = ''

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            if request.method == 'POST':

                version          = request.POST['version']
                file_Name        = request.FILES['protocol_document_location']

                try:
                    form = ProtocolFileUploadForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
                
                if form.is_valid():

                    fr__mt = check_file_content(file_Name)

                    if fr__mt == '':

                        dd = form.save(commit=False)
                        dd.project = proj
                        dd.created_by = request.user

                        try:
                            obj = ProtocolFileUpload.objects.filter(project=pro_id).latest('id').version_no
                        except ProtocolFileUpload.DoesNotExist:
                            obj = None

                        if obj is not None:

                            if version == '0.1':
                                ver, rev = obj.split('.')
                                obj = ver + '.' + str(int(rev) + 1)

                                # obj = obj + decimal.Decimal(float(version))
                            else:
                                ver, rev = obj.split('.')
                                obj = str(int(ver)+1) + '.' + str(0)
                                # obj = obj + decimal.Decimal(float(version))
                                # obj = decimal.Decimal(float(math.floor(obj)))

                        else:
                            obj = version
                            # obj = decimal.Decimal(float(version))

                        dd.version_no = obj
                        dd.save()

                        # Logging activity log
                        event = 'Protocol Upload'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            proj_name   = proj.project_name, 
                            session_id  = request.session.session_key,
                            client_ip   = get_client_ip(request)
                            )

                        try:
                            vn = ProtocolFileUpload.objects.filter(project=pro_id).latest('id')
                            post = 'Version : ' + vn.version_no
                            reason = vn.comments
                        except ProtocolFileUpload.DoesNotExist:
                            post = ''
                            reason = ''

                        # recording audit log
                        client_ip = request.META['REMOTE_ADDR']
                        upload_protocol_user_audit(pre, post, request.user, reason, client_ip, proj)


                        messages.success(request, "Protocol has been uploaded successfully!")
                        data['form_is_valid'] = True
                        data['file_data_format'] = ''

                    else:
                        data['form_is_valid'] = False
                        data['file_data_format'] = fr__mt
                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''
            else:
                form = ProtocolFileUploadForm()

                # Logging activity log
                event = 'Nav Protocol Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = proj.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'proj' : proj
            }
            data['html_form'] = render_to_string('protocol_upload.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this handle the sar upload operation in each project of user
@login_required(login_url='/')
def sar_file_upload(request, usr_id, pro_id):

    try:

        proj = ProjectInfo.objects.get(pk=pro_id)

        is_belongs = ProjectsXUsers.objects.get(project=proj, user=request.user)

        try:
            vn = SarFileUpload.objects.filter(project=pro_id).latest('id')
            pre = 'Version : ' + vn.version_no
        except SarFileUpload.DoesNotExist:
            pre = ''

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            if request.method == 'POST':

                version  = request.POST['version']

                try:
                    form = SarFileUploadForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():
                    dd = form.save(commit=False)
                    dd.project = proj
                    dd.created_by = request.user

                    try:
                        obj = SarFileUpload.objects.filter(project=pro_id).latest('id').version_no
                    except SarFileUpload.DoesNotExist:
                        obj = None

                    if obj is not None:

                        if version == '0.1':
                            ver, rev = obj.split('.')
                            obj = ver + '.' + str(int(rev) + 1)

                            # obj = obj + decimal.Decimal(float(version))
                        else:
                            ver, rev = obj.split('.')
                            obj = str(int(ver)+1) + '.' + str(0)
                            # obj = obj + decimal.Decimal(float(version))
                            # obj = decimal.Decimal(float(math.floor(obj)))

                    else:
                        obj = version
                        # obj = decimal.Decimal(float(version))

                    dd.version_no = obj
                    dd.save()
                    # logging activity log
                    event = 'SAR Upload'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        proj_name   = proj.project_name, 
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    try:
                        vn = SarFileUpload.objects.filter(project=pro_id).latest('id')
                        post = 'Version : ' + vn.version_no
                        reason = vn.comments
                    except SarFileUpload.DoesNotExist:
                        post = ''
                        reason = ''

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    upload_sar_user_audit(pre, post, request.user, reason, client_ip, proj)


                    messages.success(request, "SAR has been uploaded successfully!")
                    data['form_is_valid'] = True

                else:
                    data['form_is_valid'] = False

            else:
                form = SarFileUploadForm()

                # logging activity log
                event = 'Nav SAR Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = proj.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'proj' : proj
            }
            data['html_form'] = render_to_string('sar_upload.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this handle the another document upload operation in each project of user
@login_required(login_url='/')
def another_file_upload(request, usr_id, pro_id):

    try:

        proj = ProjectInfo.objects.get(pk=pro_id)

        is_belongs = ProjectsXUsers.objects.get(project=proj, user=request.user)

        try:
            vn = AnotherFileUploadUser.objects.filter(project=pro_id).latest('id')
            pre = 'Version : ' + vn.version_no
        except AnotherFileUploadUser.DoesNotExist:
            pre = ''

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            is_another_doc_available = AnotherFileUploadUserInfo.objects.get(project=pro_id)

            if request.method == 'POST':

                version  = request.POST['version']
                file_Name = request.FILES['another_document_location']

                try:
                    form = AnotherFileUploadUserForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():

                    fr__mt = check_file_content(file_Name)

                    if fr__mt == '':

                        dd = form.save(commit=False)
                        dd.project = proj
                        dd.created_by = request.user

                        try:
                            obj = AnotherFileUploadUser.objects.filter(project=pro_id).latest('id').version_no
                        except AnotherFileUploadUser.DoesNotExist:
                            obj = None

                        if obj is not None:

                            if version == '0.1':
                                ver, rev = obj.split('.')
                                obj = ver + '.' + str(int(rev) + 1)

                                # obj = obj + decimal.Decimal(float(version))
                            else:
                                ver, rev = obj.split('.')
                                obj = str(int(ver)+1) + '.' + str(0)
                                # obj = obj + decimal.Decimal(float(version))
                                # obj = decimal.Decimal(float(math.floor(obj)))

                        else:
                            obj = version
                            # obj = decimal.Decimal(float(version))

                        dd.version_no = obj
                        dd.save()
                        # logging activity log
                        event = 'Another Doc Upload'
                        record_user_activity_log(
                            event       = event, 
                            actor       = request.user,
                            proj_name   = proj.project_name,
                            source_name = is_another_doc_available.source_name,
                            session_id  = request.session.session_key,
                            client_ip   = get_client_ip(request)
                            )

                        try:
                            vn = AnotherFileUploadUser.objects.filter(project=pro_id).latest('id')
                            post = 'Version : ' + vn.version_no
                            reason = vn.comments
                        except AnotherFileUploadUser.DoesNotExist:
                            post = ''
                            reason = ''

                        # recording audit log
                        client_ip = request.META['REMOTE_ADDR']
                        upload_another_user_audit(is_another_doc_available.source_name, pre, post, request.user, reason, client_ip, proj)



                        messages.success(request, is_another_doc_available.source_name + " has been uploaded successfully!")
                        data['form_is_valid'] = True
                        data['file_data_format'] = ''

                    else:
                        data['form_is_valid'] = False
                        data['file_data_format'] = fr__mt

                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''
            else:
                form = AnotherFileUploadUserForm()

                # logging activity log
                event = 'Nav Another Doc Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = proj.project_name,
                    source_name = is_another_doc_available.source_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'proj' : proj,
                'is_another_doc_available' : is_another_doc_available
            }
            data['html_form'] = render_to_string('another_upload_user.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def create_project(request, usr_id):

    try:

        if request.user.id == int(usr_id) and request.is_ajax():
    
            therapeutic_area_list = TherapeuticArea.objects.all()
            client_list = ClientInfo.objects.filter(active=True)

            data = {}

            if request.method == 'POST':

                try:
                    form = CreateProjectForm(request.POST or None)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():
                    dd = form.save(commit=False)
                    dd.created_by   = request.user
                    dd.save()
                    #updating projectsXusers
                    projectxusers = ProjectsXUsers(project=dd, user=request.user, created_by=request.user)
                    projectxusers.save()
                    #updating userprojectcount
                    try:
                        y = ProjectsXUsers.objects.filter(user=usr_id, active=True).count()
                        proj_count = UserProjectCount.objects.get(user=usr_id)
                        proj_count.project_count = y
                        proj_count.save()
                    except:
                        pass

                    # updating clientprojectcount
                    try:
                        z = ClientInfo.objects.get(pk=form.cleaned_data.get('client').id)
                        z.project_count += 1
                        z.save()
                    except:
                        pass
                    
                    messages.success(request, "Project has been created successfully!")
                    data['form_is_valid'] = True

                    # recording audit log
                    pre = ''
                    post = form.cleaned_data.get('project_name')
                    reason = 'created a new project'
                    client_ip = request.META['REMOTE_ADDR']
                    createproj_audit(pre, dd, request.user, reason, client_ip, dd)

                    #recording activity log
                    event = 'Create Project'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user, 
                        proj_name   = dd.project_name, 
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    # adding to notifcation table
                    if not request.user.is_superuser:
                        notif_obj = Notifications(
                                senderId = request.user.id,
                                receiverId = 1,
                                message = request.user.username + ' created a new project - ' + request.POST.get('project_name'),
                                event_type = 'create_project',
                                projectId = dd.id
                            )
                        notif_obj.save()

                else:
                    data['form_is_valid'] = False
            else:
                form = CreateProjectForm()

                #recording activity log
                event = 'Click Create Project Btn'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'client_list' : client_list
            }
            data['html_form'] = render_to_string('create_project.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

    

# to hanlde assign projects in admin
@login_required(login_url='/')
def assign_project_new(request, prj_id):

    try:

        if request.user.is_superuser and request.is_ajax():

            post = []

            post_assigned_user_emails = []

            project = ProjectInfo.objects.get(pk=prj_id)

            # fetching SMTP configurations
            try:
                config  = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None

            pre_assigned_user_ids_all = set(ProjectsXUsers.objects.filter(project=prj_id).values_list('user', flat=True))

            # fetching active pre assigned users
            pre_assigned_users = ProjectsXUsers.objects.filter(project=prj_id, active=True)
            pre = set(pre_assigned_users.values_list('user__username', flat=True))
            pre_assigned_user_ids_active = set(pre_assigned_users.values_list('user', flat=True))


            data = {}
            
            users = get_all_users_active()

            if request.method == 'POST':

                some_values = request.POST.getlist('check_user')

                if len(some_values) > 0:
                    
                    for i in range(len(some_values)):

                        obj, _ = ProjectsXUsers.objects.get_or_create(project=ProjectInfo.objects.get(pk=prj_id), user=User.objects.get(pk=int(some_values[i])))
                        obj.active = True
                        obj.created_by = request.user
                        obj.save()

                    #this makes the record deactive if user is unchecked
                    new_values = set(int(l) for l in some_values)
                    for j in pre_assigned_user_ids_all:
                        if j in new_values:
                            pass
                        else:
                            try:
                                temp = ProjectsXUsers.objects.get(project=prj_id, user=User.objects.get(pk=j))
                                temp.active = False
                                temp.save()
                            except:
                                pass

                    #updating project count table
                    for k in users:
                        try:
                            upc = UserProjectCount.objects.get(user=k.id)
                            upc.project_count = ProjectsXUsers.objects.filter(user=k.id, active=True).count()
                            upc.save()
                        except UserProjectCount.DoesNotExist:
                            pass

                    # recording post assinged users
                    post_assigned_user_names_active = ProjectsXUsers.objects.filter(project=prj_id, active=True)
                    for i in post_assigned_user_names_active:
                        post.append(i.user.username)
                        post_assigned_user_emails.append(i.user.email)

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    reason = 'project assigned/unassigned'
                    assign_project_log(pre, post, reason, request.user, client_ip, project)

                    #recording activity log
                    event = 'Assign Project'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user, 
                        proj_name   = project.project_name,
                        list_users  = ','.join([str(elem) for elem in post]),
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )




                    #to send alert email                    
                    backend = EmailBackend(

                        host          = config.email_host,
                        username      = config.email_host_user,
                        password      = config.email_host_password,
                        port          = config.email_port,
                        use_tls       = True,
                        fail_silently = True

                    )
                    from_email = config.email_default_mail
                    current_site = get_current_site(request)
                    email_subject = 'Project Assignment in CSR.'
                    
                    for i in range(len(post)):
                        if post_assigned_user_emails[i] != '':

                            to_email = post_assigned_user_emails[i]
                            html_content = "<h3>Dear <b>"+ post[i] +"</b>,</h3><br>You have been assigned with a new project, <b>" + project.project_name + "</b><br><br><b>Thanks & Regards<br>CSR Automation</b>"

                            email = EmailMessage(subject=email_subject, body=html_content, from_email=from_email, to=[to_email], connection=backend)
                            email.content_subtype = 'html'
                            
                            # email_status = email.send()

                            email_thread = Thread(target=EmailThread, args=('Assign Project', email, to_email, from_email, email_subject, html_content, request.user))
                            email_thread.start()

                            # email_status = email_thread.join()

                            # print(email_status)

                            # print(email_status)
                    
                            # # recording Email logs
                            # e_log = LogsEmails(

                            #         event = 'Assign Project',
                            #         to_email = to_email,
                            #         from_email = from_email,
                            #         subject = email_subject,
                            #         message_body = html_content,
                            #         email_sent = email_status,
                            #         created_by = request.user

                            #     )
                            # e_log.save()
                            
                        else:
                        	pass         

                    # getting list of users who has the access to project
                    projectXusers = ProjectsXUsers.objects.filter(project=project,active=True).values_list('user', flat=True)
                    # adding notification in db table
                    if projectXusers:
                        for each in projectXusers:
                            if each != request.user.id:
                                notif_obj = Notifications(
                                    senderId = request.user.id,
                                    receiverId = each,
                                    message = 'You have been assigned with a project - ' + project.project_name,
                                    event_type = 'assign_project',
                                    projectId = project.id
                                )
                                notif_obj.save()

                            else:
                            	pass
                    else:
                    	pass

                    messages.success(request, "Project has been Assigned successfully!")
                    data['form_is_valid'] = True

                else:
                    data['form_is_valid'] = False

            else:
                #recording activity log
                event = 'Click Assign Project Btn'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user, 
                    proj_name   = project.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'users' : users,
                'project' : project,
                'config' : config,
                'pre_assigned_user_ids_active' : pre_assigned_user_ids_active

            }

            data['html_form'] =  render_to_string('assign_project.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))




#this fetches all the users project details
@login_required(login_url='/')
def get_all_users_details(request):

    try:
        if request.user.is_superuser:

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            proj_count = UserProjectCount.objects.all()
            users = get_all_users_active()

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            return render(request, 'admin_users.html', {'users' : users,  'proj_count' : proj_count, 'config' : config, 'latest_client' : latest_client})

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this fetches all the users project details
@login_required(login_url='/')
def get_all_active_users_details(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            proj_count = UserProjectCount.objects.all()
            users = get_all_users_active()
            context ={
                'users'      : users,
                'proj_count' : proj_count,
                'config'     : config
            }
            data['html_form'] =  render_to_string('admin_users_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this fetches all the users project details
@login_required(login_url='/')
def get_all_act_inact_users_details(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            proj_count = UserProjectCount.objects.all()
            users = get_all_users()
            context ={
                'users'      : users,
                'proj_count' : proj_count,
                'config'     : config
            }
            data['html_form'] =  render_to_string('admin_users_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle project editing
@login_required(login_url='/')
def edit_user_project(request, usr_id, proj_id):

    try:

        projects = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=projects, user=request.user)

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            therapeutic_area_list = TherapeuticArea.objects.all()
            client_list           = ClientInfo.objects.filter(active=True)

            data = {}

            if request.method == 'POST':

                try:
                    form = EditProjectForm(request.POST or None, instance=projects)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                if form.is_valid():

                    # recording previous state
                    previoust_state = ProjectInfo.objects.get(pk=proj_id)

                    # updating project details
                    projects.project_name     = request.POST.get('project_name')
                    projects.protocol_id      = request.POST.get('protocol_id')
                    projects.client           = ClientInfo.objects.get(pk=request.POST.get('client'))
                    projects.therapeutic_area = TherapeuticArea.objects.get(pk=request.POST.get('therapeutic_area'))
                    projects.phase            = request.POST.get('phase')
                    projects.save()

                    # recording current state
                    current_state = ProjectInfo.objects.get(pk=proj_id)

                    # recording audit log
                    reason = 'edited the project'
                    client_ip = request.META['REMOTE_ADDR']
                    edit_project_log(previoust_state, current_state, reason, projects, request.user, client_ip)

                    #recording activity log
                    event = 'Edit Project'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        proj_name   = request.POST.get('project_name'),
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    messages.success(request, "Project " + current_state.project_name + " has been updated successfully!")
                    data['form_is_valid'] = True

                    # getting list of users who has the access to project
                    projectXusers = ProjectsXUsers.objects.filter(project=projects,active=True).values_list('user', flat=True)
                    # adding notification in db table
                    if projectXusers:
                        for each in projectXusers:
                            if each != request.user.id:
                                notif_obj = Notifications(
                                    senderId = request.user.id,
                                    receiverId = each,
                                    message = request.user.username + ' has updated ' + projects.project_name + ' details.',
                                    event_type = 'edit_project',
                                    projectId = projects.id
                                )
                                notif_obj.save()

                else:
                    data['form_is_valid'] = False

            else:
                form = EditProjectForm()

                #recording activity log
                event = 'Nav Edit Project'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = projects.project_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'projects' : projects,
                'therapeutic_area_list' : therapeutic_area_list,
                'client_list' : client_list,

            }
            data['html_form'] =  render_to_string('edit_user_project.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#each project dashboard
@login_required(login_url='/')
def project_dashboard(request, usr_id, proj_id):

    try:

        projects = ProjectInfo.objects.get(pk=proj_id)

        users = get_all_users_active()

        is_belongs = ProjectsXUsers.objects.get(project=projects, user=request.user)

        if request.user.id == int(usr_id) and not request.user.is_superuser and is_belongs.is_active and is_belongs.project.client.is_active:

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            # Latest Global CSR
            try:
                csr_doc_latest = CSRTemplate.objects.filter(client=projects.client).latest('id')
            except CSRTemplate.DoesNotExist:
                csr_doc_latest = None
            # List of Global CSR
            try:
                csr_doc_list = CSRTemplate.objects.filter(client=projects.client).order_by('-created_on')[1:]
            except CSRTemplate.DoesNotExist:
                csr_doc_list = None

            # Latest Custom CSR
            try:
                custom_csr_doc_latest = CSRTemplateUser.objects.filter(project=proj_id).latest('id')
            except CSRTemplateUser.DoesNotExist:
                custom_csr_doc_latest = None
            # List of Custom CSR
            try:
                custom_csr_doc_list = CSRTemplateUser.objects.filter(project=proj_id).order_by('-created_on')[1:]
            except CSRTemplateUser.DoesNotExist:
                custom_csr_doc_list = None


            # Latest Protocol
            try:
                protocol_doc_latest = ProtocolFileUpload.objects.filter(project=proj_id).latest('id')
            except ProtocolFileUpload.DoesNotExist:
                protocol_doc_latest = None
            # List of Protocol
            try:
                protocol_doc_list = ProtocolFileUpload.objects.filter(project=proj_id).order_by('-uploaded_on')[1:]
            except ProtocolFileUpload.DoesNotExist:
                protocol_doc_list = None


            # Latest SAR
            try:
                sar_doc_latest = SarFileUpload.objects.filter(project=proj_id).latest('id')
            except SarFileUpload.DoesNotExist:
                sar_doc_latest = None
            # List of SAR
            try:
                sar_doc_list = SarFileUpload.objects.filter(project=proj_id).order_by('-uploaded_on')[1:]
            except SarFileUpload.DoesNotExist:
                sar_doc_list = None

            # Latest CSR Report
            try:
                csr_report_latest = Generated_Reports.objects.filter(project=proj_id).latest('id')
            except Generated_Reports.DoesNotExist:
                csr_report_latest = None
            # List of CSR Report
            try:
                csr_report_list = Generated_Reports.objects.filter(project=proj_id).order_by('-created_on')[1:]
            except Generated_Reports.DoesNotExist:
                csr_report_list = None

            # Check if other document info available
            try:
                is_another_doc_available = AnotherFileUploadUserInfo.objects.get(project=proj_id)
            except AnotherFileUploadUserInfo.DoesNotExist:
                is_another_doc_available = None

            # Latest another document
            try:
                another_doc_latest = AnotherFileUploadUser.objects.filter(project=proj_id).latest('id')
            except AnotherFileUploadUser.DoesNotExist:
                another_doc_latest = None
            # List of another document
            try:
                another_doc_list = AnotherFileUploadUser.objects.filter(project=proj_id).order_by('-uploaded_on')[1:]
            except AnotherFileUploadUser.DoesNotExist:
                another_doc_list = None


            # Latest Protocol
            try:
                finalcsr_doc_latest = FinalCSRFileUpload.objects.filter(project=proj_id).latest('id')
            except FinalCSRFileUpload.DoesNotExist:
                finalcsr_doc_latest = None
            # List of Protocol
            try:
                finalcsr_doc_list = FinalCSRFileUpload.objects.filter(project=proj_id).order_by('-uploaded_on')[1:]
            except FinalCSRFileUpload.DoesNotExist:
                finalcsr_doc_list = None

            # Documets shared with me
            try:
                shared_documents_list_with = SharedDocumentData.objects.filter(report__project__id=proj_id, shared_with__contains=usr_id, active=True)
            except SharedDocumentData.DoesNotExist:
                shared_documents_list_with = None

            # Documents shared by me
            try:
                shared_documents_list_by = SharedDocumentData.objects.filter(report__project__id=proj_id, shared_by__id=usr_id).exclude(shared_with=None)
            except SharedDocumentData.DoesNotExist:
                shared_documents_list_by = None


            if shared_documents_list_with:
                shared_documents_with_version_list = get_WorkDocsVersions(shared_documents_list_with)
            else:
                shared_documents_with_version_list = None

            if shared_documents_list_by:
                shared_documents_by_version_list = get_WorkDocsVersions(shared_documents_list_by)
            else:
                shared_documents_by_version_list = None
            
            context = {

                'projects'                 : projects,
                'csr_doc_latest'           : csr_doc_latest,
                'csr_doc_list'             : csr_doc_list,
                'custom_csr_doc_latest'    : custom_csr_doc_latest,
                'custom_csr_doc_list'      : custom_csr_doc_list,
                'protocol_doc_latest'      : protocol_doc_latest,
                'protocol_doc_list'        : protocol_doc_list,
                'sar_doc_latest'           : sar_doc_latest,
                'sar_doc_list'             : sar_doc_list,
                'csr_report_latest'        : csr_report_latest,
                'csr_report_list'          : csr_report_list,
                'usr_id'                   : usr_id,
                'is_another_doc_available' : is_another_doc_available,
                'another_doc_latest'       : another_doc_latest,
                'another_doc_list'         : another_doc_list,
                'latest_client'            : latest_client,
                'finalcsr_doc_latest'      : finalcsr_doc_latest,
                'finalcsr_doc_list'        : finalcsr_doc_list,
                'shared_documents_list_with' : shared_documents_list_with,
                'shared_documents_list_by' : shared_documents_list_by,
                'users'                    : users,
                'shared_documents_with_version_list' : shared_documents_with_version_list,
                'shared_documents_by_version_list' : shared_documents_by_version_list

            }

            return render(request, 'project_dashboard.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

@login_required(login_url='/')
def add_report_comments(request, report_id):
    
    try:

        data = {}

        report = Generated_Reports.objects.get(pk=report_id)

        if request.method == 'POST':

            comments = request.POST.get('comments')

            # storing comment into db
            obj = ReportComments(
                    report = report,
                    commented_by = request.user,
                    comments = comments
                )
            obj.save()

            messages.success(request, "Comments has been recorded successfully.")
            data['form_is_valid'] = True

            # recording activity log
            event = 'Add Report Comments'
            record_user_activity_log(
                event       = event, 
                actor       = request.user,
                proj_name   = report.project.project_name,
                report_name = ntpath.basename(report.generated_report_path),
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

            # getting list of users who has the access to project
            projectXusers = ProjectsXUsers.objects.filter(project=report.project,active=True).values_list('user', flat=True)
            # adding notification in db table
            if projectXusers:
                for each in projectXusers:
                    if each != request.user.id:
                        notif_obj = Notifications(
                            senderId = request.user.id,
                            receiverId = each,
                            message = request.user.username + ' commented on CSR report of ' + report.project.project_name + '.',
                            event_type = 'report_comment',
                            projectId = report.project.id
                        )
                        notif_obj.save()

        else:
            # recording activity log
            event = 'Nav Add Report Comments'
            record_user_activity_log(
                event       = event, 
                actor       = request.user,
                proj_name   = report.project.project_name,
                report_name = ntpath.basename(report.generated_report_path),
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

        context = {
            'report_id' : report_id,
        }
        data['html_form'] = render_to_string('add_comments.html', context, request=request)

        return JsonResponse(data)


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
def view_report_comments(request, report_id):
    
    try:

        data = {}

        report = Generated_Reports.objects.get(pk=report_id)

        try:
            report_comments = ReportComments.objects.filter(report=report).order_by('-updated_on')
        except ReportComments.DoesNotExist:
            report_comments = None


        # recording activity log
        event = 'View Report Comments'
        record_user_activity_log(
            event       = event, 
            actor       = request.user,
            proj_name   = report.project.project_name,
            report_name = ntpath.basename(report.generated_report_path),
            session_id  = request.session.session_key,
            client_ip   = get_client_ip(request)
            )

        context = {
            'report' : report,
            'report_comments' : report_comments,
        }

        data['html_form'] = render_to_string('view_comments.html', context, request=request)

        return JsonResponse(data)


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# To handle Documents shared by user
@login_required(login_url='/')
def shared_doc_by(request, usr_id, proj_id):

    try:

        data = {}

        try:
            shared_documents_list = SharedDocumentData.objects.filter(report__project__id=proj_id, shared_by__id=usr_id).exclude(shared_with=None)
        except SharedDocumentData.DoesNotExist:
            shared_documents_list = None

        context = {
            'shared_documents_list' : shared_documents_list,
        }
        
        data['html_form'] = render_to_string('docs_shared_by.html', context, request=request)

        return JsonResponse(data)

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def shared_doc_with(request, usr_id, proj_id):
    try:
        data = {}

        try:
            shared_documents_list = SharedDocumentData.objects.filter(report__project__id=proj_id,shared_with__contains=usr_id)
        except SharedDocumentData.DoesNotExist:
            shared_documents_list = None

        context = {
            'shared_documents_list' : shared_documents_list,
        }
        
        data['html_form'] = render_to_string('docs_shared_with.html', context, request=request)

        return JsonResponse(data)


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# To download workdocs file
@login_required(login_url='/')
def download_workdocs_doc(request, document_id):

    try:

        response = download_operation_WorkDocs(document_id)

        return HttpResponseRedirect(response)

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



#to download any file
@login_required(login_url='/')
def download(request, path):

    try:

        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):

            with open(file_path, 'rb') as fh:

                response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)

                return response

        raise Http404

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle activity log
@login_required(login_url='/')
def activity_log(request):

    try:

        if request.user.is_superuser:

            data  = {}

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None
            
            logs = LogsActivity.objects.all().order_by('-id')

            users = get_all_users()

            return render(request, 'activity_log.html', {'logs' : logs, 'users' : users, 'latest_client' : latest_client})

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# to handle audit log
@login_required(login_url='/')
def audit_log(request):

    try:

        try:
            latest_client = ClientInfo.objects.latest('id')
        except ClientInfo.DoesNotExist:
            latest_client = None

        users = get_all_users()

        projects = get_all_projects()

        if request.user.is_superuser:
            audit_logs = LogsAudit.objects.all().order_by('-id')
        else:
            audit_logs = LogsAudit.objects.filter(user=request.user.id).order_by('-id')

        return render(request, 'audit_log.html', {'audit_logs' : audit_logs, 'users' : users, 'projects' : projects, 'latest_client' : latest_client})


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# to dispaly global mapping in users role
@login_required(login_url='/')
def display_global_csr_mapping(request, cli_id):

    try:

        if not request.user.is_superuser:

            client_list   = ClientInfo.objects.filter(active=True)

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None
            try:
                req_client    = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            mapping_table = list(GlobalMappingTable.objects.filter(client=req_client).order_by('id'))
            ch_cnt        = global_mapping_table_structure(mapping_table, req_client)

            context       = {

                'mapping_table' : mapping_table,
                'ch_cnt'        : ch_cnt,
                'client_list'   : client_list,
                'latest_client' : latest_client,
                'req_client'    : req_client,

            }

            return render(request, 'global_csr_mapping.html', context=context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle generate csr as per mapping
@login_required(login_url='/')
@csrf_exempt
def generate_csr(request, usr_id, proj_id):

    try:

        projects = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=projects, user=request.user)

        if request.user.id == int(usr_id) and not request.user.is_superuser and request.is_ajax() and is_belongs.is_active:

            data = {}
            filename = ''
            version  = ''

            try:
                response_data = json.loads(request.body)
                filename      = response_data[0]
                version       = response_data[1]

            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # recording logging
            csr_logger.info("Generate CSR started for project - '" + projects.project_name +"' by - " + request.user.username)

            status = generate_csr_document(usr_id, proj_id, filename, version)

            if status == 1:
                # to update project info if csr generated
                obj = ProjectInfo.objects.get(pk=proj_id)
                obj.generated = True
                obj.save()

                # recording activity log
                event = 'Generate CSR'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = projects.project_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

                messages.success(request, "CSR generated succesfully!")
                data['form_is_valid'] = True
                # recording logging
                csr_logger.info("Generate CSR completed for project - '" + projects.project_name +"' by - " + request.user.username)

            elif status == 2:
                messages.info(request, "CSR generated succesfully! But Some sections of data is not Copied, due to invalid format.")
                data['form_is_valid'] = True

            else:
                messages.error(request, "Custom Mapping not found. Please map through Edit Mapping!")
                data['form_is_valid'] = False

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# edit csr mapping user
@login_required(login_url='/')
@csrf_exempt
def edit_csr_mapping(request, usr_id, proj_id):

    try:

        projects = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=projects, user=request.user)

        if request.user.id == int(usr_id) and not request.user.is_superuser and is_belongs.is_active and is_belongs.project.client.is_active:

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            try:
                is_another_doc_available = AnotherFileUploadUserInfo.objects.get(project=proj_id)
            except AnotherFileUploadUserInfo.DoesNotExist:
                is_another_doc_available = None

            fetched_data         = get_global_mapped_data_usr(usr_id, proj_id)
            custom_mapping       = fetched_data[0]
            csr_headings         = fetched_data[1]
            protocol_headings    = fetched_data[2]
            sar_headings         = fetched_data[3]
            another_doc_headings = fetched_data[4]

            try:
                protocol_headings_json    = json.dumps(protocol_headings)
                sar_headings_json         = json.dumps(sar_headings)
                another_doc_headings_json = json.dumps(another_doc_headings)
            except Exception as e:
                
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # global admin mapped data
            pre_global_mapping = get_global_mapping_suggestions(csr_headings, protocol_headings, sar_headings, projects)

            global_pre_mapped_headings          = pre_global_mapping[0]
            list_global_pre_mapped_csr_headings = list(map(itemgetter('csr_heading'), global_pre_mapped_headings))

            global_pre_mapped_headings_parent          = pre_global_mapping[1]
            list_global_pre_mapped_csr_headings_parent = list(map(itemgetter('csr_heading'), global_pre_mapped_headings_parent))

            record_len = len(csr_headings) + len(global_pre_mapped_headings)

            loop = len(custom_mapping)

            if request.method == 'POST':
                
                try:

                    csr_headings_data  = request.POST.getlist('csr_headings[]')
                    source_data        = request.POST.getlist('source[]')
                    copy_headings_data = request.POST.getlist('copy_headings[]')
                    reason             = request.POST.get('reason')
                    parent_ids         = request.POST.getlist('child_parent_id[]')

                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                custom_mapping_filt = filtered_pre_mapped_user_data(usr_id, proj_id)
                updated_mapping_form_data = csr_updated_user_form_data(csr_headings_data, source_data, copy_headings_data, parent_ids, custom_mapping_filt)
                changed_sections_only = changed_records_only_usr(usr_id, proj_id, updated_mapping_form_data)                
                tempe = updated_only_sections_usr(changed_sections_only,updated_mapping_form_data)

                cleaned_pre_mapped_headings = cleaned_pre_mapped_data(custom_mapping_filt)
                cleaned_updated_mapping_form_data = cleaned_csr_updated_form_data(csr_headings_data, source_data, copy_headings_data, parent_ids)

                status = load_custom_mapping_to_model(csr_headings_data, source_data, copy_headings_data,usr_id, proj_id, parent_ids)

                if status == 1:
                    messages.success(request, 'Custom Mapping table updated scuccessfully!')

                    # loading library
                    load_library_with_user_configurations(projects)

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    # edit_custom_csr_mapping_log(custom_mapping, csr_headings_data, source_data, copy_headings_data, reason, request.user, projects, client_ip)
                    if tempe:
                        edit_custom_csr_mapping_log(changed_sections_only, tempe, reason, request.user, projects, client_ip)
                    else:
                        edit_custom_csr_mapping_log(cleaned_pre_mapped_headings, cleaned_updated_mapping_form_data, reason, request.user, projects, client_ip)

                    # recording activity log
                    event = 'Edit Custom CSR'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        proj_name   = projects.project_name, 
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    return redirect('project_dashboard', usr_id=usr_id, proj_id=proj_id)
                    
                else:
                    messages.error(request, 'Please Map again!')

            else:
                # recording activity log
                event = 'Nav Edit Custom CSR'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = projects.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {
                'projects'          : projects,
                'loop'              : loop,
                'custom_mapping'    : custom_mapping,
                'csr_headings'      : csr_headings,
                'protocol_headings' : protocol_headings,
                'protocol_headings_json' : protocol_headings_json,
                'sar_headings'      : sar_headings,
                'sar_headings_json' : sar_headings_json,
                'proj_id'           : proj_id,
                'usr_id'            : usr_id,
                'global_pre_mapped_headings' : global_pre_mapped_headings,
                'list_global_pre_mapped_csr_headings' : list_global_pre_mapped_csr_headings,
                'global_pre_mapped_headings_parent' : global_pre_mapped_headings_parent,
                'list_global_pre_mapped_csr_headings_parent' : list_global_pre_mapped_csr_headings_parent,
                'record_len' : record_len,
                'is_another_doc_available' : is_another_doc_available,
                'another_doc_headings' : another_doc_headings,
                'another_doc_headings_json' : another_doc_headings_json,
                'latest_client' : latest_client,

            }
            

            return render(request, 'edit_mapping.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# csr mapping confirmation user
@login_required(login_url='/')
@csrf_exempt
def confirm_csr_mapping_user(request, usr_id, proj_id):

    try:

        projects = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=projects, user=request.user)

        if request.user.id == int(usr_id) and not request.user.is_superuser and request.is_ajax() and is_belongs.is_active:
    
            data = {}

            csr_head   = ''
            src_file   = ''
            src_head   = ''
            parent_ids = ''

            if request.is_ajax():

                try:
                    response_data = json.loads(request.body)
                    csr_head   = response_data[0]
                    src_file   = response_data[1]
                    src_head   = response_data[2]
                    parent_ids = response_data[3]

                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            custom_mapping = filtered_pre_mapped_user_data(usr_id, proj_id)
            updated_mapping_form_data = csr_updated_user_form_data(csr_head, src_file, src_head, parent_ids, custom_mapping)
            changed_sections_only = changed_records_only_usr(usr_id, proj_id, updated_mapping_form_data)
            tempe = updated_only_sections_usr(changed_sections_only,updated_mapping_form_data)

            cleaned_pre_mapped_headings = cleaned_pre_mapped_data(custom_mapping)
            cleaned_updated_mapping_form_data = cleaned_csr_updated_form_data(csr_head, src_file, src_head, parent_ids)


            context = {
                'updated_mapping_form_data' : updated_mapping_form_data,
                'custom_mapping'            : custom_mapping,
                'changed_sections_only'     : changed_sections_only,
                'tempe'                     : tempe,
                'cleaned_pre_mapped_headings' : cleaned_pre_mapped_headings,
                'cleaned_updated_mapping_form_data' : cleaned_updated_mapping_form_data
            }

            data['html_form'] = render_to_string('confirm_csr_mapping_user.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# Admin csr mapping
@login_required(login_url='/')
def csr_mapping(request, cli_id):

    try:

        try:
            req_client    = ClientInfo.objects.get(pk=cli_id)
        except ClientInfo.DoesNotExist:
            req_client = None

        if request.user.is_superuser and req_client.is_active:

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            file_locations      = get_file_locations(req_client)
            csr_headings        = GetHeadings_addHeaderNumbering(file_locations[0])
            protocol_headings   = GetHeadings_addHeaderNumbering(file_locations[1])
            sar_headings        = get_all_headings(file_locations[2])
            pre_mapped_headings = get_global_mapped_data(req_client)

            Library_suggestion_dict = get_library_suggesions(csr_headings, protocol_headings, sar_headings)

            Library_suggestion = Library_suggestion_dict[0]
            matched_csr_headings = Library_suggestion_dict[1]

            try:
                protocol_headings_json = json.dumps(protocol_headings)
                sar_headings_json      = json.dumps(sar_headings)
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            if request.method == 'POST':
                
                try:
                    csr_headings_data  = request.POST.getlist('csr_headings[]')
                    source_data        = request.POST.getlist('source[]')
                    copy_headings_data = request.POST.getlist('copy_headings[]')
                    reason             = request.POST.get('reason')
                    parent_ids         = request.POST.getlist('child_parent_id[]')

                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

                pre_mapped_headings_filter = filtered_pre_mapped_admin_data(req_client)
                updated_mapping_form_data = csr_updated_admin_form_data(csr_headings_data, source_data, copy_headings_data, parent_ids, pre_mapped_headings_filter)
                changed_sections_only = changed_records_only_admin(req_client, updated_mapping_form_data)
                tempe = updated_only_sections(changed_sections_only,updated_mapping_form_data)

                cleaned_pre_mapped_headings = cleaned_pre_mapped_data(pre_mapped_headings_filter)
                cleaned_updated_mapping_form_data = cleaned_csr_updated_form_data(csr_headings_data, source_data, copy_headings_data, parent_ids)

                status = load_mapping_to_model(csr_headings_data, source_data, copy_headings_data, parent_ids, req_client)

                if status == 1:
                    messages.success(request, 'Global Mapping table updated successfully!')

                    # loading library
                    load_library_with_admin_configurations(req_client)

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    # edit_global_csr_mapping_log(pre_mapped_headings, csr_headings_data, source_data, copy_headings_data, reason, request.user, client_ip, req_client)
                    if tempe:
                        edit_global_csr_mapping_log(changed_sections_only, tempe, reason, request.user, client_ip, req_client)
                    else:
                        edit_global_csr_mapping_log(cleaned_pre_mapped_headings, cleaned_updated_mapping_form_data, reason, request.user, client_ip, req_client)

                    # recording activity log
                    event = 'CSR Mapping'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        client_name = req_client.client_name,
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    return redirect('global_csr_upload', cli_id=cli_id)

                else:
                    messages.error(request, 'Please Map again!')

            else:
                # recording activity log
                event = 'Nav Global CSR Mapping'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    client_name = req_client.client_name,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'csr_headings'           : csr_headings,
                'protocol_headings'      : protocol_headings,
                'protocol_headings_json' : protocol_headings_json,
                'sar_headings'           : sar_headings,
                'sar_headings_json'      : sar_headings_json,
                'pre_mapped_headings'    : pre_mapped_headings,
                'latest_client'          : latest_client,
                'req_client'             : req_client,
                'Library_suggestion'     : Library_suggestion,
                'matched_csr_headings'   : matched_csr_headings,
            }
            
            return render(request, 'admin_csr_mapping.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# csr mapping confirmation admin
@login_required(login_url='/')
@csrf_exempt
def confirm_csr_mapping_admin(request, cli_id):

    try:

        if request.user.is_superuser and request.is_ajax():
    
            data = {}

            try:
                req_client = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            csr_head = ''
            src_file = ''
            src_head = ''
            parent_ids = ''

            try:
                response_data = json.loads(request.body)
                csr_head      = response_data[0]
                src_file      = response_data[1]
                src_head      = response_data[2]
                parent_ids    = response_data[3]

            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            pre_mapped_headings = filtered_pre_mapped_admin_data(req_client)
            updated_mapping_form_data = csr_updated_admin_form_data(csr_head, src_file, src_head, parent_ids, pre_mapped_headings)
            changed_sections_only = changed_records_only_admin(req_client, updated_mapping_form_data)
            tempe = updated_only_sections(changed_sections_only,updated_mapping_form_data)

            cleaned_pre_mapped_headings = cleaned_pre_mapped_data(pre_mapped_headings)
            cleaned_updated_mapping_form_data = cleaned_csr_updated_form_data(csr_head, src_file, src_head, parent_ids)

            context = {
                'updated_mapping_form_data' : updated_mapping_form_data,
                'pre_mapped_headings'       : pre_mapped_headings,
                'changed_sections_only'     : changed_sections_only,
                'tempe' : tempe,
                'cleaned_pre_mapped_headings' : cleaned_pre_mapped_headings,
                'cleaned_updated_mapping_form_data' : cleaned_updated_mapping_form_data,
            }

            data['html_form'] = render_to_string('confirm_csr_mapping_admin.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
      
    

# to handle email configurations
@login_required(login_url='/')
def email_configuration(request):

    try:

        if request.is_ajax() and request.user.is_superuser:

            data = {}

            if request.method == 'POST':

                try:
                    form = EmailConfigurationForm(request.POST)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
                    
                if form.is_valid():

                    # to delete already existed records
                    EmailConfiguration.objects.all().delete()

                    config = form.save(commit=False)
                    config.created_by = request.user
                    config.save()
                    
                    data['form_is_valid'] = True
                    messages.success(request, 'Email Configuration added succesfully')

                    # recording activity log
                    event = 'Add Email Configuration'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                else:
                    data['form_is_valid'] = False
            else:
                form = EmailConfigurationForm()

                # recording activity log
                event = 'Nav Email Configuration'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )
                
            context = {
                'form' : form
            }
            data['html_form'] = render_to_string('email_configuration.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle email logs
@login_required(login_url='/')
def mail_logs(request):

    try:

        if request.user.is_superuser:

            data = {}

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            try:
                email_logs = LogsEmails.objects.all().order_by('-id')

            except LogsEmails.DoesNotExist:

                email_logs = None

            context = {

                'email_logs'    : email_logs,
                'latest_client' : latest_client,
            }

            return render(request, 'mail_logs.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle resend emails
@login_required(login_url='/')
def resend_email(request, mail_id):

    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            obj  = LogsEmails.objects.get(pk=mail_id)

            #to resend email
            config  = EmailConfiguration.objects.last()
            backend = EmailBackend(

                host          = config.email_host,
                username      = config.email_host_user,
                password      = config.email_host_password,
                port          = config.email_port,
                use_tls       = True,
                fail_silently = True

            )
            from_email = config.email_default_mail
            email_subject = obj.subject
            to_email = obj.to_email
            html_content = obj.message_body
            email = EmailMessage(subject=email_subject, body=html_content, from_email=from_email, to=[to_email], connection=backend)
            email.content_subtype = 'html'
            email_status = email.send()

            # recording Email logs
            e_log = LogsEmails(

                    event = obj.event,
                    to_email = to_email,
                    from_email = from_email,
                    subject = email_subject,
                    message_body = html_content,
                    email_sent = email_status,
                    created_by = request.user

                )
            if email_status:

                obj.email_sent = True
                obj.save()

                e_log.email_response  = "Email sent scuccessfully"
                data['resend_status'] = True

                messages.success(request, 'Resend Email succesfully!')

                #recording activity log
                event = 'Resend Email'
                record_user_activity_log(
                    event       = event,
                    actor       = request.user, 
                    email       = to_email,
                    log_event   = obj.event, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            else:
                e_log.email_response  = "Not able to connect SMTP server"
                data['resend_status'] = False
                messages.error(request, 'Problem with connecting SMTP server. Please check the Email Configurations!')

            e_log.save()

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# to handle displayig logging
@login_required(login_url='/')
def display_logging(request):

    try:

        if request.user.is_superuser:

            log_arr = []

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            file = BASE_DIR+'\\'+'media'+'\\logs\\'+'csr_except.log'

            with open(file) as f:
                lines = f.read()
                temp = []
                spl_lines = lines.split('\n[')

                log_arr = spl_lines[::-1]

            return render(request, 'logging.html', {'log_arr' : log_arr, 'latest_client' : latest_client})

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
    

@login_required(login_url='/')
def clear_configurations__admin(request, cli_id):

    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            try:
                req_client = ClientInfo.objects.get(pk=cli_id)
            except ClientInfo.DoesNotExist:
                req_client = None

            # recording activity log
            event = 'Clear Configurations'
            record_user_activity_log(
                event       = event, 
                actor       = request.user,
                client      = req_client.client_name,
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
            )

            # to delete files from filesystem
            del_file_on_clear__config_admin(req_client)

            # To Delete GlobalMappingTable
            try:
                GlobalMappingTable.objects.filter(client=req_client).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all global/admin csr documents
            try:
                CSRTemplate.objects.filter(client=req_client).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all global/admin Protocol documents
            try:
                ProtocolAdmin.objects.filter(client=req_client).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all global/admin SAR documents
            try:
                SARAdmin.objects.filter(client=req_client).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            messages.success(request, 'All the Configurations have been deleted succesfully!')

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def clear_configurations__usr(request, usr_id, proj_id):

    try:
        data = {}

        project = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=project, user=request.user)

        if request.user.id == int(usr_id) and not request.user.is_superuser and is_belongs.is_active and request.is_ajax():

            del_file_on_clear__config_usr(project)

            del_workdocs_files_on_clear__config_usr(project)

            # To Delete GlobalMappingTable
            try:
                CustomMappingTable.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all user csr documents
            try:
                CSRTemplateUser.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all user Protocol documents
            try:
                ProtocolFileUpload.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all user SAR documents
            try:
                SarFileUpload.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all another documents
            try:
                AnotherFileUploadUser.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To Delete all another documents info
            try:
                AnotherFileUploadUserInfo.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


            # To Delete all user generated_report documents
            try:
                Generated_Reports.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To update project info if csr generated
            project.generated = False
            project.save()

            # To delete all final csr reports
            try:
                FinalCSRFileUpload.objects.filter(project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To delete all shared document reports
            try:
                SharedDocumentData.objects.filter(report__project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # To delete all reports comments
            try:
                ReportComments.objects.filter(report__project=project).delete()
            except Exception as e:
                csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

            # recording activity log
            event = 'Configurations Clear'
            record_user_activity_log(
                event       = event, 
                actor       = request.user,
                proj_name   = project.project_name, 
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
            )

            messages.success(request, 'All the Configurations have been deleted succesfully!')

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
@csrf_exempt
def add_another_document__usr(request, usr_id, proj_id):

    try:

        project = ProjectInfo.objects.get(pk=proj_id)

        is_belongs = ProjectsXUsers.objects.get(project=project, user=request.user)

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            if request.is_ajax():
                response_data = json.loads(request.body)
                source_name = response_data[0]
                
                if source_name != '':
                    instance = AnotherFileUploadUserInfo.objects.create(

                            source_name = source_name,
                            project     = project,
                            created_by  = request.user

                        )
                    instance.save()
                    messages.success(request, 'Added new document succesfully!')
                    data['add_status'] = True

                    # recording activity log
                    event = 'Another Document'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        proj_name   = project.project_name,
                        source_name = source_name,
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                    )

                else:
                    messages.error(request, 'Something went wrong, please try later!')
                    data['add_status'] = False
            
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# to create client
@login_required(login_url='/')
def add_client(request):

    try:

        if request.is_ajax() and request.user.is_superuser:

            data = {}

            if request.method == 'POST':

                try:
                    form = AddClientForm(request.POST)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
                    
                if form.is_valid():

                    obj = form.save(commit=False)
                    obj.created_by = request.user
                    obj.save()
                    
                    data['form_is_valid'] = True
                    messages.success(request, 'Client added succesfully')

                    # recording activity log
                    event = 'Add Client'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        client      = form.cleaned_data.get('client_name'),
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                    )

                    # recording audit log
                    pre = ''
                    post = form.cleaned_data.get('client_name')
                    reason = 'added a new client'
                    client_ip = request.META['REMOTE_ADDR']
                    addclient_audit(pre, post, request.user, reason, client_ip, obj)

                else:
                    data['form_is_valid'] = False
            else:
                form = AddClientForm()

                # recording activity log
                event = 'Nav Add Client'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                )
                
            context = {
                'form' : form
            }
            data['html_form'] = render_to_string('add_client.html', context, request=request)
            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


from django.db.models import Count
#this fetches all the users project details
@login_required(login_url='/')
def get_all_client_details(request):

    try:
        if request.user.is_superuser:

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            clients = ClientInfo.objects.filter(active=True)

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            return render(request, 'admin_clients.html', {'clients' : clients, 'config' : config, 'latest_client' : latest_client})

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this fetches all the users project details
@login_required(login_url='/')
def get_all_active_client_details(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            clients = ClientInfo.objects.filter(active=True)
            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            context ={
                
                'clients' : clients,
                'config' : config,
                'latest_client' : latest_client
            }
            data['html_form'] =  render_to_string('admin_clients_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


#this fetches all the users project details
@login_required(login_url='/')
def get_all_act_inact_client_details(request):

    
    try:

        if request.user.is_superuser and request.is_ajax():

            data = {}

            try:
                config = EmailConfiguration.objects.last()
            except EmailConfiguration.DoesNotExist:
                config = None
            
            clients = ClientInfo.objects.all()
            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None
            context ={
                
                'clients' : clients,
                'config' : config,
                'latest_client' : latest_client
            }
            data['html_form'] =  render_to_string('admin_clients_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def activate_client(request, cli_id):

    try:

        if request.user.is_superuser:

            client = ClientInfo.objects.get(pk=cli_id)
            client.active = True
            client.save()

            messages.success(request, client.client_name + ' has been activated successfully!')

            # updating users project count
            update_project_count_based_on_client_status()

            #recording user acivity log
            event = 'Activate Client'
            record_user_activity_log(
                event       = event, 
                actor       = request.user, 
                client      = client.client_name, 
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

            return redirect('get_all_client_details')

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def deactivate_client(request, cli_id):

    try:

        if request.user.is_superuser:

            client = ClientInfo.objects.get(pk=cli_id)
            client.active = False
            client.save()
            
            messages.success(request, client.client_name + ' has been deactivated successfully!')

            # updating users project count
            update_project_count_based_on_client_status()

            #recording user acivity log
            event = 'Deactivate Client'
            record_user_activity_log(
                event       = event, 
                actor       = request.user, 
                client      = client.client_name, 
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

            return redirect('get_all_client_details')

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))




#this handle the final csr upload operation in each project of user
@login_required(login_url='/')
def finalcsr_file_upload(request, usr_id, pro_id):

    try:

        proj = ProjectInfo.objects.get(pk=pro_id)

        is_belongs = ProjectsXUsers.objects.get(project=proj, user=request.user)

        try:
            vn = FinalCSRFileUpload.objects.filter(project=pro_id).latest('id')
            pre = 'Version : ' + vn.version_no
        except FinalCSRFileUpload.DoesNotExist:
            pre = ''

        if request.user.id == int(usr_id) and request.is_ajax() and is_belongs.is_active:

            data = {}

            therapeutic_area_list = TherapeuticArea.objects.all()

            if request.method == 'POST':

                version          = request.POST['version']
                file_Name        = request.FILES['finalcsr_document_location']

                try:
                    form = FinalCSRFileUploadForm(request.POST, request.FILES)
                except Exception as e:
                    csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))
                
                if form.is_valid():

                    # fr__mt = check_file_content(file_Name)

                    # if fr__mt == '':

                    dd = form.save(commit=False)
                    dd.project = proj
                    dd.created_by = request.user

                    try:
                        obj = FinalCSRFileUpload.objects.filter(project=pro_id).latest('id').version_no
                    except FinalCSRFileUpload.DoesNotExist:
                        obj = None

                    if obj is not None:

                        if version == '0.1':
                            ver, rev = obj.split('.')
                            obj = ver + '.' + str(int(rev) + 1)

                        else:
                            ver, rev = obj.split('.')
                            obj = str(int(ver)+1) + '.' + str(0)

                    else:
                        obj = version

                    dd.version_no = obj
                    dd.save()

                    # Logging activity log
                    event = 'FinalCSR Upload'
                    record_user_activity_log(
                        event       = event, 
                        actor       = request.user,
                        proj_name   = proj.project_name, 
                        session_id  = request.session.session_key,
                        client_ip   = get_client_ip(request)
                        )

                    try:
                        vn = FinalCSRFileUpload.objects.filter(project=pro_id).latest('id')
                        post = 'Version : ' + vn.version_no
                        reason = vn.comments
                    except FinalCSRFileUpload.DoesNotExist:
                        post = ''
                        reason = ''

                    # recording audit log
                    client_ip = request.META['REMOTE_ADDR']
                    upload_finaldoc_user_audit(pre, post, request.user, reason, client_ip, proj)


                    messages.success(request, "Final CSR has been uploaded successfully!")
                    data['form_is_valid'] = True
                    data['file_data_format'] = ''

                    # else:
                    #     data['form_is_valid'] = False
                    #     data['file_data_format'] = fr__mt
                else:
                    data['form_is_valid'] = False
                    data['file_data_format'] = ''
            else:
                form = FinalCSRFileUploadForm()

                # Logging activity log
                event = 'Nav FinalCSR Upload'
                record_user_activity_log(
                    event       = event, 
                    actor       = request.user,
                    proj_name   = proj.project_name, 
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            context = {

                'form' : form,
                'therapeutic_area_list' : therapeutic_area_list,
                'proj' : proj
            }
            data['html_form'] = render_to_string('finalcsr_upload.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def protocol(request, usr_id):

    try:

        if request.user.id == int(usr_id):

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            data = {}
            protocol_list = []

            try:
                active_projects = list(ProjectsXUsers.objects.filter(user=request.user, active=True).values_list('project__id', flat=True))
            except ProjectsXUsers.DoesNotExist:
                active_projects = None

            if active_projects:

                for each in active_projects:
                    try:
                        temp = ProtocolFileUpload.objects.filter(project=each)
                    except ProtocolFileUpload.DoesNotExist:
                        temp = None

                    if temp:
                        for i in temp:
                            protocol_list.append(i)

            context = {

                'latest_client' : latest_client,
                'protocol_list' : protocol_list,
            }
            # data['html_form'] = render_to_string('protocols_usr.html', context, request=request)

            return render(request, 'protocols_user.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def protocol_ad(request):

    try:

        if request.user.is_superuser:

            try:
                latest_client = ClientInfo.objects.latest('id')
            except ClientInfo.DoesNotExist:
                latest_client = None

            try:
                protocol_list = ProtocolAdmin.objects.all()
            except ProtocolAdmin.DoesNotExist:
                protocol_list = None

            context = {

                'latest_client' : latest_client,
                'protocol_list' : protocol_list,
            }

            return render(request, 'protocols_admin.html', context)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def filter_project_names_info(request):

    try:

        if request.is_ajax():

            projects_list_active = ProjectsXUsers.objects.filter(user=request.user,active=True)

            proj_id_name_list = list(projects_list_active.values('project__id', 'project__project_name', 'project__protocol_id'))

            return HttpResponse(json.dumps(proj_id_name_list), content_type="application/json")

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
def get_client_info(request):

    try:

        if request.is_ajax():

            client_info = ClientInfo.objects.filter(active=True)

            client_info_list = list(client_info.values('id','client_name'))

            return HttpResponse(json.dumps(client_info_list), content_type="application/json")

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
def get_therapeutic_area_info(request):

    try:

        if request.is_ajax():

            therapeutic_area = TherapeuticArea.objects.all()

            therapeutic_area_list = list(therapeutic_area.values('id','therapeutic_area'))

            return HttpResponse(json.dumps(therapeutic_area_list), content_type="application/json")

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
@csrf_exempt
def filter_protocol_user_date(request):

    try:

        if request.is_ajax():

            params = json.loads(request.body)

            from_date = datetime.strptime(params[0], "%d/%m/%Y")

            to_date = datetime.strptime(params[1], "%d/%m/%Y") + timedelta(days=1)

            data = {}

            protocol_list = []

            try:
                active_projects = list(ProjectsXUsers.objects.filter(user=request.user, active=True).values_list('project__id', flat=True))
            except ProjectsXUsers.DoesNotExist:
                active_projects = None

            if active_projects:

                for each in active_projects:
                    try:
                        temp = ProtocolFileUpload.objects.filter(project=each, uploaded_on__range=[from_date, to_date])
                    except ProtocolFileUpload.DoesNotExist:
                        temp = None

                    if temp:
                        for i in temp:
                            protocol_list.append(i)

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
@csrf_exempt
def filter_protocol_user_filterobj(request):

    try:

        if request.is_ajax():

            params = json.loads(request.body)

            filter_by = params[0]

            filter_element = params[1]

            data = {}

            protocol_list = []

            try:
                active_projects = list(ProjectsXUsers.objects.filter(user=request.user, active=True).values_list('project__id', flat=True))
            except ProjectsXUsers.DoesNotExist:
                active_projects = None

            if active_projects:

                for each in active_projects:

                    if filter_by == 'project':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__id=filter_element)
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'protocol_id':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__id=filter_element)
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'client':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__client__id=filter_element)
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'therapeutic_area':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__therapeutic_area=filter_element)
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'phase':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__phase=filter_element)
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None


                    if temp:
                        for i in temp:
                            protocol_list.append(i)

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
@csrf_exempt
def filter_protocol_user_filterdateobj(request):

    try:

        if request.is_ajax():

            params = json.loads(request.body)

            from_date = datetime.strptime(params[0], "%d/%m/%Y")

            to_date = datetime.strptime(params[1], "%d/%m/%Y") + timedelta(days=1)

            filter_by = params[2]

            filter_element = params[3]

            data = {}

            protocol_list = []

            try:
                active_projects = list(ProjectsXUsers.objects.filter(user=request.user, active=True).values_list('project__id', flat=True))
            except ProjectsXUsers.DoesNotExist:
                active_projects = None

            if active_projects:

                for each in active_projects:

                    if filter_by == 'project':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__id=filter_element, uploaded_on__range=[from_date, to_date])
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'protocol_id':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__id=filter_element, uploaded_on__range=[from_date, to_date])
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'client':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__client__id=filter_element, uploaded_on__range=[from_date, to_date])
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'therapeutic_area':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__therapeutic_area=filter_element, uploaded_on__range=[from_date, to_date])
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    elif filter_by == 'phase':

                        try:
                            temp = ProtocolFileUpload.objects.filter(project=each, project__phase=filter_element, uploaded_on__range=[from_date, to_date])
                        except ProtocolFileUpload.DoesNotExist:
                            temp = None

                    if temp:
                        for i in temp:
                            protocol_list.append(i)

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
@csrf_exempt
def filter_protocol_admin_date(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            params = json.loads(request.body)

            from_date = datetime.strptime(params[0], "%d/%m/%Y")

            to_date = datetime.strptime(params[1], "%d/%m/%Y") + timedelta(days=1)

            data = {}

            try:
                protocol_list = ProtocolAdmin.objects.filter(created_on__range=[from_date, to_date])
            except ProtocolAdmin.DoesNotExist:
                protocol_list = None

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('admin_filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
@csrf_exempt
def filter_protocol_admin_filterobj(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            params = json.loads(request.body)

            filter_by = params[0]

            filter_element = params[1]

            data = {}

            protocol_list = None

            if filter_by == 'client':

                try:
                    protocol_list = ProtocolAdmin.objects.filter(client__id=filter_element)
                except ProtocolAdmin.DoesNotExist:
                    protocol_list = None

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('admin_filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



@login_required(login_url='/')
@csrf_exempt
def filter_protocol_admin_filterdateobj(request):

    try:

        if request.user.is_superuser and request.is_ajax():

            params = json.loads(request.body)

            from_date = datetime.strptime(params[0], "%d/%m/%Y")

            to_date = datetime.strptime(params[1], "%d/%m/%Y") + timedelta(days=1)

            filter_by = params[2]

            filter_element = params[3]

            data = {}

            protocol_list = None

            if filter_by == 'client':

                try:
                    protocol_list = ProtocolAdmin.objects.filter(client__id=filter_element, created_on__range=[from_date, to_date])
                except ProtocolAdmin.DoesNotExist:
                    protocol_list = None

            context = {
                'protocol_list' : protocol_list,
            }

            data['html_form'] =  render_to_string('admin_filter_protocol_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def share_workDocs(request, report_id):

    try:
        data = {}

        report = Generated_Reports.objects.get(pk=report_id)

        try:
            is_already_shared = (list(SharedDocumentData.objects.filter(report=report).values('shared_with'))[0])['shared_with']
        except:
            is_already_shared = None

        if is_already_shared:

            is_already_shared = re.split(" |,", is_already_shared)

        projectXusers = get_all_users_active_toshare(request.user, report.project)

        if request.method == 'POST':

            checked_list = request.POST.getlist('check_user_to_share')

            status = workdocs_operations(report, request.user, checked_list)

            if status == 1:
                messages.success(request, "Document shared successfully.")
                data['form_is_valid'] = True

                # adding notifications in db table
                for each in checked_list:

                    if each != str(request.user.id):

                        notif_obj = Notifications(
                            senderId = request.user.id,
                            receiverId = int(each),
                            message = 'CSR report of ' + report.project.project_name + ' has been shared with you.',
                            event_type = 'report_share',
                            projectId = report.project.id
                            )
                        notif_obj.save()


                #recording activity log
                event = 'Share Document'
                record_user_activity_log(
                    event       = event,
                    actor       = request.user,
                    proj_name   = report.project.project_name,
                    report_name = ntpath.basename(report.generated_report_path),
                    session_id  = request.session.session_key,
                    client_ip   = get_client_ip(request)
                    )

            else:
                messages.error(request, "Something went wrong.")
                data['form_is_valid'] = False
        else:
            #recording activity log
            event = 'Nav Share Document'
            record_user_activity_log(
                event       = event,
                actor       = request.user,
                proj_name   = report.project.project_name,
                report_name = ntpath.basename(report.generated_report_path),
                session_id  = request.session.session_key,
                client_ip   = get_client_ip(request)
                )

        context = {

                'projectXusers' : projectXusers,
                'report'  : report,
                'is_already_shared' : is_already_shared,

        }
        data['html_form'] = render_to_string('share_document.html', context, request=request)

        return JsonResponse(data)

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@login_required(login_url='/')
def get_notifications(request):

    data = {}
    
    try:
        notifications = Notifications.objects.filter(receiverId=request.user.id).order_by('-id')
        notifications.update(read=True)
    except Notifications.DoesNotExist:
        notifications = None



    context = {
        'notifications' : notifications,
    }

    data['html_form'] =  render_to_string('notifications.html', context, request=request)

    return JsonResponse(data)


def get_notifications_count(request):

    data = {}

    try:
        total_notifications = Notifications.objects.filter(receiverId=request.user.id, read=False).count()
    except Notifications.DoesNotExist:
        total_notifications = None

    data['total_notifications'] = total_notifications

    return JsonResponse(data)


# Below method are to record activity logs on mouse clicks
def to_record_actlog_on_click_projects(request):

    # recording activity log
    event = 'Nav Projects'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_on_click_up_csr(request):

    # recording activity log
    event = 'Nav Global CSR Upload'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_activitylog(request):

    # recording activity log
    event = 'Nav Activity Log'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_auditlog(request):

    # recording activity log
    event = 'Nav Audit Log'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_emaillog(request):

    # recording activity log
    event = 'Nav Email Log'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_users(request):

    # recording activity log
    event = 'Nav Users'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_clients(request):

    # recording activity log
    event = 'Nav Clients'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_on_click_protsrch(request):

    # recording activity log
    event = 'Nav Protocol Search'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_on_click_gblcsrmapp(request):

    # recording activity log
    event = 'Dispaly Global CSR Mapping'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_on_client_change(request, cli_id):

    try:
        req_client = ClientInfo.objects.get(pk=cli_id)
    except ClientInfo.DoesNotExist:
        req_client = None

    # recording activity log
    event = 'Change client in UPLOAD CSR'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        client_name = req_client.client_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_actv_user_change(request, usr_name):

    # recording activity log
    event = 'Change Users Acvt'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        usr_name    = usr_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_audt_user_change(request, usr_name):

    # recording activity log
    event = 'Change Users Audt'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        usr_name    = usr_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_glbmap_client_change(request, cli_name):

    # recording activity log
    event = 'Change Client Global Mapping'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        client_name = cli_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_on_prj_dashboard(request, proj_id):

    try:
        project = ProjectInfo.objects.get(pk=proj_id)
    except ProjectInfo.DoesNotExist:
        project = None

    # recording activity log
    event = 'Nav Project Dashboard'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        proj_name   = project.project_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )

    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_gbl_csr_download(request, doc_id):

    try:
        document = CSRTemplate.objects.get(pk=doc_id)
    except CSRTemplate.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Global CSR'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        client_name = document.client.client_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_gbl_protocol_download(request, doc_id):

    try:
        document = ProtocolAdmin.objects.get(pk=doc_id)
    except ProtocolAdmin.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Global Protocol'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        client_name = document.client.client_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_gbl_sar_download(request, doc_id):

    try:
        document = SARAdmin.objects.get(pk=doc_id)
    except SARAdmin.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Global SAR'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        client_name = document.client.client_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_cust_csr_download(request, doc_id):

    try:
        document = CSRTemplateUser.objects.get(pk=doc_id)
    except CSRTemplateUser.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Custom CSR'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        proj_name   = document.project.project_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_cust_protocol_download(request, doc_id):

    try:
        document = ProtocolFileUpload.objects.get(pk=doc_id)
    except ProtocolFileUpload.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Protocol'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        proj_name   = document.project.project_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_cust_sar_download(request, doc_id):

    try:
        document = SarFileUpload.objects.get(pk=doc_id)
    except SarFileUpload.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download SAR'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        proj_name   = document.project.project_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

def to_record_actlog_another_doc_download(request, doc_id):

    try:
        document = AnotherFileUploadUser.objects.get(pk=doc_id)
    except AnotherFileUploadUser.DoesNotExist:
        document = None

    try:
        source_name = AnotherFileUploadUserInfo.objects.get(project=document.project).source_name
    except AnotherFileUploadUserInfo.DoesNotExist:
        source_name = None

    # recording activity log
    event = 'Download Another Document'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        proj_name   = document.project.project_name,
        source_name = source_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')


def to_record_actlog_report_download(request, doc_id):

    try:
        document = Generated_Reports.objects.get(pk=doc_id)
    except Generated_Reports.DoesNotExist:
        document = None

    # recording activity log
    event = 'Download Report'
    record_user_activity_log(
        event       = event, 
        actor       = request.user,
        version     = document.version_no,
        proj_name   = document.project.project_name,
        session_id  = request.session.session_key,
        client_ip   = get_client_ip(request)
        )
    context = {'success': True}
    return HttpResponse(json.dumps(context), content_type='application/json')

@csrf_exempt
def filter_acvt_log(request):
    try:
        if request.is_ajax():

            params = json.loads(request.body)

            req_user = params[0]

            try:
                from_date = datetime.strptime(params[1], "%d/%m/%Y")
                to_date = datetime.strptime(params[2], "%d/%m/%Y") + timedelta(days=1)
            except:
                from_date = ''
                to_date = ''

            data = {}

            if req_user != 'all':

                if from_date != '' and to_date != '':
                    logs  = LogsActivity.objects.filter(user=int(req_user),created_on__range=[from_date, to_date]).order_by('-id')
                elif from_date == '' and to_date == '':
                    logs = LogsActivity.objects.filter(user=int(req_user)).order_by('-id')

            else:

                if from_date != '' and to_date != '':
                    logs  = LogsActivity.objects.filter(created_on__range=[from_date, to_date]).order_by('-id')
                elif from_date == '' and to_date == '':
                    logs = LogsActivity.objects.all().order_by('-id')


            context = {
                'logs' : logs,
            }

            data['html_form'] =  render_to_string('activity_log_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


@csrf_exempt
def filter_audt_log(request):
    try:
        if request.is_ajax():

            params = json.loads(request.body)

            req_user = params[0]

            req_proj = params[1]

            try:
                from_date = datetime.strptime(params[2], "%d/%m/%Y")
                to_date = datetime.strptime(params[3], "%d/%m/%Y") + timedelta(days=1)
            except:
                from_date = ''
                to_date = ''

            data = {}

            if from_date != '' and to_date != '':

                if req_user != 'all':

                    if req_proj == 'all':
                        audit_logs = LogsAudit.objects.filter(user=int(req_user),timestamp__range=[from_date, to_date]).order_by('-id')
                    else:
                        audit_logs = LogsAudit.objects.filter(user=int(req_user),project=int(req_proj),timestamp__range=[from_date, to_date]).order_by('-id')
                else:

                    if req_proj == 'all':
                        audit_logs = LogsAudit.objects.filter(timestamp__range=[from_date, to_date]).order_by('-id')
                    else:
                        audit_logs = LogsAudit.objects.filter(project=int(req_proj),timestamp__range=[from_date, to_date]).order_by('-id')

            elif from_date == '' and to_date == '':

                if req_user != 'all':

                    if req_proj == 'all':
                        audit_logs = LogsAudit.objects.filter(user=int(req_user)).order_by('-id')
                    else:
                        audit_logs = LogsAudit.objects.filter(user=int(req_user),project=int(req_proj)).order_by('-id')
                else:

                    if req_proj == 'all':
                        audit_logs = LogsAudit.objects.all().order_by('-id')
                    else:
                        audit_logs = LogsAudit.objects.filter(project=int(req_proj)).order_by('-id')

            context = {
                'audit_logs' : audit_logs,
            }

            data['html_form'] =  render_to_string('audit_log_partial.html', context, request=request)

            return JsonResponse(data)

        else:
            return HttpResponseForbidden()


    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))