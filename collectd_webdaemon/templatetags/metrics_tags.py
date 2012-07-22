from django import template

register = template.Library()


@register.simple_tag
def embed_metrics(metrics):
    """
    Return <embed> tag with metrics as a SVG image.

    :param metrics: base64 encoded image content.
    """
    return '<embed src="data:image/svg+xml;charset=utf-8;base64,%s">' % \
        metrics
