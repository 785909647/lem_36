"""读取yaml文件"""
import yaml
import os
from config import path

def read_yaml(fpath):
    """通过 fpath 文件路径读取yaml数据。
    得到的是一个字典。
    """
    with open(fpath, encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)
    return data

def write_yaml(fpath,value):
    with open(fpath,"a+",encoding="utf-8") as f:
        yaml.dump(value,f)



yaml_path = os.path.join(path.config_path, 'alpex.yaml')
yaml_config_user = read_yaml(yaml_path)



yaml_path = os.path.join(path.config_path, 'lianxi.yaml')
yaml_conf_sql = read_yaml(yaml_path)



