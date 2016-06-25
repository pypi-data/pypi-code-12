import codecs
import sys
import time
import traceback
import ipdb
from seleniumbase.config import settings
from seleniumbase.fixtures import page_actions
from style_sheet import style

LATEST_REPORT_DIR = "latest_report"
ARCHIVE_DIR = "report_archives"
RESULTS_PAGE = "results.html"
BAD_PAGE_LOG = "results_table.csv"


def get_timestamp():
    return str(int(time.time() * 1000))

def process_successes(test, test_count):
    self.page_results_list.append(
        '"%s","%s","%s","%s","%s","%s","%s","%s"' % (
            test_count,
            "Success",
            "-",
            test.driver.current_url,
            test.browser,
            get_timestamp()[:-3],
            test.id(),
            "*"))


def process_failures(test, err, test_count):
    bad_page_name = "failed_check_%s.jpg" % test_count
    page_actions.save_screenshot(
        test.driver, bad_page_name, folder=LATEST_REPORT_DIR)
    self.page_results_list.append(
        '"%s","%s","%s","%s","%s","%s","%s","%s"' % (
            test_count,
            "FAILED!",
            bad_page_name,
            test.driver.current_url,
            test.browser,
            get_timestamp()[:-3],
            test.id(),
            "*"))

"""
def add_bad_page_log_file(self):
        abs_path = os.path.abspath('.')
        file_path = abs_path + "/%s" % LATEST_REPORT_DIR
        log_file = "%s/%s" % (file_path, BAD_PAGE_LOG)
        f = open(log_file, 'w')
        h_p1 = '''"Num","Result","Screenshot","URL","Browser","Epoch Time",'''
        h_p2 = '''"Verification Instructions","Additional Info"\n'''
        page_header = h_p1 + h_p2
        f.write(page_header)
        for line in self.page_results_list:
            f.write("%s\n" % line)
        f.close()


def process_manual_check_results(self, auto_close_results_page=False):
        self.add_bad_page_log_file()  # Includes successful results

        log_string = self.clear_out_old_logs(get_log_folder=True)
        log_folder = log_string.split('/')[-1]
        abs_path = os.path.abspath('.')
        file_path = abs_path + "/%s" % ARCHIVE_DIR
        log_path = "%s/%s" % (file_path, log_folder)
        web_log_path = "file://%s" % log_path

        tf_color = "#11BB11"
        if failures_count > 0:
            tf_color = "#EE3A3A"

        #ir_color = "#11BB11"
        #if self.incomplete_runs > 0:
        #    ir_color = "#EE3A3A"

        new_data = '''<div><table><thead><tr><th>TEST REPORT SUMMARY
              &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
              </th><th></th></tr></thead><tbody>
              <tr style="color:#00BB00"><td>TESTS PASSING: <td>%s</tr>
              <tr style="color:%s">     <td>TESTS FAILING: <td>%s</tr>
              <tr style="color:#4D4DDD"><td>TOTAL TESTS RUN: <td>%s</tr>
              </tbody></table>''' % (self.manual_check_successes,
                                     tf_color,
                                     failures_count,
                                     self.manual_check_count)

        new_view_1 = '''<h1 id="ContextHeader" class="sectionHeader" title="">
                     %s</h1>''' % new_data

        log_link_shown = '../%s%s/' % (
            ARCHIVE_DIR, web_log_path.split(ARCHIVE_DIR)[1])
        csv_link = '%s/%s' % (web_log_path, BAD_PAGE_LOG)
        csv_link_shown = '%s' % BAD_PAGE_LOG
        new_view_2 = '''<p><p><p><p><h2><table><tbody>
            <tr><td>LOG FILES LINK:&nbsp;&nbsp;<td><a href="%s">%s</a></tr>
            <tr><td>RESULTS TABLE:&nbsp;&nbsp;<td><a href="%s">%s</a></tr>
            </tbody></table></h2><p><p><p><p>''' % (
            web_log_path, log_link_shown, csv_link, csv_link_shown)

        new_view_3 = '<h2><table><tbody></div>'
        any_screenshots = False
        for line in self.page_results_list:
            line = line.split(',')
            if line[1] == '"FAILED!"' or line[1] == '"ERROR!"':
                if not any_screenshots:
                    any_screenshots = True
                    new_view_3 += '''<thead><tr><th>SCREENSHOT FILE
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                        </th><th>LOCATION OF FAILURE</th></tr></thead>'''
                line = '<a href="%s">%s</a>' % (
                    "file://" + log_path + '/' + line[2], line[2]) + '''
                    &nbsp;&nbsp;<td>
                    ''' + '<a href="%s">%s</a>' % (line[3], line[3])
                line = line.replace('"', '')
                new_view_3 += '<tr><td>%s</tr>\n' % line
        new_view_3 += '</tbody></table>'
        new_view = '%s%s%s' % (
            new_view_1, new_view_2, new_view_3)
        results_content = '<body>%s</body>' % new_view
        new_source = '<html><head>%s</head>%s</html>' % (
            style, results_content)
        results_file = self.add_results_page(new_source)
        archived_results_file = log_path + '/' + RESULTS_PAGE
        shutil.copyfile(results_file, archived_results_file)
        print "\n*** The results html page is located at: ***\n" + results_file
        self.open("file://%s" % archived_results_file)
        if auto_close_results_page:
            # Long enough to notice the results before closing the page
            time.sleep(WAIT_TIME_BEFORE_VERIFY)
        else:
            # The user can decide when to close the results page
            ipdb.set_trace()




def log_screenshot(test_logpath, driver):
    screenshot_name = settings.SCREENSHOT_NAME
    screenshot_path = "%s/%s" % (test_logpath, screenshot_name)
    driver.get_screenshot_as_file(screenshot_path)


def log_test_failure_data(test_logpath, driver, browser):
    basic_info_name = settings.BASIC_INFO_NAME
    basic_file_path = "%s/%s" % (test_logpath, basic_info_name)
    log_file = codecs.open(basic_file_path, "w+", "utf-8")
    last_page = get_last_page(driver)
    data_to_save = []
    data_to_save.append("Last_Page: %s" % last_page)
    data_to_save.append("Browser: %s " % browser)
    data_to_save.append("Traceback: " + ''.join(
        traceback.format_exception(sys.exc_info()[0],
                                   sys.exc_info()[1],
                                   sys.exc_info()[2])))
    log_file.writelines("\r\n".join(data_to_save))
    log_file.close()
"""

