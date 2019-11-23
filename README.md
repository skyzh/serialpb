# serialpb

A protocol made for reliable serial packet transmission.

## Layout

Most significant bit indicates mode. Control mode = 1, Transmission mode = 0.

### Control Mode (1xxxxxxx)

`0xFF` = new transaction

### Transmission Mode (0xxxxxxx)

Most significant bit is 0. Other 7 bits transmit data. Every 8 bits received
will be concatenated into a byte. When entering control mode, extra bits
will be ignored.

## Todo

- [ ] add tests for serial not available