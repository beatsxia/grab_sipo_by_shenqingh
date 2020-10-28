from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import os
import imgcode
from PIL import Image

# 打开浏览器
url = "http://cpquery.sipo.gov.cn/"
driver = webdriver.Firefox()
driver.get(url)
patent_no_arr = ['2015105423929','2014103182976','2014205227290','2012303147461','2016304557688','2009100023676','2011800242664','2012101517459','2012102126132']
#patent_no_arr = ['2015105423929']
# 判断某个元素是否存在
def isElementExist(element):
    browser=driver
    try:
        browser.find_element_by_css_selector(element)
        return True
    except:
        return False
# 页面显示提示
def tips(text):
    print(text)
    driver.execute_script("document.body.innerHTML=('<div style=\\'position:absolute;top:0px;left:0px;width:100%;text-align:center;background:#000;color:#fff;padding:8px;\\'>"+text+"</div>')+document.body.innerHTML")
        
main_window = driver.current_window_handle
driver.execute_script('''window.open("about:blank","_blank");''')
driver.switch_to.window(driver.window_handles[0])
WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'authImg')))
for key_mum in patent_no_arr:
    num = 0
    stop = True
    while stop:
        time.sleep(1)#等待验证码出现
        driver.save_screenshot('html.png')
        code_ele = driver.find_elements_by_id('authImg')[0]# 获取验证码的div位置
        left = code_ele.location['x']#x点的坐标
        top = code_ele.location['y']#y点的坐标
        right = code_ele.size['width']+left#上面右边点的坐标
        height = code_ele.size['height']+top#下面右边点的坐标
        image = Image.open('html.png')
        code_image = image.crop((left, top, right, height))
        imBackground = code_image.resize((70,20))
        #保存
        imBackground.save('code.png','PNG')
        crack = imgcode.PatentCrack('Patent.pkl')
        code = crack.feed(os.path.join('code.png'))
        code = int(code)
        time.sleep(1)
        driver.find_elements_by_name('select-key:shenqingh')[0].clear()
        keyword = driver.find_elements_by_name('select-key:shenqingh')[0].send_keys(key_mum)
        driver.find_elements_by_id('very-code')[0].clear()
        driver.find_elements_by_id('very-code')[0].send_keys(code)
        time.sleep(1)
        driver.find_elements_by_id('query')[0].click()  #查询按钮进行点击
        if isElementExist('.content_listx'):
            WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))
            
            patent_type = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[0].text
            patent_no = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[1].text
            patent_name = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[2].text
            applicant = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[3].text
            applicant_date = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[4].text
            auth_publication_date = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[5].text
            ipc = driver.find_elements_by_css_selector('.content_listx')[0].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[6].text
            # 判断是否超出查询限制
            if isElementExist('.binding'):
                stop =True
                tips('超出查询限制。请更换账号')
                driver.switch_to.window(driver.window_handles[0])
                driver.get(url)
                break
            if patent_no == key_mum:
                stop = False
                driver.switch_to.window(driver.window_handles[1])
                driver.get('http://cpquery.sipo.gov.cn/txnQueryBibliographicData.do?select-key:shenqingh='+key_mum)
                WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'downFrame')))
                WebDriverWait(driver,600000).until(EC.visibility_of_element_located((By.CLASS_NAME,'imfor_part1')))
                status = driver.find_element_by_name('record_zlx:anjianywzt').get_attribute('title')
                first_agency = driver.find_element_by_name('record_zldl:dailijgmc').get_attribute('title')
                driver.get('about:blank')
                driver.switch_to.window(driver.window_handles[0])
                WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))
                #data_sql = (patent_type,patent_no,patent_name,applicant_date,applicant,auth_publication_date,ipc,status,first_agency)
                data = {    
                        'patent_type':patent_type,
                        'patent_no':patent_no,
                        'patent_name':patent_name,
                        'applicant_date':applicant_date,
                        'applicant':applicant,
                        'auth_publication_date':auth_publication_date,
                        'ipc':ipc,
                        'status':status,
                        'first_agency':first_agency
                        }
                print(data)
            else:
                print('验证码错误')
        else:
            print('验证码错误')
        num = num +1
        if num>5:
            #5次输入错误停止输入
            stop = False 
            patent_type = ''
            patent_no = key_mum
            patent_name = ''
            applicant_date = ''
            applicant = ''
            auth_publication_date = ''
            ipc = ''
            status = ''
            first_agency = ''
            #data_sql = (patent_type,patent_no,patent_name,applicant_date,applicant,auth_publication_date,ipc,status,first_agency)
            data = {    
                    'patent_type':patent_type,
                    'patent_no':patent_no,
                    'patent_name':patent_name,
                    'applicant_date':applicant_date,
                    'applicant':applicant,
                    'auth_publication_date':auth_publication_date,
                    'ipc':ipc,
                    'status':status,
                    'first_agency':first_agency
                    }
            print(data)
            
            
#driver.close()






