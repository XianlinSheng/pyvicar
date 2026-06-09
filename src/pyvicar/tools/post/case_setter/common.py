def create_matplotlib_fig(c, fig, name, **kwargs):
    c.post.enable()
    c.post.reports.enable()
    fig_report = c.post.reports.get_or_create(name)
    fig_report.table_visual_by_matplotlib(fig, **kwargs)

def create_json_dict(c, d, name, indent=4, **kwargs):
    c.post.enable()
    c.post.reports.enable()
    dict_report = c.post.reports.get_or_create(name)
    dict_report.json_by_dict(d, indent=indent, **kwargs)
