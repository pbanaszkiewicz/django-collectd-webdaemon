# coding: utf-8
import requests
import simplejson as json
import pygal
from pygal.style import LightStyle
import base64


chart_config = pygal.Config()
chart_config.legend_at_bottom = True
chart_config.x_label_rotation = 30
chart_config.human_readable = True
chart_config.show_dots = False
chart_config.include_x_axis = True
chart_config.legend_box_size = 10
chart_config.legend_font_size = 12
chart_config.style = LightStyle


def metrics_tree(host):
    """
    Return tree structure of collectd's data directory.
    """
    tree = requests.get(host + "/list_tree")
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

    # TODO: own chart type with support for UNIX EPOCH style timestamps
    chart = pygal.XY(chart_config)

    for key in results.keys():
        for series in results[key]:
            chart.add(series["label"], series["data"])

    content = base64.b64encode(chart.render())
    return content


def similar_thresholds(daemon, host, plugin, type):
    """
    Return thresholds defined for similar set of (host/plugin/type).

    :param host: host
    :param plugin: plugin
    :param type: type
    """
    plugin = plugin.split("-")
    type = type.split("-")

    response = requests.get("%s/lookup_threshold/%s/%s/%s/%s/%s" % (daemon,
        host, plugin[0], "-" if len(plugin) < 2 else plugin[1], type[0],
        "-" if len(type) < 2 else type[1]))

    return response


def all_thresholds(daemon):
    """
    Return all available thresholds.
    """
    response = requests.get("%s/thresholds/" % daemon)
    return response


def get_threshold(daemon, id):
    """
    Returns the threshold.

    :param id: threshold's id.
    """
    response = requests.get("%s/threshold/%s" % (daemon, id))
    return response


def add_threshold(daemon, data):
    """
    Creates new threshold.
    """
    # Getting rid of unused, unneccessary keys
    # I can get rid of False values, because all booleans are false by default.
    for key in list(data.keys()):
        if not data[key]:
            del data[key]

    response = requests.post("%s/threshold" % daemon,
        data=dict(threshold=json.dumps(data)))
    return response


def edit_threshold(daemon, id, data):
    """
    Updates the threshold.
    """
    response = requests.put("%s/threshold/%s" % (daemon, id),
        data=dict(threshold=json.dumps(data)))
    return response


def delete_threshold(daemon, id):
    """
    Removes the threshold.
    """
    response = requests.delete("%s/threshold/%s" % (daemon, id))
    return response
