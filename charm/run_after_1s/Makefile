CC      = gcc
CFLAGS  = -g
RM      = rm -f


default: all

all: run_after_1s

run_after_1s: run_after_1s.c
	$(CC) $(CFLAGS) -o run_after_1s run_after_1s.c

clean:
	$(RM) run_after_1s

# craft parts make plugun run DESTDIR with /bin dir.
.PHONY: install
install:
	install -D run_after_1s $(DESTDIR)$(PREFIX)/bin/run_after_1s
