#!/usr/bin/python
# vim:fileencoding=utf-8
# Copyright (c) GlobalLogic.

__doc__ = "Module with the helper class for tests"
__module__ = "glsdp"
__version__ = "0.2.1"
__author__ = "Damian Giebas"
__all__ = ["GLHelper"]

class GLHelper(object):
    """Simple helper class
    Static variable:
        CHROME - Chrome webdriver method name
        EDGE - Edge webdriver method name
        FIREFOX - Firefox webdriver method name
        INTERNETEXPLORER - IE webdriver method name
        OPERA - Opera webdriver method name
        PHANTOMJS - PhantomJS webdriver method name
    """

    CHROME = "Chrome"
    EDGE = "Edge"
    FIREFOX = "Firefox"
    INTERNETEXPLORER = "Ie"
    OPERA = "Opera"
    PHANTOMJS = "PhantomJS"

    @staticmethod
    def getTopMenuTitles():
        """Method return tuple of top menu titles"""

        return (
            "Technologies",
            "Industries",
            "Services",
            "About Us",
            "Career",
            "News",
            "Contact"
        )

    @staticmethod
    def getSubMenuTitles(menuTitle):
        """Method return tuple of submenu titles for menu given as parameter"""

        submenuTitles = {
            "Technologies" : (
                "Embedded Systems",
                "Software Solutions"
            ),
            "Industries" : (
                "Automotive",
                "Maritime",
                "Semiconductors",
                "IoT & M2M",
                "Industrial Automation",
                "Telecommunication",
                "Security",
                "Web / Mobile / Enterprise Solutions"
            ),
            "Services" : (
                "Portfolio & Cooperation Models",
                "Quality Management & Assurance",
                "Processes Frameworks",
                "Information Security"
            ) ,
            "About Us" : (
                "Company Description",
                "Locations & Markets",
                "Partners & Associations ",
                "Prizes & Awards",
                "Management Board",
                "Why choose REC Global"
            ),
            "Career" : (
                "Job Offers",
                "Recruitment Steps",
                "HR Contact"
            ),
            "News" : tuple(),
            "Contact" : tuple()
        }

        menuTitle = str(menuTitle)
        return submenuTitles[menuTitle] if menuTitle in submenuTitles else None
