# coding=utf-8
from krtech.elements.list import List
from selenium.webdriver.common.by import By

from krtech.elements.base_element import BaseElement


class Calendar(BaseElement):

    @property
    def previous(self):
        return self.element.find_element(By.XPATH, ".//button[@class='xdsoft_prev']")

    @property
    def next(self):
        return self.element.find_element(By.XPATH, ".//button[@class='xdsoft_next']")

    @property
    def today(self):
        return self.element.find_element(By.XPATH, ".//button[@class='xdsoft_today_button']")

    @property
    def year(self):
        return self.element.find_element(By.XPATH, ".//div[@class='xdsoft_label xdsoft_year']/span")

    @property
    def year_list(self):
        return self.element.find_elements(By.XPATH, ".//div[contains(@class,'yearselect')]/div[1]/div")

    def get_year(self, year):
        """
        Выбирает год из открытого списка в календаре
        :param year: числовое представление года, например 2001
        :return: WebElement год
        """
        for e in self.year_list:
            if year.__class__.__name__ == 'str':
                year = int(year)
            if year == int(e.get_attribute('data-value')):
                return e
        raise Exception(u"Год '" + str(year) + "' не найден в календаре")

    @property
    def month(self):
        return self.element.find_element(By.XPATH, ".//div[@class='xdsoft_label xdsoft_month']/span")

    @property
    def month_list(self):
        return self.element.find_elements(By.XPATH, ".//div[contains(@class,'monthselect')]/div[1]/div")

    def get_month(self, month):
        """
        Выбирает месяц из открытого списка в календаре
        :param month: числовое или строковое наименование месяца, например 7 или "июль"
        :return: WebElement месяц
        """
        for e in self.month_list:
            if month.__class__.__name__ == 'int':
                if int(month) == (int(e.get_attribute('data-value')) + 1):
                    return e
            else:
                if month.lower() == e.text.lower():
                    return e
        raise Exception(u"Месяц '" + str(month) + "' не найден в календаре")

    @property
    def current_day(self):
        return self.element.find_element(By.XPATH, ".//td[contains(@class,'day') and contains(@class,'current')]")

    @property
    def day_list(self):
        return self.element.find_elements(By.XPATH, ".//td[contains(@class,'day') and not(contains(@class,'other'))]")

    def get_day(self, day):
        """
        Выбирает день из открытого списка в календаре
        :param day: числовое или строковое представление дня, например 24 или "24"
        :return: WebElement день
        """
        if len(self.day_list) != 0:
            for e in self.day_list:
                if int(day) == (int(e.text)):
                    return e
        else:
            raise Exception(u"Список дней в календаре пуст")
        raise Exception(u"День '" + str(day) + "' не найден в календаре")

    def is_day_disabled(self, day):
        return 'disabled' in self.get_day(day).get_attribute('class')

    @property
    def top(self):
        return self.element.find_element(By.XPATH, ".//div[@class='xdsoft_timepicker active']/button[1]")

    @property
    def bottom(self):
        return self.element.find_element(By.XPATH, ".//div[@class='xdsoft_timepicker active']/button[2]")

    @property
    def time_list(self):
        return self.element.find_elements(By.XPATH, ".//div[contains(@class,'time_v')]/div")

    def get_time(self, time):
        for e in self.time_list:
            if time == e.text:
                return e
        raise Exception(u"Время '" + time + "' не найдено в календаре")
