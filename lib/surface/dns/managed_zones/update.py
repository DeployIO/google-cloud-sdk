# -*- coding: utf-8 -*- #
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
"""gcloud dns managed-zone update command."""

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from googlecloudsdk.api_lib.dns import managed_zones
from googlecloudsdk.api_lib.util import apis
from googlecloudsdk.calliope import base
from googlecloudsdk.command_lib.dns import flags
from googlecloudsdk.command_lib.dns import util as command_util
from googlecloudsdk.command_lib.util.args import labels_util


def _CommonArgs(parser, messages):
  flags.GetZoneResourceArg(
      'The name of the managed-zone to be updated.').AddToParser(parser)
  flags.AddCommonManagedZonesDnssecArgs(parser, messages)
  flags.GetManagedZonesDescriptionArg().AddToParser(parser)
  labels_util.AddUpdateLabelsFlags(parser)


def _Update(zones_client, args):
  zone_ref = args.CONCEPTS.zone.Parse()

  dnssec_config = command_util.ParseDnssecConfigArgs(args,
                                                     zones_client.messages)
  labels_update = labels_util.ProcessUpdateArgsLazy(
      args, zones_client.messages.ManagedZone.LabelsValue,
      lambda: zones_client.Get(zone_ref).labels)

  return zones_client.Patch(
      zone_ref,
      dnssec_config=dnssec_config,
      description=args.description,
      labels=labels_update.GetOrNone())


@base.ReleaseTracks(base.ReleaseTrack.BETA)
class UpdateBeta(base.UpdateCommand):
  """Update an existing Cloud DNS managed-zone.

  Update an existing Cloud DNS managed-zone.

  ## EXAMPLES

  To change the description of a managed-zone, run:

    $ {command} my_zone --description="Hello, world!"

  """

  @staticmethod
  def Args(parser):
    messages = apis.GetMessagesModule('dns', 'v1beta2')
    _CommonArgs(parser, messages)

  def Run(self, args):
    zones_client = managed_zones.Client.FromApiVersion('v1beta2')
    return _Update(zones_client, args)


@base.ReleaseTracks(base.ReleaseTrack.GA)
class UpdateGA(base.UpdateCommand):
  """Update an existing Cloud DNS managed-zone.

  Update an existing Cloud DNS managed-zone.

  ## EXAMPLES

  To change the description of a managed-zone, run:

    $ {command} my_zone --description="Hello, world!"

  """

  @staticmethod
  def Args(parser):
    messages = apis.GetMessagesModule('dns', 'v1')
    _CommonArgs(parser, messages)

  def Run(self, args):
    zones_client = managed_zones.Client.FromApiVersion('v1')
    return _Update(zones_client, args)
