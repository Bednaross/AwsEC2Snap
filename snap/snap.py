import boto3
import click

session = boto3.Session(profile_name='Snap')
ec2 = session.resource('ec2')


def filter_instances(group):
    instances=[]
    if group:
        filters = [{'Name':'tag:Group', 'Values':[group]}]
        instances = ec2.instances.filter(Filters = filters)
    else: instances = ec2.instances.all()

    return instances


@click.group()
def cli():
    """ Snap manages snapshots"""


@cli.group('snapshots')
def snapshots():
    """ Commands for snapshots"""


@snapshots.command('list')
@click.option('--group', default=None,
    help="Only snapshots for given group (instance tag Group:<name>)")
def get_snapshots_info(group):
    "This function lists all snapshots for volumes"
    instances= filter_instances(group)

    for i in instances:
            for v in i.volumes.all():
                for s in v.snapshots.all():
                    print("; ".join((
                        s.id,
                        v.id,
                        i.id,
                        s.state,
                        s.progress,
                        s.start_time.strftime("%c")
                    )))

    return


@cli.group('volumes')
def volumes():
    """ Commands for volumes"""


@volumes.command('list')
@click.option('--group', default=None,
    help="Only volumes for given group (instance tag Group:<name>)")
def get_volumes_info(group):
    "This function lists all EC2 volumes"
    instances= filter_instances(group)

    for i in instances:
        for v in i.volumes.all():
            print('; '.join((
                v.id,
                i.id,
                v.state,
    			str(v.size) + "GIB",
                v.encrypted and "Encrypted" or "Not Encrypted")))

    return

@cli.group('instances')
def instances():
	""" Commands for instances"""


@instances.command('snapshot',
    help="Create snapshots of all valumes")
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def create_snapshots(group):
    "Create snapshots of all valumes"

    instances= filter_instances(group)

    for i in instances:
        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by AwsEC2Snap")

    return


@instances.command('list')
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def get_instances_info(group):
    "This function lists all EC2"
    instances= filter_instances(group)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or [] }
        print('; '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
			tags.get('Group', '<no group>'))))

    return


@instances.command('stop')
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def stop_instances(group):
    "Stop EC2 instances"
    instances= filter_instances(group)

    for i in instances:
        print("Stopping...{0}".format(i.id))
        i.stop()

    return


@instances.command('start')
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def stop_instances(group):
    "Start EC2 instances"
    instances= filter_instances(group)

    for i in instances:
        print("Starting...{0}".format(i.id))
        i.start()

    return


if __name__ == '__main__':
    cli()
