from collectors.pages_collector import PagesCollector
from urllib import parse

import async_requests
import re
import random
import string
import lxml
import lxml.html
import aiohttp


BASE_URL = "http://freeproxylists.net/?page={}"


class Collector(PagesCollector):
    """pages from 1"""

    # __collector__ = True
    # TODO: doesn't work, fix!
    # recaptcha accepts any word
    __collector__ = False

    def __init__(self):
        self.dynamic_pages_count = True

    async def process_page(self, page_index):
        async with aiohttp.ClientSession() as session:
            result = []

            resp = await async_requests.get(BASE_URL.format(page_index + 1), override_session=session)
            text = resp.text
            # matches = re.search(r"src=\"(.+?recaptcha/api/noscript.+?)\"", text)
            matches = re.search(r"src=\"(.+?recaptcha/api/challenge.+?)\"", text)

            if matches:
                captcha_url = matches.groups()[0]
                print('requesting captcha...')
                print(captcha_url)
                captcha_resp = await async_requests.get(captcha_url, override_session=session)
                print(captcha_resp.text)
                # challenge = re.search(r"recaptcha_challenge_field\".+?value=\"(.+?)\"", captcha_resp.text).groups()[0]
                # ,
                challenge = re.search(r"challenge.+'(.+?)'", captcha_resp.text).groups()[0]
                site_key = re.search(r"site.+'(.+?)'", captcha_resp.text).groups()[0]

                # data = {
                #     "recaptcha_challenge_field": challenge,
                #     "recaptcha_response_field": ''.join(random.choice(string.ascii_letters + string.digits) for _ in
                #                                         range(random.randint(4, 12))),
                #     "submit": "I'm a human",
                # }

                headers = {
                    "Referer": "http://freeproxylists.net",
                }

                # resp = await async_requests.post(captcha_url, data=data, headers=headers, override_session=session)
                reload_url = "http://www.google.com/recaptcha/api/reload?" \
                             "c={}&k={}&reason=i&type=image&lang=en" \
                             "&th=,2ypXKguwFW6UvSXto1a2LsWhsMJrZAjwAAAAaKAAAAB0awOHXxPK1pI0y7YA7ty_" \
                             "-fFe_ORT1_CMpFfrYwONVsEWIfVcS0089_1-" \
                             "eTnzeazXyZjH8zBe0B2BHoYf2tykdxDiJ6cRBLpWFx8eFpO81EDv24FV8vfwMT-" \
                             "HgejYnzg1sArxJtXC-U1bauomd8Qb1DmM8_ssEdReaiyy2Mz8h2s3eyE0kUE-" \
                             "ggt_gY5sDGo8v4_OkxHrYS16EEoDIHEs_HTXyXngZC-97bEL4nSPU0sE09TGSwRhztg6YOeDlYPOkgZ8MH-" \
                             "RDuDZbrIed0biaklXM4RSXF8PiKSkSy8iQj8hNxG_fhd51pjSd3bvVAgyhj9Nx_cFoyKYMC5cmTgSSNCPcM_" \
                             "deLNuReh33dySmp3Z6sPHlPK0ZSUR6oQo8RIhDQRE3aQ8nwOJLH7DLYGoSIzOtaqOVaf9xwLrIJtBxaWAZV4N" \
                             "z0W6OqUhDmVYFBIBepLI-Xit-Q1RzMMj1y50OvuGMWWnbA2zph7f5--" \
                             "KwG6njjK98cGUtojBB_F2CgeTbPaAXj3iB8Xl-oyThq6OjR38JbASJEud16K9HH2HHJNr8q1DbvFTp0wPQ" \
                             "4p6l0MYSAgxLLVnAh42sghUaW4q0Nt57cEh6t3DeQE7Dp87jIUozOveGAtxIEF5ab5D3M4WWysd7OAMgAic80" \
                             "4TBcABHP7_BPdDFd2uvITMe1PSQRZNknkeqatlf4LT0d0KmsjPpIzcoK2F1KsIdVAE3HK0GLp1Wyk9O7NHEfK" \
                             "bWHTq3GxwCWhEs0xBuRCQX7KJJ9TUf36evwkhFn2sBSTMeZTu-VvaaJMljMoXOAwG0dqvgoJcEGjGtSFjpWEi" \
                             "pUxi9ZHuOxUDb40mZh-CoE6EpjdTub01oTCapr1uItFgeuHQv15FMJbdxpsq5OtZLOyEbdyaz7IW_0waqKErO" \
                             "yM8ZAc5AWRtATapgChkGP37E_gIbr7OqCZBqIththvaTWYBG_JKiV_yAlD4tJj5JYtdHlqIZ1ivjxGWl9DuwR" \
                             "gFBlWqqKjM-CGY8diVjJXZDijFXbPpP1Y7a4IY5nhanpgaWTjueNBnhag0AHs_tT6ZcH7AD_f7NDYEllZzIdx1" \
                             "OBhb9zAcG_BJPnbtns4IDObBSKiwJi3eV8HWMscNA5k5mdgEYVSqc91l4EtSW6oYhuq-cDqQ7oeG2dTLKdt4Gn" \
                             "mDC1X10IIg4CkSUrF3NHuFqjzA09k_9AeTCStN3CLV".format(challenge, site_key)

                resp = await async_requests.get(reload_url, headers=headers, override_session=session)

                print(resp.text)

                challenge = re.search(r"finish_reload\('(.+?)'", resp.text).groups()[0]

                print(challenge)

                headers = {
                    "Referer": "http://freeproxylists.net/",
                }

                data = {
                    "recaptcha_challenge_field": challenge,
                    "recaptcha_response_field": ''.join(random.choice(string.ascii_letters + string.digits) for _ in
                                                        range(random.randint(4, 12))),
                }

                resp = await async_requests.get(
                    BASE_URL.format(page_index + 1), data=data, headers=headers, override_session=session)
                text = resp.text

            try:
                tree = lxml.html.fromstring(text)
                table_element = tree.xpath(".//table[@class='DataGrid']")[0]
            except BaseException:
                raise Exception("table not found: {}".format(text))

            rows = table_element.xpath('.//tr')
            for row in rows:
                try:
                    ip = row.xpath('.//td/script')[0].text
                    port = row.xpath('.//td')[1].text
                    if ip is None or port is None:
                        continue

                    ip = parse.unquote(ip)
                    ip = re.search(r">([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?</a>", ip)
                    if ip is None:
                        continue
                    ip = ip.groups()[0]

                    result.append("{}:{}".format(ip, port))
                except IndexError:
                    pass

            return result
