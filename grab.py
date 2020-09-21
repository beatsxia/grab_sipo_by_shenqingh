from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
import os
import imgcode
from PIL import Image
import pymysql
import patent_field_list

# 打开浏览器
url = "http://cpquery.sipo.gov.cn/"
#url = "http://127.0.0.1/%E4%B8%AD%E5%9B%BD%E5%8F%8A%E5%A4%9A%E5%9B%BD%E4%B8%93%E5%88%A9%E5%AE%A1%E6%9F%A5%E4%BF%A1%E6%81%AF%E6%9F%A5%E8%AF%A2.htm"
driver = webdriver.Firefox()
driver.get(url)
#patent_no_arr = ['2015105423929','2014103182976','2014205227290','2012303147461','2016304557688','2009100023676','2011800242664','2012101517459','2012102126132']

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
    

conn = pymysql.connect(
    host='127.0.0.1',
    port=3306,
    user='root',
    password='root',
    database='test',
    charset='utf8'
)
# 获取一个光标
cursor = conn.cursor()
# 定义要执行的sql语句
#sql = 'insert into kwy_patent (`patent_type`, `patent_no`, `patent_name`, `applicant_date`, `applicant`, `auth_publication_date`, `ipc`, `status`, `first_agency`) values(%s,%s,%s,%s,%s,%s,%s,%s,%s);'
sql = 'update kwy_patent SET `auth_publication_date`=(%s), `status`=(%s), `first_agency`=(%s) where `patent_no`=(%s)'

# 新建tab用于加载二级详情页面
main_window = driver.current_window_handle
driver.execute_script('''window.open("about:blank","_blank");''')
driver.switch_to.window(driver.window_handles[0])
#print(1)
WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'authImg')))
#print(2)

# 定义要执行的sql语句
sql_sel = 'select patent_no from kwy_patent'
sql_data = []
patent_no_arr = []
cursor.execute(sql_sel)
patent_no_arr_data = cursor.fetchall()
for val in patent_no_arr_data:
    patent_no_arr.append(val[0])
for key_mum in patent_no_arr:
    num = 0
    #print(key_mum)
    stop = True
    while stop:
        
        time.sleep(1)#等待验证码出现
        driver.save_screenshot('html.png')
        code_ele = driver.find_elements_by_id('authImg')[0]       # 获取验证码的div位置
        left = code_ele.location['x']#x点的坐标
        top = code_ele.location['y']#y点的坐标
        right = code_ele.size['width']+left#上面右边点的坐标
        height = code_ele.size['height']+top#下面右边点的坐标
        image = Image.open('html.png')
        code_image = image.crop((left, top, right, height))
        # Resize图片大小，入口参数为一个tuple，新的图片大小
        imBackground = code_image.resize((70,20))
        #处理后的图片的存储路径，以及存储格式
        imBackground.save('code.png','PNG')
        #print(3)
        '''
        cookies = driver.get_cookies()
        headers = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0',
                    'Cookie':cookies
                }
        authImg = driver.find_elements_by_id('authImg')[0].get_attribute('src')
        #保存验证码图片数据  
        codeimg = requests.get(authImg,headers)
        print(authImg)
        with open('code.png', 'wb') as file:
            file.write(codeimg.content)
        '''
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
        #print(4)
        if isElementExist('.content_listx'):
            #print(5)
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
                # 切换tab
                driver.switch_to.window(driver.window_handles[1])
                # 进入详情
                driver.get('http://cpquery.sipo.gov.cn/txnQueryBibliographicData.do?select-key:shenqingh='+key_mum)
                # 等待页面加载完毕
                WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'downFrame')))
                
                # 等待详情加载完毕
                WebDriverWait(driver,600000).until(EC.visibility_of_element_located((By.CLASS_NAME,'imfor_part1')))
                # 获取案件状态和代理机构名称
                status = driver.find_element_by_name('record_zlx:anjianywzt').get_attribute('title')
                first_agency = driver.find_element_by_name('record_zldl:dailijgmc').get_attribute('title')
                driver.get('about:blank')
                # 返回Tab
                driver.switch_to.window(driver.window_handles[0])
                # 防止卡顿，等待切换完毕
                WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))
                patent_type = list(patent_field_list.patent_field_list.patent_type_list.keys())[list(patent_field_list.patent_field_list.patent_type_list.values()).index(patent_type)]
                status = list(patent_field_list.patent_field_list.status_list.keys())[list(patent_field_list.patent_field_list.status_list.values()).index(status)]#一旦匹配出现不是list文件里面的就会报错，所以要积极维护 或者更改写法，不过都差不多，因为匹配出现不存在的字段也需要更新
                a = (patent_type, patent_no, patent_name, applicant_date, applicant, auth_publication_date, ipc, status, first_agency)
                sql_data.append(a)
                data = [(auth_publication_date,status,first_agency,patent_no)]
                #print(data)
                cursor.executemany(sql, data)
            else:
                print('验证码错误')  
        else:
            print('验证码错误')
        num = num +1
        if num>5:
            #5次输入错误停止输入
            stop = False
            patent_type = '0'
            patent_no = key_mum
            patent_name = '0'
            applicant_date = '1970-09-01'
            applicant = '0'
            auth_publication_date = '1970-09-01'
            ipc = '0'
            status = '0'
            first_agency = '0'
            a = (patent_type, patent_no, patent_name, applicant_date, applicant, auth_publication_date, ipc, status, first_agency)
            sql_data.append(a)
            data = [(auth_publication_date,status,first_agency,patent_no)]
            cursor.executemany(sql, data) #插入到其他表，下次抓取
        
#print(sql_data) #可以执行一次插入全部数据，但没必要,一旦出错容易造成全部数据丢失，而且查询三秒才执行一次，数据库压力极小
#cursor.executemany(sql, sql_data)  
#driver.close()






