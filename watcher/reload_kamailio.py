#!/bin/env python3

from dns.resolver import dns
import aiohttp
import asyncio


async def send_req(answers):
    async with aiohttp.ClientSession() as session:
        for record in answers:
            url = "http://{}/RPC/reload_rtpengine".format(record)
            async with session.get(url) as resp:
                pass


def reload_rtpengine():
    resolver = dns.resolver.Resolver()  # create a new instance named 'myResolver'
    # Lookup the 'A' record(s) for google.com
    answers = resolver.query("kamailio-headless.default.svc.cluster.local", "A")
    # answers = resolver.query("jerry.lab.test.ncnu.org", "A")

    asyncio.run(send_req(answers))


if __name__ == '__main__':
    reload_rtpengine()
