from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models
from stream_django.activity import Activity


class ReviewWithActivity(Activity):
    """ Enable GetStream.io support.
    See https://github.com/GetStream/stream-django for more information
    """
    @property
    def activity_object_attr(self):
        return self


class ReviewNoActivity(object):
    pass

if getattr(settings, 'REVIEW_STREAM_ENABLED', False):
    # Enable get_stream if enabled in settings
    BaseReview = ReviewWithActivity
else:
    BaseReview = ReviewNoActivity


class Review(models.Model, BaseReview):
    user = models.ForeignKey(
                             getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
                             on_delete=models.CASCADE)  # The user who created the review
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    review = models.TextField(help_text="What do you think? Try to keep it concise but not too short. "
                                        "We recommend a minimum of 500 characters.")
    RATINGS = (
        (1, '1 Star'),
        (2, '2 Star'),
        (3, '3 Star'),
        (4, '4 Star'),
        (5, '5 Star')
    )
    rating = models.IntegerField(choices=getattr(settings, 'REVIEW_RATING_CHOICES', RATINGS))
    title = models.CharField(max_length=100)


    # Generic contentype
    # See https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/
    review_object_id = models.PositiveIntegerField() # The id of the related object
    review_object_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE) # The content type of the related object
    review_object = GenericForeignKey('review_object_content_type', 'review_object_id') # The related object

    @property
    def activity_object_attr(self):
        return self

    def get_absolute_url(self):
        return reverse('Reviewable:review-detail', kwargs={'pk': self.pk})


class Reviewable(object):
    """Mixin that makes a model reviewable.

    Contains methods to deal with deletions of an object and therefore the deletions of its reviews.
    Contains methods to get a models reviews.
    """

    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)

    @property
    def reviews(self):
        """Return the reviews for the object

        Reverse generic relation not working so had to do manually.
        https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/#reverse-generic-relations
        """
        # TODO: Fix this so uses reverse generic relation
        return Review.objects.filter(review_object_content_type=self.content_type, review_object_id=self.id)

    def review(self, user, review, title, rating):
        """Create a review for the object

        keyword arguments:
        user - the user instance who is doing the reviewing
        review - A string of the review to be left
        rating - The star rating the user gave the object. 1-5
        """
        review = Review(user=user, title=title, review=review, rating=rating, review_object=self)
        review.save()
        return review

    def delete_reviews(sender, instance, **kwargs):
        """Deletes the object's reviews

        This is good to use as a receiver for a post_delete signal.
        To implement create a post_delete signal for the reviewable model that uses this as its listener

        e.g post_delete.connect(Object.delete_reviews, sender=Object)
        """
        instance.reviews.delete()

    @property
    def review_count(self):
        """Returns the total number of reviews of the object"""
        return self.reviews.count()

    @property
    def average_rating(self):
        """Gets the average score of the object's rating"""
        reviews = self.reviews
        if not reviews:
            return 0
        count = self.review_count
        total = 0
        for review in reviews:
            rating = review.rating
            total += rating
        if total > 0:
            return total/count
        return 0
