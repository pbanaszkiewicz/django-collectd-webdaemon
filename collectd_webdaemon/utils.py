# coding: utf-8
import requests


def metrics_tree(host):
    tree = requests.get(host + "/list_tree").json["tree"]
    return tree
