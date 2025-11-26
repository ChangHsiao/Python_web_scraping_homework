from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import json
import time
import re
import os
# 建立 Service 物件，指定 chromedriver.exe 的路徑

# 設定 Chrome 瀏覽器的選項
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized") # Chrome 瀏覽器在啟動時最大化視窗 避免 rwd
options.add_argument("--incognito") # 無痕模式 
options.add_argument("--disable-popup-blocking") # 停用 Chrome 的彈窗阻擋功能。

# 建立 Chrome 瀏覽器物件
driver = webdriver.Chrome(options=options)
driver.get("https://www.momoshop.com.tw/")
time.sleep(2)
cancle_product = driver.find_element(By.CSS_SELECTOR, ".relative.flex-1 input").clear()

while True:
    search_term = input("請輸入想查找的商品: ")

    insert_product = driver.find_element(By.CSS_SELECTOR, ".relative.flex-1 input").send_keys(search_term)
    start_find = driver.find_element(By.CSS_SELECTOR, ".flex.h-full.items-center.overflow-hidden button").click()
    try:
        product_div = driver.find_element(By.CSS_SELECTOR, ".listAreaUl")
        print("商品搜尋中")
        break
    except Exception as e:
        print("查無此商品，請重新輸入")

product_info = []
page_number = 1
while True:

    try: 
        # 獲得 script 中的文字
        data_element = driver.find_element(By.XPATH, "/html/body/script[@type='application/ld+json']")
        data_string = data_element.get_attribute('innerHTML')
        # print(data_string)

        # 正則表達試清除裡面的錯誤, 獲得 dict
        fix_data_string = re.sub(r",\s*]", "]", data_string)
        data_json = json.loads(fix_data_string)

        # 從 dict 中，找到包含商品資訊的 list
        product_list = data_json['mainEntity']['itemListElement']
        # print(product_list)

        # 從商品 list 中再找出想要的資訊，每一個商品包成一件 dict，放入整個 list 中


        for product in product_list:
            product_name = product['name']
            product_price = product['offers']['price']
            product_image = product['image']
            product_link = product['url']

            product_info.append({
                "product_name" : product_name,
                "product_price(NTD)": product_price,
                "product_image": product_image,
                "product_url": product_link
            })

        next_page_btn= driver.find_elements(By.CSS_SELECTOR, ".page-btn.page-next")
        if next_page_btn:
            next_page_btn = next_page_btn[1]
            next_page_btn.click()
            time.sleep(2)
            page_number += 1
        else:
            print("商品搜尋完畢，明細製作中")
            break
    except:
        current_url = driver.current_url
        print(f"網頁抓取有誤，抓取至第{page_number}頁時載入失敗，錯誤網址: {current_url}")
        
# 將資料轉為 .json 儲存
folder_name = 'momo_products_data'
timestamp = datetime.now().strftime("%Y%m%d")
file_name = f"{search_term}_{timestamp}.json"
fild_path = os.path.join(folder_name, file_name)

# 判斷存檔資料夾是否存在
if not os.path.exists(folder_name):
    print("正在建立資料夾")
    os.mkdir(folder_name)
    print("已新增資料夾")
else:
    print("資料夾已存在")

# 將 list 轉為 json 檔存入資料夾
try:
    with open(fild_path, 'w', encoding="utf-8") as f:
        json.dump(product_info, f, indent=4)
        print("商品明細存檔完成")
except Exception as e:
    print(f"文件存檔錯誤")

