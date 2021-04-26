'''添加项目测试用例执行'''
import pytest
from common.yaml_handler import yaml_config_user, write_yaml, yaml_path
from config.path import data_path
from middleware.turnover import Midd_Ware, Case_Data

excel_obj_two = Midd_Ware.excel_obj(data_path,"add")
excel = Midd_Ware.excel_obj(data_path,"add").read_data_obj2()
url = yaml_config_user["url"]+excel[0]["url"]



@pytest.mark.parametrize("case",excel)
def test_add(case,get_token):
    method = case["method"]
    headers = eval(case["Headers"])
    excepted = case["excepted"]

    #替换数据 #id# 替换自己的用例，@id@ 替换一个别人的ID
    data = Case_Data().re_repelace(case["data"],1)
    #所有数据填充好 类型转化好
    headers["Authorization"] = get_token[0]
    data = eval(data)
    resposn = Midd_Ware.req_obj.send_request(url=url,method=method,json=data,headers=headers)
    excel_obj_two.write_data(row=case["case_id"] + 1, column=10, value=str(resposn["msg"]))
    try:
        assert resposn["msg"] == excepted
        Midd_Ware.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
        excel_obj_two.write_data(row=case["case_id"] + 1, column=9, value="pass")
    except AssertionError as e:
        Midd_Ware.logger.info(
            "第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"], excepted,resposn["msg"]))
        excel_obj_two.write_data(row=case["case_id"] + 1, column=9, value="failure")
        excel_obj_two.write_data(row=case["case_id"] + 1, column=9, value="pass")
        raise e
