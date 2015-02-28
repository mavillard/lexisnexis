import csv
import datetime
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
        driver = DRIVER
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
            log = Log(self, '1: NOT FOUND')
            log.write()
        else:
            result_frame_name = result_frame.get_attribute('name')
            driver.switch_to_frame(result_frame_name)
            total_results = int(driver.find_element_by_name('totalDocsInResult').get_attribute('value'))
            
            if total_results > MAX_LEXISNEXIS_RESULTS:
                log = Log(self, '3: {} > {} (MAX RESULTS)'.format(total_results, MAX_LEXISNEXIS_RESULTS))
                log.write()
                ntimes = total_results / MAX_LEXISNEXIS_RESULTS
                return ntimes
            else:
                total_iters = total_results / MAX_DOWNLOADS + 1
                if total_results % MAX_DOWNLOADS == 0:
                    total_iters -= 1
                if total_iters > 1:
                    log = Log(self, '2: {} > {} (MAX DOWNLOADS)'.format(total_results, MAX_DOWNLOADS))
                    log.write()
                for num_iter in range(1, total_iters + 1):
                    driver.find_element_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img').click()
                    time.sleep(SLEEP)
                    
                    new_windows = driver.window_handles
                    download_window = get_most_recent(current_windows, new_windows)
                    driver.switch_to_window(download_window)
                    time.sleep(SLEEP)
                    
                    lower_index = (num_iter - 1) * MAX_DOWNLOADS + 1
                    upper_index = (num_iter - 1) * MAX_DOWNLOADS + MAX_DOWNLOADS
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
                    time.sleep(total_results / 15 + 5) # 5 extra seconds
                    download_link = self.wait(driver, 'xpath', '//*[@id="center"]/center/p/a')
                    download_link.click()
                    time.sleep(SLEEP)
                    driver.close()
                    current_windows = driver.window_handles
                    driver.switch_to_window(main_window)
                    driver.switch_to_frame('mainFrame')
                    driver.switch_to_frame(result_frame_name)
                    time.sleep(total_results / 100 + 1) # 1 extra seconds
                    
                    new_files = os.listdir(RESULT_DIR)
                    new_filename = get_most_recent(current_files, new_files)
                    result_file = ResultFile(new_filename)
                    result_file.set_unique_name()
                    result = Result(self, result_file)
                    result.write()
        log = Log(self, '0: OK')
        log.write()
        return 0


def get_most_recent(old, new):
    return set(new).difference(set(old)).pop()


class DateRange:
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
    
    def __repr__(self):
        return '<{} -- {}>'.format(self.start_date, self.end_date)
    
    def split(self, years=0, months=0, days=0):
        ranges = []
        from_date = self.start_date
        to_date = DateRange.create_range(from_date, years, months, days)[1]
        while to_date <= self.end_date:
            ranges.append(DateRange(from_date, to_date))
            from_date = to_date + datetime.timedelta(days=+1)
            to_date = DateRange.create_range(from_date, years, months, days)[1]
        else:
            ranges.append(DateRange(from_date, self.end_date))
        return ranges
    
    @staticmethod
    def create_range(base_date, years=0, months=0, days=0):
        if years > 0:
            dt = datetime.datetime(
                year=base_date.year + years,
                month=base_date.month,
                day=base_date.day
            )
        elif months > 0:
            dt = datetime.datetime(
                year=base_date.year + (base_date.month + months) / 12,
                month=(base_date.month + months) % 12 or 12,
                day=base_date.day
            )
        elif days > 0:
            dt = base_date + datetime.timedelta(days=days)
        else:
            dt = base_date + datetime.timedelta(days=1)
        
        dt = dt + datetime.timedelta(days=-1)
        return (base_date, dt)
    
    def format(self):
        return [
            self.start_date.strftime('%m/%d/%Y'),
            self.end_date.strftime('%m/%d/%Y')
        ]


class ResultFile:
    def __init__(self, filename):
        self.file_root = os.path.join(RESULT_DIR, filename)
    
    def set_unique_name(self):
        new_name = '{}--{}.html'.format(self.file_root[:-5], uuid.uuid1())
        os.rename(self.file_root, new_name)
        self.file_root = new_name


class Result:
    def __init__(self, search, result_file):
        self.report = Report(
            RESULTFILE,
            search.term,
            search.source,
            search.from_date,
            search.to_date,
            result_file.file_root
        )
    
    def write(self):
        self.report.write()


class Log:
    def __init__(self, search, log):
        self.report = Report(
            LOGFILE,
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
MAX_DOWNLOADS = 500
MAX_LEXISNEXIS_RESULTS = 990
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(CURRENT_DIR, 'documents')
RESULTFILE = os.path.join(CURRENT_DIR, 'results.csv')
LOGFILE = os.path.join(CURRENT_DIR, 'log.csv')
TERMFILE = os.path.join(CURRENT_DIR, 'terms.txt')
#SOURCEFILE = os.path.join(CURRENT_DIR, 'sources.txt')
TERMFILE = os.path.join(CURRENT_DIR, 't.txt')
SOURCEFILE = os.path.join(CURRENT_DIR, 's.txt')
CSV_DELIMITER = ' '
CSV_QUOTECHAR = '"'
INIT_TIME_SLOT = [0, 3, 0] # years, months, days (priority >)
START_DATE = [1, 1, 1999] # m, d, Y
#END_DATE = [12, 31, 2014] # m, d, Y
END_DATE = [12, 31, 2001] # m, d, Y
DRIVER = None


def global_search(term, source, global_range, time_slot):
    ranges = global_range.split(time_slot[0], time_slot[1], time_slot[2])
    for r in ranges:
        dates = r.format()
        s = Search(term, source, dates[0], dates[1])
        try:
            result = s.search()
            if result > 0:
                reduced_t_s = reduce_time_slot(time_slot)
                if reduced_t_s != time_slot:
                    global_search(term, source, r, reduced_t_s)
                else:
                    log = Log(s, '4: TIME SLOT IRREDUCIBLE')
                    log.write()
        except Exception, e:
            log = Log(s, '5: EXCEPTION - {}'.format(e.message))
            log.write()


def reduce_time_slot(time_slot):
    reduced_t_s = list(time_slot)
    if reduced_t_s[0] > 1:
        reduced_t_s[0] = 1
    elif reduced_t_s[0] == 1:
        reduced_t_s[0] = 0
        reduced_t_s[1] = 3
    elif reduced_t_s[1] == 3:
        reduced_t_s[1] = 1
    elif reduced_t_s[1] == 1:
        reduced_t_s[1] = 0
        reduced_t_s[2] = 7
    elif reduced_t_s[2] == 7:
        reduced_t_s[2] = 1
    return reduced_t_s


def start():
    if not os.path.isdir(RESULT_DIR):
        os.makedirs(RESULT_DIR)
    
    global DRIVER
    profile = webdriver.FirefoxProfile()
    profile.set_preference('browser.download.folderList', 2)
    profile.set_preference('browser.download.manager.showWhenStarting', False)
    profile.set_preference('browser.download.dir', RESULT_DIR)
    profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/html')
    DRIVER = webdriver.Firefox(profile)
    
    start_date = datetime.datetime(
        year=START_DATE[2],
        month=START_DATE[0],
        day=START_DATE[1],
    )
    end_date = datetime.datetime(
        year=END_DATE[2],
        month=END_DATE[0],
        day=END_DATE[1],
    )
    global_range = DateRange(start_date, end_date)
    
    for source in open(SOURCEFILE):
        for term in open(TERMFILE):
            global_search(term.strip(), source.strip(), global_range, INIT_TIME_SLOT)
    
    DRIVER.close()


start()
