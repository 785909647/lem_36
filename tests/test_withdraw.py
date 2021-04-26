import pytest
import json
from common.request_handler import Http_Request
from common.yaml_handler import yaml_config_user
from jsonpath import jsonpath

from config.path import data_path
from middleware.turnover import Midd_Ware


@pytest.fixture(scope="class")
def get_token():
    '''借款人token  和测试id'''
    url = yaml_config_user["url"] + "/member/login"
    method = "post"
    head = {"Content-Type":"application/json","X-Lemonban-Media-Type":"lemonban.v2"}
    data = {"mobile_phone": yaml_config_user["cases_data"]["user_name"],"pwd":yaml_config_user["cases_data"]["pwd"]}
    data = json.dumps(data)
    respose = Http_Request().send_request(method=method, url=url, data=data, headers=head)
    str_token_type = jsonpath(respose,"$..token_type")[0]
    str_token = jsonpath(respose,"$..token")[0]
    str_id = jsonpath(respose,"$..id")[0]
    token_data = str_token_type+" "+str_token
    return (token_data,str_id)


@pytest.fixture(scope="class")
def audit_inwest(get_token):
    '''创建多个项目并返回一个字典 里面存有多个设置好的项目id '''
    dict_project_data = {}
    for i in range(1,5):
        url = yaml_config_user["url"] + "/loan/add"
        method = "post"
        head = {"Content-Type":"application/json","X-Lemonban-Media-Type":"lemonban.v2","Authorization":None}
        ret = get_token
        data = {
        "member_id": ret[1],
        "title":"借借借",
        "amount":100,
        "loan_rate":11.0,
        "loan_term":22,
        "loan_date_type":2,
        "bidding_days":10}
        head["Authorization"] = ret[0]
        respose = Http_Request().send_request(method=method, url=url, json=data, headers=head)
        ret_id = jsonpath(respose,"$..id")[0]
        dict_project_data["project_id{}".format(i)] = ret_id
    return (dict_project_data)

@pytest.fixture(scope="class")
def get_root_token():
    '''返回需要处理的审核人参数处理和token'''
    token_dict = {} #返回所有token
    data_dict = {} #返回需要依赖的数据

    url = yaml_config_user["url"] + "/member/login"
    method = "post"
    head = {"Content-Type": "application/json", "X-Lemonban-Media-Type": "lemonban.v2"}
    data = {"mobile_phone": yaml_config_user["cases_data"]["root_name"], "pwd": yaml_config_user["cases_data"]["root_pwd"]}
    data = json.dumps(data)
    respose = Http_Request().send_request(method=method, url=url, data=data, headers=head)
    str_token_type = jsonpath(respose, "$..token_type")[0]
    str_token = jsonpath(respose, "$..token")[0]
    str_id = jsonpath(respose, "$..id")[0]
    token_data = str_token_type + " " + str_token
    token_dict["shenhe"] = token_data  #审核人token
    token_dict["shenhe_id"] = str_id   #审核人id

    with Midd_Ware.my_sql as f:
        max_id = f.query("select max(id) from futureloan.loan ")["max(id)"] +1#不存在的项目ID
        id_ok_one = f.query("select id  from futureloan.loan  where `status` = 2 LIMIT 1 ")["id"] #审核通过的项目
        id_ok = f.query("select id  from futureloan.loan  where `status` = 4 LIMIT 1 ")["id"] #审核通过的项目
        id_no = f.query("select id  from futureloan.loan  where `status` = 5 LIMIT 1  ")["id"] #审核不通过的项目
        id_login = f.query("select id  from futureloan.loan  where `status` = 3 LIMIT 1")["id"] #审核还款中的项目
        data_dict["N_id"] = max_id
        data_dict["yes_id"] = id_ok_one
        data_dict["no_id"] = id_no
        data_dict["give_id"] = id_ok
        data_dict["get_id"] = id_login
    return data_dict,token_dict

@pytest.fixture(scope="class")
def send_head(get_token,get_root_token):
    '''处理头'''
    excel = Midd_Ware.excel_obj(data_path, "audit")
    head = (excel.readline_data_obj("[7]"))

    for i,k in enumerate(head):
        data_valu = eval(k["Headers"])
        data_value = data_valu["Authorization"]
        if data_value:
            data_valu["Authorization"] = get_root_token[1]["shenhe"]
        else:
            data_valu["Authorization"] =get_token[0]
        head[i] = data_valu
    return head

@pytest.fixture(scope="class")
def init_audit(audit_inwest,get_root_token,send_head):
    audit_inwest.update(get_root_token[0])
    for k, v in audit_inwest.items():
        setattr(Midd_Ware, k, v)


cases  = Midd_Ware.excel_obj(data_path,"invest").readline_data_obj("[6]")
@pytest.fixture(scope="class",params=cases)
def init_project(request,audit_inwest,get_root_token):
    user = request.param
    head ={"Content-Type":"application/json","X-Lemonban-Media-Type":"lemonban.v2","Authorization":get_root_token[1]["shenhe"]}
    url = yaml_config_user["url"] + "/loan/audit"
    method = "PATCH"
    data_dict = {}
    for i in audit_inwest.values():
        a = {
        "loan_id":i,
        "approved_or_not":"true"}

        respose = Http_Request().send_request(method=method, url=url, json=a, headers=head)
        data_dict[i] = respose
    return data_dict








