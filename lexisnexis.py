import csv
import os
import time
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Search:
    def __init__(self, term, source, from_date, to_date):
        self.term = term
        self.source = source
        self.from_date = from_date
        self.to_date = to_date
        
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2)
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.download.dir', RESULT_DIR)
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/html')
    
    def wait(self, driver, by, value, time=None):
        if by == 'id':
            by = By.ID
        elif by == 'xpath':
            by = By.XPATH
        if not time:
            time = WAIT
        return WebDriverWait(driver, time).until(
            EC.presence_of_element_located((by, value))
        )
    
    def search(self, num_iters=1):
        driver = webdriver.Firefox(self.profile)
        driver.get('http://www.lexisnexis.com/hottopics/lnacademic/?')
        current_windows = driver.window_handles
        main_window = driver.current_window_handle
        driver.switch_to_frame('mainFrame')
        driver.find_element_by_id('lblAdvancDwn').click()
        time.sleep(SLEEP)
        
        self.wait(driver, 'id', 'advanceDiv')
        time.sleep(SLEEP)
        driver.find_element_by_id('txtFrmDate').send_keys(self.from_date)
        time.sleep(SLEEP)
        driver.find_element_by_id('txtToDate').send_keys(self.to_date)
        time.sleep(SLEEP)
        driver.find_element_by_id('selectAll').click()
        time.sleep(SLEEP)
        driver.find_element_by_id('sourceTitleAdv').send_keys(self.source)
        time.sleep(SLEEP)
        source_option = self.wait(driver, 'xpath', '//*[@id="titles"]/a')
        action = source_option.get_attribute('onclick')
        driver.execute_script(action)
        time.sleep(SLEEP)
        driver.find_element_by_id('txtSegTerms').send_keys(self.term)
        time.sleep(SLEEP)
        driver.find_element_by_id('OkButt').click()
        time.sleep(SLEEP)
        driver.find_element_by_id('srchButt').click()
        time.sleep(SLEEP)
        
        result_frame = self.wait(driver, 'xpath', '//*[@id="fs_main"]/frame[2]')
        result_frame_name = result_frame.get_attribute('name')
        driver.switch_to_frame(result_frame_name)
        driver.find_element_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img').click()
        time.sleep(SLEEP)
        
        total_results = int(driver.find_element_by_name('totalDocsInResult').get_attribute('value'))
        new_windows = driver.window_handles
        download_window = get_most_recent(current_windows, new_windows)
        driver.switch_to_window(download_window)
        time.sleep(SLEEP)
        
        source_option = self.wait(driver, 'xpath', '//*[@id="delFmt"]/option[2]')
        source_option.click()
        time.sleep(SLEEP)
        if total_results > MAX_LEXISNEXIS_RESULTS:
            # log
            # decrease time slot
            # search again
            pass
        elif total_results > MAX_DOWNLOAD:
            pass
        else: # total_results <= MAX_DOWNLOAD
            current_files = os.listdir(RESULT_DIR)
            download_button = self.wait(driver, 'xpath', '//*[@id="img_orig_top"]/a/img')
            download_button.click()
            time.sleep(SLEEP)
            download_link = self.wait(driver, 'xpath', '//*[@id="center"]/center/p/a')
            download_link.click()
            time.sleep(SLEEP)
            driver.close()
            driver.switch_to_window(main_window)
            
            new_files = os.listdir(RESULT_DIR)
            new_filename = get_most_recent(current_files, new_files)
            result_file = ResultFile(new_filename)
            result_file.set_unique_name()
            result = Result(self, result_file)
            result.write()
        
        driver.close()
        print 'GREAT!'


class ResultFile:
    def __init__(self, filename):
        self.file_root = os.path.join(RESULT_DIR, filename)
    
    def set_unique_name(self):
        new_name = '{}--{}.html'.format(self.file_root[:-5], uuid.uuid1())
        os.rename(self.file_root, new_name)
        self.file_root = new_name


class Result:
    def __init__(self, search, result_file):
        self.term = search.term
        self.source = search.source
        self.from_date = search.from_date
        self.to_date = search.to_date
        self.result_file = result_file.file_root
    
    def write(self):
        results = os.path.join(CURRENT_DIR, 'results.csv')
        csvfile = open(results, 'ab')
        writer = csv.writer(
            csvfile,
            delimiter=CSV_DELIMITER,
            quotechar=CSV_QUOTECHAR,
            quoting=csv.QUOTE_MINIMAL
        )
        writer.writerow([
            self.term,
            self.source,
            self.from_date,
            self.to_date,
            self.result_file
        ])


def get_most_recent(old, new):
    return set(new).difference(set(old)).pop()


SLEEP = 0.5
WAIT = 10
MAX_DOWNLOAD = 500
MAX_LEXISNEXIS_RESULTS = 1000
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(CURRENT_DIR, 'documents')
CSV_DELIMITER = ' '
CSV_QUOTECHAR = '"'


if not os.path.isdir(RESULT_DIR):
    os.makedirs(RESULT_DIR)

s = Search('executive', 'new york times, the', '01/01/1999', '01/02/1999')
s.search()
