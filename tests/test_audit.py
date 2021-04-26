'''审核项目测试用例'''
import json

import jsonpath
import pytest

from common.yaml_handler import yaml_config_user
from config.path import data_path
from middleware.turnover import Midd_Ware, Case_Data

@pytest.mark.usefixtures("init_audit")
class Test_Audit():
    mid_obj = Midd_Ware()
    mid_case = Case_Data()
    excel = mid_obj.excel_obj(data_path, "audit")
    cases = excel.read_data_obj2()
    url = yaml_config_user["url"] + cases[0]["url"]



    @pytest.mark.parametrize("case",cases)
    def test_api_audit(self,case,get_root_token,get_token):
        data = self.mid_case.re_repelace(case["data"], 1)
        excepted = case["excepted"]
        head = eval(case["Headers"])
        if head["Authorization"]:
            head["Authorization"] =  get_token[0]
        else:
            head["Authorization"] = get_root_token[1]["shenhe"]
        if case["case_id"] == 3:
            respose =  self.mid_obj.req_obj.send_request(method=case["method"], url=self.url, data=data, headers=head)
        else:
            data = eval(data)
            respose = self.mid_obj.req_obj.send_request(method=case["method"], url=self.url, json=data, headers=head)

        #断言
        try:
            for k,v in eval(case["excepted"]).items():
                assert jsonpath.jsonpath(respose, k)[0] == v
            self.mid_obj.logger.info("第{}条测试用例通过,请求参数是{}".format(case["case_id"], data))
            self.excel.write_data(row=case["case_id"] + 1, column=9, value="pass")
        except AssertionError as e:
            Midd_Ware.logger.info("第{}条测试用例不通过 ！\n 请求体是{} 请求内容是{}。预期结果是{}---返回结果是{}".format(case["case_id"], data, case["title"],excepted,respose["msg"]))
            self.excel.write_data(row=case["case_id"] + 1, column=9, value="failure")
            raise e
        finally:
            self.excel.write_data(row=case["case_id"] + 1, column=10, value=jsonpath.jsonpath(respose,"$..msg")[0])














