import re
import requests
import random
import time
import hashlib
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry


class ModianScraper:

    def __init__(self):

        self.cookies = {
            '_ga': 'GA1.2.747041794.1659791497',
            'sensorsdata2015jssdkcross': '%7B%22distinct_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMTgyNzM0ODUwMmFjODctMDc5MDRkMzE2Yjg3ZTYtMjYwMjFhNTEtMTMyNzEwNC0xODI3MzQ4NTAyYjVjZCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODI3M2NmYmRkMzhmYy0wMDQ0NDhjMmY3YTQ2YTc4LTI2MDIxYTUxLTEzMjcxMDQtMTgyNzNjZmJkZDQxMjYyIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D',
            'Hm_lvt_542ec988f8360595209d25eeb0469314': '1659800463',
            'PHPSESSID': 'l8jn9brrnd3i8kvn29aqd3pcc3',
            'ci_session': 'BUsJ7qIJ7fDtBLhOK39wHdfh7%2BBsMy6EW2fxtrxyIhXff9iKUIF%2FYfVSY7l%2B2b4F1shOnk40MWfdvC76GbZ1mZnSJYecl2zxZ34yixfBrRUcJJ%2FnUv%2BBDeb%2BWXZ8sdMJpNNHd1%2F6oTQFDHHPBdA76F2WhsW4XFhQkdIpvFGSX1tn1RFMzuUVHDPmOhGM8r6%2BHEKKAyC3JHfyq5zoSTNXglwql20IACi5aKB7ZAbubCDgzCAmxZA5W%2BKm5O%2BKM4B56c8ND28mv122e8S%2BFVtrex4nepYlQajDRkinOOc1%2F2qpNF2GgdR577mznwF1ZdvLaQpPXcqgMZfoejKhd2Ft%2B8mB9kkNTNAlAJob8fyG5HbSc%2F8wgjK3qbnBmRQnvfHqEV1BIgBavLbW4nHKI0DdAZUwwscW23Ynj7QiDHA36W4Jg%2FcVeUIn4rZWEGn81E6gUJERZHC2tx%2BBfg6TnAiMrw%3D%3D',
            'acw_tc': '082d349d16645939547506273e9c7b53691c17bedd6b07e0f9f96ee98c',
        }

        self.user_agent_list = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]

        retry_strategy = Retry(
            total=20,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    # ====================== utility function for main methods
    def gen_mt(self) -> str:

        mt = int(time.time())

        return str(mt)

    def get_sign(self, url: str, req_type: str, data: dict[str, str]) -> str:
        # generate a valid sign
        # an example of data:
        # {
        #     "pro_id": "122121",
        #     "post_id": "231435",
        #     "pro_class": "101",
        #     "order_type": 2,
        #     "page": 3,
        #     "page_size": 20,
        #     "mapi_query_time": 1664662621,
        #     "request_id": "1664662507"
        # }
        host_url = url.split("?")
        host_all = host_url[0]
        props = ""
        if len(host_url) > 1:
            if "/search/all" in url:
                try:
                    query = host_url[1]
                except:
                    query = ""
            else:
                try:
                    # query = host_url[1].encode() !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!查询encode功能
                    query = host_url[1]
                except:
                    query = ""
        else:
            query = ""
        hosts = host_all.replace('http://', '').replace('https://', '')
        apimdata = str(int((time.time())))
        paras = list()
        for key, value in data.items():
            if "/search/all" in url:
                paras.append(key + "=" + value)
            else:
                # paras.append(key+"="+value.encode()) !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!查询encode功能
                paras.append(key + "=" + value)
        paras.sort()
        if paras:
            props = "&".join(paras)
        else:
            props = ""

        if req_type == "GET":
            if props:
                if query:
                    query += "&"
                query += props

        if query:
            query = "&".join(sorted(query.split("&")))
            host_all += query

        if req_type == "GET":
            props = ""
            data = dict()  # in the original version, "" was assigned to data

        appkey = "MzgxOTg3ZDMZTgxO"
        processed_props = hashlib.md5(props.encode()).hexdigest()
        sign = hashlib.md5((hosts + appkey + apimdata + query + processed_props).encode()).hexdigest()

        return sign

    def find_pro_id(self, link_lis: list) -> list:
        """given a list of webelemts "a", return project ids inside

        Args:
            link_lis (list): a list of weblelemts "a"

        Returns:
            list: _description_
        """
        items = [i.attrs["href"] for i in link_lis]
        # print(items,locator) test statement
        items = [i for i in items if re.search("item", i)]
        items = [re.findall(r"\d+", i)[0] for i in items]
        return items

    # ================== main functions

    def get_comment(self, pro_id: str) -> list[dict]:
        """_summary_

        Args:
            pro_id (str): modian project id

        Returns:
            list[dict]: json data of comments. It is rather complicated
            so this code does not parse json data into a clean list or dictionary.
        """
        # to get all the comments, we need to send multiple requests
        # so we first define the globaally used parameters
        cookies = self.cookies
        user_agent = random.choice(self.user_agent_list)
        res_lis = list()
        # get post_id to send api requests
        post_resp = self.session.get(f"https://zhongchou.modian.com/item/{pro_id}.html", timeout=100)
        post_soup = BeautifulSoup(post_resp.content,features="html.parser")
        post_id = post_soup.select_one('input[name="post_id"]').attrs["value"]

        def get_once(pro_id: str, post_id: str, page_num: int,
                     user_agent: str, cookies: dict):
            # All these are from the source code of the javascripts on modian sites.
            request_id = self.gen_mt()

            mt = self.gen_mt()

            mapi_query_time = self.gen_mt()

            params = {
                'mapi_query_time': mapi_query_time,
                'order_type': '2',
                'page': str(page_num),
                'page_size': '20',
                'post_id': post_id,
                'pro_class': '101',
                'pro_id': pro_id,
                'request_id': request_id,
            }

            # generate a valid sign according to the params
            sign = self.get_sign(url='https://apim.modian.com/apis/mdcomment/get_reply_list',
                                 req_type="GET",
                                 data=params)

            headers = {
                'authority': 'apim.modian.com',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'build': '15000',
                'client': '11',
                # Requests sorts cookies= alphabetically
                # 'cookie': '_ga=GA1.2.747041794.1659791497; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMTgyNzM0ODUwMmFjODctMDc5MDRkMzE2Yjg3ZTYtMjYwMjFhNTEtMTMyNzEwNC0xODI3MzQ4NTAyYjVjZCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODI3M2NmYmRkMzhmYy0wMDQ0NDhjMmY3YTQ2YTc4LTI2MDIxYTUxLTEzMjcxMDQtMTgyNzNjZmJkZDQxMjYyIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; Hm_lvt_542ec988f8360595209d25eeb0469314=1659800463; PHPSESSID=l8jn9brrnd3i8kvn29aqd3pcc3; ci_session=BUsJ7qIJ7fDtBLhOK39wHdfh7%2BBsMy6EW2fxtrxyIhXff9iKUIF%2FYfVSY7l%2B2b4F1shOnk40MWfdvC76GbZ1mZnSJYecl2zxZ34yixfBrRUcJJ%2FnUv%2BBDeb%2BWXZ8sdMJpNNHd1%2F6oTQFDHHPBdA76F2WhsW4XFhQkdIpvFGSX1tn1RFMzuUVHDPmOhGM8r6%2BHEKKAyC3JHfyq5zoSTNXglwql20IACi5aKB7ZAbubCDgzCAmxZA5W%2BKm5O%2BKM4B56c8ND28mv122e8S%2BFVtrex4nepYlQajDRkinOOc1%2F2qpNF2GgdR577mznwF1ZdvLaQpPXcqgMZfoejKhd2Ft%2B8mB9kkNTNAlAJob8fyG5HbSc%2F8wgjK3qbnBmRQnvfHqEV1BIgBavLbW4nHKI0DdAZUwwscW23Ynj7QiDHA36W4Jg%2FcVeUIn4rZWEGn81E6gUJERZHC2tx%2BBfg6TnAiMrw%3D%3D; acw_tc=082d349d16645939547506273e9c7b53691c17bedd6b07e0f9f96ee98c',
                'mt': mt,
                'origin': 'https://zhongchou.modian.com',
                'referer': 'https://zhongchou.modian.com/',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'sign': sign,
                'user-agent': user_agent,
            }

            response = self.session.get('https://apim.modian.com/apis/mdcomment/get_reply_list',
                                        params=params, cookies=cookies, headers=headers,
                                        timeout=100)

            return response.json()

        page_num = 1

        try:
            first_resp = get_once(pro_id, post_id, 1, user_agent, cookies)
            total_comments = first_resp["data"]["total"]
            res_lis.extend(first_resp["data"]["list"])
        except:
            total_comments = 0

        # If there are still more comments, make another request
        while 20 * page_num < total_comments:
            page_num += 1
            new_resp = get_once(pro_id, post_id, page_num, user_agent, self.cookies)
            res_lis.extend(new_resp["data"]["list"])

        return res_lis

    def get_front_page(self):
        # this part is for retrieving the feed list, which cannot be scraped by
        # usual GET request below. 
        params = {
            'ad_position': 'pc_home_onlineproject',
        }
        sign = self.get_sign(url="https://apim.modian.com/recommend/feed_list",
                             req_type="GET",
                             data=params)
        mt = str(self.gen_mt())

        headers = {
            'authority': 'apim.modian.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'build': '15000',
            'client': '11',
            # Requests sorts cookies= alphabetically
            # 'cookie': '_ga=GA1.2.747041794.1659791497; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMTgyNzM0ODUwMmFjODctMDc5MDRkMzE2Yjg3ZTYtMjYwMjFhNTEtMTMyNzEwNC0xODI3MzQ4NTAyYjVjZCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODI3M2NmYmRkMzhmYy0wMDQ0NDhjMmY3YTQ2YTc4LTI2MDIxYTUxLTEzMjcxMDQtMTgyNzNjZmJkZDQxMjYyIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; Hm_lvt_542ec988f8360595209d25eeb0469314=1659800463; PHPSESSID=l8jn9brrnd3i8kvn29aqd3pcc3; ci_session=Atpxm%2F3B5QKi%2FHRlYnIfPowalg4e2DWntTbKVgpJImVi2BBsoilHohaWY4eSV%2BX9xoZ6t5Q7xj5qeu0IR7M%2Bz5gELqvyR1gbun%2FHzPq3LEslvZnIlfGgc6f7JLPh1EOY3hbC8xeKdvWd8Tq1VmrTFJeGnkInWeny9AMYGVf%2BGQUT1jXVI3dYeLHV6yCgqRG18z8Twr2VmEE7T6726DhnmZIRGc%2F25quaO%2FFBzAiIWqUzwf7hkUuLKyYiAhNfwSpsv3jRrYs%2BByWqIK7SP5NbU7JeNAL8lb8cJWHwycZMUspQCi0ytOJ5wz7QICasGrTY%2BvbBn1TklOrvkYCI0kV6y1ODnF9Qc49pEHEjip9NeMNPM9neAiZuei2xcGBfIggUtiNQmj6KvrZPuLRf1nG%2FEL4dj8lTyrVWOiEj7AFdbv4t0paVaHKe9QpFCP3B4B%2FxC2Y9gkbY6MLATmpvs8WGxw%3D%3D',
            'mt': mt,
            'origin': 'https://www.modian.com',
            'referer': 'https://www.modian.com/',
            'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'sign': sign,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        }

        feed_resp = self.session.get('https://apim.modian.com/recommend/feed_list',
                                     params=params, cookies=self.cookies, headers=headers,
                                     timeout=10)
        feed_lis_pro = [i["card_info"]["id"] for i in feed_resp.json()["data"]]

        # now perform ordinary requests
        pro_id_lis = list()
        pro_id_lis.extend(feed_lis_pro)
        front_page_resp = self.session.get("https://www.modian.com/", timeout=100)
        front_page_soup = BeautifulSoup(front_page_resp.content,features="html.parser")
        locator_lis = ["li.slider-item a",
                       "div.hot-left-main a"]
        # delete "div.hot-right a" because they only contain immature projects.
        for locator in locator_lis:
            pro_id_lis.extend(self.find_pro_id(front_page_soup.select(locator)))
        return list(set(pro_id_lis))

    def get_backer_list(self, pro_id: str):
        user_agent = random.choice(self.user_agent_list)
        cookies = self.cookies

        def get_backer_list_once(pro_id: str, page_num: int,
                                 user_agent: str, cookies: dict) -> dict:
            json_callback = "jQuery1111"
            json_callback += str(random.random()).replace(".", "")
            json_callback += "_"
            json_callback += str(int(time.time() * 1000))

            headers = {
                'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'keep-alive',
                # Requests sorts cookies= alphabetically
                # 'Cookie': '_ga=GA1.2.747041794.1659791497; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221827348502ac87-07904d316b87e6-26021a51-1327104-1827348502b5cd%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMTgyNzM0ODUwMmFjODctMDc5MDRkMzE2Yjg3ZTYtMjYwMjFhNTEtMTMyNzEwNC0xODI3MzQ4NTAyYjVjZCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODI3M2NmYmRkMzhmYy0wMDQ0NDhjMmY3YTQ2YTc4LTI2MDIxYTUxLTEzMjcxMDQtMTgyNzNjZmJkZDQxMjYyIn0%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; Hm_lvt_542ec988f8360595209d25eeb0469314=1659800463; PHPSESSID=l8jn9brrnd3i8kvn29aqd3pcc3; acw_tc=b65cfd2916647781866892820e71f54a13d1d1f66c35d61013f736028ee90c; ci_session=xNuEsul9ebD9pzZDpGol4uOG0pgjVKk8aUeTroChYA8AAyuDzMOw7YT3Or1slKJkwqsJBA2eDeeQYba0v%2BnTPslDyeSUxzY%2FdEJyOsBRYyCYFcslQbkMrbtmBmL5aIzjay6avGrfC0LX8IqyszUvE01hV%2BL%2BE%2FmzWw%2Fdcibkz7%2BMhF5%2F1VpSRzvlkwcsKZcYEzdTpgUUir4%2FKuZ5mp2KD%2F1ybcg01U6iQeYEsZavxedeudD%2FAe53d7v12vtO6OMCJ%2BdIO0TOxIu6aAiy2e7TRn3aEvdNIlFGN4o5bWjHYeLl%2BE7Kmsq5QKrhkU7J%2F1IMlPm8%2F8jt4y9bkrG99GUSjNfXtIRrJSCsHBr6vqeOBwNQpZfr82Cyc%2F%2FUBFikqG40Whn61Jq7ygbsvZWE7e5HGTbU8dMXZCj323KpMGJyZV%2Fbvfq%2BCqT7DdHHSpj2OEcwRSdzN%2FWcYxw7xq1eMOBEzw%3D%3D; SERVERID=d629393cddb80c19f9606f612eb8d10f|1664778187|1664778186',
                'Referer': f'https://zhongchou.modian.com/item/{pro_id}.html',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin',
                'User-Agent': user_agent,
                'X-Requested-With': 'XMLHttpRequest',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }

            params = {
                'jsonpcallback': json_callback,
                'origin_id': pro_id,
                'type': 'backer_list',
                'page': str(page_num),
                'page_size': '20',
                '_': str(int(time.time() * 1000)),
            }

            response = self.session.get('https://zhongchou.modian.com/realtime/ajax_dialog_user_list',
                                        params=params, cookies=cookies, headers=headers,
                                        timeout=100)

            # 转化成中文
            response_text = response.text.encode().decode("unicode-escape")
            response_text = response_text.replace("\n", "")

            html_text = re.findall(r'{"html":.*,"title"', response_text)[0]
            html_text = html_text.replace('{"html":', "")
            html_text = html_text.replace(',"title"', "")
            html_text = html_text.replace("\\", "")
            # There are emoji strings in the text, so force the program to ignore error when encoding
            soup = BeautifulSoup(html_text.encode('utf-8', errors="ignore"),features="html.parser")
            links = [link.get("href") for link in soup.find_all("a")]
            uid = [re.findall(r"(?<=uid=)\d+", link)[0] for link in links if re.search(r"(?<=uid=)\d+", link)]
            name_bottom_text = [i.text for i in soup.select('div.name_bottom')]
            pro_supported = [re.findall(r"(?<=已支持)\d+", text)[0] for text in name_bottom_text
                             if re.search(r"(?<=已支持)\d+", text)]
            pro_supported = [int(i) for i in pro_supported]
            title = re.findall(r'"title".*}', response_text)[0]
            supporter_num = re.findall(r'\s\d+', title)[0]
            supporter_num = int(supporter_num)
            return {"uid": uid, "pro_supported": pro_supported,
                    "supporter_num": supporter_num}

        # create lists to store the results
        uid_lis = list()
        pro_supported_lis = list()
        page_num = 1
        try:
            resp_dict = get_backer_list_once(pro_id, page_num,
                                             user_agent, cookies)
            supporter_num = resp_dict.get("supporter_num")
            uid_lis.extend(resp_dict.get("uid"))
            pro_supported_lis.extend(resp_dict.get("pro_supported"))
        except:
            supporter_num = 0

        while page_num * 20 < supporter_num:
            page_num += 1
            resp_dict = get_backer_list_once(pro_id, page_num,
                                             user_agent, cookies)
            uid_lis.extend(resp_dict.get("uid"))
            pro_supported_lis.extend(resp_dict.get("pro_supported"))

        return {"uid": uid_lis, "pro_supported": pro_supported_lis}

    def get_active_pro(self) -> list[str]:
        page_num = 1
        pro_lis = list()

        while True:
            req_link = f"https://zhongchou.modian.com/all/top_time/going/{page_num}"
            resp = self.session.get(req_link, timeout=100)
            soup = BeautifulSoup(resp.content,features="html.parser")
            link_element = soup.select("a")
            pro_links = self.find_pro_id(link_element)
            if not pro_links: break
            pro_lis.extend(pro_links)
            page_num += 1

        return list(set(pro_lis))

    def get_main_info(self, pro_id: str) -> dict:
        """Accept a modian project id, make a request to 
        its project and website and return related information.

        Args:
            pro_id (str): a modian project id

        Returns:
            dict: A dictionary containing project information.
        """

        link = "https://zhongchou.modian.com/item/"
        link = ''.join([link, pro_id, ".html"])
        req_time = 1

        while req_time <= 5:
            resp = self.session.get(link, timeout=100)
            if resp.status_code == 200:
                break
            req_time += 1

        content = BeautifulSoup(resp.content,features="html.parser")

        def parse_content(content: BeautifulSoup):
            clean_str = lambda x: x.replace(",", "")
            find_number = lambda x: re.findall(r"[0-9]+\.?[0-9]*|\.[0-9]+",
                                               x)[0]

            goal_money = content.select_one('span.goal-money').text
            goal_money = clean_str(goal_money)
            goal_money = find_number(goal_money)
            goal_money = float(goal_money)

            backer_money = content.select_one(r"span[backer_money]").text
            backer_money = clean_str(backer_money)
            backer_money = find_number(backer_money)
            backer_money = float(backer_money)

            backer_count = content.select_one(r"span[backer_count]").text
            backer_count = clean_str(backer_count)
            backer_count = find_number(backer_count)
            backer_count = int(backer_count)

            reward_list = content.select(r"div.back-list[rew_id]")

            # There might be multiple prices. 
            price_eles = [i.select_one('.head span') for i in reward_list]
            price = [i.text for i in price_eles]
            price = [clean_str(i) for i in price]
            price = [find_number(i) for i in price]
            price = [float(i) for i in price]

            subtitle_eles = [i.select_one('div.back-sub-title') for i in reward_list]
            subtitle = [i.text for i in subtitle_eles]
            
            # Whethere a reward has a purchase upper bound.
            limit_eles = [i.select_one('div.head em') for i in reward_list]
            limit_str = [i.text for i in limit_eles]
            parse_limit_str = lambda x: re.findall(r"\d+",x)[-1] if \
            "限" in x else "0"
            limit = [parse_limit_str(i) for i in limit_str]
            limit = [int(i) for i in limit]

            quantity = content.select(".head em")
            quantity = [i.attrs.get("i", "0") for i in quantity]
            quantity = [clean_str(i) for i in quantity]
            quantity = [find_number(i) for i in quantity]
            quantity = [int(i) for i in quantity]

            reward_info= list(zip(subtitle,price,quantity,limit))

            times = content.select_one(".remain-time h3").attrs
            start_time = times["start_time"]
            end_time = times["end_time"]

            try:
                updates = content.select_one(".pro-gengxin span").text
                updates = int(updates)
            except:
                updates = 0

            user_id = content.select_one("a.avater").attrs
            user_id = user_id["href"]
            user_id = find_number(user_id)

            pro_class = content.select_one(".tags span").text
            pro_class = pro_class.replace("项目类别：", "")

            attention = content.select_one("li.atten span").text
            attention = int(attention)

            comment = content.select_one('.nav-comment span').text
            comment = int(comment)

            return {"goal": goal_money,
                    "backer_money": backer_money,
                    "backer_num": backer_count,
                    "reward_info": reward_info,
                    "start_time": start_time,
                    "end_time": end_time,
                    "update_num": updates,
                    "creator_id": user_id,
                    "category": pro_class,
                    "attention": attention,
                    "comment_num": comment,
                    "project_id": pro_id}

        try:
            return parse_content(content)
        except:
            try:
                # If so, this project has not been supported by anyone and the html
                # source is thus different
                clean_str = lambda x: x.replace(",", "")
                find_number = lambda x: re.findall(r"[0-9]+\.?[0-9]*|\.[0-9]+",
                                                   x)[0]
                attention = content.select_one("li.atten span").text
                attention = int(attention)

                goal_money = content.select_one('div.project-goal span').text
                goal_money = clean_str(goal_money)
                goal_money = find_number(goal_money)
                goal_money = float(goal_money)

                pro_class = content.select_one(".tags span").text
                pro_class = pro_class.replace("项目类别：", "")

                user_id = content.select_one('input[name="creater_user_id"]').attrs
                user_id = user_id["value"]
                user_id = find_number(user_id)

                reward_list = content.select(r"div.back-list[rew_id]")

                price = content.select(r".head span")
                price = [i.text for i in price]
                price = [clean_str(i) for i in price]
                price = [find_number(i) for i in price]
                price = [float(i) for i in price]

                quantity = [0] * len(price)

                subtitle_eles = [i.select_one('div.back-sub-title') for i in reward_list]
                subtitle = [i.text for i in subtitle_eles]
                
                # Whethere a reward has a purchase upper bound.
                limit_eles = [i.select_one('div.head em') for i in reward_list]
                limit_str = [i.text for i in limit_eles]
                parse_limit_str = lambda x: re.findall(r"\d+",x)[-1] if \
                "限" in x else "0"
                limit = [parse_limit_str(i) for i in limit_str]
                limit = [int(i) for i in limit]

                reward_info = list(zip(subtitle,price, quantity,limit))

                # use post id to get comment count
                post_id = content.select_one('input[name="post_id"]').attrs["value"]
                params = {
                    'post_id': post_id,
                }
                headers = {
                    'Accept': 'application/json, text/javascript, */*; q=0.01',
                    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                    'Connection': 'keep-alive',
                    # Requests sorts cookies= alphabetically
                    # 'Cookie': 'PHPSESSID=7033i7rmbfcnroo694shm8olu6; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22183baa0ba8afb8-041c4c863a431c-26021f51-1821369-183baa0ba8b980%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%22183baa0ba8afb8-041c4c863a431c-26021f51-1821369-183baa0ba8b980%22%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfYW5vbnltb3VzX2lkIjoiMTgzYmFhMGJhOGFmYjgtMDQxYzRjODYzYTQzMWMtMjYwMjFmNTEtMTgyMTM2OS0xODNiYWEwYmE4Yjk4MCIsIiRpZGVudGl0eV9jb29raWVfaWQiOiIxODNiYWEwY2Y3ODQyZS0wMmFiODZlYjAwMTFmYWMtMjYwMjFmNTEtMTgyMTM2OS0xODNiYWEwY2Y3OTE4OGYifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%7D; ci_session=4aICn2sfi%2FlvYFEcqzgBDu6unWJkr8F8SD%2B5nhHciECb5anK7cW2zHKoSw7BuNsvoCok1RXMzGhGLVD5ZF95Ntawy0OBj0%2BJO9BSrGSmgoaZ6G2ScDISTTcyc8gckHtc0WBpHCVmkuUVwJeuiA030jFhb8svv9qRwLdCrhPi0MNnlAXyoPlIiD7qdrGtlRD2jp8Q4lSb5Fx1yH3siOfJtH7wot5BsfJCeoNYJDsCqHGZ8xEHn9kF1ORsbsJ%2FZNIWs9Ndvx5NFD0pYGuN8aKglJskxMAKA8fII9mecS8tfD7GCJED4ozjlFxWv8wiaosZSONf6RMR4mtUVAgoi4B7t1CCXNPB0TaZH8cMlbRk%2FJX13DFIIVhy3jMyb73orvGSdibXZNX64EVLLBOB0q%2F5gDCysqFr28AibQH4H2A3orsNQT%2Blo6UnERSg9suBXvAyhKbWKuCsT1ZpnQUWeim94A%3D%3D; acw_tc=082db09a16654576033681985eae58d47d9fda2ce19e01876a5abed238',
                    'Origin': 'https://zhongchou.modian.com',
                    'Referer': 'https://zhongchou.modian.com/',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-site',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
                    'build': '15000',
                    'client': '11',
                    'dnt': '1',
                    'mt': self.gen_mt(),
                    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"',
                    'sign': self.get_sign('https://apim.modian.com/apis/mdcomment/project_info',
                                          req_type="GET",
                                          data=params),
                    'user_id': '',
                    'userid': '',
                }
                comment_data = self.session.get('https://apim.modian.com/apis/mdcomment/project_info',
                                                params=params, cookies=self.cookies, headers=headers).json()
                comment = comment_data.get("data").get("comment_count")
                comment = int(comment)

                time_code = re.findall(r"(?<=realtime_sync\.pro_time\().*(?=\))", resp.text)
                time_code = time_code[0].split(",")
                start_time = time_code[0]
                end_time = time_code[1]

                return {"project_id": pro_id,
                        "backer_money": 0,
                        "backer_num": 0,
                        "update_num": 0,
                        "category": pro_class,
                        "attention": attention,
                        "creator_id": user_id,
                        "reward_info": reward_info,
                        "start_time": start_time,
                        "end_time": end_time,
                        "comment_num": comment,
                        "goal": goal_money
                        }
            except:
                print(f"{pro_id} bad html!")
                return {"project_id": pro_id}


if __name__ == "__main__":
    scraper = ModianScraper()
    # test_lis = scraper.get_comment('122121')
    # print(test_lis[0:2])
    # print(test_lis)
    # scraper.get_front_page()
    # print(scraper.get_front_page())
    # print(scraper.get_main_info("125364"))
    # test a project with 0 purcharse
    print(scraper.get_main_info("124819"))
    # print(scraper.get_comment("122121"))
    # print(scraper.get_backer_list("122121"))
