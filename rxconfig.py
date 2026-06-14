import reflex as rx

config = rx.Config(
    app_name="reflex_pragmatic_drag_and_drop",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)