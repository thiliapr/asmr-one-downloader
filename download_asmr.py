"获取音声作品（RJ号）的元数据及文件清单，并下载到指定目录。支持自定义镜像站点和代理设置。"

# SPDX-FileCopyrightText: 2025 thiliapr <thiliapr@tutanota.com>
# SPDX-FileContributor: thiliapr <thiliapr@tutanota.com>
# SPDX-License-Identifier: AGPL-3.0-or-later

import argparse
from functools import partial
from io import StringIO
import pathlib
import subprocess
import shutil
import tempfile
from typing import Optional
import orjson


def request_by_curl(
    url: str,
    doh_url: str,
    save_to_file: Optional[pathlib.Path] = None,
    show_progress: bool = False,
    proxy: Optional[str] = None,
    timeout: Optional[float] = None,
    curl_path: Optional[pathlib.Path] = None,
    args: Optional[list[str]] = None
) -> bytes:
    """
    使用 curl 命令获取指定 URL 的内容。

    Args:
        url: 要获取的 URL。
        doh_url: DoH URL，用于 DNS over HTTPS 查询。
        save_to_file: 如果指定，则将内容保存到该文件路径，否则输出到标准输出。
        show_progress: 是否显示下载进度条。
        proxy: 代理地址，格式为 {protocol}://{host}:{port}。
        timeout: 超时时间，单位为秒。
        curl_path: curl 命令路径，如果为 None，则使用系统默认的 curl。
        args: 可选的其他 curl 参数。

    Returns:
        获取到的内容字节串。
    """
    # 如果未指定 curl_path，则尝试使用 shutil.which 查找系统中的 curl 命令。
    if curl_path is None:
        curl_path = shutil.which("curl")

    # 如果 curl_path 为 None 或不存在，则抛出异常。
    if curl_path is None or not pathlib.Path(curl_path).exists():
        raise FileNotFoundError(f"curl 文件（{curl_path}）未找到，请安装 curl 或指定其路径。")

    # 构建 curl 命令
    cmd = [str(curl_path), "--http3", "--doh-url", doh_url, url]

    # 如果指定了保存路径，则添加 -o 参数
    # 否则，使用 -o - 将输出重定向到标准输出。
    if save_to_file is not None:
        cmd.extend(["--output", str(save_to_file), "--continue-at", "-"])
    else:
        cmd.extend(["--output", "-"])  # 输出到标准输出

    # 添加进度条或静默模式
    if show_progress:
        cmd.append("--progress-bar")
    else:
        cmd.append("--silent")

    # 添加代理设置
    if proxy:
        cmd.extend(["--proxy", proxy])

    # 添加超时时间设置
    if timeout:
        cmd.extend(["--connect-timeout", str(timeout)])

    # 如果提供了额外的 curl 参数，则添加到命令中
    if args:
        cmd.extend(args)

    # 执行 curl 命令并返回输出
    return subprocess.check_output(cmd)


def convert_directory_to_files(directory: dict, current_path: pathlib.PurePath = pathlib.PurePath(".")) -> list[tuple[pathlib.PurePath, dict]]:
    """
    将目录结构转换为文件列表。

    Args:
        directory: 目录结构字典，包含子目录和文件信息。
        current_path: 当前路径，用于递归构建完整路径。

    Returns:
        包含所有文件的完整路径列表。
    """
    # 初始化文件列表
    files = []

    # 遍历目录中的子项
    for item in directory.get("children", []):
        # 如果子项是文件夹，则递归调用函数获取其下的文件
        if item["type"] == "folder":
            files.extend(convert_directory_to_files(item, current_path / item["title"]))
        # 如果子项是文件，则将其完整路径添加到文件列表
        else:
            files.append((current_path / item["title"], item))

    # 返回所有文件的完整路径列表
    return files


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """
    解析命令行参数。

    Args:
        args: 可选的命令行参数列表。如果为 None，则使用 sys.argv[1:]。
    
    Returns:
        解析后的命令行参数对象。
    """
    parser = argparse.ArgumentParser(description="从 asmr.one 获取音声作品的元数据和文件清单，并下载到指定目录。")
    parser.add_argument("rj_id", type=int, help="音声的 RJ 号。例如网址为 https://www.dlsite.com/maniax/work/=/product_id/RJ285384.html，则 RJ 号为 285384")
    parser.add_argument("-e", "--endpoint", type=str, default="https://api.asmr-200.com", help="下载的镜像站点，默认为 %(default)s")
    parser.add_argument("-o", "--output-path", type=pathlib.Path, help="音声保存路径，默认为: 当前目录 / work / '{TITLE} [{RJ_ID}] [{circle_name}]'，其中 TITLE 为音声标题，RJ_ID 为音声 RJ 号，circle_name 为社团名称")
    parser.add_argument("-d", "--doh-url", type=str, default="https://v.recipes/dns-query", help="DoH URL，默认为 %(default)s")
    parser.add_argument("-c", "--curl-path", type=pathlib.Path, help="curl 命令的路径，如果未指定则使用系统默认的 curl")
    parser.add_argument("-i", "--editor-path", type=pathlib.Path, help="编辑器的路径。如果未指定，则尝试使用系统默认的编辑器（notepad 或 gedit）")
    parser.add_argument("-p", "--proxy", type=str, help="代理地址，格式为 {protocol}://{host}:{port}，例如 socks5h://127.0.1:1080（socks5h的`h`表示解析域名时使用代理，不建议省略）")
    parser.add_argument("-t", "--timeout", type=int, default=10, help="请求超时时间，单位为秒，默认为 %(default)s 秒")
    parser.add_argument("-v", "--detail", action="store_true", help="在询问要下载的文件时，显示文件大小和音频时长等详细信息")
    return parser.parse_args(args)


def main(args: argparse.Namespace):
    # 使用 partial 函数预设参数，方便后续调用
    fast_curl = partial(request_by_curl, doh_url=args.doh_url, proxy=args.proxy, timeout=args.timeout, curl_path=args.curl_path)

    # 获取音声信息
    work_info = orjson.loads(fast_curl(f"{args.endpoint}/api/workInfo/{args.rj_id}"))

    # 打印音声信息
    print("音声信息:")
    for key, value in work_info.items():
        if isinstance(value, str):
            print(f"{key}: {value}")
    print()

    # 设置输出路径
    output_path = args.output_path or pathlib.Path.cwd() / f"work/{work_info['title']} [{work_info['id']}] [{work_info['name']}]"

    # 获取音声目录结构
    directory = {
        "type": "folder",
        "children": orjson.loads(fast_curl(f"{args.endpoint}/api/tracks/{args.rj_id}?v=2"))
    }

    # 将目录结构转换为文件列表
    files = convert_directory_to_files(directory)

    # 获取文本编辑器
    if args.editor_path:
        editor_path = args.editor_path
    else:
        # 尝试使用系统默认的文本编辑器
        if editor_path := shutil.which("notepad"):
            pass
        elif editor_path := shutil.which("gedit"):
            pass
        else:
            raise FileNotFoundError("未找到可用的文本编辑器，请指定 --editor-path 参数。")

        # 确保编辑器路径是 pathlib.Path 对象
        editor_path = pathlib.Path(editor_path)

    # 检测编辑器是否存在
    if not editor_path.exists():
        raise FileNotFoundError(f"编辑器文件（{editor_path}）未找到，请安装编辑器或指定其路径。")

    with tempfile.TemporaryDirectory() as temp_dir:
        # 将文件列表写入临时文件，然后打开notepad编辑，以询问哪个文件需要下载（像git commit一样）
        temp_file_path = pathlib.Path(temp_dir) / f"asmr_one_download_{args.rj_id}.txt"

        # 使用 StringIO 来构建文件内容
        content = StringIO()
        content.write("# 每一行代表一个文件。注释行以 # 开头，不用管它们。\n")
        content.write("# 请删除不想下载的文件，然后保存并关闭编辑器。\n\n")

        for path, info in files:
            if args.detail:
                # 写入文件信息
                content.write(f"# size={info['size'] / 1024 ** 2:.3f} MiB")

                # 如果是音频文件，添加时长信息
                if info["type"] == "audio":
                    duration = info['duration']
                    content.write(f", duration={int(duration // 60)}min{duration % 60:.2f}sec")

                # 添加换行
                content.write("\n")

            # 写入文件路径
            content.write(f"{path}\n")

        # 创建临时文件并写入内容
        with open(temp_file_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(content.getvalue())

        # 打开临时文件以供用户编辑
        subprocess.run([str(editor_path), str(temp_file_path)], check=True)

        # 读取用户选择的文件列表
        with open(temp_file_path, "r", encoding="utf-8") as temp_file:
            selected_files = [line.strip() for line in temp_file if line.strip() and not line.strip().startswith("#")]

    # 筛选出用户选择的文件
    selected_files_data = [file for file in files if str(file[0]) in selected_files]

    # 打印用户选择的文件路径
    print("将要下载的文件:")
    for file_path, _ in selected_files_data:
        print(file_path)
    print()

    with tempfile.TemporaryDirectory() as download_temp_dir:
        download_temp_dir = pathlib.Path(download_temp_dir)

        # 下载用户选择的文件
        for file_path, file_info in selected_files_data:
            # 确保输出路径的父目录存在
            file_output_path = output_path / file_path
            file_output_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件到临时目录
            # 使用哈希值作为文件名，避免 curl 下载时的路径问题
            download_temp_file = download_temp_dir / file_info["hash"].replace("/", "_")
            if file_output_path.exists():
                if file_output_path.stat().st_size >= file_info["size"]:
                    continue
                shutil.copy(file_output_path, download_temp_file)
            else:
                download_temp_file.write_bytes(b"")  # 确保文件存在

            # 打印正在下载的文件
            print(file_path)

            # 获取文件下载链接
            url = file_info["mediaDownloadUrl"]

            # 获取下载链接状态码，如果状态码不是 200，则尝试 mediaStreamUrl 作为备用下载链接
            response_header = fast_curl(url, args=["--head"])
            if int(response_header.splitlines()[0].split()[1]) != 200:
                # 尝试 mediaStreamUrl 作为备用下载链接
                url = file_info["mediaStreamUrl"]

                # 如果 mediaStreamUrl 也不可用，则跳过下载
                response_header = fast_curl(url, args=["--head"])
                status_code = int(response_header.splitlines()[0].split()[1])
                if status_code != 200:
                    continue

            # 下载到临时文件
            try:
                while download_temp_file.stat().st_size < file_info["size"]:
                    try:
                        fast_curl(url, save_to_file=download_temp_file, show_progress=True)
                    except subprocess.CalledProcessError:
                        # 如果下载失败，可能是网络问题或链接失效，重试下载
                        pass
            except KeyboardInterrupt:
                break
            finally:
                # 将下载的文件移动到输出路径
                shutil.move(download_temp_file, file_output_path)


if __name__ == "__main__":
    main(parse_args())
