from exec_pypeline.action import Action


class PassAction(Action):
    def forward(self, *args, **kwargs):
        pass

    def backward(self, *args, **kwargs):
        pass
