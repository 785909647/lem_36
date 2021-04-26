import os
import re

from faker import Faker
from common.excel_handler import ReadExcel,CaseData
from common.logger import get_logger
from common.mysql_handler import MD
from common.request_handler import Http_Request
from common.yaml_handler import read_yaml, yaml_config_user
from config import path


class Midd_Ware():
    '''中间件'''
    #操作测试excel用例对象
    excel_obj = ReadExcel
    #临时存放 类属性的对象
    depo_obj = CaseData

    # 日志收集文件
    log_file = os.path.join(path.logs_path, 'py36.log')
    #日志收集器对象
    logger = get_logger(file=log_file)

    #数据库对象
    my_sql = MD()

    #请求request对象
    req_obj = Http_Request()

    #读取yaml文件配置
    yaml_path = os.path.join(path.config_path, 'alpex.yaml')
    yaml_config_user = read_yaml(yaml_path)


    @staticmethod
    def generate_new_phone():
        """自动生成手机号"""
        fk = Faker(locale='zh_CN')
        phone = fk.phone_number()
        while True:
            with MD() as f:
                data = f.query("select * from futureloan.member where mobile_phone = {}".format(phone))
                if data == None:
                    return phone
    @staticmethod
    def get_note_id(one=None):
        '''获取一个其他用户的ID'''
        with MD() as q:
            res = q.query("select max(id) from futureloan.member")["max(id)"]
            if one:
                res+=9
            return res
    @staticmethod
    def register_phone():
        '''返回已经注册的手机号'''
        with MD() as f:
            register_phone = f.query("select  mobile_phone from futureloan.member ORDER BY id desc LIMIT 1", one=False)[0]["mobile_phone"]
            return register_phone



class Case_Data(Midd_Ware):
    '''存放测试用例参数化所需类属性'''
    case_data = {}
    def __new__(cls, *args, **kwargs):
        # if not hasattr(cls,"_isince"):
            setattr(Case_Data,'case_data',yaml_config_user["cases_data"])
            # Case_Data._isince = super().__new__(cls)
            return super().__new__(cls)

    def __init__(self,**kwargs):
        setattr(Case_Data, 'case_data', yaml_config_user["cases_data"])
        if kwargs:
            for i,v in kwargs.items():
                setattr(Case_Data,i,v)

    def re_repelace(self,string,one=None,**kwargs):
        '''匹配元串 完成替换操作'''
        pattern = re.compile('#(.+?)#')
        if one:
            for i in re.finditer(pattern,string):
                try:
                    cloun_data = str(getattr(self,"case_data")[i.group(1)])
                    if cloun_data == "jie":
                        print(111)
                    if cloun_data in dir(self):
                        cloun_data = str(getattr(self,cloun_data)())
                    string = string.replace(i.group(), cloun_data)
                except KeyError as e :
                    if kwargs:
                        for k,v in kwargs.items():
                            setattr(self,k,v)
                            cloun_data = str(getattr(self,k))
                            string = string.replace(i.group(), cloun_data)
                    cloun_data = str((getattr(self,str(i.group(1)))))
                    string = string.replace(i.group(), cloun_data)

        else:
            ret = re.search(pattern,string)
            data = (ret.group())
        # 得到要替换的参数    得到 替换的参数  完成替换
            try:
                t_data = getattr(self,"case_data")[ret.group(1)]
            except AttributeError as e:
                print("没有这个属性{}".format(ret.group(1)))
                raise e
            string = string.replace(data,str(t_data))
        return string



