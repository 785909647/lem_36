'''登录测试用例执行'''

from config.path import data_path
import pytest
from common.yaml_handler import yaml_config_user
from middleware.turnover import Midd_Ware, Case_Data

excel_obje = Midd_Ware.excel_obj(data_path, "login")
cases = excel_obje.read_data_obj2()
url = yaml_config_user["url"] + cases[0]["url"]

@pytest.mark.parametrize("case",cases)
def test_login(case):
    data = (case["data"]) #请求方法
    headers = eval(case["Headers"]) #请求头
    excepted = case["excepted"] # 预期结果
    #user_name# 已注册账号登录， #no_user_name# 传入未注册的账号
    sset = Case_Data()
    data = sset.re_repelace(data,1)
    #发请求
    respose = Midd_Ware.req_obj.send_request(method=case["method"], url=url, json=eval(data), headers=headers)
    excel_obje.write_data(row=case["case_id"]+1,column=10,value=str(respose["msg"]))
    # 断言
    try:
        assert respose['msg'] == excepted
        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
        excel_obje.write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info("第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"], excepted,respose["msg"]))
        excel_obje.write_data(row=case["case_id"] + 1, column=9, value="failure")
        raise e






