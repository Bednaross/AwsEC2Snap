import boto3
import click

session = boto3.Session(profile_name='Snap')
ec2 = session.resource('ec2')


@click.command()
def get_instances_info():
    "This function lists all EC2"
    for i in ec2.instances.all():
        print('; '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'])))

    return


if __name__ == '__main__':
    get_instances_info()
