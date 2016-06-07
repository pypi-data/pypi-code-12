from rancon.common import CommonBase


class SourceBase(CommonBase):

    required_opts = ()
    additional_opts = ()

    def get_services(self, **kwargs):
        pass
