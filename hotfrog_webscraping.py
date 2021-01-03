from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as W
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
driver =  webdriver.Chrome(ChromeDriverManager().install())
driver.implicitly_wait(20)
import xlwt 
from xlwt import Workbook

def removed_ad(driver):
    try:
        action = webdriver.common.action_chains.ActionChains(driver)
        action.move_by_offset(150,0) 
        action.click()
        action.perform()
        print("ad removed")
    except:
        pass

def append_data(data,sheet,row_counter):
    print("--- appending data to google sheet for one record ")
    sheet.write( row_counter, 1, data["categoryName"] + " : " + data["categoryValue"] )
    sheet.write( row_counter, 2, data["Phone"])
    sheet.write( row_counter, 3, data["Email"])
    sheet.write( row_counter, 4, data["Website"])
    sheet.write( row_counter, 5, data["Address"])
    sheet.write( row_counter, 6, data["BusinessProfile"])

def get_data(driver):
    # Initalizing empty dict values
    data = dict({
        "categoryName": "",
        "categoryValue" : "",
        "Phone" : "",
        "Email": "",
        "Website" : "",
        "Address" : "",
        "BusinessProfile" : "",
    })
    try:
        removed_ad(driver)
        data_page_main = W(driver,10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"container.hf-bdp.p-3"))
            )
        print("A1")

        print("B")
        # Adding Category
        category_field = data_page_main.find_elements_by_class_name("lead.hfhl")
        print("C")

        try:
            data["categoryName"] = category_field[0].text
            data["categoryValue"] = category_field[1].text
        except:
            pass   
        try:
            Business_profile = driver.find_elements_by_id("description")[0]
            description = Business_profile.find_elements_by_tag_name("small")
            data["BusinessProfile"] = description[0].text
        except:
            pass 
        # Adding Phone, Website and Address
        first_table_data_page = W(data_page_main,10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"row.small"))
        )

        labels = first_table_data_page.find_elements_by_class_name("col-3.col-md-2.py-1")
        values = first_table_data_page.find_elements_by_class_name("col-9.col-md-10.py-1")
        print("F")

        keys = []
        for label in labels:
            keys.append(label.text)

        index = 0
        for value in values:
            data[keys[index]] = value.text
            index = index + 1
    except Exception as e:
        print(e)
    
    return data

def second_page_pagination_handling(sheet, row_counter, category_name):
    print("9")
    second_page_index = 1
    while True:
        print("10")
        # if second_page_index == 3:
        #     print("A1")
        #     break
        if second_page_index != 1:
            try:
                print("11")
                removed_ad(driver)
                next_page =   driver.find_element_by_xpath("//a[contains(text(),'Next')]")
                removed_ad(driver)
                next_page.click()
                removed_ad(driver)
                is_next_page_clicked = True
            except:
                print("12")
                is_next_page_clicked = False

            try:
                print("13")
                if is_next_page_clicked == False:
                    driver.get("https://www.hotfrog.com/search/us/" + category_name + "/" + second_page_index)
                    removed_ad(driver)
                    try:
                        print("14")
                        driver.find_element_by_xpath("//a[contains(text(),'Next')]")
                    except:
                        print("15")
                        print(category_name + "reached to " + category_name +" :: Breaking for other categories")
                        break
            except:
                print("16")
                second_page_index = second_page_index +1
                continue
        is_second_page_list_found = False 
        try:
            print("17")
            time.sleep(10)
            second_page_list = driver.find_elements_by_xpath("//h3[contains(@class,'h6 mb-0')]") # taking time
            total_result = len(second_page_list)
            is_second_page_list_found = True
        except:
            print("18")
            driver.get("https://www.hotfrog.com/search/us/" + category_name + "/" + second_page_index)
            removed_ad(driver)
            second_page_list = driver.find_elements_by_xpath("//h3[contains(@class,'h6 mb-0')]")
            total_result = len(second_page_list)
            is_second_page_list_found  = True
        if is_second_page_list_found == False:
            print("19")
            second_page_index = second_page_index +1
            continue

        print("total_result",total_result)
        for i in range(0, total_result):
            print("20")
            removed_ad(driver)
            time.sleep(20)
            try:
                print("21")
                # time.sleep(5)
                second_page_main = W(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME,"serpspage")))
                removed_ad(driver)
                second_page_list_temp = second_page_main.find_elements_by_xpath("//h3[contains(@class,'h6 mb-0')]")
                removed_ad(driver)
                print("22")
                category = second_page_list_temp[i] 
                clickable_cat = W(category,10).until(EC.presence_of_element_located((By.TAG_NAME,"a")))
                print("23")
                clickable_cat.click()
                print("23")
                # Need to wait till reload the page
                # time.sleep(20)
                removed_ad(driver)
            except Exception as e:
                print("23A continue", e)
                continue
            try:
                # import pdb;pdb.set_trace()
                print("24")
                data = get_data(driver)
                print(data)
                if  data["categoryName"] != "":
                    append_data(data,sheet,row_counter)
                    row_counter = row_counter + 1
            except:
                print("24A")
                pass

            if driver.current_url != "https://www.hotfrog.com/search/us/" + category_name:
                try:
                    print("25")
                    driver.back()
                    removed_ad(driver)
                    print("Completed " + str(i))
                except:
                    print("26")
                    print("Skiped " + str(i))
        second_page_index = second_page_index +1
        print("27")


#---------------------- For Google Sheet ----------------------
wb = Workbook() 
  
sheet = wb.add_sheet('data') 

colum_name = ["Category","Phone","Email","Website","Address","Business Profile"]

row_counter = 1
col_counter = 1
for col in colum_name:
    sheet.write(0, col_counter, col)
    col_counter = col_counter + 1

#starting with hotfrog.com
try:
    print("1")
    driver.get("https://www.hotfrog.com/")
    print("2")
    removed_ad(driver)
    print(driver.current_url)
    print("3")
    try:
        categories = driver.find_elements_by_xpath("//div[contains(@class,'col-3')]")
        total_categories = len(categories)
    except:
        print("Total categories not Loaded")
        total_categories = 0
    print("4")
    print("total_categories", total_categories)
    for i in range(1,2):
        print("5")
        if driver.current_url != "https://www.hotfrog.com/":
            driver.get("https://www.hotfrog.com/")
        removed_ad(driver)
        try:
            print("6")
            first_page_list_temp = driver.find_elements_by_xpath("//div[contains(@class,'col-3')]")
            removed_ad(driver)
            category = first_page_list_temp[i]
            category_name = '-'.join((category.text).lower().split()) 
            print("7")
            category.click()
            print("8")
            removed_ad(driver)
            second_page_pagination_handling(sheet,row_counter,category_name)
            print("28")
            if driver.current_url != "https://www.hotfrog.com/":
                print("29")
                driver.back()
        except:
            print("30")
            pass
        print("31")
        
except Exception as e:
    print("error is ", e)


wb.save('scrapedpagination_advertising.xls')
driver.quit()
