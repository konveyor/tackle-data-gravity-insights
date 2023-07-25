################################################################################
# Copyright IBM Corporation 2021, 2022
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License a#t˚†
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
################################################################################

"""
Logging functions
"""

import logging

logging.basicConfig(
    level="INFO", format="%(asctime)s %(message)s", datefmt="%d%m%y::%H%M"
)


class Log:
    """Common Logger"""

    log = logging.getLogger()

    @staticmethod
    def info(msg: str):
        """Log level INFO"""
        Log.log.info(msg, extra={"markup": True})

    @staticmethod
    def warn(msg: str):
        """Log level WARNING"""
        Log.log.warning(msg, extra={"markup": True})

    @staticmethod
    def debug(msg: str):
        """Log level DEBUG"""
        Log.log.debug(msg, extra={"markup": True})

    @staticmethod
    def error(msg: str):
        """Log level ERROR"""
        Log.log.error(msg, extra={"markup": True})
