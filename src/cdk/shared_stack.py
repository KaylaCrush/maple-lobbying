from aws_cdk import CfnOutput, Duration, RemovalPolicy, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_logs as logs
from constructs import Construct


class SharedStack(Stack):
    """Manages common resources used by all developers."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # A virtual private network that allows everything in Maple's cloud to
        # talk to each other.
        self.vpc = ec2.Vpc(self, "VPC", vpc_name="maple-net")

        self.ssh_key_pair = ec2.CfnKeyPair(
            self, "SshKeyPair", key_name="maple-cluster-ssh"
        )

        # An AWS RDS Postgres instance. This instance contains all maple-related
        # production databases.
        self._make_rds_instance()

        # Create a "cluster" to run the scraper and act as a bastion host for
        # accessing the VPC.
        self._make_ecs_ec2_cluster()

    def _make_ecs_ec2_cluster(self):
        self.cluster = ecs.Cluster(self, "Cluster", vpc=self.vpc)
        self.cluster.add_capacity(
            "BaseCapacity",
            instance_type=ec2.InstanceType("t3.nano"),
            desired_capacity=1,
            key_name=self.ssh_key_pair.key_name,
        )

    def _make_rds_instance(self):
        self.db_admin = rds.Credentials.from_generated_secret("mapleadmin")
        self.db = rds.DatabaseInstance(
            self,
            "PostgresInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_14_6
            ),
            # db.t3.micro, 2cpu, 1g ram, $13/mo
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO
            ),
            database_name="maple",
            # start with 10g storage, expand up to 200g
            allocated_storage=10,
            max_allocated_storage=200,
            storage_type=rds.StorageType.GP2,
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            publicly_accessible=True,
            auto_minor_version_upgrade=True,
            enable_performance_insights=True,
            backup_retention=Duration.days(30),
            cloudwatch_logs_exports=["postgresql"],
            cloudwatch_logs_retention=logs.RetentionDays.TWO_MONTHS,
            removal_policy=RemovalPolicy.RETAIN,
            credentials=self.db_admin,
        )

        self.db.connections.allow_default_port_from_any_ipv4("Postgres Endpoint")
