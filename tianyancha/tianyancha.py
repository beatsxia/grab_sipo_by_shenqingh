from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time
from PIL import Image
import random
import pandas as pd
import requests
import pymysql
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import re
import math
from sqlalchemy import create_engine
from io import BytesIO

def conn_cur():
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        database='wky_oa',
        charset='utf8'
    )
    # 获取一个光标
    cursor = conn.cursor()
    return cursor,conn
#连接数据库
cursor,conn = conn_cur()
driver = webdriver.Firefox()

# 定义要执行的sql语句
#sql = 'insert into kwy_corp_drafts (name,corp_avater,credit_code,birthday,summary,legal_person,phone,email,website,address,reg_address,status,industry,staff_size,business,is_new_tech,trademark_number,patent_number,copyright_number,guid) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);'
sql = 'update kwy_corp_drafts SET corp_avater = (%s),credit_code = (%s),birthday = (%s),summary = (%s),legal_person = (%s),phone = (%s),email = (%s),website = (%s),address = (%s),reg_address = (%s),status = (%s),industry = (%s),staff_size = (%s),business = (%s),is_new_tech = (%s),trademark_number = (%s),patent_number = (%s),copyright_number = (%s),guid = (%s),is_pull = (%s),pull_time = (%s) where name = (%s) '


def get_html(gongsi_name):
    def get_patent_list(url):
        driver.get(url)
        tab = driver.page_source
        soup = BeautifulSoup(tab, 'html.parser')   #文档对象
        # 非法URL 1
        invalidLink1='#'
        # 非法URL 2
        invalidLink2='javascript:void(0)'
        # 集合
        result=[]
        # 计数器
        mycount=0
        #查找文档中所有a标签
        for k in soup.find_all('a'):
            #print(k)
            #查找href标签
            link=k.get('href')
            # 过滤没找到的
            if(link is not None):
                #过滤非法链接
                if link==invalidLink1:
                  pass
                elif link==invalidLink2:
                  pass
                elif link.find("javascript:")!=-1:
                  pass
                else:
                  result.append(link)
                  mycount=mycount+1
            
        if mycount > 0:
            df = pd.read_html(tab)
            if isinstance(df, list):
                df = df[0]
            
            if len(result) == len(df):
                df['操作'] = pd.Series(result)#添加列 将操作列的值替换成链接url值
                col_name = df.columns.tolist()
                col_name.append('corp_guid')
                col_name.append('created_time')
                df = df.reindex(columns=col_name,fill_value=company_no)
                df['created_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                #for row in df.iterrows():#循环
                #   print(row)
                df.columns = ['idx','app_pub_date','patent_name','patent_no','app_pub_no','patent_type','detail_url','corp_guid','created_time']
        else:
            df = pd.DataFrame()
        return df
    
    
    
    url = "https://www.tianyancha.com/search?key=%s" % gongsi_name
    driver.get(url)
    #等待页面加载出现
    WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'tips-num')))
    #长时间没有反应就是查不到内容
    #出现内容  js-search-container
    try:
        url2=driver.find_element_by_xpath('//*[@id="web-content"]//div[@class="header"]//a[position()<2]').get_attribute('href')
        #print('成功查询')
        jixu = True
        company_no = re.search(r'https://www.tianyancha.com/company/(\d+)', url2)
        company_no = company_no.group(1)
    except:
        print('登陆过于频繁，请1分钟后再次尝试。')
    if jixu:
        #详情页
        driver.get(url2)
        name = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[1]/h1').text
        div1 = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[2]/div').find_elements_by_css_selector('.tag-common')
        status = ''
        is_new_tech = '0'
        for j in range(len(div1)):
            div1_val = div1[j].text
            if j == 0:
                status = div1_val
            if div1_val=='高新技术企业':
                is_new_tech = '1'
        if status in ['吊销','注销','迁出']:
            print('不用查了')
        
        #拿图标 //*[@id="company_web_top"]/div[2]/div[1]/div[1]/div[2]/img
        try:
            img_url = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[1]/div[1]/div[2]/img').get_attribute('data-src')
            r = requests.get(img_url)
            # 将获取到的图片二进制流写入本地文件
            tu_t = 'img/%s.png' % int(time.time())
            with open(tu_t, 'wb') as f:
                # 对于图片类型的通过r.content方式访问响应内容，将响应内容写入baidu.png中
                f.write(r.content)
            corp_avater = tu_t
        except :
            corp_avater = ''
        try:
            phone = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[1]/span[2]').text
            email = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[1]/div[2]/span[2]').text
            website = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[2]/div[1]/a').text
            address = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[2]/div[2]/div/div').text
            #预留address进行省市县匹配
            
        except:
            phone = ''
            email = ''
            website = ''
            address = ''
        try:
            summary = driver.find_element_by_xpath('//*[@id="company_web_top"]/div[2]/div[3]/div[3]/div[3]/div/div/text()').text
        except:
            summary = ''
        try:   
            legal_person = driver.find_elements_by_css_selector('.humancompany')[0].find_elements_by_css_selector('a')[0].get_attribute('title')
            tab = driver.find_element_by_xpath('//*[@id="_container_baseInfo"]').find_elements_by_tag_name('table')[1]
        except:
            legal_person = ''
            tab = driver.find_element_by_xpath('//*[@id="_container_baseInfo"]').find_elements_by_tag_name('table')[0]
        #基本信息 
        df = pd.read_html('<table>' + tab.get_attribute('innerHTML') + '</table>')
        if isinstance(df, list):
            df = df[0]
        #df.drop(df.columns[4], axis=1, inplace=True)#裁掉第5列 部分表格只有4列
        #with pd.ExcelWriter(gongsi_name+'.xlsx') as writer:
        #    df.to_excel(writer, sheet_name=gongsi_name, index=None)
        zidian_list = {}
        #转换成字典 {中文状态:状态值}
        for row in df.iterrows():
            zidian_list[row[1][0]] = row[1][1]
            zidian_list[row[1][2]] = row[1][3]
        '''
        i的可以取值参数如下：
        人员规模
        公司类型
        参保人数
        实缴资本
        工商注册号
        成立日期
        曾用名
        核准日期
        注册地址
        注册资本
        登记机关
        纳税人识别号纳税人识别号是税务登记证上的号码，通常简称为“税号”，每个企业的纳税人识别号都是唯一的。由15位、17位、18或者20位码（字符型）组成。这个属于每个人自己且终身不变的数字代码很可能成为我们的第二张“身份证”。没有帮助有帮助
        纳税人资质
        组织机构代码组织机构代码是组织机构在社会经济活动中统一赋予的“单位身份证”，是对国内依法注册、登记的机关、企事业单位、社会团体，以及其他组织机构颁发的唯一的、始终不变的代码标识。由8位数字（或大写字母）本体代码和1位数字（或大写字母）校验码组成。三证合一、五证合一之后，组织机构代码已经被统一社会信用代码取代。没有帮助有帮助
        经营状态
        经营范围
        统一社会信用代码一般指法人和其他组织统一社会信用代码，相当于让法人和其他组织拥有了一个全国统一的“身份证号”。标准规定统一社会信用代码用18位阿拉伯数字或大写英文字母表示。没有帮助有帮助
        英文名称
        营业期限
        行业
        董事长
        股本
        押记登记册
        已告解散日期/不再是独立实体日期
        重要事项
        '''
        industry = ''
        staff_size = ''
        business = ''
        reg_address = ''
        birthday = ''
        credit_code = ''
        for i in list(zidian_list.keys()):
            if i == '行业':
                industry = zidian_list[i]
            elif i == '人员规模':
                staff_size = zidian_list[i]
            elif i == '经营范围':
                business = zidian_list[i]
            elif i == '注册地址':
                reg_address = zidian_list[i]
            elif i == '成立日期':
                birthday = zidian_list[i]
            elif i == '统一社会信用代码一般指法人和其他组织统一社会信用代码，相当于让法人和其他组织拥有了一个全国统一的“身份证号”。标准规定统一社会信用代码用18位阿拉伯数字或大写英文字母表示。没有帮助有帮助':
                credit_code = zidian_list[i]
        try:
            trademark_number = driver.find_element_by_xpath('//*[@id="nav-main-tmCount"]/span[2]').text#商标数量
        except :
            trademark_number = '0'
        try:
            copyright_number = driver.find_element_by_xpath('//*[@id="nav-main-cpoyRCount"]/span[2]').text#版权数量
        except :
            copyright_number = '0'
        try:
            patent_number = driver.find_element_by_xpath('//*[@id="nav-main-patentCount"]/span[2]').text#专利量
            you_patent = True
            #查询专利详情（先不做）
        except:
            patent_number = '0'
            you_patent = False
        is_pull = 1
        pull_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        
        res = (corp_avater,credit_code,birthday,summary,legal_person,phone,email,website,address,reg_address,status,industry,staff_size,business,is_new_tech,trademark_number,patent_number,copyright_number,company_no,is_pull,pull_time,gongsi_name)
        #print(res)
        cursor.execute(sql, res)
        
        
        #如果有专利
        if you_patent:
            #查询出该公司id
            ps  = 30#每页条数
            all_page = int(patent_number)/ps #除法
            all_page = math.ceil(all_page) + 1#进一取值  后range天然少1 ，所以+1
            
            urls = []
            if all_page>1:#多线程抓取
                for pn in range(1,all_page):
                    table_url = 'https://www.tianyancha.com/pagination/patent.xhtml?ps=%s&pn=%s&id=%s' % (ps,pn,company_no)
                    urls.append(table_url)
                executor = ThreadPoolExecutor(max_workers=10)#本电脑i5线程12 最大设置为60  设置为5的倍数
                result = executor.map(get_patent_list, urls)
                for data in result:
                    if data.empty:
                        pass
                    else:
                        #插入dataframe数据到mysql
                        engine = create_engine('mysql+pymysql://root:root@localhost/wky_oa?charset=utf8')
                        original_data = data.to_sql(name='kwy_corp_patent', con=engine, chunksize=1000, if_exists='append', index=None)#if_exists='replace'替换同名表
                        original_data#执行
            else:#直接查询
                #查询专利列表
                data = scrapy(driver,['patent'])
                print(data)
        return '%s爬取成功' % gongsi_name



def tryonclick(table): # table实质上是selenium WebElement
    # 测试是否有翻页
    ## 把条件判断写进tryonclick中
    try:
        # 找到有翻页标记
        table.find_element_by_tag_name('ul')
        onclickflag = 1
    except Exception:
        print("没有翻页") ## 声明表格名称: name[x] +
        onclickflag = 0
    return onclickflag
def tryontap(table):
    # 测试是否有翻页
    try:
        table.find_element_by_xpath("//div[@class='company_pager pagination-warp']")
        ontapflag = 1
    except:
        print("没有时间切换页") ## 声明表格名称: name[x] +
        ontapflag = 0
    return ontapflag
#正常的表格爬取数
def get_table_info(table):
    tab=table.find_element_by_tag_name('table')
    #print(tab.get_attribute('innerHTML'))
    # 解析成文档对象
    soup = BeautifulSoup(tab.get_attribute('innerHTML'), 'html.parser')   #文档对象
    # 非法URL 1
    invalidLink1='#'
    # 非法URL 2
    invalidLink2='javascript:void(0)'
    # 集合
    result=[]
    # 计数器
    mycount=0
    #查找文档中所有a标签
    for k in soup.find_all('a'):
        #print(k)
        #查找href标签
        link=k.get('href')
        # 过滤没找到的
        if(link is not None):
              #过滤非法链接
              if link==invalidLink1:
                pass
              elif link==invalidLink2:
                pass
              elif link.find("javascript:")!=-1:
                pass
              else:
                mycount=mycount+1
                result.append(link)  
    df = pd.read_html('<table>' + tab.get_attribute('innerHTML') + '</table>')
    if isinstance(df, list):
        df = df[0]
        
    if len(result) == 10:
        df['操作'] = pd.Series(result)#将操作列的值替换成链接url值
        col_name = df.columns.tolist()
        col_name.insert(7,'corp_guid')
        df.reindex(columns=col_name,fill_value=1)
    return df

def change_page(table, df, driver):
    # 抽象化：频繁变换点
    # PageCount = table.find_element_by_class_name('company_pager').text #历史class_name（天眼查的反爬措施）：'total'
    # PageCount = re.sub("\D", "", PageCount)  # 使用正则表达式取字符串中的数字 ；\D表示非数字的意思
    PageCount = len(table.find_elements_by_xpath(".//ul[@class='pagination']/li")) - 1

    for _ in range(int(PageCount) - 1):
        # 抽象化：频繁变换点
        button = table.find_element_by_xpath(".//a[@class='num -next']") #历史class_name（天眼查的反爬措施）：'pagination-next  ',''
        driver.execute_script("arguments[0].click();", button)
        ####################################################################################
        time.sleep(0.2) # 更新换页时间间隔,以应对反爬虫
        ####################################################################################
        df2 = get_table_info(table) ## 应该可以更换不同的get_XXXX_info
        df = df.append(df2)
    return df

def scrapy(driver,table='all',quit_driver=False):

    if isinstance(table, str):
        list_table = []
        list_table.append(table)
        table = list_table

    time.sleep(1)
    js="var q=document.documentElement.scrollTop=100000"  
    driver.execute_script(js)   #执行滑至底部
    
    time.sleep(1)
    tables = driver.find_elements_by_xpath("//div[contains(@id,'_container_')]")
    c = '_container_'
    name = [0] * (len(tables) - 2)
    # 生成一个独一无二的十六位参数作为公司标记，一个公司对应一个，需要插入多个数据表
    table_dict = {}
    for x in range(len(tables)-2):
        name[x] = tables[x].get_attribute('id')
        name[x] = name[x].replace(c, '')  # 可以用这个名称去匹配数据库
        if ((name[x] in table) or (table == ['all'])):
            # 检查用
            print('正在爬取' + str(name[x]))

            df = get_table_info(tables[x])
            onclickflag = tryonclick(tables[x])
            ontapflag = tryontap(tables[x])
            # 判断此表格是否有翻页功能
            if onclickflag == 1:
                df = change_page(tables[x], df, driver)
            # if ontapflag == 1:
            #     df = change_tap(tables[x], df)
            table_dict[name[x]] = df
        else:
            pass
            
    if quit_driver:
        driver.quit()
    return table_dict

def get_track(distance):
    """
    根据偏移量获取移动轨迹
    :param distance: 偏移量
    :return: 移动轨迹
    """
    # 移动轨迹
    track = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 7/8
    # 计算间隔
    t=random.randint(2,3)/10
    # 初速度
    v=0  
 
    while current < distance:
        if current < mid:
        # 加速度为正2 
            a = 5
        else:
            # 加速度为负3
            a = -3
            # 初速度v0
        v0 = v
        # 当前速度v = v0 + at
        v = v0 + a * t
        # 移动距离x = v0t + 1/2 * a * t^2
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move
        # 加入轨迹
        track.append(round(move))
    return track

''' 
@description: 登录方法
@param {type} 
@return: 
'''
def autologin(text_login,text_password):

    driver.get('http://www.tianyancha.com')
    time.sleep(2)
    driver.maximize_window()
    driver.implicitly_wait(10)
    #关底部
    try:
        driver.find_element_by_xpath('//*[@id="tyc_banner_close"]').click()
    except:
        pass
        
    #登陆按钮
    # driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[1]/div/div/div[2]/div/div[4]/a').click()
    #2020/06/04更新
    driver.find_element_by_xpath('//*[@id="web-content"]/div/div[1]/div[1]/div[1]/div/div[2]/div/div[5]/a').click()

    time.sleep(2)

    # 这里点击密码登录时用id去xpath定位是不行的，因为这里的id是动态变化的，所以这里换成了class定位
    # driver.find_element_by_xpath(
    #     './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[1]/div[2]').click()
    
    driver.find_element_by_xpath(
        './/*[@class="sign-in"]/div/div[2]').click()
    time.sleep(2)
    # 天眼查官方会频繁变化登录框的占位符,所以设置两个新参数来定义占位符
    #输入用户名和密码
    #2020/06/04更新
    driver.find_elements_by_xpath("//input[@placeholder='{}']".format('请输入手机号'))[-2].send_keys(text_login)  

    driver.find_elements_by_xpath("//input[@placeholder='{}']".format('请输入登录密码'))[-1].send_keys(text_password)

    # clixp = './/div[@class="modal-dialog -login-box animated"]/div/div[2]/div/div/div[3]/div[2]/div[5]'
    clixp = './/*[@class="sign-in"]/div[2]/div[2]'

    driver.find_element_by_xpath(clixp).click()
    time.sleep(2)


    #获取图
    img = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
    time.sleep(0.5)
    location = img.location
    size = img.size
    top,bottom,left,right = location['y'], location['y']+size['height'], location['x'], location['x']+size['width']
    # 截取第一张图片(无缺口的)
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    captcha1 = screenshot.crop((left, top, right, bottom))
    print('--->', captcha1.size)
    captcha1.save('captcha1.png')
    
    #获取第二张图，先点击
    driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]').click()
    time.sleep(2)
    img1 = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[1]/div[2]/div[1]')
    time.sleep(0.5)
    location1 = img1.location
    size1 = img1.size
    top1,bottom1,left1,right1 = location1['y'], location1['y']+size1['height'], location1['x'], location1['x']+size1['width']
    screenshot = driver.get_screenshot_as_png()
    screenshot = Image.open(BytesIO(screenshot))
    captcha2 = screenshot.crop((left1, top1, right1, bottom1))
    captcha2.save('captcha2.png')

    # 获取偏移量
    left = 8  # 这个是去掉开始的一部分
    for i in range(left, captcha1.size[0]):
        for j in range(captcha1.size[1]):
            # 判断两个像素点是否相同
            pixel1 = captcha1.load()[i, j]
            pixel2 = captcha2.load()[i, j]
            threshold = 60
            if abs(pixel1[0] - pixel2[0]) < threshold and abs(pixel1[1] - pixel2[1]) < threshold and abs(
                pixel1[2] - pixel2[2]) < threshold:
                pass
            else:
                left = i
                if left>=55:
                    break
        if left < 55:
            pass
        else:
            break
            
    print('缺口位置', left)
    
    time.sleep(3)

    left-=7#left-1
     # 开始移动
    track = get_track(left)

    print('滑动轨迹', track)
    #track += [5,-5]  # 滑过去再滑过来，不然有可能被吃
    # 拖动滑块
    starttime=time.time()
    slider = driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]')
    ActionChains(driver).click_and_hold(slider).perform()
    for x in track:
        ActionChains(driver).move_by_offset(xoffset=x, yoffset=0).perform()
    imitate=ActionChains(driver).move_by_offset(xoffset=-1, yoffset=0)
    time.sleep(0.015)
    imitate.perform()
    time.sleep(random.randint(6,10)/10)
    imitate.perform()
    time.sleep(0.04)
    imitate.perform()
    time.sleep(0.012)
    imitate.perform()
    time.sleep(0.019)
    imitate.perform()
    time.sleep(0.033)
    ActionChains(driver).move_by_offset(xoffset=1, yoffset=0).perform()
    #放开鼠标
    ActionChains(driver).pause(random.randint(7,14)/10).release().perform()

    endtime=time.time()
    print("时间：")
    print(endtime-starttime)
    time.sleep(1)
    try:
        if driver.find_element_by_xpath('/html/body/div[10]/div[2]/div[2]/div[2]/div[2]'):
            print('能找到滑块，正在重新登录')
            driver.delete_all_cookies()
            driver.refresh()
            autologin(text_login, text_password) #重新登陆 
        else:
            print('login success')
    except:
        print('login success')


def run(auto=True):
    #开始  
    keyword = []
    sql_key = "select name from kwy_corp_drafts where is_pull=0;"
    you_key = cursor.execute(sql_key)
    if you_key:
        key_list = cursor.fetchall()
        for key in key_list:
            for j in range(len(key)):
                keyword.append(key[j])
    '''
    keyword = ['广东科沃园技术有限公司','大连港股份有限公司','内蒙古蒙牛乳业（集团）股份有限公司']
    '''
    if keyword:
        if auto:
            autologin(text_login='账号', text_password='密码')
        else:
            driver.get('https://www.tianyancha.com/login')
            time.sleep(0.5)
            #先自己登陆
            driver.find_element_by_xpath("//div[@tyc-event-ch='Login.PasswordLogin']").click()
            print('请手动登陆，登陆后自动进行抓取')
        
        #登陆后自动进行抓取
        WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'home-main-search')))
        for kw in keyword:
            res = get_html(kw)
            print(res)
    else:
        print('没有要抓取的数据')
        
    
if __name__ == "__main__":
    #如果要循环从此次开始
    run()
    cursor.close()#用完记得关闭数据连接
    conn.close()
    driver.close()