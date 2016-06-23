from yolapy.services import Yola


class User(object):

    """Yola User - a service model that uses the yola client for persistence.

    Example use:
    ```
    from yolapy.models import User as YolaUser

    yola_user = YolaUser(
        email='test@example.com',
        name='Jane',
        surname='Doe',
        partner_id='WL_PARTNER',
        preferences={'locale': 'en'})

    yola_user.save()
    ```
    """

    def __init__(self, active=False, deleted=None, email=None, id=None,
                 name=None, partner_id=None, preferences=None,
                 signup_date=None, surname=None):
        """Construct a Yola User.

        The data in a User instance does not persist until it has been saved.


        :param active: Bool, toggled ``False`` when user is deactivated
        :param deleted: Timestamp, date the user was deleted
        :param email: Str, user's email address
        :param id: Str, user's 32 character ID
        :param name: Str, user's first name
        :param partner_id: Str, yola partner responsible the user
        :param preferences: Dict, user's preferences
        :param signup_date: Timestamp, date the user signed up
        :param surname: Str, user's second name

        :return: :class:`User <User>` object
        :rtype: yolapy.users.models.User

        """
        self.client = Yola()

        self.partner_id = partner_id or self.client.username
        self.active = active
        self.deleted = deleted
        self.email = email
        self.id = id
        self.name = name
        self.preferences = preferences or {}
        self.signup_date = signup_date
        self.surname = surname

    @classmethod
    def get(cls, user_id):
        """Get a user from the Yola API."""
        user_attributes = Yola().get_user(user_id)
        user_attributes['signup_date'] = user_attributes.pop('signupDate')
        return cls(**user_attributes)

    def _save_create(self):
        user = self.client.create_user(
            email=self.email,
            name=self.name,
            partner_id=self.partner_id,
            preferences=self.preferences,
            surname=self.surname)
        self.update(**user)

    def _save_update(self):
        raise NotImplementedError()

    def save(self):
        """POST the user data back to the service."""
        if self.id:
            self._save_update()
        else:
            self._save_create()

    def update(self, **attributes):
        """Update all keyword arguments to update instance attributes."""
        for attr, val in attributes.items():
            setattr(self, attr, val)
