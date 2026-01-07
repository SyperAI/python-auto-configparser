from configparser import ConfigParser
from pathlib import Path
from typing import Dict, Any, OrderedDict

from pydantic import BaseModel


def _flatten(d: Dict[str, Any], parent: list[str] = None) -> Dict:
    parent = parent or []
    if any(isinstance(v, dict) for v in d.values()):
        out: Dict[str, Dict] = {}
        for key, val in d.items():
            if isinstance(val, dict) and any(isinstance(v2, dict) for v2 in val.values()):
                out.update(_flatten(val, parent + [key]))
            elif isinstance(val, dict):
                section = ".".join(parent + [key])
                out[section] = {
                    k: "" if v is None else str(v)
                    for k, v in val.items()
                }
        return out
    else:
        section = ".".join(parent)
        if section == '':
            raise ValueError("Section cannot be empty. Read docs to understand how to create config class.")
        return {section: {k: "" if v is None else str(v) for k, v in d.items()}}


def _get_defaults(model) -> Dict:
    return _flatten(model.model_dump())


def _parse_config_file(model, config_file: str, allow_missing: bool = False) -> Dict:
    config_data = {}

    parser = ConfigParser(dict_type=OrderedDict)
    parser.read_dict(_get_defaults(model))
    parser.read(config_file, encoding="utf-8")

    with open(config_file, "w", encoding="utf-8") as f:
        parser.write(f)

    if not allow_missing:
        missing: list[str] = []
        for sect in parser.sections():
            for key, val in parser.items(sect):
                if val == "":
                    missing.append(f"{sect}.{key}")
        if missing:
            raise ValueError(f"Missing values for: {', '.join(missing)} fields in {config_file}")


    for section in parser.sections():
        main_section = section.split('.')[0]

        if section != main_section:
            secondary_section = section.split('.')[1]
            if main_section in config_data.keys():
                config_data[main_section][secondary_section] = dict(parser.items(section))
            else:
                config_data[main_section] = {}
                config_data[main_section][secondary_section] = dict(parser.items(section))
        else:
            config_data[section] = dict(parser.items(section))

    if len(config_data) == 0:
        raise EnvironmentError("No config file")

    return config_data


def _write_default_config(model, path: str = "config.ini", rewrite: bool = False) -> None:
    parser = ConfigParser()
    parser.read_dict(_get_defaults(model))

    if Path(path).exists() and not rewrite:
        parser.read(path, encoding="utf-8")

    with open(path, "w", encoding="utf-8") as f:
        parser.write(f)


class AutoConfig(BaseModel):
    """
    Base class for config actions automation

    Attributes:
        allow_missing: If True config will be not checked for missing fields. Default: False
    """
    allow_missing: bool = False

    def load(self, config_file: str = "config.ini"):
        """
        Loads config state from given file

        :param config_file: Path to config file
        :return:
        """

        self.__init__(**_parse_config_file(self, config_file, self.allow_missing))
        return self

    def save(self, config_file: str = "config.ini") -> None:
        """
        Saves current config state to given file

        :param config_file: Path to config file
        :return:
        """

        parser = ConfigParser(dict_type=OrderedDict)
        parser.read_dict(self.model_dump())

        with open(config_file, "w", encoding="utf-8") as f:
            parser.write(f)