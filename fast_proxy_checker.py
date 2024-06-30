import asyncio
import aiohttp
from aiohttp import ClientError
import time

async def check_proxy(session, proxy, timeout=10):
    try:
        start_time = time.time()
        async with session.get('http://httpbin.org/ip', proxy=f"http://{proxy}", timeout=timeout) as response:
            if response.status == 200:
                elapsed = time.time() - start_time
                return proxy, True, elapsed
    except Exception as e:
        pass
    return proxy, False, None

async def main(proxy_file, output_file, list_file):
    async with aiohttp.ClientSession() as session:
        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]

        tasks = [check_proxy(session, proxy) for proxy in proxies]
        results = await asyncio.gather(*tasks)

        working_proxies = [r for r in results if r[1]]
        
        print(f"Checked {len(proxies)} proxies.")
        print(f"Working proxies: {len(working_proxies)}")
        
        with open(output_file, 'w') as out_f, open(list_file, 'w') as list_f:
            out_f.write(f"Checked {len(proxies)} proxies.\n")
            out_f.write(f"Working proxies: {len(working_proxies)}\n\n")
            
            for proxy, _, elapsed in working_proxies:
                out_f.write(f"Proxy: {proxy}, Response time: {elapsed:.2f} seconds\n")
                list_f.write(f"{proxy}\n")
                print(f"Proxy: {proxy}, Response time: {elapsed:.2f} seconds")

        print(f"\nResults written to {output_file}")
        print(f"Working proxy list written to {list_file}")

if __name__ == "__main__":
    proxy_file = "proxy_list.txt"  # Replace with your input proxy file name
    output_file = "working_proxies_details.txt"
    list_file = "working_proxies_list.txt"
    asyncio.run(main(proxy_file, output_file, list_file))