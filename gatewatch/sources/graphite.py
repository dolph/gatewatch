# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import requests

from gatewatch import backend
from gatewatch import tasks


GRAPHITE_ENDPOINT = 'http://graphite.openstack.org/render'
MERGE_PROBABILITY = {
    'format': 'json',
    'from': '-10seconds',
    'target': 'alias(secondYAxis(lineWidth(asPercent(transformNull(multiplySeries(transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-neutron.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-neutron.{SUCCESS,FAILURE})),%2728hours%27),1),transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-full.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-full.{SUCCESS,FAILURE})),%2728hours%27),1),transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-grenade-dsvm.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-grenade-dsvm.{SUCCESS,FAILURE})),%2728hours%27),1),transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-neutron-large-ops.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-neutron-large-ops.{SUCCESS,FAILURE})),%2728hours%27),1),transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-large-ops.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-large-ops.{SUCCESS,FAILURE})),%2728hours%27),1),transformNull(movingAverage(divideSeries(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-postgres-full.SUCCESS,sum(stats.zuul.pipeline.gate.job.gate-tempest-dsvm-postgres-full.{SUCCESS,FAILURE})),%2728hours%27),1))),1),2)),%27Patch%20Pass%20Chance%20Moving%20Average%27)'}


def _build_url(endpoint, query):
    url = endpoint
    url = url + '?'
    url = url + '&'.join(['%s=%s' % (k, v) for k, v in query.iteritems()])
    return url


@tasks.app.task
def merge_probability():
    r = requests.get(_build_url(GRAPHITE_ENDPOINT, MERGE_PROBABILITY))
    merge_probability = int(round(r.json()[0]['datapoints'][0][0]))

    backend.write(merge_probability=merge_probability)
    return merge_probability
