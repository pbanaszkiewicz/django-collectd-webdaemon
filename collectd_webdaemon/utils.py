# coding: utf-8
import requests
import simplejson as json
import pygal
from pygal.util import compute_scale
from pygal.style import LightStyle
import base64

from django.utils.formats import date_format
from datetime import datetime


TIMEOUT = 10
chart_config = pygal.Config()
chart_config.legend_at_bottom = True
chart_config.x_label_rotation = 30
chart_config.human_readable = True
chart_config.show_dots = False
chart_config.include_x_axis = True
chart_config.legend_box_size = 10
chart_config.legend_font_size = 12
chart_config.style = LightStyle


class XY_Timestamps(pygal.XY):
    """
    XY Line graph with timestamps in X-axis.
    """

    def _display_date(self, timestamp):
        return date_format(datetime.fromtimestamp(timestamp),
            "SHORT_DATETIME_FORMAT")

    @property
    def _format_x(self):
        return self._display_date

    def _compute(self):
        """
        This method was taken from Pygal.XY class, with my minor changes. It's
        licensed under GPL v3 or greater.
        """
        for serie in self.series:
            for metadata in serie.metadata:
                if not hasattr(metadata.value, '__iter__'):
                    metadata.value = (metadata.value, self.zero)

        xvals = [val[0]
                 for serie in self.series
                 for val in serie.values
                 if val[0] is not None]
        yvals = [val[1]
                 for serie in self.series
                 for val in serie.values
                 if val[1] is not None]
        xmin = min(xvals)
        xmax = max(xvals)
        rng = (xmax - xmin)

        for serie in self.series:
            serie.points = serie.values
            if self.interpolate:
                vals = zip(*sorted(serie.points, key=lambda x: x[0]))
                serie.interpolated = self._interpolate(
                    vals[1], vals[0], xy=True, xy_xmin=xmin, xy_rng=rng)
                if not serie.interpolated:
                    serie.interpolated = serie.values

        if self.interpolate:
            xvals = [val[0]
                     for serie in self.series
                     for val in serie.interpolated]
            yvals = [val[1]
                     for serie in self.series
                     for val in serie.interpolated]

        self._box.xmin, self._box.xmax = min(xvals), max(xvals)
        self._box.ymin, self._box.ymax = min(yvals), max(yvals)
        x_pos = compute_scale(self._box.xmin, self._box.xmax, self.logarithmic,
            self.order_min)
        y_pos = compute_scale(self._box.ymin, self._box.ymax, self.logarithmic,
            self.order_min)

        self._x_labels = zip(map(self._format_x, x_pos), x_pos)
        self._y_labels = zip(map(self._format, y_pos), y_pos)


def metrics_tree(host):
    """
    Return tree structure of collectd's data directory.
    """
    tree = requests.get(host + "/list_tree", timeout=TIMEOUT)
    return tree


def metrics_hosts(host):
    """
    Return list of hosts watched on specified metrics server.
    """
    hosts = requests.get(host + "/list_hosts", timeout=TIMEOUT)
    return hosts


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
            data={"rrds": paths}, timeout=TIMEOUT)
    else:
        response = requests.post(host + "/get/", data={"rrds": paths},
            timeout=TIMEOUT)

    if response.status_code != 200:
        # TODO: throw requests.RequestException?
        raise requests.exceptions.RequestException("Wrong status code.")

    results = response.json

    # chart = pygal.XY(chart_config)
    chart = XY_Timestamps(chart_config)

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
        "-" if len(type) < 2 else type[1]), timeout=TIMEOUT)

    return response


def all_thresholds(daemon):
    """
    Return all available thresholds.
    """
    response = requests.get("%s/thresholds/" % daemon, timeout=TIMEOUT)
    return response


def get_threshold(daemon, id):
    """
    Returns the threshold.

    :param id: threshold's id.
    """
    response = requests.get("%s/threshold/%s" % (daemon, id), timeout=TIMEOUT)
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
        data=dict(threshold=json.dumps(data)), timeout=TIMEOUT)
    return response


def edit_threshold(daemon, id, data):
    """
    Updates the threshold.
    """
    response = requests.put("%s/threshold/%s" % (daemon, id),
        data=dict(threshold=json.dumps(data)), timeout=TIMEOUT)
    return response


def delete_threshold(daemon, id):
    """
    Removes the threshold.
    """
    response = requests.delete("%s/threshold/%s" % (daemon, id),
        timeout=TIMEOUT)
    return response


def generate_thresholds(daemon):
    """
    Requests daemon to save the thresholds from the DB and then to restart
    collectd.
    """
    response = requests.get("%s/generate_threshold" % daemon, timeout=TIMEOUT)
    return response
