from selenium import webdriver
from splinter import Browser


class Search:
    MAX_DOWNLOAD = 500
    
    def __init__(self, term, source, from_date, to_date):
        self.term = term
        self.source = source
        self.from_date = from_date
        self.to_date = to_date
        
        self.profile = webdriver.FirefoxProfile()
        self.profile.set_preference('browser.download.folderList', 2) # custom location
        self.profile.set_preference('browser.download.manager.showWhenStarting', False)
        self.profile.set_preference('browser.download.dir', '/home/antonio/git/lexisnexis/')
        self.profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/html')
    
    def search(self, num_results=None):
        import ipdb;ipdb.set_trace()
        
        browser = Browser(self.profile)
        browser.visit('http://www.lexisnexis.com/hottopics/lnacademic/?')
        current_windows = browser.driver.window_handles
        main_window = browser.driver.current_window_handle
        
        browser.driver.switch_to_frame('mainFrame')
        browser.find_by_id('lblAdvancDwn').click()
        browser.find_by_id('txtFrmDate').type(self.from_date)
        browser.find_by_id('txtToDate').type(self.to_date)
        browser.uncheck('selectAll')
        browser.fill('sourceTitleAdv', self.source)
#        browser.find_by_xpath('//*[@id="titles"]/a').click() #DOESN'T WORK :(
        browser.fill('txtSegTerms', self.term)
        browser.find_by_id('OkButt').click()
        browser.find_by_id('srchButt').click()
        
        result_frame = browser.driver.find_element_by_xpath('//*[@id="fs_main"]/frame[2]')
        result_frame_name = result_frame.get_attribute('name')
        browser.driver.switch_to_frame(result_frame_name)
        browser.find_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img').click()
        
        total_results = int(browser.find_by_name('totalDocsInResult').value)
        new_windows = browser.driver.window_handles
        result_window = set(new_windows).difference(set(current_windows)).pop()
        browser.driver.switch_to_window(result_window)
        
        browser.select('delFmt', 'QDS_EF_HTML')
        if(total_results <= self.MAX_DOWNLOAD):
            browser.find_by_xpath('//*[@id="img_orig_top"]/a/img').click()
            browser.find_by_xpath('//*[@id="center"]/center/p/a').click()
        else:
            pass
        
        
        print 'GREAT!'


class Result:
    def __init__(self, search, source, from_date, to_date):
        self.term = term
        self.source = source
        self.from_date = from_date
        self.to_date = to_date
    


s = Search('director', 'new york times, the', '01/01/1999', '01/02/1999')
s.search()
