"""
Compatibility shim for aiohttp ClientConnectorDNSError.

In aiohttp 3.9+, ClientConnectorDNSError was removed and DNS errors
are now part of ClientConnectorError. This shim adds it back as an alias
for compatibility with google-adk/a2a-sdk that expects the old exception name.

This must be imported BEFORE any code that uses aiohttp.
"""

import aiohttp

# Add ClientConnectorDNSError as an alias to ClientConnectorError
# This maintains compatibility with code expecting the old exception name
if not hasattr(aiohttp, 'ClientConnectorDNSError'):
    aiohttp.ClientConnectorDNSError = aiohttp.ClientConnectorError


