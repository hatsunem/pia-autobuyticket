import os
import sched
import time
from datetime import datetime
import bs4
import requests

TICKET_INFO = {
    "url": "http://ticket.pia.jp/pia/ticketInformation.do?eventCd=1809381&rlsCd=001&lotRlsCd=",
    "event_cd": "1809381",
    "rls_cd": "001",
    "place": "会場：ブルーノート東京 (東京都)",
    "date": "2018/4/28(土) 20:00 開演 ( 19:00 開場 )"
}

LOGIN_URL = 'https://ticket-auth.pia.jp/pia/login'

info = TICKET_INFO
s = requests.session()


def buy_ticket():
    #  アーティストページに移動
    res = s.get(info["url"])
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    seet_info = soup.find("li", class_="Y15-seet-info")
    # print(soup)
    while seet_info is None:
        res = s.get(info["url"])
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        seet_info = soup.find("li", class_="Y15-seet-info")
        print("Sorry...")
    print("アーティストページ " + res.url)

    # 公演、枚数などを指定して購入手続き開始
    stknd_cd = seet_info.find("input", class_="stkSeatCd").get("value")
    sale_seat_cd = seet_info.find("input", class_="saleSeatCd").get("value")
    sale_seat_name = seet_info.find("input", class_="valiation").get("value")
    unit_num = seet_info.find("input", class_="tanni_maisu").get("value")
    price = seet_info.find("input", class_="prices").get("value")
    stknd_cmnt = seet_info.find("input", class_="slStkndCmnt").get("value")
    event_cd = info["event_cd"]
    rls_cd = info["rls_cd"]
    perf_cd = seet_info.find("a").get("data-perf-cd")
    seat_type_flg = seet_info.find("input", class_="seatTypeFlg").get("value")
    from_id = seet_info.find("input", class_="fromId").get("value")
    zone_cd = seet_info.find("input", class_="zoneCd").get("value")
    venue_name = info["place"]
    max_num = seet_info.find("input", class_="maxnum").get("value")
    perf_day = info["date"]
    return_url = "/ticketInformation.do?eventCd=" + event_cd + "&rlsCd=" + rls_cd
    multiple_seven_dlvry = soup.find("input", id="isMultipleSevenDlvry").get("value")
    next_url = soup.find("input", id="nextUrl").get("value")

    event_data = {
        "ticketQuantity": "",
        "ticketCount": "2",
        "rlsChoosedDto.seatList[0].num": "0",
        "slStkndCd": stknd_cd,
        "rlsChoosedDto.seatList[0].saleSeatCd": sale_seat_cd,
        "rlsChoosedDto.seatList[0].saleSeatName": sale_seat_name,
        "rlsChoosedDto.seatList[0].unitNum": unit_num,
        "rlsChoosedDto.seatList[0].price": price,
        "slStkndCmnt": stknd_cmnt,
        "eventCd": event_cd,
        "selectedRlsCd": rls_cd,
        "perfCd": perf_cd,
        "seatTypeFlg": seat_type_flg,
        "stkStkndCd": stknd_cd,
        "fromId": from_id,
        "zoneCd": zone_cd,
        "venueZoneCd": zone_cd,
        "rlsChoosedDto.zoneCd": zone_cd,
        "selectedId": stknd_cd,
        "rlsChoosedDto.venueName": venue_name,
        "rlsChoosedDto.maxNum": max_num,
        "rlsChoosedDto.perfDay": perf_day,
        "rlsChoosedDto.unitType": "枚",
        "returnUrl": return_url,
        "isMultipleSevenDlvry": multiple_seven_dlvry
    }
    res = s.post(next_url, data=event_data)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    print("login page " + res.url)

    # login
    inputs = soup.find_all("input")
    em_parameter = inputs[3].get("value")
    request_token = inputs[4].get("value")

    login_data = {
        "ep_parameters": em_parameter,
        "request_token": request_token,
        "login_id": "",  # Mail Address
        "auto_login": "true",
        "password": "",  # Password
        "login_button.x": "0",
        "login_button.y": "0",
        "auto_login_openid": "true"
    }

    res = s.post(LOGIN_URL, data=login_data)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    print("画像認証ページ " + res.url)

    # 画像認証
    flow_id = soup.find_all("input")[6].get("value")
    next_url = "https://ticket-sale.pia.jp/pia/purchase/NT0101S11OpenIdCaptchaAction.do"
    title = soup.find("title").string
    print(title)

    while "決済" not in title:
        if "ご確認ください" in title:
            print(soup)
        capture_img = soup.find("img", id="capchaImg").get("src")
        with open("auth_img.jpg", "wb") as f:
            f.write(requests.get("https://ticket-sale.pia.jp" + capture_img).content)
            os.system("open auth_img.jpg")
        auth_number = input('>> ')
        auth_data = {
            "flowId": flow_id,
            "BCAssign": "",
            "url_change_att_image": "/pia/membmng/FreshCapchaAction.do",
            "captyaInput": auth_number,
            "x": "0",
            "y": "0"
        }
        res = s.post(next_url, data=auth_data)
        soup = bs4.BeautifulSoup(res.text, "html.parser")
        title = soup.find("title").string
        print(title)

    print("決済方法選択ページ " + res.url)

    # 決済・取引方法選択
    form = soup.find("form", id="form1")
    next_url = "https://ticket-sale.pia.jp" + form.get("action")
    form_input = form.find_all("input")
    card_knd_typ = form_input[1].get("value")
    card_payment_methd_typ = form_input[2].get("value")
    exhalant_side = form_input[3].get("value")
    index = form_input[4].get("value")
    validate_flg = form_input[5].get("value")
    card_trmvld_up_no_flg0 = soup.find("input", id="cardTrmvldUpNoFlg0").get("value")
    credit_card_no = soup.find("td", class_="col_card_radio").get("value")
    dspt_no = soup.find("td", class_="col_send_radio").get("value")

    purchase_data = {
        "flowId": flow_id,
        "cardKndTyp": card_knd_typ,  # 3
        "cardPaymentMethdTyp": card_payment_methd_typ,  # 1
        "exhalantSide": exhalant_side,  # 1
        "index": index,  # -1
        "validateFlg": validate_flg,  #
        "stlmntMndSl": "credit",
        "cardTrmvldUpNoFlg0": card_trmvld_up_no_flg0,  # 0
        "creditCardNo": credit_card_no,  # 2
        "trmvldMonth": "11",
        "trmvldYear": "2022",
        "dlvryMndSl": "7",  # セブンイレブン
        "dsptNo": dspt_no,
        "x": "0",
        "y": "0"
    }

    res = s.post(next_url, data=purchase_data)
    soup = bs4.BeautifulSoup(res.text, "html.parser")
    print("購入内容確認ページ " + res.url)

    # 最終確認
    form = soup.find("form", id="form1")
    next_url = "https://ticket-sale.pia.jp" + form.get("action")
    form_input = soup.find_all("input")
    pia_key = form_input[0].get("value")
    selected_stlmnt_mnd_typ = form_input[2].get("value")
    selected_card_trmvld_change_flg = form_input[6].get("value")

    final_data = {
        "pia.bety.sessiontraceid.parameter.key": pia_key,
        "flowId": flow_id,
        "selectedStlmntMndTyp": selected_stlmnt_mnd_typ,
        "selectedDlvryMndTyp": "7",
        "selectedOwnCardNo": credit_card_no,
        "selectedDsptNo": dspt_no,
        "selectedCardTrmvldChangeFlg": selected_card_trmvld_change_flg,
        "selectedCardPaymentMethdTyp": card_payment_methd_typ,
        "trmvldMonth": "11",
        "trmvldYear": "2022",
        "scrtyCd": "",  # security code
        "agreeCheck": "1",
        "x": "0",
        "y": "0"
    }

    res = s.post(next_url, data=final_data)
    print("もう一度確認ページ " + res.url)


try:
    sc = sched.scheduler(time.time, time.sleep)
    run_at = datetime.strptime('2018-3-17 10:00:00', '%Y-%m-%d %H:%M:%S')
    run_at = int(time.mktime(run_at.utctimetuple()))
    sc.enterabs(run_at, 1, buy_ticket)
    sc.run()
except Error:
    print("Error")
    while True:
        try:
            buy_ticket()
            break
        except Error:
            print("Error")
    print("Complete!")
else:
    print("Complete!")

buy_ticket()
