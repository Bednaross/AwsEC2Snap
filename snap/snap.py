import boto3
import click
import botocore

#start session first
session = boto3.Session(profile_name='Snap')
ec2 = session.resource('ec2')


def filter_instances(group):
    instances = []
    #look for instances with a group tag
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
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume")
def get_snapshots_info(group, list_all):
    "This function lists all snapshots for volumes"
    instances= filter_instances(group)

    #collect basic info about snapshots
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
                    #take only last snapshots
                    if s.state == 'completed' and not list_all: break
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
    #collect basic info about vol

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
        # before taking snapshots stop instance first
        print("Stopping {0}...".format(i.id))

        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description="Created by AwsEC2Snap")

        #start instance
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()

    return


@instances.command('list')
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def get_instances_info(group):
    "This function lists all EC2"
    instances= filter_instances(group)

    #collect basic info about instances

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
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Unable to stop instance {0} ".format(i.id) + str(e))

    return


@instances.command('start')
@click.option('--group', default=None,
    help="Only EC2 for given group (instance tag Group:<name>)")
def stop_instances(group):
    "Start EC2 instances"
    instances= filter_instances(group)

    for i in instances:
        print("Starting...{0}".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Unable to start instance {0}".format(i.id) + str(e))

    return


if __name__ == '__main__':
    cli()
