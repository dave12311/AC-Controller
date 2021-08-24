#!/usr/bin/env python3
from ac_interface import IR, nec_codes
from time import sleep

ir = IR()
ir.send_code(nec_codes.TEMPERATURE(24))