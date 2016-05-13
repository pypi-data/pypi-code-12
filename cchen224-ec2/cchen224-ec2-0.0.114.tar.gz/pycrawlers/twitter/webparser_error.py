def is_page_exists(soup):
    try:
        content = soup.find('div', class_='body-content').h1.text.strip()
        if content == 'Sorry, that page doesnt exist!':
            return False
    except AttributeError:
        return True


def is_content_not_protected(soup):
    try:
        content = soup.find('div', class_='message-inside').span.text.strip()
        if content == 'Sorry, you are not authorized to see this status.':
            return False
        else: return True
    except AttributeError:
        return True


def is_account_not_suspended(soup):
    try:
        content = soup.find('div', class_='flex-module error-page clearfix').h1.text.strip()
        if content == 'Account suspended':
            return False
    except AttributeError:
        return True
