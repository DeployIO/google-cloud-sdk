# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for setting minimum CPU platform for virtual machine instances."""

from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute.operations import poller
from googlecloudsdk.api_lib.util import waiter
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.compute import flags
from googlecloudsdk.command_lib.compute.instances import flags as instance_flags
from googlecloudsdk.core import log


@base.ReleaseTracks(base.ReleaseTrack.ALPHA)
class SetMinCpuPlatform(base.UpdateCommand):
  # pylint: disable=line-too-long
  """Set minimum CPU platform for Google Compute Engine virtual machine instance."""

  @staticmethod
  def Args(parser):
    instance_flags.INSTANCE_ARG.AddArgument(parser)
    instance_flags.AddMinCpuPlatformArgs(parser, required=True)
    base.ASYNC_FLAG.AddToParser(parser)

  def Collection(self):
    return 'compute.instances'

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    instance_ref = instance_flags.INSTANCE_ARG.ResolveAsResource(
        args,
        holder.resources,
        scope_lister=flags.GetDefaultScopeLister(client))

    embedded_request = client.messages.InstancesSetMinCpuPlatformRequest(
        minCpuPlatform=args.min_cpu_platform or None)
    request = client.messages.ComputeInstancesSetMinCpuPlatformRequest(
        instance=instance_ref.instance,
        project=instance_ref.project,
        instancesSetMinCpuPlatformRequest=embedded_request,
        zone=instance_ref.zone)

    operation = client.apitools_client.instances.SetMinCpuPlatform(request)

    operation_ref = holder.resources.Parse(
        operation.selfLink, collection='compute.zoneOperations')

    if args.async:
      log.UpdatedResource(
          operation_ref,
          kind='gce instance [{0}]'.format(instance_ref.Name()),
          async=True,
          details='Use [gcloud compute operations describe] command '
                  'to check the status of this operation.'
      )
      return operation

    operation_poller = poller.Poller(client.apitools_client.instances)
    return waiter.WaitFor(
        operation_poller, operation_ref,
        'Changing minimum CPU platform of instance [{0}]'.format(
            instance_ref.Name()))


SetMinCpuPlatform.detailed_help = {
    'brief': ('Set minimum CPU platform for Google Compute Engine virtual '
              'machines'),
    'DESCRIPTION':
        """\
        `{command}` changes the minimum CPU platform of a virtual
        machine with the *TERMINATED* status (a virtual machine  instance that
        has been stopped).

        For example if `example-instance` virtual machine currently has the
        *TERMINATED* status running:

          $ {command} example-instance --zone us-central1-a\
        --min-cpu-platform "Intel Broadwell"

        will set the minimum CPU platform to `Intel Broadwell`. When
        you start `example-instance` later it will be provisioned using at
        least `Intel Broadwell` CPU platform.

        To get a list of available CPU platforms in us-central1-a zone, run:

          $ gcloud alpha compute zones describe us-central1-a\
        --format="value(availableCpuPlatforms)"
        """,
}
