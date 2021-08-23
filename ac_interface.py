#!/usr/bin/env python3
# Python IR transmitter

import time
import pigpio

class NEC():
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
	
	def process_code(self, ircode):
		for r in range(2):
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
		self.protocol = NEC()
	
	def send_code(self, ircode):
		print("Processing IR code: %s" % ircode)

		self.protocol.process_code(ircode)
		self.protocol.pigpio.wave_clear()
		self.protocol.pigpio.wave_add_generic(self.protocol.pulses)
		wave_id = self.protocol.pigpio.wave_create()

		self.protocol.pigpio.wave_send_once(wave_id)

		while self.protocol.pigpio.wave_tx_busy():
			time.sleep(0.1)
		
		self.protocol.pigpio.wave_delete(wave_id)
