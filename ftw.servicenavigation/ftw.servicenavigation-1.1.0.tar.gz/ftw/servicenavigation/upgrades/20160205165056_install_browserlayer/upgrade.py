from ftw.upgrade import UpgradeStep


class InstallBrowserlayer(UpgradeStep):
    """Install browserlayer.
    """

    def __call__(self):
        self.install_upgrade_profile()
