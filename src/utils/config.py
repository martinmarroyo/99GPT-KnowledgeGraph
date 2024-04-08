import os
import json
import yaml
from yaml import SafeLoader
from pprint import PrettyPrinter
from dotenv import dotenv_values
from dotenv import load_dotenv

class Config:
  def __init__(self,
               config_dict=None, 
               from_env=False,
               env_filter=None,
               dotenv_path=None,
               yaml_path=None):
    
    self._config = {}
    self._printer = PrettyPrinter(indent=4)
    self._from_env = from_env
    self._from_dotenv = True if dotenv_path else False
    self._from_yaml = True if yaml_path else False
    self._from_dict = config_dict is not None

    if config_dict:
      self.add_props(config=config_dict)

    if from_env or env_filter is not None:
      self._load_from_env(env_filter=env_filter)
      
    if self._from_dotenv or dotenv_path is not None:
      self._load_from_dotenv(dotenv_file=dotenv_path)

    if self._from_yaml or yaml_path is not None:
      self._load_from_yaml(yaml_path)
  
  def __getitem__(self, key):
    item = self.config_dict.get(key)
    if isinstance(item, dict):
      item = Config(config_dict=item)
    return item

  def __repr__(self):
    conf_str = (json.dumps(self._config)
                    .strip()
                    .replace("\n", "")
                    .replace("\\", ""))
    status_str = f"{conf_str}\n{json.dumps(self.built_from, indent=4)}"
    return status_str

  def __str__(self):
    conf_str = (json.dumps(self._config)
                    .strip()
                    .replace("\n", "")
                    .replace("\\", ""))
    return conf_str
  
  def _load_from_env(self, env_filter: list = None) -> None:
    self._from_env = True
    if env_filter is None:
      self.add_props(config=os.environ)
    else:
      self.add_props(config={
          key: val 
          for key, val in os.environ.items()
          if key in env_filter
      })

    return None

  def _load_from_yaml(self, yaml_file) -> None:
    def get_yaml_props(yaml_file) -> dict:
      with open(yaml_file, mode="r") as f:
        yaml_props = yaml.load(f, Loader=SafeLoader)
      
      return yaml_props
    
    if isinstance(yaml_file, list):
      payload = list(map(get_yaml_props, yaml_file))
      for cfg in payload:
        self.add_props(config=cfg)
    else:
      payload = get_yaml_props(yaml_file)
      self.add_props(config=payload)

    self._from_yaml = True
    return None

  def _load_from_dotenv(self, dotenv_file: str) -> None:
    dotenv_vars = dotenv_values(dotenv_path=dotenv_file)
    # Load dotenv variables into environment
    load_dotenv(dotenv_file, override=True)
    self._from_dotenv = True
    self.add_props(config=dotenv_vars)
    return None
  
  def keys(self):
    return self.config_dict.keys()
  
  def print(self):
    # Pretty representation of config\
    self._printer.pprint(self.built_from)
    self._printer.pprint(self.config_dict)

  def add_props(self, config: dict) -> None:
    props = []
    for key in config:
      prop_name = str(key).lower()
      prop_val = config[key]
      if isinstance(prop_val, dict):
        new_config = Config()
        new_config.add_props(config=prop_val)
        prop_val = new_config
      props.append((prop_name, prop_val))

    for prop, val in props:
      self.__setattr__(prop, val)
      self._config.update(
          {prop: val.config_dict if isinstance(val, Config) else val})

  @property
  def config_dict(self):
    return self._config
  
  @property
  def built_from(self):
    return {
      "from_dict": self._from_dict,
      "from_env": self._from_env,
      "from_dotenv": self._from_dotenv,
      "from_yaml": self._from_yaml,
    }
      