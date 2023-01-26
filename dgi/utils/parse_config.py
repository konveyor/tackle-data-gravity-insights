################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""A container to hold all configurations.

Config contains methods to read a yaml file and create an object to hold the configration. Once initialized, 
we can use the dot notation to access the configurations.

E.g.,
Let's say we have a yaml file called conf.yml

foo:
    bar: "bar"
    baz:
        baza: 1
        bazb: False

After reading this, we can use it as follows:

>>> conf = Config("conf.yml")
>>> conf = conf.load_config()
>>> print(conf.bar)
bar
>>> print(conf.baz.baza)
1
>>> print(conf.baz.bazb)
False
"""

import os
import re
import yaml
from typing import Any, Generator

__author__ = "Rahul Krishna"
__license__ = "Apache 2.0"
__version__ = "1.0"
__maintainer__ = "Rahul Krishna"
__email__ = "rkrsn@ibm.com"
__status__ = "Research Prototype"


class Config:
    def __init__(self, config_file: str = None) -> None:
        self.config_file = config_file
        self._num_attributes = 0

    def __iter__(self):
        """ Iterates over all the attributes.

        Yields:
            Generator[str, Config or dict_like]: Key is the name of the attribute. 
            Value is either an instance of Config or any value
        """

        for attr_name, attr_val in list(self.__dict__.items()):
            yield attr_name, attr_val

    def get_num_attributes(self) -> int:
        """ A getter method for number of attributes
        """
        return self._num_attributes

    def set_config(self, key: str, val: Any):
        """ Set config attribute

        Args:
            key (str): Name of the config
            val (Any): The value

        Returns:
            Config: A reference back to self
        """

        # If the config file is nested, then recurse.
        if isinstance(val, dict):
            cfg_cls = Config()
            for sub_key, sub_val in list(val.items()):
                cfg_cls = cfg_cls.set_config(sub_key, sub_val)
            val = cfg_cls

        self._num_attributes += 1

        # If the value has environment variables, replace them with the correct values or the defaults
        reg = re.compile("\${[^\}]*}")
        if isinstance(val, str) and reg.match(val):
            raw_str = re.sub("[${\ }]", "", val)
            sub_str = raw_str.split("|")
            env_val = sub_str[0]
            default = None
            if len(sub_str) == 2:
                default = sub_str[1]

            val = os.getenv(env_val)

            if not val:
                assert (default), "Enviroment variable {val} not set, and default value is not set. Please set {val}".format(
                    val=env_val)
                val = default

        setattr(self, key, val)
        return self

    def load_config(self):
        """
        Read a yaml file with all the configurations and set them.

        Parameters
        ----------
        config_file: path_str
            Path to the config yaml file

        Returns
        -------
        self: self
            A reference to self
        """
        with open(self.config_file, 'r') as cfg:
            yaml_loader = yaml.load(cfg, Loader=yaml.FullLoader)
            for attr_name, attr_val in list(yaml_loader.items()):
                self.set_config(attr_name, attr_val)

        return self
