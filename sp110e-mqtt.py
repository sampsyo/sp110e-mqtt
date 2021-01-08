import asyncio
import bleak
import asyncio_mqtt
import sys


async def run(addr, host):
    async with asyncio_mqtt.Client(host) as mqtt:
        async with bleak.BleakClient(addr) as dev:
            svcs = await dev.get_services()
            for char in svcs.characteristics.values():
                if char.uuid.startswith('0000ffe1'):
                    light_char = char
                    break
            else:
                print('not found')
                return

            print(light_char)

            topic = 'led/{}/rgb'.format(addr)
            print(topic)
            async with mqtt.filtered_messages(topic) as msgs:
                await mqtt.subscribe(topic)
                async for msg in msgs:
                    rgb_str = msg.payload.decode()
                    print(rgb_str)
                    parts = [int(n) for n in rgb_str.split()]
                    for val in parts:
                        assert 0 <= val <= 255
                    r, g, b = parts
                    data = bytearray([r, g, b, 0x1e])
                    await dev.write_gatt_char(light_char, data)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(*sys.argv[1:]))
