hz = 554  # Pitch in Hz
s = 0.1  # Duration in seconds
v = 99  # Duty in % - Volume

# Every Tuple in the Dictionary dic represents a different melody
# The Melody Tuple can contain any number of 3 numbers Tuples
# Every Tuple in the Melody represent a musical Note
# 0: Duty Cycle in % PWM (similar to Volume)
# 1: Pitch in Hz
# 2: Duration of the Note in Seconds

dic = {
    "check_in": ((v, hz, s * 2), (v, hz * 1.28, s * 2), (v, 5, s * 2)),
    "check_out": ((v, hz * 1.26, s), (v, hz, s), (v, 5, s)),
    "FALSE": (
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
    ),
    "comERR1": (
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
    ),
    "comm_failed": (
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
        (v, hz * 2, s / 2),
        (v, 20, s),
    ),
    "Local": ((v, hz, s / 2), (v, 20, s), (v, hz, s / 2), (v, 20, s)),
    "ContactAdm": (
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
        (v, hz * 4, s / 4),
        (v, 20, s / 2),
    ),
    "odoo_async": ((v, hz, s / 2), (v, 20, s), (v, hz, s / 2), (v, 20, s)),
    "cardswiped": (
        (v, hz, s / 4),
        (v, 20, s / 2),
        (v, hz * 1.28, s),
        (v, 20, s / 2),
        (v, hz, s / 2),
        (v, 20, s),
    ),
    "OK": ((v, hz / 2, s), (v, 5, s / 2)),
    "down": ((v, hz / 2 * 1.26, s), (v, 5, s / 2)),
    "back_to_menu": ((v, hz / 3, s / 2), (v, 20, s), (v, hz / 3, s / 2), (v, 20, s)),
}
