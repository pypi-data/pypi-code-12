"""Classes module. These are objects **goldfinchsong** uses to keep state and perform business logic."""
from datetime import datetime, timezone
from . import utils


class Manager:
    """
    Manages tweet posting through twitter API.

    Attributes:
        api: A tweepy API instance.
        db (TinyDB): A database (TinyDB) instance for storing tweet image history.
        content (tuple): The class expects a tuple with a file name string
            and status text string.
    """
    def __init__(self, credentials=None, db=None, image_directory=None, text_conversions=None):
        self.db = db
        self.content = utils.load_content(db, image_directory, text_conversions)
        if credentials:
            self.api = utils.access_api(credentials)

    def post_tweet(self):
        """
        Attempts a tweet status post with image.

        After a successful tweet update call, the method saves a dict
        to the Manager's `db` property. The format of the dict saved is::

            {
                'image': 'just-the-image-name-not-full-path.jpg',
                'delivered_on': '2016-05-04T17:06:54.987654+00:00'
            }

        The image name is the file name of the image alone, not the path to
        the image.  The delivery timestamp is an ISO 8601 time string;
        Python's built-in libraries omit the allowed 'Z' is in favor
        of just a ``+`` or ``-`` marker.  The **goldfinchsong** timestamps
        use UTC, so the increment will be ``00:00`` as in the above example.

        Returns:
            tuple: A content tuple with the full image path, status text,
                and image file name.
        Raises:
            Exception: Raises exception if content property is ``None``.
        """
        if self.content is not None:
            self.api.update_with_media(self.content[0], self.content[1])
            delivery_timestamp = datetime.now(tz=timezone.utc).isoformat()
            tweet = {'image': self.content[2], 'delivered_on': delivery_timestamp}
            self.db.insert(tweet)
            return self.content
        else:
            raise Exception("Can't post a tweet. No content available. Check image directory.")
