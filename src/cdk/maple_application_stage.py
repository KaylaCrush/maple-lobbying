from aws_cdk import Stage, CfnOutput
from .shared_stack import SharedStack
from .lobbying_stack import LobbyingStack


class MapleApplication(Stage):
    def __init__(self, scope, id, **kwargs):
        super().__init__(scope, id, **kwargs)

        shared = SharedStack(self, "SharedStack")
        LobbyingStack(self, "LobbyingStack", cluster=shared.cluster, db=shared.db)
