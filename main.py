from datetime import datetime
import requests
import pprint

TOKEN = "YOUR_TOKEN_IS_HERE"
URL = "https://api-invest.tinkoff.ru/openapi/portfolio"
MOEX_API_URL = "https://iss.moex.com/iss/statistics/engines/stock/markets/bonds/bondization/"


def get_positions_list(r_url, r_token):
    r = requests.get(r_url, headers={"Authorization": f"Bearer {r_token}"})
    return r.json()["payload"]["positions"]


def get_obligations_list(p_list):
    result_list = []
    for position in p_list:
        if position["instrumentType"] == "Bond":
            result_list.append(position)
    return result_list


def load_coupons_payments(obligations_list, moes_api_url):
    result_list = []
    for obligation in obligations_list:
        r = requests.get(f"{moes_api_url}{obligation['ticker']}.json")
        data = {"name": obligation["name"],
                "ticker": obligation["ticker"],
                "balance": obligation["balance"],
                "data": format_table(r.json()["coupons"]["data"])}
        result_list.append(data)

    return result_list


def format_table(data):
    result_data = []
    for element in data:
        temp_data = {
            "coupondate": element[3][:-3],
            "value": element[9]
        }
        result_data.append(temp_data)
    return result_data


def monthly_income(current_date, schedule_data):
    result_data = {}
    for ticker in schedule_data:
        balance = float(ticker["balance"])
        for coupon_data in ticker["data"]:
            coupon_date = coupon_data["coupondate"]
            if datetime.strptime(coupon_data["coupondate"], "%Y-%m") >= current_date:
                if coupon_data["value"] is not None:
                    if coupon_date not in result_data.keys():
                        result_data[coupon_date] = balance * float(coupon_data["value"])
                    else:
                        result_data[coupon_date] += balance * float(coupon_data["value"])
    return result_data


if __name__ == '__main__':
    current_date = datetime.today().strftime("%Y-%m")
    current_date = datetime.strptime(current_date, "%Y-%m")

    positions_list = get_positions_list(URL, TOKEN)
    obligations_list = get_obligations_list(positions_list)
    schedule_data = load_coupons_payments(obligations_list, MOEX_API_URL)

    pprint.pprint(monthly_income(current_date, schedule_data))
