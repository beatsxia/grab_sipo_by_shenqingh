from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from xlutils.copy import copy
import xlwt
import xlrd  
import time
import winsound
import os

# 打开浏览器
url = "http://cpquery.sipo.gov.cn/"
driver = webdriver.Firefox()
driver.get(url)

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

# 恢复至页码
def to_page(p):
    # 设置当前页码
    WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'form-control')))
    pe = driver.find_elements_by_css_selector('.form-control')[0]
    driver.execute_script("arguments[0].value='"+str(p)+"'", pe)
    time.sleep(1)
    # 按回车键换页
    pe.send_keys(Keys.ENTER)
    tips('正在恢复到第'+str(p)+'页，请稍后。如长时间未响应，请手动再底部输入页码'+str(page)+'并回车')
    # 根据页码是否正确判断页面是否加载完成
    time.sleep(1)
    WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))

# 新建tab用于加载二级详情页面
main_window = driver.current_window_handle
driver.execute_script('''window.open("about:blank","_blank");''')
driver.switch_to.window(driver.window_handles[0])

# 等待登陆查询完成
WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'login_butt')))
tips('请手动登陆账号，然后在查询页面输入关键词、验证码等信息，点击查询后系统自动开始导出')
WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))

# 获取关键词
keyword = driver.find_elements_by_name('select-key:shenqingrxm')[0].get_attribute('value')

# 读取xlxs或建立
xls_path = keyword+'.xls'
#xls_path = 'data/'+keyword+'.xls'
if os.path.exists(xls_path):
    # 如果存在，则读取已存在的xls
    xls = xlrd.open_workbook(xls_path)
    page = int(xls.sheet_by_index(1).row_values(0)[0])
    # APP重新运行，恢复至指定页码
    to_page(page)
    # 将xls读入对象转为写入对象
    workbook = copy(xls)
    booksheet = workbook.get_sheet(0)
    current_page_sheet = workbook.get_sheet(1)
else:
    # 如果不存在，创建新excel
    workbook = xlwt.Workbook(encoding='utf-8')  
    booksheet = workbook.add_sheet('data', cell_overwrite_ok=True)  
    current_page_sheet = workbook.add_sheet('current page', cell_overwrite_ok=True) 
    page = 1 

# # 等待第一页加载完成
# next = next = driver.find_element_by_link_text('>')
# next.click()
# e = WebDriverWait(driver,600000).until(EC.text_to_be_present_in_element_value((By.CLASS_NAME,'form-control'),'2'))

# # 替换为500
# next = driver.find_element_by_link_text('>')
# u = next.get_attribute('href')[:-1].replace('record_page-row=10','record_page-row=10000')
# driver.execute_script("arguments[0].setAttribute(arguments[1], arguments[2]);", next, "href", u)
# next.click()

# 标记是否处于超出查询限制
stop = False

while True:
    # 如果出于暂停状态
    if stop:
        # 播放声音同hi在
        winsound.Beep(400, 500)
        # 判断是否重新重新登陆后并且点击了查询
        if isElementExist('.content_listx'):
            stop = False
            # 用户已经重新登陆了，恢复到页面page
            to_page(page)
        time.sleep(5)
        continue
    # 获取总页面数
    WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'form-control')))
    WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[1]/div[2]/ul/li[3]')))
    total_page = int(driver.find_elements_by_css_selector('.form-control')[0].find_element_by_xpath('..').text.replace('/','').strip())
    # 遍历每一页
    for i in range(page,total_page):  
        tips("正在导出，当前在第"+str(page)+"页")
        es = driver.find_elements_by_css_selector('.content_listx')
        c = len(es)
        # 遍历每一行数据
        for j in range(c):
            # 获取列表内容
            # 切换标签页可能会卡，这里等待切换回来
            WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))
            item = driver.find_elements_by_css_selector('.content_listx')[j].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')
            for l in range(len(item)):
                item[l] = driver.find_elements_by_css_selector('.content_listx')[j].find_element_by_class_name('content_listx_patent').find_elements_by_css_selector('td')[l].text
            # 切换tab
            driver.switch_to.window(driver.window_handles[1])
            # 进入详情
            driver.get('http://cpquery.sipo.gov.cn/txnQueryBibliographicData.do?select-key:shenqingh='+item[1])
            # 等待页面加载完毕
            WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.ID,'downFrame')))
            # 判断是否超出查询限制
            if isElementExist('.binding'):
                stop =True
                tips('超出查询限制。请更换账号')
                driver.switch_to.window(driver.window_handles[0])
                driver.get(url)
                break
            # 等待详情加载完毕
            WebDriverWait(driver,600000).until(EC.visibility_of_element_located((By.CLASS_NAME,'imfor_part1')))
            # 获取案件状态和代理机构名称
            anjianywzt = driver.find_element_by_name('record_zlx:anjianywzt').get_attribute('title')
            dailijgmc = driver.find_element_by_name('record_zldl:dailijgmc').get_attribute('title')
            driver.get('about:blank')
            # 返回Tab
            driver.switch_to.window(driver.window_handles[0])
            # 防止卡顿，等待切换完毕
            WebDriverWait(driver,600000).until(EC.presence_of_element_located((By.CLASS_NAME,'content_listx')))
            # 每一列数据写进表格item
            for k in range(len(item)):
                booksheet.write((page-1)*10+j,k,item[k])
            booksheet.write((page-1)*10+j,len(item),anjianywzt)
            booksheet.write((page-1)*10+j,len(item)+1,dailijgmc)
        # 超出查询限制，不继续查询，退出
        if stop:
            break
        # 防止频率过高，休息一下
        tips("准备抓取下一页")
        time.sleep(5)
        # 待处理页码+1
        page = page + 1
        tips("正在查询第"+str(page)+"个页面")
        # 保存当前页码
        current_page_sheet.write(0,0,str(page))
        # 保存本页数据
        workbook.save(xls_path)
        # 点击下一页
        next = driver.find_element_by_link_text('>')
        next.click()
        # 超出查询限制，不继续查询，退出
        if isElementExist('.binding'):
            stop =True
            tips('超出查询限制。请更换账号')
            driver.get(url)
            break
    if stop is False:
        tips('全部导出完成')
        break