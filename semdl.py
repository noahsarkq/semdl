import asyncio, shlex, shutil, string, random, time, argparse
from asyncio import Semaphore
import aiofiles.os as aios
from asyncio.events import AbstractEventLoop
from urllib.parse import urlparse


async def get_rcode_out_err(cmd: list[str]):
    """
    Run subprocess and get rcode, out and err
    """
    process = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    out, err = [x.decode().strip() for x in await process.communicate()]
    rcode = process.returncode

    return rcode, out, err


async def ytdl_dl(ytdl_opts: str, url: str):
    """
    Download url using youtube-dl
    """
    cmd = shlex.split(f'yt-dlp {ytdl_opts} "{url}"')
   # print(cmd)
    rcode, out, err = await get_rcode_out_err(cmd)
    if rcode:
        print(err)
    return rcode


async def download_sem(url: str, filename: str = None, refer: str = None):
    sem = Semaphore(2)
    if refer == None:
        pu = urlparse(url)
        base_url = f"{pu.scheme}://{pu.netloc}"
    else:
        base_url = refer

    referx = f"--referer {base_url} --add-header Origin:{base_url} --add-header referer:{base_url}"
    ytdl_opts = (
        f'{referx} --downloader aria2c --downloader-args "aria2c: -s 8 -k 2m -x 16 -j 32"'
    )
    audio_p = ''.join([
        random.choice(string.digits + string.ascii_lowercase)
        for _ in range(20)
    ])
    video_p = ''.join([
        random.choice(string.digits + string.ascii_lowercase)
        for _ in range(20)
    ])

    ytdl_opts = f'{ytdl_opts} -f "ba" -o "{audio_p}"'
    audio_dl = ytdl_dl_sem(ytdl_opts, url, sem)
    ytdl_opts = f'{ytdl_opts} -f "bv" -o "{video_p}"'
    video_dl = ytdl_dl_sem(ytdl_opts, url, sem)
    await asyncio.gather(audio_dl, video_dl)
    if filename == None:
        filename = f"{int(time.time())}_{''.join([random.choice(string.ascii_lowercase) for _ in range(5)])}.mkv"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_p,
        "-i",
        audio_p,
        "-c",
        "copy",
        filename,
    ]
    # print(cmd)
    rcode3, out3, err3 = await get_rcode_out_err(cmd)
    # print(rcode3, out3, err3)
    await aios.remove(audio_p)
    await aios.remove(video_p)


async def ytdl_dl_sem(ytdl_opts: str, url: str, sem: Semaphore):
    """
    Download url using youtube-dl, with semaphore
    """
    async with sem:
        return await ytdl_dl(ytdl_opts, url)


async def real_main():
    """
    Run from command line
    """
    parser = argparse.ArgumentParser(description="Download videos from url",
                                     allow_abbrev=True)
    parser.add_argument("URL", help="video urls")

    parser.add_argument(
        "--output",
        "-o",
        dest="filename",
        type=str,
        help="Filename for downloaded video. Default is output.mp4",
        default=None,
        required=False,
    )
    parser.add_argument(
        "--referer",
        "-r",
        dest="refer",
        type=str,
        help="Referer",
        default=None,
        required=False,
    )

    args = parser.parse_args()

    urls = args.URL
    await download_sem(urls, args.filename, args.refer)


def main():
    loop: AbstractEventLoop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(real_main())
    loop.close()


if __name__ == "__main__":
    main()