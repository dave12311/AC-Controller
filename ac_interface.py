#!/usr/bin/env python3
# Python IR transmitter

import time
import pigpio

class nec_codes():
	ON = "B24DBF40B04F"
	OFF = "B24D7B84E01F"
	SWING = "B24D6B94E01F"
	DIRECT = "B24D0FF0E01F" # No repeat send
	TURBO = "B54AF50AA25D"
	LED = "B54AF50AA55A"


	class _fan_speeds():
		AUTO = "B24DBF40B04F"
		LOW = "B24D9F60B04F"
		MEDIUM = "B24D5FA0B04F"
		HIGH = "B24D3FC0B04F"

	FAN_SPEED = _fan_speeds

	class _modes():
		DRY = "B24D01FEC4FF"
		HEAT = "B24DA15ECCFF"
		FAN = "B24DA15EE4FF"
		AUTO = "B24D01FEC8FF"
		COOL = "B24DA15EC0FF"

	MODE = _modes

	@staticmethod
	def TIMER_OFF(t):
		timers = [
			"B24DBF40C03F", # 0
			"B24DA15EC0FF", # 0.5
			"B24DA35CC0FF",
			"B24DA55AC0FF",
			"B24DA758C0FF",
			"B24DA956C0FF",
			"B24DAB54C0FF",
			"B24DAD52C0FF",
			"B24DAF50C0FF",
			"B24DB14EC0FF",
			"B24DB34CC0FF",
			"B24DB54AC0FF",
			"B24DB748C0FF",
			"B24DB946C0FF",
			"B24DBB44C0FF",
			"B24DBD42C0FF",
			"B24DBF40C0FF",
			"B24DA15EC1FF",
			"B24DA35CC1FF",
			"B24DA55AC1FF",
			"B24DA758C1FF", # 10
			"B24DAB54C1FF", # 11
			"B24DAF50C1FF",
			"B24DB34CC1FF",
			"B24DB748C1FF",
			"B24DBB44C1FF",
			"B24DBF40C1FF",
			"B24DA35CC2FF",
			"B24DA758C2FF",
			"B24DAB54C2FF",
			"B24DAF50C2FF",
			"B24DB34CC2FF",
			"B24DB748C2FF",
			"B24DBB44C2FF",
			"B24DBF40C2FF"  # 24
		]

		if t < 0.5:
			return timers[0]
		elif t > 24:
			return timers[34]
		elif t < 10:
			return timers[t * 2]
		else:
			return timers[10 + t]

	@staticmethod
	def TEMPERATURE(t):
		temps = [
			"B24DBF4000FF", # 17
			"B24DBF4010EF",
			"B24DBF4030CF",
			"B24DBF4020DF",
			"B24DBF40609F",
			"B24DBF40708F",
			"B24DBF4050AF",
			"B24DBF4040BF",
			"B24DBF40C03F",
			"B24DBF40D02F",
			"B24DBF40906F",
			"B24DBF40807F",
			"B24DBF40A05F",
			"B24DBF40B04F"  # 30
		]

		if t < 17:
			return temps[0]
		elif t > 30:
			return temps[13]
		else:
			return temps[t - 17]
	
class _nec():
	def __init__(self):
		# Setup pigpio
		self.gpio_pin = 23
		self.pigpio = pigpio.pi()
		self.pigpio.set_mode(self.gpio_pin, pigpio.OUTPUT)

		# Set NEC constants
		self.frequency = 38000
		self.duty_cycle = 0.33
		self.leading_pulse_duration = 4300
		self.leading_gap_duration = 4400
		self.one_pulse_duration = 562
		self.one_gap_duration = 1625
		self.zero_pulse_duration = 562
		self.zero_gap_duration = 525

		self.pulses = []

	def _zero(self, duration):
		self.pulses.append(pigpio.pulse(0, 1 << self.gpio_pin, duration))
	
	def _one(self, duration):
		period_time = 1000000.0 / self.frequency
		on_duration = int(round(period_time * self.duty_cycle))
		off_duration = int(round(period_time * (1.0 - self.duty_cycle)))
		total_periods = int(round(duration/period_time))
		total_pulses = total_periods * 2

		for i in range(total_pulses):
			if i % 2 == 0:
				self.pulses.append(pigpio.pulse(1 << self.gpio_pin, 0, on_duration))
			else:
				self.pulses.append(pigpio.pulse(0, 1 << self.gpio_pin, off_duration))
	
	def process_code(self, ircode: str, repeat: bool):
		if repeat is False:
			loops = 1
		else:
			loops = 2

		for r in range(loops):
			if (self.leading_pulse_duration > 0) or (self.leading_gap_duration > 0):
				self._one(self.leading_pulse_duration)
				self._zero(self.leading_gap_duration)
			
			for i in ircode:
				if i == "0":
					self._one(self.zero_pulse_duration)
					self._zero(self.zero_gap_duration)
				elif i == "1":
					self._one(self.one_pulse_duration)
					self._zero(self.one_gap_duration)
				else:
					print("ERROR! Non-binary digit in IR code!")
					return 1
			
			# Send trailing pulse
			self._one(self.one_pulse_duration)

class IR():
	def __init__(self):
		self.protocol = _nec()
	
	def send_code(self, nec_code):
		# Do not repeat if DIRECT
		if nec_code == nec_codes.DIRECT:
			self.protocol.process_code(format(int(nec_code, 16), "048b"), False)
		else:
			self.protocol.process_code(format(int(nec_code, 16), "048b"), True)

		self.protocol.pigpio.wave_clear()
		self.protocol.pigpio.wave_add_generic(self.protocol.pulses)
		wave_id = self.protocol.pigpio.wave_create()

		self.protocol.pigpio.wave_send_once(wave_id)

		while self.protocol.pigpio.wave_tx_busy():
			time.sleep(0.1)
		
		self.protocol.pigpio.wave_delete(wave_id)
