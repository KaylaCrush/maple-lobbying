from aws_cdk import (
    IgnoreMode,
    Stack,
    StackProps,
    aws_lambda as _lambda,
    Duration,
    CfnOutput,
    aws_iam as iam,
    aws_s3 as s3,
    aws_rds as rds,
    aws_ecs as ecs,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
import os


class LobbyingStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        cluster: ecs.Cluster,
        db: rds.DatabaseInstance,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.db = db
        self.cluster = cluster
        self.define_scraper_task()
        self.schedule_scraper_task()

    def schedule_scraper_task(self):
        events.Rule(
            self,
            "ScraperRule",
            schedule=events.Schedule.expression("rate(6 months)"),
            targets=[
                targets.EcsTask(cluster=self.cluster, task_definition=self.scraper_task)
            ],
        )

    def define_scraper_task(self):
        self.scraper_task = ecs.Ec2TaskDefinition(self, "ScraperTask")
        self.scraper_task.add_container(
            "Scraper",
            image=ecs.AssetImage(
                ".",
                file="Dockerfile",
                ignore_mode=IgnoreMode.DOCKER,
            ),
            memory_reservation_mib=16,
            command=["poetry run python main.py -a -v"],
        )
