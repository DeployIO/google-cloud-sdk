# Copyright 2015 Google Inc. All Rights Reserved.
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
"""gcloud dns operations describe command."""

from googlecloudsdk.api_lib.dns import util
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dns import flags
from googlecloudsdk.core import properties


class Describe(base.DescribeCommand):
  """Describe an operation.

  This command displays the details of a single managed-zone operation.

  ## EXAMPLES

  To describe a managed-zone operation:

    $ {command} 1234 --zone my_zone
  """

  @staticmethod
  def Args(parser):
    flags.GetZoneArg('Name of zone to get operations from.').AddToParser(parser)
    parser.add_argument('operation_id', metavar='OPERATION_ID')

  def Run(self, args):
    dns_client = apis.GetClientInstance('dns', 'v1beta2')

    zone_ref = util.GetRegistry('v1beta2').Parse(
        args.zone,
        params={
            'project': properties.VALUES.core.project.GetOrFail,
        },
        collection='dns.managedZones')

    return dns_client.managedZoneOperations.Get(
        dns_client.MESSAGES_MODULE.DnsManagedZoneOperationsGetRequest(
            operation=args.operation_id,
            managedZone=zone_ref.Name(),
            project=zone_ref.project))
