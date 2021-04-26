import requests

from common.logger import logger


class Http_Request(object):
    def send_request(self,method,url,data=None,headers=None,json=None,params=None,**kw):
        if method == "get":

            resp = requests.request(method=method,url=url,headers=headers,params=params,**kw)
        else:
            if json:

                resp = requests.request(method=method,url=url,headers=headers,json=json,**kw)
            else:

                resp = requests.request(method=method, url=url, headers=headers, data=data, **kw)

        try:
            ret = resp.json()
        except:
            ret = resp.text()
        return ret










