# coding: utf-8
import requests
import simplejson as json
import pygal
from pygal.style import LightStyle
import base64


def metrics_tree(host):
    """
    Return tree structure of collectd's data directory.
    """
    try:
        tree = requests.get(host + "/list_tree").json["tree"]
    except requests.RequestException, e:
        # TODO: fail quietly?
        # TODO: or maybe catch exceptions in GWM and handle as errors!
        tree = dict()
    return tree


def arbitrary_metrics(host, paths, start=None, end=None):
    """
    Return metrics for given set of full paths.
    :param paths: list of paths for which metrics are shown. Example:
        ["host1/plugin1/type1.rrd", "host1/plugin1/type2.rrd"]
    :param start: time specification according to http://goo.gl/VcLEC
    :param end: like above
    """
    results = dict()

    try:
        paths = json.dumps(paths)
        if start and end:
            response = requests.post("%s/get/%s/%s" % (host, start, end),
                data={"rrds": paths})
        else:
            response = requests.post(host + "/get/", data={"rrds": paths})

        if response.status_code != 200:
            # TODO: throw requests.RequestException?
            return results

        results = response.json

    except requests.RequestException, e:
        # TODO: fail quietly?
        # TODO: or maybe catch exceptions in GWM and handle as errors!
        return results

    # TODO: own chart type with support for UNIX EPOCH style timestamps
    chart = pygal.XY(legend_at_bottom=True, x_label_rotation=30,
        human_readable=True, show_dots=False, include_x_axis=True,
        legend_box_size=20, style=LightStyle)

    for key in results.keys():
        for series in results[key]:
            chart.add(series["label"], series["data"])

    content = base64.b64encode(chart.render())
    return content
