from pyramid.static import static_view

# expose monitor_js in a static view
static_view = static_view(
    "xbus.monitor:static/monitor_js/sources",
    use_subpath=True
)
