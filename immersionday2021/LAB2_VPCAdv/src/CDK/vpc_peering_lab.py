import os.path
from aws_cdk import core
from aws_cdk.aws_s3_assets import Asset
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_s3 as s3

dirname = os.path.dirname(".")

class VpcPeeringLabStack(core.Stack):

    outputs = [] 
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #Get context
        #AWS_region=self.node.try_get_context("region")
        #instance_type=self.node.try_get_context("instance_type")


        #VPC - We only need 1 AZ for this benchmark purpose
        vpc1 = ec2.Vpc(
            self, "VPC-10.1.0.0/16",
            cidr='10.1.0.0/16',
            max_azs=1,
            #nat_gateways=0,
            #subnet_configuration=[ec2.SubnetConfiguration(name="VPC-A-Private", subnet_type=ec2.SubnetType.PRIVATE, cidr_mask=24)]

        )
        core.CfnOutput(
             self, "VPC1",
             value=vpc1.vpc_id
         ) 

        vpc2 = ec2.Vpc(
            self, "VPC-10.2.0.0/16",
            cidr='10.2.0.0/16',
            max_azs=1,
            #nat_gateways=0,
            #subnet_configuration=[ec2.SubnetConfiguration(name="VPC-B-Private", subnet_type=ec2.SubnetType.PRIVATE, cidr_mask=24)]
        )
        core.CfnOutput(
             self, "VPC2",
             value=vpc2.vpc_id
         )

        # Instance Role and SSM Managed Policy
        role = iam.Role(self, "InstanceSSM", assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"))
        role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"))
        
        #Security groups

        sg1 = ec2.SecurityGroup(
            self, f"SG1--VPCPeeringLab",
            vpc=vpc1,
            allow_all_outbound=False
        )
        sg2 = ec2.SecurityGroup(
            self, f"SG2--VPCPeeringLab",
            vpc=vpc2,
            allow_all_outbound=False
        )

        #Ping for connectivity test in the Lab
        sg1.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_icmp()
        )
        #no restriction for outgoing traffic
        sg1.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_tcp()
        )
        sg1.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_icmp()
        ) 
        #Ping for connectivity test in the Lab
        sg2.add_ingress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_icmp()
        )
        #no restriction for outgoing traffic
        sg2.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_tcp()
        )
        sg2.add_egress_rule(
            ec2.Peer.any_ipv4(),
            ec2.Port.all_icmp()
        )
        # AMI
        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )
        
        # Instances
        instanceA = ec2.Instance(self, "Instance A",
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=amzn_linux,
            vpc = vpc1,
            role = role,
            security_group=sg1
        )
        core.CfnOutput(
             self, "InstanceA",
             value=instanceA.instance_id
        ) 

        # Instances
        instanceB = ec2.Instance(self, "Instance B",
            instance_type=ec2.InstanceType("t3.nano"),
            machine_image=amzn_linux,
            vpc = vpc2,
            role = role,
            security_group=sg2
        )
        core.CfnOutput(
             self, "InstanceB",
             value=instanceB.instance_id
        )

         
