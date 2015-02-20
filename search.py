from splinter import Browser


class Search:
    def __init__(self, term, source, from_date, to_date):
        self.term = term
        self.source = source
        self.from_date = from_date
        self.to_date = end_date
    
    def search(self):
        from_date = '01/01/1999'
        to_date = '02/01/1999'
        source = 'new york times, the'
        term = 'executive'
        
        browser = Browser()
        browser.visit('http://www.lexisnexis.com/hottopics/lnacademic/?')
        
        browser.driver.switch_to_frame('mainFrame')
        browser.find_by_id('lblAdvancDwn').click()
        browser.find_by_id('txtFrmDate').type(from_date)
        browser.find_by_id('txtToDate').type(to_date)
        browser.uncheck('selectAll')
        browser.fill('sourceTitleAdv', source)
        browser.find_by_xpath('//*[@id="titles"]/a').click() #DOESN'T WORK :(
        browser.fill('txtSegTerms', term)
        browser.find_by_id('OkButt').click()
        browser.find_by_id('srchButt').click()
        
        browser.find_by_xpath('//*[@id="deliveryContainer"]/table/tbody/tr/td[6]/table/tbody/tr/td[1]/table/tbody/tr/td/a[3]/img')
        result_frame = browser.driver.find_element_by_xpath('//*[@id="fs_content"]/frame')
        result_frame_name = result_frame.get_attribute('name')
        
