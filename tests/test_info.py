'''测试提现接口'''
import json
import re
from common.mysql_handler import MD
from common.yaml_handler import yaml_config_user
from middleware.turnover import Midd_Ware, Case_Data
from config.path import data_path
import pytest

excel = Midd_Ware.excel_obj(data_path,"withdraw")
cases = excel.read_data_obj2()



@pytest.mark.parametrize("case",cases)
def test_withdraw(case,get_token):
    url = yaml_config_user["url"]+case["url"]
    headers = eval(case["Headers"])
    excepted = case["excepted"]
    data = Case_Data().re_repelace(case["data"],1)
    #替换数据  #id 替换自己的iD #note_id 数据库拿一个id,#no_id# 去数据库查最大ID+1
    if 14 == case["case_id"]:
        data["member_id"] = int(data["member_id"])+9
        data = json.dumps(data)
    if case['check_sql']:
        with MD() as q:
            q.query(case["check_sql"])
            pattern = re.compile(r'\d+')  # pattern可以理解为一个匹配模式
            ret = re.search(pattern,case["check_sql"])
            number = ret.group()
            ret = q.query("select leave_amount from futureloan.member where id=1000104510")["leave_amount"]
            print("查到账户的余额是{}。要修改的数据是{}".format(ret,number))
    headers["Authorization"] = get_token[0]
    data = eval(data)
    # 发请求
    respose = Midd_Ware.req_obj.send_request(url=url,headers=headers,json=data,method=case["method"])
    excel.write_data(row=case["case_id"]+1,column=10,value=str(respose["msg"]))
    try:
        assert respose["msg"] == excepted
        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
        excel.write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info(
            "第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"], excepted,
                                                                      respose["msg"]))
        excel.write_data(row=case["case_id"] + 1, column=9, value="failure")
        raise e


