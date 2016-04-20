# coding=utf-8
from datetime import datetime
from time import sleep

import allure
import selenium.webdriver.support.expected_conditions as ec
from hamcrest import assert_that, equal_to, is_, not_none, none, contains_string, equal_to_ignoring_case, has_item, \
    not_, is_in
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


class UserSteps(object):
    def __init__(self, config):
        self.config = config
        self.driver = config.driver
        self.element_wait = int(config.element_wait)

    @allure.step("Открывает страницу '{1}'")
    def opens(self, url):
        self.driver.get(str(url))

    @allure.step("Проверяет наличие элемента '{1}' на странице")
    def should_see_element(self, element):
        assert_that(element.element, not_none(), u'Элемент отсутствует на странице ' + self.driver.current_url)

    @allure.step("Проверяет отсутствие элемента '{1}' на странице")
    def should_not_see_element(self, element):
        assert_that(element.element, none(), u'Элемент присутствует на странице ' + self.driver.current_url)

    @allure.step("Проверяет значение '{3}' атрибута '{2}' у элемента '{1}'")
    def should_see_attribute_value(self, element, attribute, value):
        if 'Input' in str(element.__class__):
            element_ = element.input
        elif 'Textarea' in str(element.__class__):
            element_ = element.textarea
        else:
            element_ = element.element

        element_attribute = element_.get_attribute(attribute)
        assert_that(element_attribute, not_none(), u'Атрибут отсутствует у элемента')
        assert_that(element_attribute, equal_to_ignoring_case(str(value)),
                    u'Значение атрибута ' + attribute + ' не соответствует ожидаемому')

    @allure.step("Ожидает исчезновение элемента '{1}'")
    def waits_for_element_disappeared(self, element, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until_not(
                lambda s: self.driver.find_element(element.by, element.locator).is_displayed())
        except TimeoutException:
            assert_that(not TimeoutException, u'Элемент не должен присутствовать в верстке страницы '
                        + self.driver.current_url)

    @allure.step("Ожидает появление элемента '{1}'")
    def waits_for_element_displayed(self, element, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda s: self.driver.find_element(element.by, element.locator).is_displayed())
            return element
        except TimeoutException:
            assert_that(not TimeoutException, u'Элемент не отображается на странице '
                        + self.driver.current_url)

    @allure.step("Текст элемента '{1}' соответствует '{2}'")
    def should_see_element_with_text(self, element, text):
        assert_that(element.element.text, equal_to(str(text)), u'Текст не соответствует ожидаемому значению')

    @allure.step("Текст элемента '{1}' содержит '{2}'")
    def should_see_element_contains_text(self, element, text):
        assert_that(element.element.text, contains_string(str(text)), u'Текст не сожержится в ожидаемом значении')

    @allure.step("Элемент '{1}' соответствует '{2}'")
    def should_see_element_matched_to(self, element, matcher):
        assert_that(element.element.text, matcher, u'Параметры элемента не соответствует ожидаемому значению')

    @allure.step("Текст ошибки '{1}' соответствует '{2}'")
    def should_see_field_error_text(self, element, text):
        try:
            WebDriverWait(self.driver, self.element_wait).until(lambda x: element.error).is_displayed()
        except TimeoutException:
            assert_that(False, u'Поле не отмечено как содержащее ошибку')

        assert_that(element.error.text, contains_string(str(text)),
                    u'Текст ошибки не соответствует ожидаемому значению')

    @allure.step("Значение в поле '{1}' соответствует '{2}'")
    def should_see_field_value(self, input_, value):
        assert_that(input_.value, equal_to(str(value)),
                    u'Значение в поле не соответствует ожидаемому')

    @allure.step("Список '{1}' содержит '{2}' элемент(a/ов)")
    def should_see_list_size(self, list_, size):
        assert_that(len(list_.elements), is_(size), u'Список не содержит ожидаемое количество элементов')

    @allure.step("Нажимает элемент '{1}'")
    def clicks(self, element):
        try:
            WebDriverWait(self.driver, self.element_wait).until(ec.element_to_be_clickable(
                    (element.by, element.locator)))
            element.click()
        except TimeoutException:
            assert_that(element.element, not_none(), u'Невозможно нажать на элемент на странице ' +
                        self.driver.current_url)

    @allure.step("Выбирает значение '{2}' из списка '{1}'")
    def chooses_from_select(self, select, value):
        select.select.select_by_visible_text(value)

    @allure.step("Выбранный пункт списка '{1}' соответствует '{2}'")
    def should_see_selected_text(self, select, text):
        assert_that(select.select.first_selected_option.text, equal_to(str(text)),
                    u'Выбранный в списке текст не соответствует ожидаемому значению')

    @allure.step("Выбирает пункт '{2}' из списка '{2}' по названию")
    def selects_from_list_by_text(self, list_, text):
        list_.get_element_contains_text(text).element.click()

    @allure.step("Выбирает пункт '{2}' из списка '{2}' по значению атрибута")
    def selects_from_list_by_attr_value(self, list_, attr, value):
        list_.get_element_by_attribute(attr, value).element.click()

    @allure.step("Устанвливает элемент '{1}' выбранным")
    def selects_checkbox(self, checkbox):
        if not checkbox.is_checked():
            checkbox.element.click()

    @allure.step("Устанавливает элемент '{1}' не выбранным")
    def unselects_checkbox(self, checkbox):
        if checkbox.is_checked():
            checkbox.element.click()

    @allure.step("'{1}' содержит текст '{2}'")
    def should_see_text_in_list(self, list_, *text):
        sequence = list(map(lambda x: x.text, list_.elements))
        assert_that(sequence, has_item(is_in(text)), u'Текст отсутствует в списке')

    @allure.step("'{2}' присутствует в '{1}'")
    def should_matches_to_list_item(self, list_, matcher):
        """
        Проверяет, присутствует ли ожидаемое условие (matcher) в списке list_
        :param list_: список елементов
        :param matcher: ожидаемое условие, например contains_text('текст не в списке')
        """
        sequence = list(map(lambda x: x.text, list_.elements))
        assert_that(sequence, has_item(matcher), u'Список не содержит ожидаемого условия')

    @allure.step("'{2}' отсутствует в '{1}'")
    def should_not_matches_to_list_item(self, list_, matcher):
        """
        Проверяет, отсутствует ли ожидаемое условие (matcher) в списке list_
        :param list_: список елементов
        :param matcher: условие, например contains_text('текст не в списке')
        """
        sequence = list(map(lambda x: x.text, list_.elements))
        assert_that(sequence, not_(has_item(matcher)), u'Список содержит ожидаемое условие')

    @allure.step("'{2}' присутствует в каждом элементе списка '{1}'")
    def should_matches_to_every_list_item(self, list_, matcher):
        """
        Проверяет, присутствует ли ожидаемое условие (matcher) в каждом элементе списка list_
        :param list_: список елементов
        :param matcher: ожидаемое условие, например contains_text('текст не в списке')
        """
        sequence = list(map(lambda x: x.text, list_.elements))
        for item in sequence:
            assert_that(item, matcher, u'Список не содержит ожидаемого условия')

    @allure.step("'{2}' отсутствует в каждом элементе списка '{1}'")
    def should_not_matches_to_every_list_item(self, list_, matcher):
        """
        Проверяет, отсутствие ожидаемого условия (matcher) в каждом элементе списка list_
        :param list_: список елементов
        :param matcher: ожидаемое условие, например contains_text('текст не в списке')
        """
        sequence = list(map(lambda x: x.text, list_.elements))
        for item in sequence:
            assert_that(item, not_(matcher), u'Список не должен содержать ожидаемого условия')

    @allure.step("'{1}' не должен содержать текст '{2}'")
    def should_not_see_text_in_list(self, list_, text):
        assert_that(list(map(lambda x: x.text, list_.elements)), not (has_item(text)), u'Текст присутствует в списке')

    @allure.step("Проверяет доступность элемента '{1}'")
    def should_see_element_enabled(self, element):
        if element.__class__.__name__ == 'Input':
            element_ = element.input
        elif element.__class__.__name__ == 'Textarea':
            element_ = element.textarea
        else:
            element_ = element.element
        assert_that(element_.is_enabled(), is_(True), u'Элемент недоступен')

    def is_element_present(self, element):
        return bool(len(self.driver.find_elements(element.by, element.locator)))

    @allure.step("Ожидает доступность элемента '{1}'")
    def waits_for_element_enabled(self, element, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda s: self.driver.find_element(element.by, element.locator).is_enabled())
            return element
        except TimeoutException:
            assert_that(not TimeoutException, u'Элемент не доступен на странице ' + self.driver.current_url)

    @allure.step("Не должен содержать текст '{1}' на странице")
    def should_not_see_text(self, text):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        assert_that(body.text, not_(contains_string(str(text))), u'Текст присутствует на странице')

    @allure.step("Страница содержит текст '{1}'")
    def should_see_text(self, text):
        body = self.driver.find_element(By.TAG_NAME, 'body')
        assert_that(body.text, contains_string(str(text)), u'Текст отсутствует на странице')

    @allure.step("Ожидает '{1}' секунд(ы)")
    def waits_for(self, timeout=3):
        sleep(timeout)

    @allure.step("Вводит текст '{2}' в '{1}'")
    def enters_text(self, element, text):
        if element.__class__.__name__ == 'Input':
            element.input.clear()
            element.input.send_keys(text)
        elif element.__class__.__name__ == 'Textarea':
            element.textarea.clear()
            element.textarea.send_keys(text)
        else:
            element.element.clear()
            element.element.send_keys(text)

    @allure.step("Вводит текст '{2}' в '{1}'")
    def appends_text(self, element, text):
        if element.__class__.__name__ == 'Input':
            element.input.send_keys(text)
        elif element.__class__.__name__ == 'Textarea':
            element.textarea.send_keys(text)
        else:
            element.element.send_keys(text)

    @allure.step("Ожидает завершения AJAX запроса")
    def waits_for_ajax(self, timeout=5):
        try:
            WebDriverWait(self.driver, int(timeout)).until(lambda s: s.execute_script('return $.active == 0'))
        except TimeoutException:
            assert_that(not TimeoutException, u'Истекло время ожидания AJAX запроса %s секунд' % str(timeout))

    @allure.step(u"Ожидает появление диалогового окна")
    def waits_for_alert(self, timeout=5):
        try:
            WebDriverWait(self.driver, timeout).until(ec.alert_is_present())
        except TimeoutException:
            assert_that(not TimeoutException, u'Истекло время ожидания диалогового окна, %s секунд' % str(timeout))

    @allure.step(u"Подтверждает диалог")
    def accepts_alert(self):
        Alert(self.driver).accept()

    @allure.step(u"Отклоняет диалог")
    def dismiss_alert(self):
        Alert(self.driver).dismiss()

    @allure.step("Перегружает текущую страницу")
    def reloads_page(self):
        self.config.driver.refresh()

    @allure.step("Выбирает дату '{2}' в '{1}'")
    def set_calendar_date(self, calendar, date):
        """
        Устанавливает дату и время регистрации
        :param date Строковое значение даты в формате 'гггг-мм-дд'
        :return: boolean True/False в зависимости от того была установлена дата успешно или нет,
        например день недоступен
        """
        month_name = ['Январь', 'Февраль', 'Март', 'Апрель', 'Мая', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь',
                      'Ноябрь', 'Декабрь']
        d = datetime.strptime(date, '%Y-%m-%d')

        js = "$('.xdsoft_scroller_box div').attr('style','margin-top: 0px;');" \
             "$('.xdsoft_scroller_box').scrollTop(0);" \
             "$('.xdsoft_scroller_box').scrollTop($('[data-value='+%s+']').position().top);"

        if calendar.year.text != str(d.year):
            calendar.year.click()
            sleep(1)
            self.driver.execute_script(js % d.year)
            calendar.get_year(d.year).click()

        if calendar.month.text.lower() != month_name[d.month - 1].lower():
            calendar.month.click()
            sleep(1)
            self.driver.execute_script(js % str(d.month - 1))
            calendar.get_month(d.month).click()

        day = calendar.get_day(d.day)

        if calendar.is_day_disabled(d.day):
            return False
        day.click()
        return True

    @allure.step("Выбирает время '{2}' в '{1}'")
    def set_calendar_time(self, calendar, time):
        """
        Устанавливает время в элементе Calendar
        :param calendar Элемент Calendar
        :param time Строковое значение времени в формате 'чч:мм'.
                    Если задано, то выбирается первое значение.
        :return: Количество элементов в списке время Calendar.time_list
        """
        js_time_top = "$('.xdsoft_time_box.xdsoft_scroller_box div').attr('style','margin-top: 0px;');" \
                      "$('.xdsoft_time_box.xdsoft_scroller_box').scrollTop(0);"
        js_time = js_time_top + "$('.xdsoft_time_box.xdsoft_scroller_box').scrollTop($('[data-hour=%s]')" \
                                ".position().top);"

        if len(calendar.time_list) != 0:
            if not (time == "" or time is None):
                t = datetime.strptime(time, '%H:%M')
                self.driver.execute_script(js_time % t.hour)
                calendar.get_time(time).click()
            else:
                self.driver.execute_script(js_time_top)
                calendar.time_list[0].click()

        return len(calendar.time_list)
