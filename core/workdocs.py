import json
import boto3
import requests
import urllib
import os
import logging
import traceback

from django.conf import settings
from django.contrib.auth.models import User

from .models import *
from .data_encrypt import *

csr_logger        = logging.getLogger('csr')
csr_except_logger = logging.getLogger('csr_except')


client = boto3.client('workdocs', aws_access_key_id=settings.AWS_ACCESS_KEY_ID, aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='ap-southeast-1')
ParentFolderId = '99fe1357c771fc800a572119e017f5a53ce422b54068dbf646eba6a6bb9d0119'
Organization_ID = 'd-966718c1c4'


def create_user_WorkDocs(csr_user, created_by):

    try:

        csr_user_pass = CredInfo.objects.get(user=csr_user)

        password = decrypt_message(csr_user_pass.key_pass)

        # creating user using api call in workdocs
        create_user = client.create_user(
            OrganizationId=Organization_ID,
            Username=csr_user.username,
            EmailAddress=csr_user.email,
            GivenName=csr_user.first_name,
            Surname=csr_user.last_name,
            Password=password,
        )

        # storing the details in reviews model
        db_model = ReviewersWorkdocs(

                wdocs_usr_id = create_user['User']['Id'],
                csr_usr_id = csr_user,
                created_by = created_by,

            )
        db_model.save()

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# This will add the permissions to the document.
def share_document_WorkDocs(resource_id, checked_list, shared_by):

    try:

        share = False

        if checked_list:

            workdocs_UserIds = [ReviewersWorkdocs.objects.get(csr_usr_id__id=each).wdocs_usr_id for each in checked_list]

            Principals = [{'Id': i,'Type' : 'USER', 'Role' : 'CONTRIBUTOR'} for i in workdocs_UserIds]

            share_resp = client.add_resource_permissions(

                    ResourceId = resource_id,
                    Principals = Principals,
                    NotificationOptions={

                        'SendEmail': True,
                        'EmailMessage': 'Please review this document',
                    }
            )
            share = True

        else:
            reset_resorce_perm = client.remove_all_resource_permissions(

                ResourceId=resource_id
            )

        try:
            checked_listToStr = ','.join([str(elem) for elem in checked_list if elem != str(shared_by.id)])
            print(checked_listToStr)
        except:
            checked_listToStr = None


        # updating database record
        db_model = SharedDocumentData.objects.get(document_id=resource_id)
        db_model.shared_with = checked_listToStr
        db_model.save()

        return share

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def upload_document_WorkDocs(FolderId, file):

    try:

        file_name = os.path.basename(file)
        
        # Initializing a new document to upload into new folder.
        initiate_document_version_upload = client.initiate_document_version_upload(

            Name = file_name,
            ContentType = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            ParentFolderId = FolderId
        )
        document_id       = initiate_document_version_upload['Metadata']['Id']
        version_id_latest = initiate_document_version_upload['Metadata']['LatestVersionMetadata']['Id']
        url               = initiate_document_version_upload['UploadMetadata']['UploadUrl']
        SignedHeaders     = initiate_document_version_upload['UploadMetadata']['SignedHeaders']


        # uploading the file to the workDocs.
        file_data = open(settings.MEDIA_ROOT + '/' + file, 'rb').read()
        file_data_response = requests.put(url, headers=SignedHeaders, data=file_data)

        # Updating the document version and activating the document.
        document_version_response = client.update_document_version(
            DocumentId    = document_id,
            VersionId     = version_id_latest,
            VersionStatus = 'ACTIVE'
        )

        return [document_id, file_name]

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


def workdocs_operations(report, shared_by, checked_list):

    try:
        # import pdb;
        # pdb.set_trace();

        status = 0

        folder_name = report.project.project_name + '-' + report.project.protocol_id

        # check the user is created if not creating the users in workdocs
        if checked_list:

            checked_list.append(str(shared_by.id))

            for each in checked_list:

                try:
                    ReviewersWorkdocs.objects.get(csr_usr_id__id=each)

                except ReviewersWorkdocs.DoesNotExist:
                    user_obj = User.objects.get(pk=each)
                    create_user_WorkDocs(user_obj, shared_by)

            # creating account in workdocs for sharedby user also
            # create_user_WorkDocs(shared_by, shared_by)


        # check whether document/folder already exists
        try:
            is_already_shared = SharedDocumentData.objects.get(report=report)
        except SharedDocumentData.DoesNotExist:
            is_already_shared = None

        try:
            is_folder_exist = SharedDocumentData.objects.filter(folder_name=folder_name)
        except SharedDocumentData.DoesNotExist:
            is_folder_exist = None

        # if document already shared
        if is_already_shared != None and is_folder_exist:
            
            resource_id = SharedDocumentData.objects.get(report=report).document_id
            share_document_WorkDocs(resource_id, checked_list, shared_by)

        # if folder already exists
        elif is_already_shared == None and is_folder_exist:

            folder = SharedDocumentData.objects.filter(folder_name=folder_name).latest('id')

            upload_document = upload_document_WorkDocs(folder.folder_id, report.generated_report_path)

            # storing data into db
            db_model = SharedDocumentData(
                    folder_id = folder.folder_id,
                    folder_name = folder_name,
                    document_id = upload_document[0],
                    document_name = upload_document[1],
                    report = report,
                    shared_by = shared_by
                )
            db_model.save()

            share_document_WorkDocs(upload_document[0], checked_list, shared_by)

        else:
            # Creating a new folder in workDocs using api call.
            create_folder = client.create_folder(
                Name = folder_name,
                ParentFolderId = ParentFolderId
            )
            newly_created_folder_Id = create_folder['Metadata']['Id']

            upload_document = upload_document_WorkDocs(newly_created_folder_Id, report.generated_report_path)

            # storing data into db
            db_model = SharedDocumentData(
                    folder_id = newly_created_folder_Id,
                    folder_name = folder_name,
                    document_id = upload_document[0],
                    document_name = upload_document[1],
                    report = report,
                    shared_by = shared_by
                )
            db_model.save()

            share_document_WorkDocs(upload_document[0], checked_list, shared_by)

        status = 1

        return status

    
    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



def download_operation_WorkDocs(document_id):

    try:

        get_document = client.get_document(
            DocumentId = document_id
        )
        doc_ver = get_document['Metadata']['LatestVersionMetadata']['Id']
        doc_name = get_document['Metadata']['LatestVersionMetadata']['Name']

        get_document_version = client.get_document_version(
            DocumentId = document_id,
            VersionId = doc_ver,
            Fields = 'SOURCE',
        )
        download_url = get_document_version['Metadata']['Source']['ORIGINAL']

        return download_url

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))


# To get the version of document from the WorkDocs
def get_WorkDocsVersions(documents_list):

    try:

        document_versions_dict = {}
        
        for each in documents_list:

            describe_document_versions = client.describe_document_versions(
                    DocumentId = each.document_id
                )

            document_versions_dict[each.document_id] = float(len(describe_document_versions['DocumentVersions']))

        return document_versions_dict

    except Exception as e:
        csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))



# To delete the folder on clear configurations
def del_workdocs_files_on_clear__config_usr(project):

    try:
        workdocs_folder_id = SharedDocumentData.objects.filter(report__project=project).latest('id')

    except SharedDocumentData.DoesNotExist:
        workdocs_folder_id = None

    if workdocs_folder_id:

        try:
            delete_folder = client.delete_folder(
                FolderId=workdocs_folder_id.folder_id
            )
        except Exception as e:
            csr_except_logger.critical(str(e) + '\n' + str(traceback.format_exc()))

    else:
        pass