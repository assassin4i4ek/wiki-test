from typing import Optional

import re
import wikitextparser as wtp

from wikitest.api.model import Person


class PersonPageParser:
    def __init__(self):
        self.log = False
        self._name_parser = PersonNameParser()
        self._date_parser = PersonDateParser()
        self._article_fmt = PersonArticleFormatter()

    def try_parse(self, title: str, text: str) -> Optional[Person]:
        try:
            wikitext = wtp.parse(text)
            if not self._can_parse_person(title, wikitext):
                return None
            return self._parse_person(title, wikitext)
        except Exception as e:
            print(e)
            return None

    def _can_parse_person(self, title: str, wikitext: wtp.WikiText) -> bool:
        target_templates = ('особа', )
        target_args = ('народженн', 'смерті')
        for t in wikitext.templates:
            t_name = t.normal_name().strip().lower()
            if t_name in target_templates:
                if self.log:
                    print(f'matched template "{t_name}" with one of {target_templates}')
                return True
            for t_arg in t.arguments:
                t_arg_name = t_arg.name.strip().lower()
                if t_arg_name in target_args:
                    if self.log:
                        print(f'matched template arg "{t_arg_name}" with one of {target_args}')
                    return True
                for a_target in target_args:
                    if a_target in t_arg_name:
                        if self.log:
                            print(f'matched template arg "{t_arg_name}" with "{a_target}"')
                        return True
        
        target_sections = ('біографі', 'життєпис')
        for s in wikitext.sections:
            if not s.title:
                continue
            s_title = s.title.strip().lower()
            if s_title in target_sections:
                if self.log:
                    print(f'matched section "{s_title}" with one of "{target_sections}"')
                return True
            for s_target in target_sections:
                if s_target in s_title:
                    if self.log:
                        print(f'matched section "{s_title}" with "{s_target}"')
                    return True
        return False

    def _parse_person(self, title: str, wikitext: wtp.WikiText) -> Person:
        name, surname, patronymic = self._name_parser.parse_names(title, wikitext)
        birth_date, death_date = self._date_parser.parse_dates(title, wikitext)
        src_article = self._article_fmt.format_article(title, wikitext)
        return Person(
            name=name, surname=surname, patronymic=patronymic,
            birth_date=birth_date, death_date=death_date, src_article=src_article,
        )


class PersonNameParser():
    def parse_names(self, title: str, wikitext: wtp.WikiText) -> tuple[str, Optional[str], Optional[str]]:
        title_split = title.split()
        if len(title_split) >= 3:
            surname, name, patronymic = title_split[:3]
        elif len(title_split) == 2:
            name, surname = title_split
            patronymic = None
        elif len(title_split) == 1:
            name = title_split[0]
            surname = patronymic = None
        return name, surname, patronymic


class PersonDateParser():
    def __init__(self):
        # parse dates from template
        self._birth_tmpl_arg_name_rx = re.compile(r'дата[\s|_]народження')
        self._death_tmpl_arg_name_rx = re.compile(r'дата[\s|_]смерті')
        self._tmpl_arg_val_rx = re.compile(r'\d{1,2}\.\d{1,2}\.\d{3,4}')

    def parse_dates(self, title: str, wikitext: wtp.WikiText) -> tuple[Optional[str], Optional[str]]:
        # try parse from infobox template args
        for t in wikitext.templates:
            dates = None
            for a in t.arguments:
                res = self._try_parse_from_tmpl_arg(a)
                dates = self._ext_dates_tuple(dates, res)
            if dates is not None:
                return dates
        
        # try to parse directly from the template
        dates = None
        for t in wikitext.templates:
            res = self._try_parse_from_tmpl(t)
            dates = self._ext_dates_tuple(dates, res)
        if dates is not None:
            return dates
        return (None, None)

    def _try_parse_from_tmpl_arg(self, arg: wtp.Argument) -> Optional[tuple[Optional[str], Optional[str]]]:
        res = None
        arg_name = arg.name.strip().lower()
        if self._birth_tmpl_arg_name_rx.search(arg_name):
            birth_date_match = self._tmpl_arg_val_rx.search(arg.value)
            if birth_date_match is not None:
                res = self._ext_dates_tuple(res, (birth_date_match.group(), None))
        if self._death_tmpl_arg_name_rx.search(arg_name):
            death_date_match = self._tmpl_arg_val_rx.search(arg.value)
            if death_date_match is not None:
                res = self._ext_dates_tuple(res, (None, death_date_match.group()))
        return res

    def _try_parse_from_tmpl(self, tmpl: wtp.Template) -> Optional[tuple[Optional[str], Optional[str]]]:
        if tmpl.normal_name().strip().lower() == 'дн':
            if len(tmpl.arguments) < 3:
                raise ValueError("Invalid template")
            birth_date = '.'.join([a.value for a in tmpl.arguments[:3]])
            return (birth_date, None)
        if tmpl.normal_name().strip().lower() == 'дс':
            if len(tmpl.arguments) < 3:
                raise ValueError("Invalid template")
            death_date = '.'.join([a.value for a in tmpl.arguments[:3]])
            
            return (None, death_date)

    def _ext_dates_tuple(
            self,
            prev: Optional[tuple[Optional[str], Optional[str]]],
            new: Optional[tuple[Optional[str], Optional[str]]]
    ) -> Optional[tuple[Optional[str], Optional[str]]]:
        if prev is None:
            return new
        if new is None:
            return prev
        
        res_1, res_2 = prev
        new_1, new_2 = new
        if new_1 is not None:
            res_1 = new_1
        if new_2 is not None:
            res_2 = new_2
        return (res_1, res_2)


class PersonArticleFormatter():
    def format_article(self, title: str, wikitext: wtp.WikiText) -> str:
        return wikitext.plain_text()
