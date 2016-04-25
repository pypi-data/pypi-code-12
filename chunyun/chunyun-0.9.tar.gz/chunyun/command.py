from abc import ABCMeta, abstractclassmethod
import os


class Command(metaclass=ABCMeta):
    """
    抽象命令类
    """

    def __init__(self, args):
        """
        初始化命令类，并接收参数
        :param args: 命令参数
        :return: None
        """
        self.args = args

    @abstractclassmethod
    def run(self):
        """
        执行命令
        :return: None
        """
        pass


