'''投资用例测试'''
import json
from multiprocessing import Process
from threading import  Thread
import pytest
from jsonpath import jsonpath
from common.request_handler import Http_Request
from common.yaml_handler import yaml_config_user
from config.path import data_path
from middleware.turnover import Midd_Ware, Case_Data




class Get_Init(Case_Data):
    #登录URL 后期维护
    login_url = yaml_config_user["url"] + "/member/login"
    #添加项目URL  后期维护
    add_url = yaml_config_user["url"] + "/loan/add"
    #审核项目URL  后期维护
    audit_url = yaml_config_user["url"] + "/loan/audit"
    #投资项目 URL  后期维护
    invest_url = yaml_config_user["url"] + "/member/invest"
    # 目前暂定请求方法  后期维护
    method = "post"
    # 目前暂定请求投  后期维护
    head = {"Content-Type":"application/json","X-Lemonban-Media-Type":"lemonban.v2","Authorization":None}
    # 测试投资用例data  后期维护
    cases = Midd_Ware.excel_obj(data_path, "invest").readline_data_obj("[6]")
    inwest_cases = Midd_Ware.excel_obj(data_path, "invest").read_data_obj2()
    # 测试投资依赖用例data  后期维护
    body_data = {"jie":{"mobile_phone": yaml_config_user["cases_data"]["user_name"],
                       "pwd": yaml_config_user["cases_data"]["pwd"]}, #借款人请求body
                 "shen":{"mobile_phone": yaml_config_user["cases_data"]["root_name"],
                       "pwd": yaml_config_user["cases_data"]["root_pwd"]},#审核人请求body
                  "add":{"member_id":None,"title":"借借借","amount":100,"loan_rate":11.0,
                          "loan_term":22,"loan_date_type":2,"bidding_days":10},
                  "audit":{"loan_id":None,"approved_or_not":"true"}}
    # 根据什么样的属性 去反射
    pro_ject = {}

    def __init__(self,):
        #project --调用成功的  ，#projecr----调用创建的项目未审核，#give_id----调用已结束的项目
        #project---调用已生成还款计划的，
        with Midd_Ware.my_sql as f:
            try:
                max_id = f.query("select max(id) from futureloan.loan ")["max(id)"] + 9  # 不存在的项目ID
                id_ok_one = f.query("select id  from futureloan.loan  where `status` = 1 LIMIT 1 ")["id"]  # 审核中的项目
                try:
                    id_ok = f.query("select id  from futureloan.loan  where `status` = 4 LIMIT 1 ")["id"]  # 还款完成通过的项目
                except:
                    id_ok = f.query("update futureloan.loan set `status` =4 where id = 2052534")
                id_no = f.query("select id  from futureloan.loan  where `status` = 5 LIMIT 1  ")["id"]  # 审核不通过的项目
                id_login = f.query("select id  from futureloan.loan  where `status` = 3 LIMIT 1")["id"]  # 审核还款中的项目
                f.query("update  futureloan.member set leave_amount = 2000 where id = {}".format(yaml_config_user["cases_data"]["id"]))
            except:
                pass

        self.pro_ject["N_id"] = max_id
        self.pro_ject["projecr"] = id_ok_one
        self.pro_ject["give_id"] = id_ok
        self.pro_ject["login_id"] = id_login
        self.pro_ject["id_no"] = id_no
        self.pro_ject["jie_id"] = self.get_token["jieid"]
        self.pro_ject["shen_id"] = self.get_token["shenid"]
        self.pro_ject["project"] = "audit_success_id"
        self.cas_data.update(self.pro_ject)
        self.amount = self.get_amount


    @property
    def get_amount(self):
        '''返回用户余额'''
        with Midd_Ware.my_sql as f:
            ret = f.query("select leave_amount from futureloan.member where id = {} ".format(self.pro_ject["jie_id"]))["leave_amount"]
            return ret




    @property
    def get_token(self):
        '''借款人token 审核人token 绑定一个类属性 dict对象'''

        dict_data = {}
        data_dict = {k:v for k,v in self.body_data.items() if k in ("jie","shen") }

        for k,v in data_dict.items():
            respose = Http_Request().send_request(method=self.method, url=self.login_url, json=v, headers=self.head)
            str_token_type = jsonpath(respose, "$..token_type")[0]
            str_token = jsonpath(respose, "$..token")[0]
            str_id = jsonpath(respose, "$..id")[0]
            token_data = str_token_type + " " + str_token
            dict_data[k+"token"] = token_data
            dict_data[k+"id"] = str_id

        return dict_data


    def audit_success_id(self):
        '''调用即返回一个审核好的项目'''
        id = None
        susscess = {"code":0,"msg":"OK"}
        data_dict = {k: v for k, v in self.body_data.items() if k in ("add", "audit")}
        for  k ,v in data_dict.items():
            if k == "add":
                data_dict[k]["member_id"] = self.get_token["jieid"]
                self.head["Authorization"] = self.get_token["jietoken"]
                respose = Http_Request().send_request(method=self.method, url=self.add_url, json=v,
                                                      headers=self.head)
                id = jsonpath(respose, "$..id")[0]
            else:
                v["loan_id"]= id
                self.head["Authorization"] = self.get_token["shentoken"]
                respose = Http_Request().send_request(method="PATCH",url=self.audit_url, json=v,
                                                  headers=self.head)
                if respose["msg"] == "OK":
                    return id
                else:
                    raise KeyError("审核项目失败，失败原因是{},请检查第67-75行}".format(respose))



    def test_one(self,n):
        '''供map迭代'''
        ret = eval(self.re_repelace(str(n),1))
        return ret


    def gevi_map(self):
        #返回所有投资的测试数据
        data = list(map(self.test_one,self.inwest_cases))
        return data




get_obj = Get_Init()
test_ret_invest = pytest.mark.parametrize


@pytest.mark.parametrize("case",get_obj.gevi_map())
def test_ret_invest(case):
    data = eval(case["data"])
    headers = eval(case["Headers"])
    excepted = eval(case["excepted"])
    if not headers["Authorization"]:
        headers["Authorization"] = get_obj.get_token["jietoken"]
    else:
        headers["Authorization"] = get_obj.get_token["shentoken"]

    if case["check_sql"]:
        if str(case["check_sql"]).isdigit():
            front_amount = get_obj.get_amount
        else:
            str_ret = case["check_sql"]
            re_data = data["member_id"]
            str_ret.replace("#jie_id#",re_data)
            front_amount = get_obj.get_amount
            with Midd_Ware.my_sql as f:
                amount = f.query(str_ret)
            print("修改前账户余额{}  修改后账户余额{}".format(front_amount,amount))




    #发请求
    respose = Midd_Ware.req_obj.send_request(method=case["method"], url=get_obj.invest_url, data=json.dumps(data), headers=headers)
    respose.pop("copyright")
    Midd_Ware.excel_obj(data_path, "invest").write_data(row=case["case_id"] + 1, column=10, value=str(respose["msg"]))
    # 断言
    try:
        case_stutas = False
        for k,v in excepted.items():
            assert respose[k] == excepted[k]
            if not respose["code"]:
                case_stutas  = True
                behind_amount = get_obj.get_amount
                assert front_amount -  behind_amount  == data["amount"]

        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
        Midd_Ware.excel_obj(data_path, "invest").write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info(
            "第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"], excepted,
                                                                      respose["msg"]))
        if case_stutas:
            Midd_Ware.excel_obj(data_path, "invest").write_data(row=case["case_id"] + 1, column=9, value="failure/ 请求前余额{},请求后余额{}".format(front_amount,behind_amount))
        else:
            Midd_Ware.excel_obj(data_path, "invest").write_data(row=case["case_id"] + 1, column=9, value="failure")
        raise e




