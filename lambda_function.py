import urllib3
import json
from ses import send_email

headers_template = {
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
    'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'
}

product_mapping = {
    "128gb": "MLTT3LL/A",
    "256gb": "MLU03LL/A",
    "test": "MGH73LL/A"
}

url_template = "https://www.apple.com/shop/fulfillment-messages?pl=true&mt=compact&cppart=UNLOCKED/US&parts.0={}&searchNearby=true&store=R039"


def check_availability(capacity):
    headers = {
        **headers_template,
        'referer': f"https://www.apple.com/shop/buy-iphone/iphone-13-pro/6.1-inch-display-{capacity}-sierra-blue-unlocked"
    }
    product = product_mapping[capacity]
    url = url_template.format(product)
    http = urllib3.PoolManager()
    r = http.request("GET", url, headers=headers)
    j = json.loads(r.data.decode('utf-8'))
    available_stores = []
    for store in j["body"]["content"]["pickupMessage"]["stores"]:
        if store["partsAvailability"][product]["storeSelectionEnabled"]:
            available_stores.append(store["storeName"])
    return available_stores


def lambda_handler(event, context):
    iphone_128_stores = check_availability("128gb")
    iphone_256_stores = check_availability("256gb")

    if len(iphone_128_stores) == 0 and len(iphone_256_stores) == 0:
        return {
            'statusCode': 200,
            'body': 'Iphone 13 Pro is NOT available for pickup'
        }
    else:
        iphone_128_str = "\r\n".join(iphone_128_stores)
        iphone_256_str = "\r\n".join(iphone_256_stores)
        subject = "Iphone 13 Pro is now available for pickup"
        body = f"128GB:\r\n{iphone_128_str}\r\n\r\n256GB:\r\n{iphone_256_str}"
        send_email(subject, body)
        return {
            'statusCode': 200,
            'body': 'Iphone 13 Pro is now available for pickup'
        }
