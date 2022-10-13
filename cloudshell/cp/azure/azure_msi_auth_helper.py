import logging
import time

from msrestazure.azure_active_directory import _ImdsTokenProvider, MSIAuthentication

try:
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs

from requests import HTTPError
import requests

from msrestazure.azure_exceptions import MSIAuthenticationTimeoutError

_LOGGER = logging.getLogger(__name__)

PROXIES = {
    "http": None,
    "https": None
}


class QualiImdsTokenProvider(_ImdsTokenProvider):
    def _retrieve_token_from_imds_with_retry(self, resource):
        import random
        import json
        request_uri = 'http://169.254.169.254/metadata/identity/oauth2/token'
        payload = {
            'resource': resource,
            'api-version': '2018-02-01'
        }
        if self.identity_id:
            payload[self.identity_type] = self.identity_id

        retry, max_retry, start_time = 1, 12, time.time()
        slots = [100 * ((2 << x) - 1) / 1000 for x in range(max_retry)]
        has_timed_out = self.timeout == 0
        while True:
            result = requests.get(request_uri, params=payload,
                                  headers={'Metadata': 'true',
                                           'User-Agent': self._user_agent},
                                  proxies=PROXIES)
            _LOGGER.debug("MSI: Retrieving a token from %s, with payload %s",
                          request_uri, payload)
            if result.status_code in [404, 410, 429] or (
                    499 < result.status_code < 600):
                if has_timed_out:
                    raise MSIAuthenticationTimeoutError(
                        'MSI: Failed to acquired tokens before timeout {}'.format(
                            self.timeout))
                elif retry <= max_retry:
                    wait = random.choice(slots[:retry])
                    _LOGGER.warning("MSI: wait: %ss and retry: %s", wait, retry)
                    has_timed_out = self._sleep(wait, start_time)
                    retry += 1
                else:
                    if result.status_code == 410:
                        gap = 70 - (time.time() - start_time)
                        if gap > 0:
                            _LOGGER.warning(
                                "MSI: wait till 70 seconds when IMDS is upgrading")
                            has_timed_out = self._sleep(gap, start_time)
                            continue
                    break
            elif result.status_code != 200:
                raise HTTPError(request=result.request, response=result.raw)
            else:
                break

        if result.status_code != 200:
            raise MSIAuthenticationTimeoutError(
                'MSI: Failed to acquire tokens after {} times'.format(max_retry))

        _LOGGER.debug('MSI: Token retrieved')
        token_entry = json.loads(result.content.decode())
        return token_entry


class QualiMSIAuthentication(MSIAuthentication):
    def set_token(self):
        if not isinstance(self._vm_msi, QualiImdsTokenProvider):
            cache = self._vm_msi.cache
            timeout = self._vm_msi.timeout
            self._vm_msi = QualiImdsTokenProvider(self.msi_conf, timeout)
            self._vm_msi.cache = cache
        super().set_token()
