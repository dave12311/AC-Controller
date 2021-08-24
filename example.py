#!/usr/bin/env python3
from ac_interface import IR
import nec_codes

ir = IR()
ir.send_code(nec_codes.OFF)