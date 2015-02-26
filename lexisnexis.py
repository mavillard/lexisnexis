import csv
import os
import time
import uuid

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
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
        try:
            element = WebDriverWait(driver, time).until(
                EC.presence_of_element_located((by, value))
            )
        except TimeoutException:
            element = None
        return element
    
    def search(self):
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
        if not result_frame:
            log = Log(LOGFILE, self, '0 RESULTS')
            log.write()
        else:
            result_frame_name = result_frame.get_attribute('name')
            driver.switch_to_frame(result_frame_name)
            total_results = int(driver.find_element_by_name('totalDocsInResult').get_attribute('value'))
            
            if total_results > MAX_LEXISNEXIS_RESULTS:
                log = Log(LOGFILE, self, '{} RESULTS'.format(MAX_LEXISNEXIS_RESULTS))
                log.write()
                # decrease time slot
                # search again
                pass
            else:
                # log? CODE 0,1,2
                total_iters = total_results / MAX_DOWNLOAD + 1
                for num_iter in range(1, total_iters + 1):
                    driver.find_element_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img').click()
                    time.sleep(SLEEP)
                    
                    new_windows = driver.window_handles
                    download_window = get_most_recent(current_windows, new_windows)
                    driver.switch_to_window(download_window)
                    time.sleep(SLEEP)
                    
                    lower_index = (num_iter - 1) * MAX_DOWNLOAD + 1
                    upper_index = (num_iter - 1) * MAX_DOWNLOAD + MAX_DOWNLOAD
                    upper_index = min(upper_index, total_results)
                    driver.find_element_by_id('sel').click()
                    range_download = '{}-{}'.format(lower_index, upper_index)
                    driver.find_element_by_id('rangetextbox').send_keys(range_download)
                    source_option = self.wait(driver, 'xpath', '//*[@id="delFmt"]/option[2]')
                    source_option.click()
                    time.sleep(SLEEP)
                    
                    current_files = os.listdir(RESULT_DIR)
                    download_button = self.wait(driver, 'xpath', '//*[@id="img_orig_top"]/a/img')
                    download_button.click()
                    time.sleep(SLEEP)
                    download_link = self.wait(driver, 'xpath', '//*[@id="center"]/center/p/a')
                    download_link.click()
                    time.sleep(SLEEP)
                    driver.close()
                    current_windows = driver.window_handles
                    driver.switch_to_window(main_window)
                    driver.switch_to_frame('mainFrame')
                    driver.switch_to_frame(result_frame_name)
                    
                    new_files = os.listdir(RESULT_DIR)
                    new_filename = get_most_recent(current_files, new_files)
                    result_file = ResultFile(new_filename)
                    result_file.set_unique_name()
                    result = Result(RESULTFILE, self, result_file)
                    result.write()
#        driver.close()
        print 'GREAT!'


def get_most_recent(old, new):
    return set(new).difference(set(old)).pop()


def download(search, driver):
    return set(new).difference(set(old)).pop()


class ResultFile:
    def __init__(self, filename):
        self.file_root = os.path.join(RESULT_DIR, filename)
    
    def set_unique_name(self):
        new_name = '{}--{}.html'.format(self.file_root[:-5], uuid.uuid1())
        os.rename(self.file_root, new_name)
        self.file_root = new_name


class Result:
    def __init__(self, filename, search, result_file):
        self.report = Report(
            filename,
            search.term,
            search.source,
            search.from_date,
            search.to_date,
            result_file.file_root
        )
    
    def write(self):
        self.report.write()


class Log:
    def __init__(self, filename, search, log):
        self.report = Report(
            filename,
            search.term,
            search.source,
            search.from_date,
            search.to_date,
            log
        )
    
    def write(self):
        self.report.write()


class Report:
    def __init__(self, filename, term, source, from_date, to_date, report):
        self.filepath = os.path.join(CURRENT_DIR, filename)
        self.term = term
        self.source = source
        self.from_date = from_date
        self.to_date = to_date
        self.report = report
    
    def write(self):
        csvfile = open(self.filepath, 'ab')
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
            self.report
        ])


SLEEP = 0.5
WAIT = 10
MAX_DOWNLOAD = 20
MAX_LEXISNEXIS_RESULTS = 1000
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(CURRENT_DIR, 'documents')
RESULTFILE = 'results.csv'
LOGFILE = 'log.csv'
CSV_DELIMITER = ' '
CSV_QUOTECHAR = '"'


if not os.path.isdir(RESULT_DIR):
    os.makedirs(RESULT_DIR)

s = Search('executive', 'new york times, the', '01/01/1999', '01/02/1999')
s.search()
