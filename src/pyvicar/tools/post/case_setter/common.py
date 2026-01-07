def create_matplotlib_fig(c, fig, name, **kwargs):
    c.post.enable()
    c.post.reports.enable()
    fig_report = c.post.reports.get_or_create(name)
    fig_report.table_visual_by_matplotlib(fig, **kwargs)
