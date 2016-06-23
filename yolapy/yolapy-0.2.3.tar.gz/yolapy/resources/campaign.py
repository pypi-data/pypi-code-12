class CampaignResourceMixin(object):
    """Methods for managing Campaign resources."""

    def list_campaigns(self, site_id, **options):
        """Return list of campaigns for a site."""
        return self.get(self._campaign_path(site_id), params=options).json()

    def get_campaign(self, site_id, campaign_id):
        """Return details for a particular campaign.

        >>> campaign = yola.get_campaign('site_id', 'campaign_id')
        >>> campaign['name']
        'My Campaign'
        """
        return self.get(self._campaign_path(site_id, campaign_id)).json()

    def delete_campaign(self, site_id, campaign_id):
        """Delete a campaign."""
        self.delete(self._campaign_path(site_id, campaign_id))

    def subscribe_to_campaign(self, site_id, campaign_id):
        """Subscribe to a campaign.

        >>> params = {...}
        >>> yola.subscribe_to_campaign('site_id', 'campaign_id', params)

        See https://wl.qa.yola.net/sites/SITE_ID/campaigns/ for expected
        params.
        """
        self.post(self._campaign_path(site_id, campaign_id, 'subscribe'))

    def cancel_campaign_subscription(self, site_id, campaign_id):
        """Cancel a campaign subscription."""
        self.post(
            self._campaign_path(site_id, campaign_id, 'cancel_subscription'))

    def _campaign_path(self, site_id, *parts):
        path = '/'.join(['sites', site_id, 'campaigns'] + list(parts))
        return '/%s/' % path
