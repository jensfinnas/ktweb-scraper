# encoding: utf-8
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from body import Body
from meeting import Meeting
import re


class Site(object):
    """ Represents a KT Web site
    """
    def __init__(self, url):
        self.url = url
        base_url_regex = r"^(.+?[^\/:](?=[?\/]|$)/)"
        self.base_url = re.search(base_url_regex, url).group(1)
        self.name = url.split("//")[1].split("/")[0]

    def bodies(self):
        """ Lists all bodies
        """
        if not hasattr(self, "body_list"):
            r = requests.get(self.url + "epj_tek.htm")
            soup = BeautifulSoup(r.text, 'html.parser')
            options = soup.find("form", {"name": "form1"})\
                          .find("select", {"name": "kirjaamo"})\
                          .find_all("option")
            self.body_list = [Body(x.text, x["value"]) for x in options]

        return self.body_list

    def meetings(self, body):
        """ Returns a list of all meetings
        """
        if not isinstance(body, Body):
            """ This function can be called with either a Body object or string
            """
            body = self._guess_body(body)

        url = self.url + "pk_kokl.htm"
        form_data = {
            "oper": "where",
            "kirjaamo": body.id,
            "pvm1": "",
            "pvm2": "",
        }
        r = requests.post(url, form_data)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all("tr", {"class": "data0"}) +\
            soup.find_all("tr", {"class": "data1"})
        meetings = []
        for row in rows:
            cells = row.find_all("td")
            date = datetime.strptime(cells[0].text, '%d.%m.%Y %H:%M')
            body = self._guess_body(cells[1].text)
            meetings.append(Meeting(self, body, date))
        return meetings

    def _guess_body(self, body_str):
        """ Returns a Body object given a name or id of a body
        """
        for body in self.bodies():
            if body_str in body.id:
                return body
            elif body_str in body.name:
                return body
        raise ValueError("%s is not a valid body name. Try %s instead." %
                         (body_str, ", ".join(self.bodies())))
