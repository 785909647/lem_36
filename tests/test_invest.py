'''充值接口测试用例'''
import pytest
from config.path import data_path
import json
from common.yaml_handler import yaml_config_user
from common.mysql_handler import MD
from middleware.turnover import Midd_Ware, Case_Data

data_excel = Midd_Ware.excel_obj(data_path,"recharge")
cases = data_excel.read_data_obj2()
url = yaml_config_user["url"] + cases[0]["url"]


@pytest.mark.parametrize("case",cases)
def test_invest(get_token,case):
    data = Case_Data().re_repelace(case["data"],1)
    data = eval(data)
    headers = eval(case["Headers"])
    headers["Authorization"] = get_token[0]
    excepted = case["excepted"]

    if case["title"] == "正常的充值":
        with MD() as sql:
            user_blacene = sql.query("select leave_amount from futureloan.member  where mobile_phone = 18873839536")["leave_amount"]
        increase = eval(data["amount"])
    data = json.dumps(data)

    # 发请求
    respose = Midd_Ware.req_obj.send_request(method=case["method"], url=url, data=data, headers=headers)
    data_excel.write_data(row=case["case_id"] + 1, column=10, value=str(respose["msg"]))
    if respose["msg"] == "OK" and case["title"] == "正常的充值":
        with MD() as sql:
            blacene = sql.query("select leave_amount from futureloan.member  where mobile_phone = 18873839536")["leave_amount"]
        ret = blacene - user_blacene
        try:
            assert ret == increase
            print("充值了{} 数据库增加了{} 比对正确".format(increase,ret))
        except AssertionError as e :
            print("请求前 账户余额{}。请求后账户余额{} 充值了{} 实际增加了{}".format(user_blacene,blacene,increase,ret))


    # 断言
    try:
        assert respose['msg'] == excepted
        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
        data_excel.write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info(
            "第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"], excepted,                                                                      respose["msg"]))
        data_excel.write_data(row=case["case_id"] + 1, column=9, value="failure")
        raise e








