import asyncio
from patchright.async_api import async_playwright, expect
from fake_useragent import FakeUserAgent
from names_generator import generate_name
from config import list_types_knowledges
import random

from loguru import logger

with open('emails.txt', 'r') as file:
    emails = [line.strip() for line in file.readlines()]
logger.debug(f'loaded {len(emails)} mails')

with open('proxy.txt', 'r') as file:
    proxys = [line.strip() for line in file.readlines()]
logger.debug(f'loaded {len(proxys)} proxy')

async def registration(mail_address, proxy):
    async with async_playwright() as pw:
        context = await pw.chromium.launch_persistent_context(
            user_data_dir="",
            channel="chrome",
            headless=False,
            no_viewport=True,
            proxy=proxy,
            user_agent=FakeUserAgent().random
        )

        page = await context.new_page()
        await page.goto('https://hi.saharalabs.ai/get-started')

        first_name = page.get_by_placeholder('First name *')
        last_name = page.get_by_placeholder('Last name *')
        email = page.get_by_placeholder('Email *')

        name = generate_name().split('_')

        await expect(first_name).to_be_enabled()
        await first_name.fill(name[0])

        await expect(last_name).to_be_enabled()
        await last_name.fill(name[1])

        await expect(email).to_be_enabled()
        await email.fill(mail_address)

        check_box = page.locator('//*[@id="hsForm_b8ef3646-4f6a-4389-a9b1-3958123c4778_67"]/fieldset[3]/div/div/div/ul/li[1]/label/span')
        await expect(check_box).to_be_enabled()
        await check_box.click()

        check_box_xpath = random.choice(list_types_knowledges)

        check_box = page.locator(check_box_xpath)
        await expect(check_box).to_be_enabled()
        await check_box.click()

        xpath = '//*[@id="hsForm_b8ef3646-4f6a-4389-a9b1-3958123c4778_67"]/fieldset[5]/div/div/div/div/div/ul/li/label'
        check_box = page.locator(xpath)
        await expect(check_box).to_be_enabled()
        await check_box.click()

        await asyncio.sleep(3)

        btn = page.locator('//*[@id="hsForm_b8ef3646-4f6a-4389-a9b1-3958123c4778_67"]/div/div[2]/input')
        await expect(btn).to_be_enabled()
        await btn.click()

        await asyncio.sleep(10)
        if 'success' in page.url:
            logger.info(f'success registration in wl || email -> {mail_address}')
        else:
            logger.error(f'error registration in wl || email -> {mail_address}')

        await context.close()

async def main():
    if len(proxys) != len(emails):
        logger.error(f'the number of proxies({len(proxys)}) and emails({len(emails)}) does not match')
        logger.error(f'кол-во проксей({len(proxys)}) и емайлов({len(emails)}) не совпадает')
        raise
    
    for i in range(len(proxys)):
        proxy = proxys[i]
        proxy = proxy.split(':')

        proxy = {
            'server':f'http://{proxy[0]}:{proxy[1]}',
            'username':f'{proxy[2]}',
            'password':f'{proxy[3]}'
        }

        email = emails[i]
        await registration(proxy=proxy,mail_address=email)

asyncio.run(main())
