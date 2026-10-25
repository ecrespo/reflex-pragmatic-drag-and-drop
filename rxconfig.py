import reflex as rx

config = rx.Config(
    app_name="reflex_pragmatic_drag_and_drop",
    plugins=[
        # Explicit since Reflex 0.9: implicit Radix Themes enablement is
        # deprecated and will be removed in 1.0.
        rx.plugins.RadixThemesPlugin(),
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)
