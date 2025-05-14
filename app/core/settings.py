from jinja2 import Environment, FileSystemLoader


jinja_env = Environment(
    loader=FileSystemLoader("app/mail_templates"),
    enable_async=True,
)