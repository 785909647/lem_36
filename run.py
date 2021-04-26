
import os,sys

dir =  os.path.dirname(os.path.abspath(__file__))
sys.path.append(dir)
sys.path.append(r"C:\Users\luluh\PycharmProjects\api_test_pytest\venv\Lib\site-packages")
import pytest



pytest.main(["-s","-v"])