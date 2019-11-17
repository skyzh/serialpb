# serialpb

A protocol made for reliable serial packet transmission.

## Layout

Most significant bit indicates mode: control mode and transmission mode.

### Control Mode (1)

`0xFF` = new transaction

### Transmission Mode

Most significant bit is 0. Other 7 bits transmit data. Every 8 bits received
will be concatenated into a byte. When entering control mode, extra bits
will be ignored.
