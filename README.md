# serialpb

A protocol made for reliable serial packet transmission.

## Layout

All data on serial are transmitted in 32-byte packet.

First packet

```
| Header (2)  |  Size (2) | Partial Data (26) | Checksum (2) |
| 0xde | 0xad |   short   |      ......       |    CRC-16    |
```

Other packets

```
| Header (2)  |  Size (2) | Partial Data (26) | Checksum (2) |
| 0xbe | 0xef |   short   |      ......       |    CRC-16    |
```
