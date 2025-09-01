#!/usr/bin/env python3

"""
    metronome
    
    Tool that runs to enrich SONiC Redis with additional metrics.
    
"""
import asyncio

from metronome import Engine, TaskRegistry


async def _main():
    engine = Engine(TaskRegistry)

    await engine.run()


def main():
    """Synchronous wrapper for the async main function"""
    asyncio.run(_main())
