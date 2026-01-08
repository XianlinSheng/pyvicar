def allow_restart(c):
    c.restart.read()
    if c.restart:
        c.restart.to_restart_in()
        c.input.domain.iRestart = True

    return c
