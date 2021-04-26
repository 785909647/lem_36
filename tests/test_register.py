'''注册测试用例执行'''
from config.path import data_path
import pytest
from common.yaml_handler import yaml_config_user
from common.mysql_handler import MD
from middleware.turnover import Midd_Ware, Case_Data

excel = Midd_Ware.excel_obj(data_path, "register").read_data_obj2()




@pytest.mark.parametrize("case",excel)
def test_register(case):

    url =yaml_config_user["url"] +case["url"]
    data = (case["data"])
    headers = eval(case["Headers"])
    excepted = case["excepted"]
    #测试数据  有  #user_name# 传入正确的数据  #phone# 传入已注册的账号 #pwd#传入正确的密码
    sset = Case_Data()
    data = sset.re_repelace(data,1)

    #发请求
    respose = Midd_Ware.req_obj.send_request(method=case["method"],url=url,json=eval(data),headers=headers)
    Midd_Ware.excel_obj(data_path, "register").write_data(row=case["case_id"]+1,column=10,value=str(respose["msg"]))
    print(data)
    #断言
    try:
        assert respose['msg'] == excepted
        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"],data))
        Midd_Ware.excel_obj(data_path, "register").write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info("第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"],data,case["title"],excepted,respose["msg"]))
        Midd_Ware.excel_obj(data_path, "register").write_data(row=case["case_id"] + 1, column=9, value="failure")
        raise e









