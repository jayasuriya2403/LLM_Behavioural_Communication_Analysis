from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(["html"])
)


def candidate_report(result):
    template = env.get_template("candidate_report.html")
    return template.render(result=result)


def recruiter_report(result):
    template = env.get_template("recruiter_report.html")
    return template.render(result=result)
