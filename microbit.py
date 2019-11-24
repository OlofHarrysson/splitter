from microbit import button_a, button_b
import music


def startsound():
  # music.pitch(frequency, duration in ms)
  # music.pitch(500, 500) # Was used for inital trials
  music.pitch(100, 100)
  music.pitch(800, 100)
  music.pitch(100, 100)
  music.pitch(800, 100)
  # music.pitch(1600, 100)


def endsound():
  music.pitch(800, 1000)


while True:
  if button_a.is_pressed():
    startsound()

  elif button_b.is_pressed():
    endsound()
