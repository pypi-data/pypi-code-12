from datetime import datetime


def load_data(apps, schema_editor):
    HolidayType = apps.get_model("acp_calendar", "HolidayType")
    for holiday_type in get_holiday_type_list():
        HolidayType.objects.create(**holiday_type)

    ACPHoliday = apps.get_model("acp_calendar", "ACPHoliday")
    for holiday_data in get_holidays_list():
        holiday_type = HolidayType.objects.get(name=holiday_data['holiday_type'])
        holiday_data['holiday_type'] = holiday_type
        ACPHoliday.objects.create(**holiday_data)


def get_holiday_type_list():
    holiday_types = [{'name': 'Año Nuevo'},
                     {'name': 'Día de los Mártires'},
                     {'name': 'Martes Carnaval'},
                     {'name': 'Viernes Santo'},
                     {'name': 'Día del Trabajador'},
                     {'name': 'Toma de Posesión Presidencial'},
                     {'name': 'Día de la Separación de Panamá de Colombia'},
                     {'name': 'Día de Colón'},
                     {'name': 'Primer Grito de Independencia'},
                     {'name': 'Independencia de Panamá de España'},
                     {'name': 'Día de la Madre'},
                     {'name': 'Navidad'},
                     ]
    return holiday_types


def get_holidays_list():
    holidays_16 = [{'date': datetime.strptime('2016-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2016-01-08', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2016-02-09', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2016-03-25', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2016-05-02', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2016-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2016-11-04', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2016-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2016-11-28', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2016-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2016-12-26', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    holidays_15 = [{'date': datetime.strptime('2015-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2015-01-09', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2015-02-17', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2015-04-03', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2015-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2015-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2015-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2015-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2015-11-27', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2015-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2015-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

# Contains 12 entries as opposed to the standard 11:
    holidays_14 = [{'date': datetime.strptime('2014-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2014-01-09', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2014-03-04', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2014-04-18', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2014-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2014-07-01', '%Y-%m-%d'), 'holiday_type': 'Toma de Posesión Presidencial'},
                   {'date': datetime.strptime('2014-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2014-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2014-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2014-12-01', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2014-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2014-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    holidays_13 = [{'date': datetime.strptime('2013-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2013-01-07', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2013-02-12', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2013-03-29', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2013-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2013-11-04', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2013-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2013-11-11', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2013-12-02', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2013-12-09', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2013-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    holidays_12 = [{'date': datetime.strptime('2012-01-02', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2012-01-09', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2012-02-21', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2012-03-06', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2012-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2012-11-02', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2012-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2012-11-09', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2012-11-26', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2012-12-07', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2012-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

# Contains 10 entries as opposed to the standard 11:
    holidays_11 = [{'date': datetime.strptime('2011-01-10', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2011-03-08', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2011-04-22', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2011-05-02', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2011-11-02', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2011-11-04', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2011-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2011-11-28', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2011-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2011-12-26', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

# Contains 12 entries as opposed to the standard 11:
    holidays_10 = [{'date': datetime.strptime('2010-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2010-01-08', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2010-02-16', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2010-04-02', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2010-04-30', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2010-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2010-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2010-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2010-11-27', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2010-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2010-12-24', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   {'date': datetime.strptime('2010-12-31', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   ]

    holidays_9 = [{'date': datetime.strptime('2009-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2009-01-12', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2009-02-24', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2009-04-10', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2009-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2009-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2009-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2009-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2009-11-29', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2009-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2009-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    holidays_8 = [{'date': datetime.strptime('2008-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2008-01-07', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2008-02-05', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2008-03-21', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2008-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2008-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2008-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2008-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2008-12-01', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2008-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2008-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    holidays_7 = [{'date': datetime.strptime('2007-01-01', '%Y-%m-%d'), 'holiday_type': 'Año Nuevo'},
                   {'date': datetime.strptime('2007-01-09', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2007-02-20', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2007-04-06', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2007-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2007-11-02', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2007-11-05', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2007-11-09', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2007-11-28', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2007-12-07', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2007-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    # Contains 10 entries as opposed to the standard 11:
    holidays_6 = [{'date': datetime.strptime('2006-01-09', '%Y-%m-%d'), 'holiday_type': 'Día de los Mártires'},
                   {'date': datetime.strptime('2006-02-28', '%Y-%m-%d'), 'holiday_type': 'Martes Carnaval'},
                   {'date': datetime.strptime('2006-04-14', '%Y-%m-%d'), 'holiday_type': 'Viernes Santo'},
                   {'date': datetime.strptime('2006-05-01', '%Y-%m-%d'), 'holiday_type': 'Día del Trabajador'},
                   {'date': datetime.strptime('2006-11-03', '%Y-%m-%d'),
                    'holiday_type': 'Día de la Separación de Panamá de Colombia'},
                   {'date': datetime.strptime('2006-11-06', '%Y-%m-%d'), 'holiday_type': 'Día de Colón'},
                   {'date': datetime.strptime('2006-11-10', '%Y-%m-%d'),
                    'holiday_type': 'Primer Grito de Independencia'},
                   {'date': datetime.strptime('2006-11-28', '%Y-%m-%d'),
                    'holiday_type': 'Independencia de Panamá de España'},
                   {'date': datetime.strptime('2006-12-08', '%Y-%m-%d'), 'holiday_type': 'Día de la Madre'},
                   {'date': datetime.strptime('2006-12-25', '%Y-%m-%d'), 'holiday_type': 'Navidad'},
                   ]

    return (holidays_6 + holidays_7 + holidays_8 + holidays_9 + holidays_10 + holidays_11 + holidays_12 + holidays_13 +
            holidays_14 + holidays_15 + holidays_16)



