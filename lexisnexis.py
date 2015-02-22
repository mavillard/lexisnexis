import csv
import os
import uuid

from selenium import webdriver


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
    
    def search(self, num_iters=1):
        import ipdb;ipdb.set_trace()
        
        driver = webdriver.Firefox(self.profile)
        driver.get('http://www.lexisnexis.com/hottopics/lnacademic/?')
        current_windows = driver.window_handles
        main_window = driver.current_window_handle
        
        driver.switch_to_frame('mainFrame')
        driver.find_element_by_id('lblAdvancDwn').click()
        driver.find_element_by_id('txtFrmDate').send_keys(self.from_date)
        driver.find_element_by_id('txtToDate').send_keys(self.to_date)
        driver.find_element_by_id('selectAll').click()
        driver.find_element_by_id('sourceTitleAdv').send_keys(self.source)
#        driver.find_element_by_xpath('//*[@id="titles"]/a').click() #DOESN'T WORK :(
        driver.find_element_by_id('txtSegTerms').send_keys(self.term)
        driver.find_element_by_id('OkButt').click()
        driver.find_element_by_id('srchButt').click()
        
        result_frame = driver.find_element_by_xpath('//*[@id="fs_main"]/frame[2]')
        result_frame_name = result_frame.get_attribute('name')
        driver.switch_to_frame(result_frame_name)
        driver.find_element_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img').click()
        
        total_results = int(driver.find_element_by_name('totalDocsInResult').get_attribute('value'))
        new_windows = driver.window_handles
        download_window = get_most_recent(current_windows, new_windows)
        driver.switch_to_window(download_window)
        
        driver.find_element_by_xpath('//*[@id="delFmt"]/option[2]').click()
        if(total_results <= MAX_DOWNLOAD):
            current_files = os.listdir(RESULT_DIR)
            driver.find_element_by_xpath('//*[@id="img_orig_top"]/a/img').click()
            driver.find_element_by_xpath('//*[@id="center"]/center/p/a').click()
            new_files = os.listdir(RESULT_DIR)
            new_filename = get_most_recent(current_files, new_files)
            result_file = ResultFile(new_filename)
            result_file.set_unique_name()
            result = Result(self, result_file)
            result.write()
        else:
            pass
        
        
        print 'GREAT!'


class ResultFile:
    def __init__(self, filename):
        self.file_root = os.path.join(RESULT_DIR, filename)
    
    def set_unique_name(self):
        new_name = '{}-{}.html'.format(self.file_root[:-5], uuid.uuid1())
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


MAX_DOWNLOAD = 500
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
RESULT_DIR = os.path.join(CURRENT_DIR, 'documents')
CSV_DELIMITER = ' '
CSV_QUOTECHAR = '|'


if not os.path.isdir(RESULT_DIR):
    os.makedirs(RESULT_DIR)
s = Search('director', 'new york times, the', '01/01/1999', '01/02/1999')
s.search()
