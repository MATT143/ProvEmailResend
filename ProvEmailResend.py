#Maa

import sys
import json
import requests
import cx_Oracle
instance=sys.argv[1]
Wbid = sys.argv[2]
WebOrderId=[Wbid]

WID=['%'+WebOrderId[0]+'%']

#----------------------TS1 FUNCTIONS---------------------------#
def GetBaseOrderEmailidTS1(WebOrderId):
    dsn_tns_cg1 = cx_Oracle.makedsn('173.38.21.150', '1841', service_name='ts1cg1_srvc_oth.cisco.com')
    con_cg1 = cx_Oracle.connect(user='APPSRO', password='Read0nly', dsn=dsn_tns_cg1)
    cur_cg1=con_cg1.cursor()
    query="select action_sub_type,provision_info_email from XXOPL.XXOPL_ORDER_LINES_ALL WHERE item_type_code='MAJOR' and subscription_ref_id in (select distinct SUBSCRIPTION_REF_ID from XXOPL.XXOPL_ORDER_LINES_ALL where header_id in (select distinct header_id from apps.xxopl_order_headerS_all where ORIG_SYS_DOCUMENT_REF=:1))"
    cur_cg1.execute(query,WebOrderId)
    result=cur_cg1.fetchall()
    provMailDict=dict()
    for r in result:
        provMailDict.update({r[0]:r[1]})
    ProvisioningEmail =provMailDict['0']
    return ProvisioningEmail

def InvokePayloadTS1(WID,ProvEmail):
    dsn_tns_isrv = cx_Oracle.makedsn('64.100.226.168', '1541', service_name='SVSINT.cisco.com')
    con_isrv = cx_Oracle.connect(user='isrv', password='isrv2009', dsn=dsn_tns_isrv)
    cur_isrv=con_isrv.cursor()
    cur_isrv.execute("select payload from xx_servorch_engine_state where EXTERNAL_ID like :1 ",WID)
    OrderPayload=json.loads(cur_isrv.fetchone()[0].read())
    OrderPayload['orderRequest']['orderLines'][0]['majorLine']['lineStatus']='1'
    OrderPayload['orderRequest']['orderLines'][0]['majorLine']['provInfoEmail'] = ProvEmail
    OrderPayload['orderRequest']['sender']['serviceContext']['requestType']='CREATE'
    InvokeProvisioningPayload=json.dumps(OrderPayload)
    return InvokeProvisioningPayload

def InvokeCallTS1(InvPld):
    InvokeUrl='https://sbpsfl-st1.cloudapps.cisco.com/sfl/rest/provision'
    InvokeRequest=InvPld
    BasicToken='Basic c2Jwc2VydmljZXMuZ2VuOmNpc2NvQFNCUCMxMjM='
    Resp = requests.post(url=InvokeUrl, data=InvokeRequest,headers={'Content-type': 'application/json', 'Authorization': BasicToken})
    InvokeResponse=Resp.json()
    return InvokeResponse

def ClearSFLRecordsTs1(WID):
    dsn_tns_sfl = cx_Oracle.makedsn('64.100.226.169', '1541', service_name='SVSINT.cisco.com')
    con_sfl = cx_Oracle.connect(user='SFL', password='Sfl#123#', dsn=dsn_tns_sfl)
    cur_sfl=con_sfl.cursor()
    cur_sfl.execute("delete from XX_SERVORCH_ENGINE_STATE where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from XX_SERVORCH_ORCHSTATUS  where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from XX_SERVORCH_WORKFLOW_TASK  where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_PROVISIONING_DETAILS where SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_PROVISIONING_PLANS  where SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID =:1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_SERVICE_ITEMS  where SFL_ORDER_LINE_ID IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID =:1)",WebOrderId)
    cur_sfl.execute("delete from SFL_SUBSCRIPTIONS WHERE  SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_LINES where WEB_ORDER_ID = :1",WebOrderId)
    con_sfl.commit()
    return

def LineStatusCheckTS1(WebOrderId):
    dsn_tns_com = cx_Oracle.makedsn('64.100.226.168', '1541', service_name='SVSINT.cisco.com')
    con_com = cx_Oracle.connect(user='COMUSER', password='cmusr10', dsn=dsn_tns_com)
    cur_com = con_com.cursor()
    cur_com.execute("select line_status from COM_ORDER_MAPPER where order_id IN (select ORDER_ID from com_order where salesorder_id=:1)",WebOrderId)
    LineStatus=cur_com.fetchone()
    return LineStatus[0]

def UpdatedProvEmailCheckTS1(WebOrderId):
    dsn_tns_sfl = cx_Oracle.makedsn('64.100.226.169', '1541', service_name='SVSINT.cisco.com')
    con_sfl = cx_Oracle.connect(user='SFL', password='Sfl#123#', dsn=dsn_tns_sfl)
    cur_sfl = con_sfl.cursor()
    cur_sfl.execute("select provisioning_request from SFL_ORDER_PROVISIONING_DETAILS where provisioning_interface='PI_WEBEX_DC' and SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    Prov_request=cur_sfl.fetchone()
    return Prov_request[0]


#-------------------------TS3 Functions------------------------------------------------------------------#

def LineStatusCheckTS3(WebOrderId):
    dsn_tns_com = cx_Oracle.makedsn('64.100.226.170', '1541', service_name='SVSTST.cisco.com')
    con_com = cx_Oracle.connect(user='COMUSER', password='resu_6passmoc', dsn=dsn_tns_com)
    cur_com = con_com.cursor()
    cur_com.execute("select line_status from COM_ORDER_MAPPER where order_id IN (select ORDER_ID from com_order where salesorder_id=:1)",WebOrderId)
    LineStatus=cur_com.fetchone()
    return LineStatus[0]

def GetBaseOrderEmailidTS3(WebOrderId):
    dsn_tns_cg1 = cx_Oracle.makedsn('173.38.21.150', '1841', service_name='ts3cg1_srvc_oth.cisco.com')
    con_cg1 = cx_Oracle.connect(user='APPSRO', password='Lj0V0s6G', dsn=dsn_tns_cg1)
    cur_cg1=con_cg1.cursor()
    query="select action_sub_type,provision_info_email from XXOPL.XXOPL_ORDER_LINES_ALL WHERE item_type_code='MAJOR' and subscription_ref_id in (select distinct SUBSCRIPTION_REF_ID from XXOPL.XXOPL_ORDER_LINES_ALL where header_id in (select distinct header_id from apps.xxopl_order_headerS_all where ORIG_SYS_DOCUMENT_REF=:1))"
    cur_cg1.execute(query,WebOrderId)
    result=cur_cg1.fetchall()
    provMailDict=dict()
    for r in result:
        provMailDict.update({r[0]:r[1]})
    ProvisioningEmail =provMailDict['0']
    return ProvisioningEmail

def InvokePayloadTS3(WID,ProvEmail):
    dsn_tns_isrv = cx_Oracle.makedsn('64.100.226.171', '1541', service_name='SVSTST.cisco.com')
    con_isrv = cx_Oracle.connect(user='ISRV', password='pass_1vrsi', dsn=dsn_tns_isrv)
    cur_isrv=con_isrv.cursor()
    cur_isrv.execute("select payload from xx_servorch_engine_state where EXTERNAL_ID like :1 ",WID)
    OrderPayload=json.loads(cur_isrv.fetchone()[0].read())
    OrderPayload['orderRequest']['orderLines'][0]['majorLine']['lineStatus']='1'
    OrderPayload['orderRequest']['orderLines'][0]['majorLine']['provInfoEmail'] = ProvEmail
    OrderPayload['orderRequest']['sender']['serviceContext']['requestType']='CREATE'
    InvokeProvisioningPayload=json.dumps(OrderPayload)
    return InvokeProvisioningPayload

def InvokeCallTS3(InvPld):
    InvokeUrl='https://sbpsfl-st2.cloudapps.cisco.com/sfl/rest/provision'
    InvokeRequest=InvPld
    BasicToken='Basic c2Jwc2VydmljZXMuZ2VuOmNpc2NvQFNCUCMxMjM='
    Resp = requests.post(url=InvokeUrl, data=InvokeRequest,headers={'Content-type': 'application/json', 'Authorization': BasicToken})
    InvokeResponse=Resp.json()
    return InvokeResponse

def ClearSFLRecordsTs3(WID):
    dsn_tns_sfl = cx_Oracle.makedsn('64.100.226.170', '1541', service_name='SVSTST.cisco.com')
    con_sfl = cx_Oracle.connect(user='SFL_RO', password='Sfl_ro#123', dsn=dsn_tns_sfl)
    cur_sfl=con_sfl.cursor()
    cur_sfl.execute("delete from XX_SERVORCH_ENGINE_STATE where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from XX_SERVORCH_ORCHSTATUS  where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from XX_SERVORCH_WORKFLOW_TASK  where external_id IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_PROVISIONING_DETAILS where SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_PROVISIONING_PLANS  where SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID =:1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_SERVICE_ITEMS  where SFL_ORDER_LINE_ID IN (select to_char(sfl_order_line_id) from SFL_ORDER_LINES where WEB_ORDER_ID =:1)",WebOrderId)
    cur_sfl.execute("delete from SFL_SUBSCRIPTIONS WHERE  SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    cur_sfl.execute("delete from SFL_ORDER_LINES where WEB_ORDER_ID = :1",WebOrderId)
    con_sfl.commit()
    return

def UpdatedProvEmailCheckTS3(WebOrderId):
    dsn_tns_sfl = cx_Oracle.makedsn('64.100.226.170', '1541', service_name='SVSTST.cisco.com')
    con_sfl = cx_Oracle.connect(user='SFL_RO', password='Sfl_ro#123', dsn=dsn_tns_sfl)
    cur_sfl = con_sfl.cursor()
    cur_sfl.execute("select provisioning_request from SFL_ORDER_PROVISIONING_DETAILS where provisioning_interface='PI_WEBEX_DC' and SFL_ORDER_LINE_ID IN (select sfl_order_line_id from SFL_ORDER_LINES where WEB_ORDER_ID = :1)",WebOrderId)
    Prov_request=cur_sfl.fetchone()
    return Prov_request[0]

#-----------------------------------------Main----------------------------------------------------#
if instance.lower()=='ts1':
    try:
        lineStatus=LineStatusCheckTS1(WebOrderId)
        if lineStatus=='32' or lineStatus=='11':
            ClearSFLRecordsTs1(WebOrderId)
            print("Record Cleared")
            ProvisioningEmail=GetBaseOrderEmailidTS1(WebOrderId)
            print(ProvisioningEmail)
            InvokePayload=InvokePayloadTS1(WID,ProvisioningEmail)
            print(InvokePayload)
            InvokeResponse=InvokeCallTS1(InvokePayload)
            print(InvokeResponse)
            if InvokeResponse['orderResponse']['processResult']=='SUCCESS':
                print(UpdatedProvEmailCheckTS1(WebOrderId))
                if UpdatedProvEmailCheckTS1(WebOrderId) != None:
                    UpdatedEmail = json.loads(UpdatedProvEmailCheckTS1(WebOrderId).read())['common']['provisioningContactEmail']
                    if UpdatedEmail==ProvisioningEmail:
                        print("PROVISIONING EMAIL CORRECTION : SUCCESSFUL")
                        print("PLEASE CHECK THE INBOX IN {}".format(ProvisioningEmail))
                else:
                    print("EMPTY REQUEST FOR PI_WEBEX_DC")
            else:
                print("PROVISIONING EMAIL CORRECTION:{}".format(InvokeResponse['orderResponse']['processResult']))
    except Exception as e:
        print(e)

elif instance.lower()=='ts3':
    try:
        lineStatus=LineStatusCheckTS3(WebOrderId)
        if lineStatus=='32' or lineStatus=='11':
            ClearSFLRecordsTs3(WebOrderId)
            ProvisioningEmail=GetBaseOrderEmailidTS3(WebOrderId)
            InvokePayload=InvokePayloadTS3(WID,ProvisioningEmail)
            InvokeResponse=InvokeCallTS3(InvokePayload)
            if InvokeResponse['orderResponse']['processResult'] == 'SUCCESS':
                if UpdatedProvEmailCheckTS3(WebOrderId) != None:
                    UpdatedEmail = json.loads(UpdatedProvEmailCheckTS3(WebOrderId).read())['common']['provisioningContactEmail']
                    if UpdatedEmail == ProvisioningEmail:
                        print("PROVISIONING EMAIL CORRECTION : SUCCESSFUL")
                        print("PLEASE CHECK THE INBOX IN {}".format(ProvisioningEmail))
                else:
                    print("EMPTY REQUEST FOR PI_WEBEX_DC")
            else:
                print("PROVISIONING EMAIL CORRECTION:{}".format(InvokeResponse['orderResponse']['processResult']))
    except Exception as e:
        print(e)


















